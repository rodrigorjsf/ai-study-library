# Profiling one command

The command of step 4, profiled by CPU sampling. Pick the row of the runtime that executes the slow work, which is the runtime of the worker process, not of the tool that launched it. Flags move between versions: confirm each against the tool's `--help` before you trust an empty result.

| Runtime | Timing per unit | CPU profile of one command |
|---|---|---|
| Node.js (any test runner) | the runner's JSON or verbose reporter: duration per file and per test | `node --cpu-prof --cpu-prof-dir=<dir> <script>`; under a runner that forks workers, pass the flag to the workers (Vitest: `--pool=forks --no-file-parallelism --execArgv=--cpu-prof --execArgv=--cpu-prof-dir=<dir>`; Jest: `node --cpu-prof node_modules/.bin/jest --runInBand`) |
| Python | `pytest --durations=25`; `python -X importtime` for slow startup | `python -m cProfile -o out.prof <script>`, read with `python -m pstats`; `py-spy record -o out.svg -- <command>` for a process you cannot edit |
| Go | `go test -json` (elapsed per test); `go build -x` for the build | `go test -cpuprofile cpu.out -run <Test>`, then `go tool pprof -top cpu.out` |
| JVM | the build tool's test report (Gradle `--profile`, Maven surefire reports) | `java -XX:StartFlightRecording=filename=rec.jfr ...` or `jcmd <pid> JFR.start`, read with `jfr print --events jdk.ExecutionSample rec.jfr`; async-profiler for a flame graph |
| Rust | `cargo test -- --report-time` (nightly) or `cargo nextest run`; `cargo build --timings` for the build | `samply record <command>` or `perf record -g <command>` on a build with debug symbols |
| .NET | `dotnet test --logger "trx"` (duration per test) | `dotnet-trace collect -- <command>`, read with `dotnet-trace report` |
| Ruby | `rspec --profile 25` | `stackprof` (`StackProf.run`), or `rbspy record -- <command>` |
| Any native process | `time`, `hyperfine '<command>'` for a stable mean | `perf record -g <command>` then `perf report`; `strace -c` or `ltrace -c` when the time is in system or library calls |

## Reading a profile

- **Self time by module.** Sum the samples by the library or package of each frame. One module holding most of the time names the kind of work (a date library, a query builder, a serializer), before you know the caller.
- **Nearest own frame.** For each sample, walk up the stack to the first frame in the project's own source and sum by that frame. This names the line of your code that asks for the work.
- **A sampled profile in JSON** (Node's `.cpuprofile`, speedscope files) is read in a few lines of script: `samples` and `timeDeltas` give the time per node, `nodes` give each node's `callFrame` and children. Build the parent map once, then the two sums above.

## When the profile misleads

- **Mostly idle.** The profile is of a parent that waited on a child. Profile the child: pass the flag through the launcher, or attach to the worker.
- **No profile file.** A worker killed at the end of the run never wrote it. Run the workers one at a time and let them exit on their own.
- **Time in a call that should be free.** A cheap call made a hundred thousand times is the finding: count the calls (the profile's hit count, or a counter in a scratch copy) and look for the loop that makes them.
- **Wall time far above CPU time.** The work is waiting: on I/O, a lock, a sleep, a network call. A CPU profile will not show it; trace the system calls or time the awaited operations.
- **Different on each run.** Something else is using the machine. Record load and free memory before each run, and repeat when either moved.
