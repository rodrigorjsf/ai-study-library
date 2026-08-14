package com.example.arch;

import com.tngtech.archunit.base.DescribedPredicate;
import com.tngtech.archunit.core.domain.*;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchCondition;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.ConditionEvents;
import com.tngtech.archunit.lang.SimpleConditionEvent;
import com.tngtech.archunit.library.freeze.FreezingArchRule;

import java.util.List;
import java.util.Set;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.*;

/**
 * V2 of ConcurrencyArchTest. Enforces .claude/rules/java-concurrency-static.md.
 *
 * Differences from V1:
 *  - dead placeholder rule removed; the real SYNCHRONIZED-modifier check is the only one
 *  - non-final static check rewritten as an explicit ArchCondition (readable intent)
 *  - record immutability validated recursively instead of assumed
 *  - I/O detection follows indirection via @PerformsIo instead of only direct SDK calls
 *  - every rule wrapped in FreezingArchRule: existing violations are recorded once,
 *    only NEW violations fail the build
 *
 * First run: set -Darchunit.freeze.store.default.allowStoreCreation=true to create the
 * baseline, then commit archunit_store/ so the whole team shares it. Never regenerate it
 * casually — that silently forgives real regressions.
 *
 * Known blind spot (not fixable in ArchUnit): synchronized BLOCKS compile to
 * monitorenter/monitorexit, which the bytecode importer does not expose. Cover
 * `synchronized (` in static context with Error Prone or a CI grep.
 */
@AnalyzeClasses(
        packages = "com.example",
        importOptions = {ImportOption.DoNotIncludeTests.class, ImportOption.DoNotIncludeJars.class})
class ConcurrencyArchTestV2 {

    // ==================================================================
    // Vocabulary
    // ==================================================================

    private static final Set<String> IMMUTABLE_VALUE_TYPES = Set.of(
            "java.lang.String", "java.lang.Integer", "java.lang.Long", "java.lang.Double",
            "java.lang.Boolean", "java.lang.Character", "java.lang.Byte", "java.lang.Short",
            "java.lang.Float", "java.lang.Class", "java.math.BigDecimal", "java.math.BigInteger",
            "java.time.Duration", "java.time.Period", "java.time.ZoneId", "java.time.ZoneOffset",
            "java.time.format.DateTimeFormatter", "java.util.UUID", "java.util.regex.Pattern",
            "java.net.URI");

    private static final Set<String> MUTABLE_HOLDER_TYPES = Set.of(
            "java.util.List", "java.util.ArrayList", "java.util.LinkedList",
            "java.util.Map", "java.util.HashMap", "java.util.LinkedHashMap", "java.util.TreeMap",
            "java.util.Set", "java.util.HashSet", "java.util.LinkedHashSet", "java.util.TreeSet",
            "java.util.Collection", "java.util.Date", "java.util.Calendar",
            "java.util.concurrent.ConcurrentHashMap", "java.util.concurrent.ConcurrentMap",
            "java.lang.StringBuilder", "java.text.SimpleDateFormat");

    private static final Set<String> IO_CLIENT_TYPES = Set.of(
            "software.amazon.awssdk.services.dynamodb.DynamoDbClient",
            "software.amazon.awssdk.services.dynamodb.DynamoDbAsyncClient",
            "software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient",
            "software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedAsyncClient",
            "io.lettuce.core.RedisClient",
            "io.lettuce.core.api.StatefulRedisConnection",
            "io.lettuce.core.cluster.RedisClusterClient",
            "redis.clients.jedis.Jedis",
            "redis.clients.jedis.JedisPool",
            "org.springframework.data.redis.core.RedisTemplate",
            "java.net.http.HttpClient",
            "org.apache.kafka.clients.producer.KafkaProducer",
            "org.apache.kafka.clients.consumer.KafkaConsumer",
            "javax.sql.DataSource");

    private static final Set<String> IO_PACKAGE_PREFIXES = Set.of(
            "software.amazon.awssdk.services", "io.lettuce", "redis.clients",
            "java.net.http", "org.apache.kafka.clients");

    /** Marker your own factories/wrappers carry, so indirection is still caught. */
    private static final String PERFORMS_IO = "com.example.arch.PerformsIo";

    // ==================================================================
    // Helpers
    // ==================================================================

    private static boolean isIoTarget(JavaMethodCall call) {
        JavaClass owner = call.getTargetOwner();
        if (IO_CLIENT_TYPES.contains(owner.getName())) return true;
        if (IO_PACKAGE_PREFIXES.stream().anyMatch(p -> owner.getName().startsWith(p))) return true;
        // follow indirection: our own code annotated as doing I/O
        if (owner.isAnnotatedWith(PERFORMS_IO)) return true;
        return call.getTarget().resolveMember()
                .map(m -> m.isAnnotatedWith(PERFORMS_IO))
                .orElse(false);
    }

    /** Recursive immutability check — a record with a List component is NOT immutable. */
    private static boolean isDeeplyImmutable(JavaClass type, int depth) {
        if (depth > 4) return false; // give up rather than guess
        if (type.isPrimitive() || type.isEnum()) return true;
        if (IMMUTABLE_VALUE_TYPES.contains(type.getName())) return true;
        if (type.isArray()) return false;
        if (MUTABLE_HOLDER_TYPES.contains(type.getName())) return false;
        if (type.isRecord()) {
            return type.getFields().stream()
                    .allMatch(f -> isDeeplyImmutable(f.getRawType(), depth + 1));
        }
        return false;
    }

    private static ArchRule frozen(ArchRule rule) {
        return FreezingArchRule.freeze(rule);
    }

    // ==================================================================
    // Section 1 — no mutable static state
    // ==================================================================

    @ArchTest
    static final ArchRule no_non_final_static_fields = frozen(
            fields().that().areStatic().and().areNotFinal()
                    .should(new ArchCondition<>("not exist") {
                        @Override
                        public void check(JavaField field, ConditionEvents events) {
                            events.add(SimpleConditionEvent.violated(field,
                                    "non-final static field " + field.getFullName()
                                            + " has no cross-thread visibility guarantee: the JIT may hoist "
                                            + "the read out of a loop, and long/double admit torn reads. "
                                            + "Replace with AtomicReference<ImmutableSnapshot> or an injected singleton"));
                        }
                    }));

    @ArchTest
    static final ArchRule static_final_fields_must_be_deeply_immutable = frozen(
            fields().that().areStatic().and().areFinal()
                    .should(new ArchCondition<>("hold a deeply immutable type") {
                        @Override
                        public void check(JavaField field, ConditionEvents events) {
                            JavaClass type = field.getRawType();
                            if (MUTABLE_HOLDER_TYPES.contains(type.getName())) {
                                events.add(SimpleConditionEvent.violated(field,
                                        "static final " + field.getFullName() + " holds mutable type "
                                                + type.getName() + " — final protects the reference, not the "
                                                + "contents, and the field is a GC root that never releases. "
                                                + "Move to a singleton bean (Caffeine) or to Redis/Dynamo if the "
                                                + "state must be global to the system rather than per JVM"));
                            } else if (type.isRecord() && !isDeeplyImmutable(type, 0)) {
                                events.add(SimpleConditionEvent.violated(field,
                                        "static final " + field.getFullName() + " holds record " + type.getName()
                                                + " with at least one mutable component — shallow immutability "
                                                + "is not thread safety"));
                            }
                        }
                    }));

    @ArchTest
    static final ArchRule no_thread_locals_anywhere = frozen(
            noFields().should().haveRawType(ThreadLocal.class)
                    .because("with virtual threads every thread carries its own copy — at hundreds of "
                            + "thousands of VTs that is a memory leak, and orphaned entries are never "
                            + "cleaned. Use ScopedValue (JEP 506) for request context"));

    // ==================================================================
    // Section 1 & 3 — no class-level monitor
    // ==================================================================

    @ArchTest
    static final ArchRule static_synchronized_is_forbidden = frozen(
            methods().that().areStatic()
                    .should(new ArchCondition<>("not be synchronized") {
                        @Override
                        public void check(JavaMethod method, ConditionEvents events) {
                            if (method.getModifiers().contains(JavaModifier.SYNCHRONIZED)) {
                                events.add(SimpleConditionEvent.violated(method,
                                        "static synchronized " + method.getFullName() + " locks the Class object "
                                                + "— one global monitor for every request. JEP 491 removed VT "
                                                + "pinning but not the contention: the queue remains and p99 "
                                                + "degrades before the mean moves. Use a striped/per-key lock"));
                            }
                        }
                    }));

    // ==================================================================
    // Section 1 & 4 — I/O clients need a lifecycle
    // ==================================================================

    @ArchTest
    static final ArchRule io_clients_are_never_static = frozen(
            noFields().that().areStatic()
                    .should().haveRawType(new DescribedPredicate<>("an I/O client type") {
                        @Override
                        public boolean test(JavaClass type) {
                            return IO_CLIENT_TYPES.contains(type.getName());
                        }
                    })
                    .because("a static client has no lifecycle: no ordered close() on SIGTERM (5xx during "
                            + "every rolling update), no credential rotation, no per-environment timeouts. "
                            + "Declare a singleton bean instead — same single instance, but managed"));

    @ArchTest
    static final ArchRule raw_jedis_is_never_a_field = frozen(
            noFields().should().haveRawType("redis.clients.jedis.Jedis")
                    .because("a raw Jedis wraps one socket over a sequential request/response protocol. "
                            + "Two threads sharing it means one receives the other's response — silent "
                            + "data corruption under load. Use JedisPool, or Lettuce"));

    // ==================================================================
    // Section 1 — nothing risky in <clinit>
    // ==================================================================

    @ArchTest
    static final ArchRule static_initializers_do_no_io = frozen(
            noCodeUnits().that().haveName("<clinit>")
                    .should().callMethodWhere(new DescribedPredicate<>("an I/O call") {
                        @Override
                        public boolean test(JavaMethodCall call) {
                            return isIoTarget(call);
                        }
                    })
                    .because("the JVM holds a per-class lock during <clinit>: every thread stalls on the "
                            + "first hit right after deploy. Worse, a throw yields ExceptionInInitializerError "
                            + "once and NoClassDefFoundError forever after — no retry or circuit breaker "
                            + "recovers it, only a pod restart"));

    // ==================================================================
    // Section 3 — virtual threads
    // ==================================================================

    @ArchTest
    static final ArchRule no_pooling_of_virtual_threads = frozen(
            noClasses().should().callMethodWhere(new DescribedPredicate<>(
                    "Executors.newFixedThreadPool/newCachedThreadPool with a ThreadFactory") {
                @Override
                public boolean test(JavaMethodCall call) {
                    if (!call.getTargetOwner().getName().equals("java.util.concurrent.Executors")) return false;
                    String name = call.getTarget().getName();
                    boolean pooling = name.equals("newFixedThreadPool") || name.equals("newCachedThreadPool");
                    return pooling && call.getTarget().getRawParameterTypes().stream()
                            .anyMatch(p -> p.getName().equals("java.util.concurrent.ThreadFactory"));
                }
            }).because("virtual threads are not pooled — one per task via newVirtualThreadPerTaskExecutor(), "
                    + "with concurrency bounded by an explicit Semaphore sized to downstream capacity"));

    // ==================================================================
    // Section 5 — I/O must be interceptable
    // ==================================================================

    @ArchTest
    static final ArchRule static_methods_do_not_perform_io = frozen(
            noMethods().that().areStatic()
                    .should().callMethodWhere(new DescribedPredicate<>("an external I/O call") {
                        @Override
                        public boolean test(JavaMethodCall call) {
                            return isIoTarget(call);
                        }
                    })
                    .because("invokestatic cannot be intercepted by a proxy: you lose annotation-driven "
                            + "retry, circuit breaker, bulkhead — and the OTEL span. A static I/O call is a "
                            + "hole in the distributed trace"));

    // ==================================================================
    // Section 2 — utility classes stay pure
    // ==================================================================

    @ArchTest
    static final ArchRule utility_classes_hold_no_state = frozen(
            classes().that().haveSimpleNameEndingWith("Utils")
                    .or().haveSimpleNameEndingWith("Helper")
                    .should(new ArchCondition<>("declare only deeply immutable constants") {
                        @Override
                        public void check(JavaClass clazz, ConditionEvents events) {
                            List<JavaField> offenders = clazz.getFields().stream()
                                    .filter(f -> !isDeeplyImmutable(f.getRawType(), 0))
                                    .toList();
                            offenders.forEach(f -> events.add(SimpleConditionEvent.violated(f,
                                    "utility field " + f.getFullName() + " is not a deeply immutable constant "
                                            + "— stateful utilities are hidden dependencies that leak between "
                                            + "requests and between tests sharing a JVM")));
                        }
                    }));
}
