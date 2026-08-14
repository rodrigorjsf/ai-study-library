package com.example.errorprone;

import com.google.auto.service.AutoService;
import com.google.errorprone.BugPattern;
import com.google.errorprone.VisitorState;
import com.google.errorprone.bugpatterns.BugChecker;
import com.google.errorprone.bugpatterns.BugChecker.SynchronizedTreeMatcher;
import com.google.errorprone.matchers.Description;
import com.google.errorprone.util.ASTHelpers;
import com.sun.source.tree.*;
import com.sun.tools.javac.code.Symbol;

import javax.lang.model.element.Modifier;

import static com.google.errorprone.BugPattern.SeverityLevel.ERROR;
import static com.google.errorprone.matchers.Description.NO_MATCH;

/**
 * Closes the blind spot ArchUnit cannot see.
 *
 * ArchUnit reads bytecode and never observes monitorenter/monitorexit, so
 * `static void f() { synchronized (Lock.class) { ... } }` passes every
 * structural rule while behaving exactly like `static synchronized`.
 * Error Prone works on the AST during compilation, where the block is visible.
 *
 * Flags a synchronized block when the monitor is effectively process-wide:
 *   1. the block sits in a static method or a static initializer
 *   2. the lock is a class literal (Foo.class) or getClass()
 *   3. the lock resolves to a static field
 *
 * Each of these serializes every request in the JVM through one monitor.
 * JEP 491 (Java 24+) stopped such a block from pinning a carrier thread, but
 * the contention is unchanged: with virtual threads the queue simply moves,
 * and p99 latency degrades well before the mean does.
 */
@AutoService(BugChecker.class)
@BugPattern(
        name = "StaticMonitorSynchronization",
        summary = "synchronized on a class-wide or static monitor serializes every request in the JVM",
        explanation =
                "A synchronized block whose monitor is a class literal, a static field, or which sits "
                        + "in a static context, is a single global lock for the whole process. Under high "
                        + "RPM this is a hard throughput ceiling and the first thing to show up in tail "
                        + "latency. JEP 491 removed virtual-thread pinning for monitors, which often "
                        + "masks the problem: the carrier no longer stalls, so the symptom disappears "
                        + "while the bottleneck remains.\n\n"
                        + "Replace with a lock scoped to the contended key (a striped lock keyed by "
                        + "tenant, account, or entity id), an immutable snapshot published through "
                        + "AtomicReference, or a lock-free structure. If the state must be consistent "
                        + "across replicas, a JVM lock was never sufficient anyway — it is a singleton "
                        + "per JVM, not per system: use an atomic operation in Redis or DynamoDB.",
        severity = ERROR,
        linkType = BugPattern.LinkType.CUSTOM,
        link = "https://internal.example.com/rules/java-concurrency-static")
public final class StaticMonitorSynchronization extends BugChecker implements SynchronizedTreeMatcher {

    @Override
    public Description matchSynchronized(SynchronizedTree tree, VisitorState state) {
        String reason = diagnose(tree, state);
        if (reason == null) {
            return NO_MATCH;
        }
        return buildDescription(tree)
                .setMessage(message() + " — " + reason)
                .build();
    }

    /** Returns a human-readable reason, or null when the block is acceptable. */
    private static String diagnose(SynchronizedTree tree, VisitorState state) {
        ExpressionTree lock = ASTHelpers.stripParentheses(tree.getExpression());

        // 2. Foo.class as a monitor — the same object the JVM uses for `static synchronized`.
        if (lock.getKind() == Tree.Kind.MEMBER_SELECT) {
            MemberSelectTree select = (MemberSelectTree) lock;
            if (select.getIdentifier().contentEquals("class")) {
                return "the monitor is a class literal, the same object `static synchronized` locks";
            }
        }

        // 2b. getClass() — one monitor per class, shared by every instance.
        if (lock.getKind() == Tree.Kind.METHOD_INVOCATION) {
            MethodInvocationTree call = (MethodInvocationTree) lock;
            Symbol.MethodSymbol sym = ASTHelpers.getSymbol(call);
            if (sym != null && sym.getSimpleName().contentEquals("getClass")) {
                return "the monitor is getClass(), which is shared by every instance of the class";
            }
        }

        // 3. A static field used as the monitor.
        Symbol lockSymbol = ASTHelpers.getSymbol(lock);
        if (lockSymbol != null
                && lockSymbol.getKind().isField()
                && lockSymbol.getModifiers().contains(Modifier.STATIC)) {
            return "the monitor is the static field `" + lockSymbol.getSimpleName()
                    + "`, so all threads in the JVM contend on it";
        }

        // 1. Static context: even an instance-looking monitor is process-wide here.
        if (inStaticContext(state)) {
            return "the block is in a static context, so the monitor is process-wide "
                    + "regardless of what it locks";
        }

        return null;
    }

    private static boolean inStaticContext(VisitorState state) {
        for (Tree parent : state.getPath()) {
            if (parent instanceof MethodTree method) {
                return method.getModifiers().getFlags().contains(Modifier.STATIC);
            }
            // A static initializer appears as a BlockTree with isStatic() == true,
            // directly under the ClassTree.
            if (parent instanceof BlockTree block && block.isStatic()) {
                return true;
            }
            if (parent instanceof LambdaExpressionTree) {
                // Keep walking: a lambda inherits the staticness of its enclosing member.
                continue;
            }
            if (parent instanceof ClassTree) {
                // Reached the class without finding a method — anonymous/initializer edge.
                return false;
            }
        }
        return false;
    }
}
