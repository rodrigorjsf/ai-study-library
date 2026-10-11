# Resolving the Sonar scope

The review measures coverage the way the project's quality gate does, and stays out of every directory the project excludes.

## Where the properties live

Check all of these; a property can be set in more than one place, and a command-line value wins over a file.

- `sonar-project.properties` at the repo root or in a module
- Maven: `<properties>` in `pom.xml` (`<sonar.exclusions>` and friends), in parent and child modules
- Gradle: the `sonar { properties { ... } }` or `sonarqube { ... }` block in `build.gradle` / `build.gradle.kts`
- .NET: `/d:sonar.*=` arguments to `dotnet sonarscanner begin`
- CI: `-Dsonar.*=` arguments or `with: args:` in workflow files, and scanner environment variables

## Which properties matter

| Property | Effect on this review |
|---|---|
| `sonar.sources`, `sonar.tests` | the source and test roots |
| `sonar.exclusions` | files not analysed at all: outside the review |
| `sonar.inclusions` | when set, only these files are analysed |
| `sonar.test.exclusions`, `sonar.test.inclusions` | which test files count as tests: excluded test files are not candidates |
| `sonar.coverage.exclusions` | files left out of the coverage number: their lines are not counted toward the target, and tests that exist only to cover them are outside the review |
| `sonar.coverage.jacoco.xmlReportPaths`, `sonar.javascript.lcov.reportPaths`, `sonar.python.coverage.reportPaths`, `sonar.go.coverage.reportPaths`, `sonar.cs.opencover.reportsPaths` and the stack's equivalent | the coverage reports the quality gate reads. Several paths mean the gate merges them (unit plus integration is common) |
| `sonar.cpd.exclusions` | duplication only: no effect here |

Patterns are path globs relative to the module base directory: `*` matches within one path segment, `**` matches across segments, `?` matches one character, and several patterns are comma-separated.

## Other exclusions that shape the number

The coverage tool has its own excludes, and the project's reported number already reflects them. Read them too and take the union:

- JaCoCo: `<excludes>` in the Maven plugin, `classDirectories` filters in Gradle
- Jest / Vitest: `coveragePathIgnorePatterns`, `collectCoverageFrom`, `coverage.exclude`
- coverage.py: `omit` and `exclude_lines` in `.coveragerc`, `pyproject.toml`, or `setup.cfg`
- Go: packages left out of the `-coverpkg` list
- Coverlet: `Exclude`, `ExcludeByFile`, `ExcludeByAttribute`

## Computing coverage over the scope

Produce every report the gate reads, by running the same build tasks CI runs before the scanner, and merge them as Sonar does: a line is covered when any report covers it. Where the gate reads only the unit report, that one report is the number. Then drop every file the resolved scope excludes, and compute covered over coverable lines for what remains. Use this number, overall and per module, everywhere the skill says coverage.

The target is checked against this merged number, since it is the one the project is held to. Integration tests are never edited by this review, so their contribution is constant from baseline to end.

Record the resolved scope in the report: each property, where it was set, its value, and the report files used. With no Sonar configuration and no tool excludes, the scope is every production source file.
