# Ecosystems

Per-stack facts the steps need. This file is a cache of tool documentation: confirm each option against the version the repo actually uses (`--help`, the plugin's docs) before relying on it. For a stack not listed, find the same five facts in its documentation: the parameterize construct, the coverage tool, per-test coverage, the mutation tool (and whether it reports which tests kill each mutant), and the speed levers.

## Java and Kotlin (JUnit 5, Maven or Gradle)

- **Parameterize:** `@ParameterizedTest` with `@CsvSource`, `@ValueSource`, `@EnumSource`, or `@MethodSource` for objects; name rows with `name = "{0} -> {1}"`. `@Nested` groups cases that share setup. Kotest: `withData`. Spock: `where:` tables.
- **Coverage:** JaCoCo (`jacoco.xml`).
- **Per-test coverage:** run one test class with JaCoCo and diff the reports.
- **Mutation:** PIT (`pitest-maven`, `gradle-pitest-plugin`), scoped with `targetClasses` and `targetTests`. **Kill matrix:** yes, with `fullMutationMatrix` set to true and `outputFormats` including `XML`; the XML then lists every test that kills each mutant.
- **Speed levers:**
  - JUnit parallel execution (`junit.jupiter.execution.parallel.enabled`), once tests share no mutable state.
  - Maven Surefire `forkCount` and `reuseForks`; Gradle `maxParallelForks` and `forkEvery`.
  - Spring: every distinct context configuration starts a new application context. `@MockBean` / `@MockitoBean`, `@DirtiesContext`, and differing `@TestPropertySource` values each break the context cache. Share one configuration across tests, and use slices (`@WebMvcTest`, `@DataJpaTest`, `@JsonTest`) or plain unit tests in place of `@SpringBootTest` for logic that needs no container.
  - Testcontainers: one container per suite (singleton pattern, or reuse) in place of one per class.
  - Mockito: inline mock maker and static mocking are slow; real objects are faster where the smells file already prefers them.
  - Gradle build cache and test-result caching; Maven or Gradle test selection in CI for unchanged modules.

## JavaScript and TypeScript (Jest, Vitest)

- **Parameterize:** `test.each` / `it.each` with a table; `describe.each` for shared setup.
- **Coverage:** Istanbul or V8 provider (`lcov.info`).
- **Per-test coverage:** run a single file with `--coverage` and diff.
- **Mutation:** Stryker (`@stryker-mutator/core`), scoped with `mutate` globs. **Kill matrix:** yes, with `coverageAnalysis: "perTest"` and the JSON reporter; read the per-mutant list of killing tests from a generated report.
- **Speed levers:**
  - Worker count (`--maxWorkers`, Vitest `pool` and `poolOptions`), and CI sharding (`--shard`).
  - Environment: `node` in place of `jsdom` for tests that touch no DOM.
  - Transform cost: SWC or esbuild transformer in place of `ts-jest` with type-checking; type-check once in a separate step.
  - Module isolation: `jest.resetModules` and per-test re-imports are expensive; Vitest `isolate: false` for pure suites.
  - Fake timers in place of real waiting.

## Python (pytest)

- **Parameterize:** `@pytest.mark.parametrize` with `ids=`; `pytest.param(..., id=...)` for named rows.
- **Coverage:** coverage.py through `pytest-cov`.
- **Per-test coverage:** `--cov-context=test` records which test covered each line.
- **Mutation:** mutmut, or Cosmic Ray, scoped by path. **Kill matrix:** no dependable per-test output; treat candidates as lower confidence and lean on `--cov-context=test`.
- **Speed levers:**
  - `pytest-xdist` (`-n auto`), with `--dist loadscope` when fixtures are expensive.
  - Fixture scope: session or module scope for expensive immutable fixtures.
  - Database tests: transaction rollback per test in place of recreate; `--reuse-db` with pytest-django.
  - Import time: `python -X importtime` on the slowest test modules finds heavy top-level imports.
  - `--durations=20` to list the slowest tests.

## Go

- **Parameterize:** table-driven tests with `t.Run(tc.name, ...)`.
- **Coverage:** `go test -coverprofile`, with `-coverpkg` for cross-package coverage.
- **Per-test coverage:** `go test -run '^TestName$' -coverprofile`.
- **Mutation:** Gremlins, or go-mutesting, scoped by package. **Kill matrix:** no; lower confidence.
- **Speed levers:**
  - `t.Parallel()` in tests that share no state; `-p` for package parallelism.
  - The test cache: avoid `-count=1` in CI unless needed, and keep tests free of environment and file reads that defeat caching.
  - `-short` with `testing.Short()` guards to separate slow tests.
  - Shared setup in `TestMain` for expensive fixtures.

## C# and .NET (xUnit, NUnit, MSTest)

- **Parameterize:** xUnit `[Theory]` with `[InlineData]` / `[MemberData]`; NUnit `[TestCase]` / `[TestCaseSource]`; MSTest `[DataRow]`.
- **Coverage:** Coverlet (Cobertura or OpenCover XML).
- **Per-test coverage:** run with `--filter` and diff.
- **Mutation:** Stryker.NET, scoped with `--mutate`. **Kill matrix:** check the JSON report of the installed version for per-mutant killing tests; without them, lower confidence.
- **Speed levers:**
  - xUnit runs test collections in parallel; a shared `[Collection]` serialises everything in it, so keep collections small.
  - Class and collection fixtures for expensive setup; `WebApplicationFactory` shared across a class.
  - `dotnet test` with `--no-build` in CI after a separate build step; `-m` for project-level parallelism.

## Any stack: CI

- Split the unit suite across parallel jobs by timing data, once local parallelism is exhausted.
- Run only the affected modules' tests on pull requests where the build tool tracks the dependency graph, and the full suite on the main branch.
- Fail fast on the first failure in pull-request runs.
