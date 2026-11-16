import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_support as support

MODELS = support.FORMAL_MODELS
FORMAL = MODELS.parent
STATECHART = FORMAL / "statechart" / "scripts" / "statechart"
MODEL = "Dispatcher"
CHART_CFG = f"{MODEL}.chart.cfg"
VIEW = f"{MODEL}.view.mjs"
CHART = f"{MODEL}.chart.mmd"
REPORT = f"{MODEL}.report.md"
CHART_BUDGET = 500
OWNER_STATES = {"running", "interrupted", "resumed", "reviewing", "done"}
OWNER_ARROWS = {
    ("running", "interrupted"),
    ("interrupted", "resumed"),
    ("running", "reviewing"),
    ("resumed", "reviewing"),
    ("reviewing", "interrupted"),
    ("reviewing", "done"),
}
BROKEN_IN_CHART_SCOPE = ["NeverIntegratedTwice", "FailedNeverMerged", "NoOrphanSurvivesRecovery", "EveryTicketResolved"]
REGENERATE_COMMAND = f"../statechart/scripts/statechart {MODEL}.tla --config {CHART_CFG} --view {VIEW} --out"

TLA_TEXT = (MODELS / f"{MODEL}.tla").read_text()
MODEL_CFG_TEXT = (MODELS / f"{MODEL}.cfg").read_text()
CHART_CFG_TEXT = (MODELS / CHART_CFG).read_text()
VIEW_TEXT = (MODELS / VIEW).read_text()
STORED_CHART = (MODELS / CHART).read_text()
STORED_REPORT = (MODELS / REPORT).read_text()
MAINTAIN_TEXT = (FORMAL / "maintain-formal-check.md").read_text()
BREAK_EDITS = {name: how for name, _, how in support.model_matches(MODEL)[1]}


def labels_of(chart):
    return dict(re.findall(r"^  (s\d+): (\w+)$", chart, re.M))


def arrows_of(chart):
    labels = labels_of(chart)
    return {(labels[a], labels[b]) for a, b in re.findall(r"^  (s\d+) --> (s\d+)", chart, re.M)}


def lines_outside_constants(cfg_text):
    return [line for line in cfg_text.splitlines() if not line.startswith(" ") and line != "CONSTANTS"]


def states_reached(report):
    return int(re.search(r"TLC reached ([\d,]+) states", report).group(1).replace(",", ""))


def run_statechart(tla_text):
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / f"{MODEL}.tla").write_text(tla_text)
        for name in (CHART_CFG, VIEW):
            shutil.copy(MODELS / name, work / name)
        result = subprocess.run(
            [str(STATECHART), f"{MODEL}.tla", "--config", CHART_CFG, "--view", VIEW, "--out", str(work / "out")],
            cwd=work, capture_output=True, text=True, timeout=900)
        written = {path.name: path.read_text() for path in (work / "out").glob("*")} if (work / "out").exists() else {}
        return result, written


assert sorted(labels_of(STORED_CHART).values()) == sorted(OWNER_STATES), STORED_CHART
assert arrows_of(STORED_CHART) == OWNER_ARROWS, arrows_of(STORED_CHART)
assert not re.search(r"^  class s\d+ (?:breaks|mayBreak|bugPath)$", STORED_CHART, re.M), STORED_CHART
assert "## Rules that hold" in STORED_REPORT and " breaks" not in STORED_REPORT, STORED_REPORT
assert states_reached(STORED_REPORT) <= CHART_BUDGET, STORED_REPORT

assert lines_outside_constants(CHART_CFG_TEXT) == lines_outside_constants(MODEL_CFG_TEXT), CHART_CFG_TEXT
assert "export const state" in VIEW_TEXT and "export const step" in VIEW_TEXT, VIEW_TEXT

for needed in (REGENERATE_COMMAND, CHART_CFG, VIEW, CHART, REPORT):
    assert needed in MAINTAIN_TEXT, needed

tla2tools = os.environ.get("TLA2TOOLS")
if tla2tools and shutil.which("node"):
    result, written = run_statechart(TLA_TEXT)
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert written["chart.mmd"] == STORED_CHART, "stored chart is stale: regenerate it with maintain-formal-check.md"
    assert written["report.md"] == STORED_REPORT, "stored report is stale: regenerate it with maintain-formal-check.md"
    for invariant in BROKEN_IN_CHART_SCOPE:
        old, new = BREAK_EDITS[invariant].split(" => ", 1)
        result, written = run_statechart(support.broken_model_text(TLA_TEXT, old, new))
        assert result.returncode == 1, (invariant, result.stdout, result.stderr)
        assert f"## {invariant} breaks" in written["report.md"], (invariant, written["report.md"])
        assert f"Breaks {invariant}" in written["chart.mmd"], (invariant, written["chart.mmd"])
        assert re.search(r"^  class s\d+ (?:breaks|mayBreak)$", written["chart.mmd"], re.M), (invariant, written["chart.mmd"])
else:
    print("TLA2TOOLS not set: statechart runs skipped")

print("ok")
