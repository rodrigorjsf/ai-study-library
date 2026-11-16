import re
from pathlib import Path

FORMAL = Path(__file__).resolve().parent.parent / "run-spec-dev" / "formal"
CREATE_PROCEDURE_TEXT = (FORMAL / "create-formal-check.md").read_text()
MAINTAIN_PROCEDURE_TEXT = (FORMAL / "maintain-formal-check.md").read_text()
NOTICE = (FORMAL / "NOTICE").read_text()
RUN_TS = (FORMAL / "statechart" / "scripts" / "run.ts").read_text()

SOURCE_COMMIT = "bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7"
SOURCE_REPOSITORY = "https://github.com/cursor/plugins"


def pinned(constant):
    return re.search(rf'const {constant} =\s*"([^"]+)"', RUN_TS).group(1)


assert SOURCE_REPOSITORY in NOTICE and SOURCE_COMMIT in NOTICE and "MIT License" in NOTICE, NOTICE

for name, text in {"create-formal-check.md": CREATE_PROCEDURE_TEXT, "maintain-formal-check.md": MAINTAIN_PROCEDURE_TEXT}.items():
    assert "NOTICE" in text and SOURCE_COMMIT in text, name

mise_install = f"mise install {pinned('JAVA_TOOL')} '{pinned('TLC_TOOL')}'"
assert mise_install in CREATE_PROCEDURE_TEXT, mise_install

print("ok")
