import re
from pathlib import Path

FORMAL = Path(__file__).resolve().parent.parent / "run-spec-dev" / "formal"
CREATE_PROCEDURE_TEXT = (FORMAL / "create-formal-check.md").read_text()
MAINTAIN_PROCEDURE_TEXT = (FORMAL / "maintain-formal-check.md").read_text()
NOTICE_TEXT = (FORMAL / "NOTICE").read_text()
RUN_TS_TEXT = (FORMAL / "statechart" / "scripts" / "run.ts").read_text()

SOURCE_COMMIT = "bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7"
SOURCE_REPOSITORY = "https://github.com/cursor/plugins"


def pinned(constant):
    return re.search(rf'const {constant} =\s*"([^"]+)"', RUN_TS_TEXT).group(1)


assert SOURCE_REPOSITORY in NOTICE_TEXT and SOURCE_COMMIT in NOTICE_TEXT and "MIT License" in NOTICE_TEXT, NOTICE_TEXT

for name, text in {"create-formal-check.md": CREATE_PROCEDURE_TEXT, "maintain-formal-check.md": MAINTAIN_PROCEDURE_TEXT}.items():
    assert "NOTICE" in text and SOURCE_COMMIT in text, name

mise_install = f"mise install {pinned('JAVA_TOOL')} '{pinned('TLC_TOOL')}'"
assert mise_install in CREATE_PROCEDURE_TEXT, mise_install

crlf_files = [path.relative_to(FORMAL).as_posix() for path in sorted(FORMAL.rglob("*"))
              if path.is_file() and "node_modules" not in path.parts and b"\r\n" in path.read_bytes()]
assert not crlf_files, (
    f"{len(crlf_files)} files under {FORMAL} have CRLF line endings, first {crlf_files[0]}; rewrite them with "
    "`git ls-files -z ai/skills/run-spec-dev | xargs -0 touch && git ls-files -z ai/skills/run-spec-dev | xargs -0 git checkout-index -f --` from the repository root"
)

print("ok")
