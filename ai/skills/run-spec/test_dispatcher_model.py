import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_support as support

REPO = Path(__file__).resolve().parent.parent.parent.parent
MODELS = support.FORMAL_MODELS
SKILL_PATH = "ai/skills/run-spec/SKILL.md"
MODEL = "Dispatcher"
NOT_A_PROMISE = {"TypeOK"}

TLA_TEXT = (MODELS / f"{MODEL}.tla").read_text()
CFG_TEXT = (MODELS / f"{MODEL}.cfg").read_text()
MATCHES_HEADER, MATCHES_ROWS = support.model_matches(MODEL)


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def cfg_invariants():
    names = []
    for line in CFG_TEXT.splitlines():
        if line.startswith("INVARIANT"):
            names += line.split()[1:]
    return [name for name in names if name not in NOT_A_PROMISE]


header = re.fullmatch(r"matches skill at commit ([0-9a-f]{40})", MATCHES_HEADER)
assert header, MATCHES_HEADER
commit = header.group(1)
assert git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0, commit

skill_lines = git("show", f"{commit}:{SKILL_PATH}").stdout.splitlines()
assert skill_lines, (commit, SKILL_PATH)

rows = MATCHES_ROWS
assert rows and all(len(row) == 3 for row in rows), rows
names = [name for name, _, _ in rows]
assert len(names) == len(set(names)), names
assert sorted(names) == sorted(cfg_invariants()), (names, cfg_invariants())

break_edits = {}
for name, citation, how in rows:
    path, _, number = citation.rpartition(":")
    assert path == SKILL_PATH and number.isdigit() and 1 <= int(number) <= len(skill_lines), (name, citation)
    assert skill_lines[int(number) - 1].strip(), (name, citation)
    assert re.search(rf"^{name} ==", TLA_TEXT, re.M), name
    break_edits[name] = support.broken_model_text(TLA_TEXT, how)

assert not [line for line in TLA_TEXT.splitlines() if "\\*" in line or "(*" in line], "comments in the model"


def tlc(model_dir, java, tla2tools):
    result = subprocess.run(
        [java, "-XX:+UseParallelGC", "-cp", tla2tools, "tlc2.TLC", "-workers", "4",
         "-metadir", str(Path(model_dir) / "states"), "-config", f"{MODEL}.cfg", f"{MODEL}.tla"],
        cwd=model_dir, capture_output=True, text=True, timeout=1800)
    return result.stdout + result.stderr


def run_in_copy(tla_text, java, tla2tools):
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / f"{MODEL}.tla").write_text(tla_text)
        (Path(tmp) / f"{MODEL}.cfg").write_text(CFG_TEXT)
        return tlc(tmp, java, tla2tools)


tla2tools = os.environ.get("TLA2TOOLS")
if tla2tools:
    java = os.environ.get("JAVA", "java")
    passing = run_in_copy(TLA_TEXT, java, tla2tools)
    assert "Model checking completed. No error has been found." in passing, passing[-2000:]
    for invariant, broken_text in break_edits.items():
        output = run_in_copy(broken_text, java, tla2tools)
        assert f"Invariant {invariant} is violated" in output, (invariant, output[-2000:])
else:
    print("TLA2TOOLS not set: TLC runs skipped")

print("ok")
