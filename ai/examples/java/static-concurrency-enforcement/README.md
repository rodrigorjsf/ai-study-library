# Static / concurrency enforcement — executable examples

Reference implementations that make the Java concurrency & `static` rule
([Claude](../../../rules/claude/java-concurrency-static.md) ·
[Cursor](../../../rules/cursor/java-concurrency-static.mdc)) executable in CI. The rule
file guides the agent; these files stop a regression from merging. A rule that is not
enforced by the build is a suggestion.

## Contents

| File | Tool | Covers |
| --- | --- | --- |
| `archunit/ConcurrencyArchTest.java` | ArchUnit + JUnit 5 | First pass: one rule per numbered section of the document |
| `archunit/ConcurrencyArchTestV2.java` | ArchUnit + JUnit 5 | Revised pass: recursive immutability, I/O detected through indirection, all rules frozen against a baseline |
| `errorprone/StaticMonitorSynchronization.java` | Error Prone `BugChecker` | `synchronized (...)` blocks on a class-wide or static monitor |

## Why three files and not one

ArchUnit reads **bytecode**. A `synchronized` block compiles to `monitorenter` /
`monitorexit`, which the importer does not expose, so
`static void f() { synchronized (Lock.class) { … } }` passes every structural rule while
behaving exactly like `static synchronized`. Error Prone runs on the **AST** during
compilation, where the block is still visible — hence the `BugChecker`. The two tools are
complementary, not alternatives.

## V1 → V2

- The dead placeholder rule (`no_static_synchronized_methods`, matching
  `alwaysFalse()`) is removed; the real `JavaModifier.SYNCHRONIZED` check is the only one left.
- `no_non_final_static_fields` is written as an explicit `ArchCondition` instead of an
  always-true `notBeDeclaredInClassesThat` predicate — same outcome, readable intent.
- Record immutability is checked **recursively**: a `record` holding a `List` component is
  no longer treated as a safe constant.
- I/O detection follows indirection through a `@PerformsIo` marker, so a hand-rolled
  factory or wrapper is caught, not just direct SDK calls.
- Every rule is wrapped in `FreezingArchRule`: existing violations are recorded once in a
  baseline, and only **new** violations break the build. This is what makes the rule
  adoptable on an existing codebase.

## Adopting these

1. Add the dependencies (`com.tngtech.archunit:archunit-junit5`, and
   `com.google.errorprone:error_prone_check_api` + `com.google.auto.service:auto-service`
   for the checker) and rename the `com.example` package to your own.
2. Review the vocabulary sets — `IMMUTABLE_VALUE_TYPES`, `MUTABLE_HOLDER_TYPES`,
   `IO_CLIENT_TYPES` — against your actual stack. Extend deliberately, never casually:
   adding a type to `IMMUTABLE_VALUE_TYPES` silently disables a check for it.
3. For V2, create the freeze baseline once with
   `-Darchunit.freeze.store.default.allowStoreCreation=true`, then commit
   `archunit_store/` so the whole team shares it. Regenerating it casually forgives real
   regressions without anyone noticing.
4. Register the Error Prone checker on the compiler's annotation processor path and keep
   its severity at `ERROR`.

## Caveats

These files are teaching examples, not a drop-in library. They target Java 25 (virtual
threads, `ScopedValue`, `StructuredTaskScope`) and a specific stack — AWS SDK v2 /
DynamoDB, Lettuce and Jedis, Kafka, OpenTelemetry. On a different stack the rules still
hold, but the type lists do not.
