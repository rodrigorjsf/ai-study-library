import re
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROUTE = KIT / "route.py"

AXES = ("Acceptance", "Standards", "Security", "UX/AIX", "Design", "Hygiene")
CLEAN = {
    "Acceptance": "COUNT: 0 blocking, 0 unverified",
    "Standards": "COUNT: 0 proven, 0 unproven",
    "Security": "COUNT: 0 blocking, 0 needs-human",
    "UX/AIX": "COUNT: 0",
    "Design": "COUNT: 0 proven, 0 unproven",
    "Hygiene": "COUNT: 0",
}


def report(**counts):
    lines = {**CLEAN, **{axis.replace("_", "/"): line for axis, line in counts.items()}}
    return "".join(f"## {axis}\n- none\n{lines[axis]}\n\n" for axis in AXES)


def run_route(*arguments):
    return subprocess.run([sys.executable, "-I", str(ROUTE), *arguments], capture_output=True, text=True)


def route(text, directory):
    path = Path(directory) / "review-1.md"
    path.write_text(text)
    return run_route(str(path))


def verdict(result):
    assert result.returncode == 0 and result.stderr == "", result
    fields = dict(line.split(": ", 1) for line in result.stdout.splitlines())
    return fields["blocking"], fields["advisory"], fields["route"]


with tempfile.TemporaryDirectory() as tmp:
    assert verdict(route(report(), tmp)) == ("0", "0", "clean")

    only_unproven = report(Standards="COUNT: 0 proven, 2 unproven", Design="COUNT: 0 proven, 1 unproven")
    assert verdict(route(only_unproven, tmp)) == ("0", "3", "advisory-only")

    one_proven_design = report(Design="COUNT: 1 proven, 0 unproven")
    assert verdict(route(one_proven_design, tmp)) == ("1", "0", "blocking")

    one_proven_standards = report(Standards="COUNT: 1 proven, 0 unproven")
    assert verdict(route(one_proven_standards, tmp)) == ("1", "0", "blocking")

    only_unverified = report(Acceptance="COUNT: 0 blocking, 3 unverified")
    assert verdict(route(only_unverified, tmp)) == ("0", "0", "clean")

    only_needs_human = report(Security="COUNT: 0 blocking, 2 needs-human")
    assert verdict(route(only_needs_human, tmp)) == ("0", "2", "advisory-only")

    only_uxaix = report(**{"UX_AIX": "COUNT: 4"})
    assert verdict(route(only_uxaix, tmp)) == ("0", "4", "advisory-only")

    only_hygiene = report(Hygiene="COUNT: 1")
    assert verdict(route(only_hygiene, tmp)) == ("1", "0", "blocking")

    everything = report(Acceptance="COUNT: 2 blocking, 1 unverified", Standards="COUNT: 1 proven, 3 unproven",
                        Security="COUNT: 1 blocking, 2 needs-human", Design="COUNT: 2 proven, 1 unproven",
                        Hygiene="COUNT: 1", **{"UX_AIX": "COUNT: 4"})
    assert verdict(route(everything, tmp)) == ("7", "10", "blocking")

    counts_line = route(everything, tmp).stdout.splitlines()[0]
    assert counts_line == ("counts: Acceptance 2/1, Standards 1 proven/3 unproven, Security 1, UX/AIX 4, "
                           "Design 2 proven/1 unproven, Hygiene 1"), counts_line

    skipped = report().replace("## UX/AIX\n- none\n", "## UX/AIX\nskipped: no UI or agent-surface files\n")
    skipped_result = route(skipped, tmp)
    assert verdict(skipped_result) == ("0", "0", "clean")
    assert "UX/AIX skipped" in skipped_result.stdout, skipped_result.stdout

    quoting_a_count = report().replace(
        "## Standards\n- none\n",
        '## Standards\n- [hard] a.py:1 rule — said "COUNT: 9 proven, 9 unproven". Proof: `x` → y\n')
    assert verdict(route(quoting_a_count, tmp)) == ("0", "0", "clean")


def failure(text, directory, *, mentions):
    result = route(text, directory)
    assert result.returncode == 2 and result.stdout == "", result
    assert mentions in result.stderr, result.stderr


with tempfile.TemporaryDirectory() as tmp:
    old_standards_count = report(Standards="COUNT: 3")
    failure(old_standards_count, tmp, mentions="Standards")

    old_design_count = report(Design="COUNT: 2")
    failure(old_design_count, tmp, mentions="Design")

    failure(report().replace("COUNT: 0 blocking, 0 needs-human\n", ""), tmp, mentions="Security")
    failure(report().replace("## Hygiene\n- none\nCOUNT: 0\n", ""), tmp, mentions="Hygiene")
    failure(report() + "## Design\n- none\nCOUNT: 0 proven, 0 unproven\n", tmp, mentions="Design")
    failure(report(Acceptance="COUNT: x blocking, 0 unverified"), tmp, mentions="Acceptance")

    missing = run_route(str(Path(tmp) / "absent.md"))
    assert missing.returncode == 2 and missing.stdout == "" and "absent.md" in missing.stderr, missing

    no_argument = run_route()
    assert no_argument.returncode == 2 and no_argument.stdout == "", no_argument


def count_line_of(path):
    lines = [line for line in path.read_text().splitlines() if line.startswith("COUNT: ")]
    assert len(lines) == 1, (path, lines)
    return re.sub(r"<[^>]*>", "1", lines[0])


with tempfile.TemporaryDirectory() as tmp:
    briefs = {
        "Acceptance": KIT / "agents/acceptance-verifier.md",
        "Standards": KIT / "axes/standards.md",
        "Security": KIT / "axes/security.md",
        "UX/AIX": KIT / "axes/ux-aix.md",
        "Design": KIT / "axes/design.md",
    }
    for axis, brief in briefs.items():
        written = report(**{axis.replace("/", "_"): count_line_of(brief)})
        result = route(written, tmp)
        assert result.returncode == 0, (axis, result)

    standards = count_line_of(briefs["Standards"])
    design = count_line_of(briefs["Design"])
    assert standards == design == "COUNT: 1 proven, 1 unproven", (standards, design)

print("ok")
