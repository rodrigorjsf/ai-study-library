import json
import os
import random
import stat
import sys
from pathlib import Path

FORMAL_MODELS = Path(__file__).resolve().parent.parent / "run-spec-dev" / "formal" / "models"


def model_matches(model):
    lines = (FORMAL_MODELS / f"{model}.matches").read_text().splitlines()
    return lines[0], [line.split("\t") for line in lines[1:]]


def broken_model_text(tla_text, old, new):
    assert tla_text.count(old) == 1, old
    return tla_text.replace(old, new)


PROPERTY_SEED = int(os.environ.get("RUN_SPEC_PROPERTY_SEED", "20261115"))
PROPERTY_CASES = 300

FAKE_GH = (
    "#!/bin/sh\n"
    '[ -n "$FAKE_GH_DIR" ] || { echo "fake gh: no fixture" >&2; exit 1; }\n'
    'case "$1 $2 $5" in\n'
    '"repo view "*) echo o/r;;\n'
    '"issue list "*) cat "$FAKE_GH_DIR/list.json";;\n'
    '"issue view title") cat "$FAKE_GH_DIR/title.txt";;\n'
    '"issue view state") cat "$FAKE_GH_DIR/state-$3.txt" 2>/dev/null || echo OPEN;;\n'
    '"issue view "*) cat "$FAKE_GH_DIR/issue-$3.json";;\n'
    '"api "*) ;;\n'
    '*) echo "fake gh: unexpected $*" >&2; exit 1;;\n'
    "esac\n"
)


REVIEW_AXES = ("Acceptance", "Standards", "Security", "UX/AIX", "Design", "Hygiene")
CLEAN_COUNTS = {
    "Acceptance": "COUNT: 0 blocking, 0 unverified",
    "Standards": "COUNT: 0 proven, 0 unproven",
    "Security": "COUNT: 0 blocking, 0 needs-human",
    "UX/AIX": "COUNT: 0",
    "Design": "COUNT: 0 proven, 0 unproven",
    "Hygiene": "COUNT: 0",
}


def review_report(findings=None, **counts):
    count_lines = {**CLEAN_COUNTS, **{axis.replace("_", "/"): line for axis, line in counts.items()}}
    bodies = {**dict.fromkeys(REVIEW_AXES, ["- none"]), **(findings or {})}
    return "".join(f"## {axis}\n" + "".join(f"{line}\n" for line in bodies[axis]) + f"{count_lines[axis]}\n\n"
                   for axis in REVIEW_AXES)


def run_properties(properties, script, seed, *args):
    return {name: prop(random.Random(f"{seed}/{name}"), script, *args) for name, prop in properties.items()}


def failure_report(results, seed):
    return [f"property {name} failed with seed {seed}; rerun with RUN_SPEC_PROPERTY_SEED={seed}\n" + "\n".join(details)
            for name, details in results.items() if details]


def check_properties(properties, script, *args):
    results = run_properties(properties, script, PROPERTY_SEED, *args)
    for name, details in results.items():
        print(f"property {name}: {PROPERTY_CASES} cases, seed {PROPERTY_SEED}, {'FAILED' if details else 'passed'}")
    if any(results.values()):
        sys.exit("\n\n".join(failure_report(results, PROPERTY_SEED)))


def with_fake_gh(env, bin_dir):
    gh = Path(bin_dir) / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    return {**env, "PATH": f"{bin_dir}{os.pathsep}{env['PATH']}"}


def with_fake_gh_issues(env, fixture_dir, issues, title="Spec: demo"):
    fixture = Path(fixture_dir)
    (fixture / "title.txt").write_text(title + "\n")
    (fixture / "list.json").write_text(json.dumps([{"number": issue["number"], "body": issue["body"]}
                                                   for issue in issues.values()]))
    for number, issue in issues.items():
        (fixture / f"issue-{number}.json").write_text(json.dumps(issue))
        (fixture / f"state-{number}.txt").write_text(issue["state"] + "\n")
    return {**env, "FAKE_GH_DIR": str(fixture)}
