import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
SKILLS = KIT.parent
SKILL = SKILLS / "run-spec-correct" / "SKILL.md"
sys.dont_write_bytecode = True
sys.path.insert(0, str(KIT))
from findings import OUTCOMES
from runlog import FINDING_FIELDS

skill_text = SKILL.read_text()
_, frontmatter, body = skill_text.split("---\n", 2)
fields = dict(line.split(": ", 1) for line in frontmatter.splitlines())
assert fields["name"] == "run-spec-correct", fields
assert fields["disable-model-invocation"] == "true", fields
assert fields["description"].strip('"'), fields

assert "run-spec/findings.tsv" in body
for key in FINDING_FIELDS:
    assert f"`{key}`" in body, key
for outcome in OUTCOMES:
    assert f"`{outcome}`" in body, outcome

assert re.findall(r"^[1-5]\. \*\*(\w+)", body, re.M) == ["Architecture", "Types", "Lint", "Test", "Docs"]
assert "twice" in body
assert "The new check fails on the recorded past mistake" in body
assert "`follow-up-issue`" in body
assert "The Findings buffer is empty" in body

readme_text = (KIT / "README.md").read_text()
cursor_table = readme_text.split("\n## Claude Code and Cursor\n")[1].split("\n## Status")[0]
assert any(row.startswith("| `run-spec-correct` |") for row in cursor_table.splitlines())
assert any(row.startswith("| [`../run-spec-correct/SKILL.md`]") for row in readme_text.splitlines())
assert any(row.startswith("| [`run-spec-correct`]") for row in (SKILLS / "README.md").read_text().splitlines())

print("ok")
