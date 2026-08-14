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

import java.util.List;
import java.util.Set;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.*;

/**
 * Enforces .claude/rules/java-concurrency-static.md in CI.
 * Each rule maps to a numbered section of that document.
 */
@AnalyzeClasses(
        packages = "com.example",
        importOptions = {ImportOption.DoNotIncludeTests.class, ImportOption.DoNotIncludeJars.class})
class ConcurrencyArchTest {

    // ------------------------------------------------------------------
    // Shared vocabulary
    // ------------------------------------------------------------------

    /** Types safe to hold in a static final field. Extend deliberately, never casually. */
    private static final Set<String> IMMUTABLE_VALUE_TYPES = Set.of(
            "java.lang.String", "java.lang.Integer", "java.lang.Long", "java.lang.Double",
            "java.lang.Boolean", "java.lang.Character", "java.lang.Byte", "java.lang.Short",
            "java.lang.Float", "java.lang.Class", "java.math.BigDecimal", "java.math.BigInteger",
            "java.time.Duration", "java.time.Period", "java.time.ZoneId", "java.time.ZoneOffset",
            "java.time.format.DateTimeFormatter", "java.util.UUID", "java.util.regex.Pattern",
            "java.net.URI");

    /** Mutable collection/date types that must never be static, even when final. */
    private static final Set<String> MUTABLE_HOLDER_TYPES = Set.of(
            "java.util.List", "java.util.ArrayList", "java.util.LinkedList",
            "java.util.Map", "java.util.HashMap", "java.util.LinkedHashMap", "java.util.TreeMap",
            "java.util.Set", "java.util.HashSet", "java.util.LinkedHashSet", "java.util.TreeSet",
            "java.util.Collection", "java.util.Date", "java.util.Calendar",
            "java.util.concurrent.ConcurrentHashMap", "java.util.concurrent.ConcurrentMap",
            "java.lang.StringBuilder", "java.text.SimpleDateFormat");

    /** I/O clients that need a managed lifecycle (shutdown on SIGTERM), so never static. */
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

    private static boolean isImmutableConstant(JavaField field) {
        String type = field.getRawType().getName();
        return field.getRawType().isPrimitive()
                || IMMUTABLE_VALUE_TYPES.contains(type)
                || field.getRawType().isEnum()
                // records are only safe if their components are; treat as safe but review
                || field.getRawType().isRecord();
    }

    // ------------------------------------------------------------------
    // Section 1 — no mutable static state
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule no_non_final_static_fields =
            fields().that().areStatic().and().areNotFinal()
                    .should().notBeDeclaredInClassesThat(new DescribedPredicate<>("any class") {
                        @Override
                        public boolean test(JavaClass input) {
                            return true;
                        }
                    })
                    .because("a non-final static field has no visibility guarantee across threads; "
                            + "the JIT may hoist the read out of a loop, and long/double admit torn reads. "
                            + "Use AtomicReference<ImmutableSnapshot> or an injected singleton instead");

    @ArchTest
    static final ArchRule static_final_fields_must_hold_immutable_types =
            fields().that().areStatic().and().areFinal()
                    .should(new ArchCondition<>("hold an immutable type") {
                        @Override
                        public void check(JavaField field, ConditionEvents events) {
                            String type = field.getRawType().getName();
                            if (MUTABLE_HOLDER_TYPES.contains(type)) {
                                events.add(SimpleConditionEvent.violated(field,
                                        "static final field " + field.getFullName() + " holds mutable type " + type
                                                + " — final protects the reference, not the contents. "
                                                + "Move it to a singleton bean (Caffeine) or to Redis/Dynamo "
                                                + "if the state must be global to the system, not per JVM"));
                            }
                        }
                    });

    @ArchTest
    static final ArchRule no_static_thread_locals =
            noFields().that().areStatic()
                    .should().haveRawType(ThreadLocal.class)
                    .because("with virtual threads each thread carries its own copy — at hundreds of "
                            + "thousands of VTs this is a memory leak, and an orphaned ThreadLocal is "
                            + "never cleaned. Use ScopedValue (JEP 506)");

    // ------------------------------------------------------------------
    // Section 1 & 3 — no class-level monitor
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule no_static_synchronized_methods =
            noMethods().that().areStatic()
                    .should().beAnnotatedWith(DescribedPredicate.alwaysFalse()) // placeholder, real check below
                    .because("see static_synchronized_condition");

    @ArchTest
    static final ArchRule static_synchronized_is_forbidden =
            methods().that().areStatic()
                    .should(new ArchCondition<>("not be synchronized") {
                        @Override
                        public void check(JavaMethod method, ConditionEvents events) {
                            if (method.getModifiers().contains(JavaModifier.SYNCHRONIZED)) {
                                events.add(SimpleConditionEvent.violated(method,
                                        "static synchronized method " + method.getFullName()
                                                + " locks the Class object — one global monitor for every request. "
                                                + "JEP 491 removed VT pinning but not the contention: the queue "
                                                + "remains and p99 latency degrades before the mean moves. "
                                                + "Use a striped/per-key lock or a lock-free structure"));
                            }
                        }
                    });

    // ------------------------------------------------------------------
    // Section 1 & 4 — I/O clients must be managed beans
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule io_clients_are_never_static =
            noFields().that().areStatic()
                    .should().haveRawType(new DescribedPredicate<>("an I/O client type") {
                        @Override
                        public boolean test(JavaClass type) {
                            return IO_CLIENT_TYPES.contains(type.getName());
                        }
                    })
                    .because("a static client has no lifecycle: no ordered close() on SIGTERM (5xx during "
                            + "every rolling update), no credential rotation, no per-environment timeouts. "
                            + "Declare it as a singleton bean instead — same single instance, managed");

    /** Raw Jedis is not thread-safe at all: concurrent use interleaves the RESP stream. */
    @ArchTest
    static final ArchRule raw_jedis_is_never_a_shared_field =
            noFields().that().areStatic()
                    .should().haveRawType("redis.clients.jedis.Jedis")
                    .because("a raw Jedis instance wraps one socket with a sequential request/response "
                            + "protocol. Two threads sharing it means one receives the other's response — "
                            + "silent data corruption under load. Use JedisPool, or Lettuce");

    // ------------------------------------------------------------------
    // Section 1 — no I/O in static initializers
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule static_initializers_do_no_io =
            noCodeUnits().that().haveName("<clinit>")
                    .should().callMethodWhere(new DescribedPredicate<>("an I/O or client-building call") {
                        @Override
                        public boolean test(JavaMethodCall call) {
                            String owner = call.getTargetOwner().getName();
                            return IO_CLIENT_TYPES.contains(owner)
                                    || owner.startsWith("software.amazon.awssdk")
                                    || owner.startsWith("io.lettuce")
                                    || owner.startsWith("redis.clients")
                                    || owner.startsWith("java.net")
                                    || owner.startsWith("java.nio.file")
                                    || owner.startsWith("org.apache.kafka");
                        }
                    })
                    .because("the JVM holds a per-class lock during <clinit>: every thread stalls on the "
                            + "first hit right after deploy. Worse, a throw there yields "
                            + "ExceptionInInitializerError once and NoClassDefFoundError forever after — "
                            + "no retry or circuit breaker recovers it, only a pod restart");

    // ------------------------------------------------------------------
    // Section 3 — virtual threads
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule no_pooling_of_virtual_threads =
            noClasses().should().callMethodWhere(new DescribedPredicate<>(
                    "Executors.newFixedThreadPool/newCachedThreadPool with a virtual thread factory") {
                @Override
                public boolean test(JavaMethodCall call) {
                    boolean executors = call.getTargetOwner().getName().equals("java.util.concurrent.Executors");
                    String name = call.getTarget().getName();
                    return executors && (name.equals("newFixedThreadPool") || name.equals("newCachedThreadPool"))
                            && call.getTarget().getRawParameterTypes().stream()
                            .anyMatch(p -> p.getName().equals("java.util.concurrent.ThreadFactory"));
                }
            }).because("virtual threads are not pooled — create one per task with "
                    + "newVirtualThreadPerTaskExecutor() and bound concurrency with an explicit Semaphore "
                    + "sized to downstream capacity");

    @ArchTest
    static final ArchRule thread_locals_are_not_used_for_request_context =
            noFields().should().haveRawType(ThreadLocal.class)
                    .because("use ScopedValue for request context; it is immutable, scope-bound, "
                            + "inherited by StructuredTaskScope, and released automatically");

    // ------------------------------------------------------------------
    // Section 5 — I/O must be interceptable (no static I/O)
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule static_methods_do_not_perform_io =
            noMethods().that().areStatic()
                    .should().callMethodWhere(new DescribedPredicate<>("an external I/O call") {
                        @Override
                        public boolean test(JavaMethodCall call) {
                            String owner = call.getTargetOwner().getName();
                            return owner.startsWith("software.amazon.awssdk.services")
                                    || owner.startsWith("io.lettuce")
                                    || owner.startsWith("redis.clients")
                                    || owner.startsWith("java.net.http")
                                    || owner.startsWith("org.apache.kafka.clients");
                        }
                    })
                    .because("invokestatic cannot be intercepted by a proxy: you lose annotation-driven "
                            + "retry, circuit breaker, bulkhead — and the OTEL span. A static I/O call is "
                            + "a hole in the distributed trace");

    // ------------------------------------------------------------------
    // Section 2 — utility classes stay pure
    // ------------------------------------------------------------------

    @ArchTest
    static final ArchRule utility_classes_hold_no_state =
            classes().that().haveSimpleNameEndingWith("Utils")
                    .or().haveSimpleNameEndingWith("Helper")
                    .should(new ArchCondition<>("declare only immutable constants") {
                        @Override
                        public void check(JavaClass clazz, ConditionEvents events) {
                            List<JavaField> offenders = clazz.getFields().stream()
                                    .filter(f -> !isImmutableConstant(f))
                                    .toList();
                            offenders.forEach(f -> events.add(SimpleConditionEvent.violated(f,
                                    "utility class field " + f.getFullName() + " is not an immutable constant — "
                                            + "a stateful utility is a hidden dependency that leaks between "
                                            + "requests and between tests in the same JVM")));
                        }
                    });
}
