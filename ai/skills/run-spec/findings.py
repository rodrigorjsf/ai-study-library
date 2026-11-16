import re
import sys
from functools import partial
from pathlib import Path
from typing import NamedTuple

sys.dont_write_bytecode = True

from route import AXES, UnreadableReport, read_review, round_numbers, sections

OUTCOMES = ("fixed", "dismissed", "follow-up", "needs-human", "unproven")
USER_AXIS = "user"
NO_LOCATION = "-"
ID_PREFIXES = {"Acceptance": "A", "Standards": "S", "Security": "SEC", "UX/AIX": "UX", "Design": "D", "Hygiene": "H"}
NOT_FINDING_VERDICTS = ("- [PASS]", "- [UNVERIFIED]")
LOCATION = re.compile(r"(?:\[[^\]]*\] )?(?P<location>[^\s:\"`\[]+:[0-9]+(?:-[0-9]+)?)(?=[\s:]|$)")
OUTCOME_LINE = re.compile(rf"- (?P<id>[A-Z]+[0-9]+) (?P<outcome>{'|'.join(OUTCOMES)})(?:\s+(?P<note>.*))?")
REVIEW_FILE = re.compile(r"review-([0-9]+)(-fix)?\.md")
USER_FIX_FILE = re.compile(r"user-([0-9]+)-fix\.md")
ROUND = re.compile(r"[0-9]+|user-[0-9]+")


class Finding(NamedTuple):
    round: str
    axis: str
    location: str
    text: str
    outcome: str


class Reported(NamedTuple):
    axis: str
    location: str
    text: str


class Outcome(NamedTuple):
    outcome: str
    note: str


def single_line(text):
    return " ".join(text.split())


def is_finding(axis, line):
    if not line.startswith("- ") or line.strip() == "- none":
        return False
    return not (axis == "Acceptance" and line.startswith(NOT_FINDING_VERDICTS))


def reported_findings(path, axis_keys):
    read_review(path)
    found = sections(Path(path).read_text(encoding="utf-8"))
    reported = {}
    for section in AXES:
        bullets = [single_line(line[2:]) for line in found[section] if is_finding(section, line)]
        for number, text in enumerate(bullets, start=1):
            location = LOCATION.match(text)
            reported[f"{ID_PREFIXES[section]}{number}"] = Reported(
                axis_keys[section], location["location"] if location else NO_LOCATION, text)
    return reported


def fixer_outcomes(path):
    try:
        lines = [line.rstrip() for line in Path(path).read_text(encoding="utf-8").splitlines()]
    except (OSError, UnicodeDecodeError) as error:
        raise UnreadableReport(f"{path}: {error}") from error
    if "FINDINGS:" not in lines:
        raise UnreadableReport(f"{path}: no FINDINGS: line")
    outcomes = {}
    for line in lines[lines.index("FINDINGS:") + 1:]:
        if not line.startswith("- "):
            break
        if line == "- none":
            continue
        match = OUTCOME_LINE.fullmatch(line)
        if not match:
            raise UnreadableReport(f"{path}: unreadable outcome line '{line}'")
        if match["id"] in outcomes:
            raise UnreadableReport(f"{path}: {match['id']} appears twice")
        outcomes[match["id"]] = Outcome(match["outcome"], single_line((match["note"] or "").lstrip("—- ")))
    return outcomes


def disagreement(reported, outcomes):
    without_outcome = [id for id in reported if id not in outcomes]
    without_finding = [id for id in outcomes if id not in reported]
    parts = []
    if without_outcome:
        parts.append(f"no outcome for {' '.join(without_outcome)}")
    if without_finding:
        parts.append(f"no finding for {' '.join(without_finding)}")
    return "; ".join(parts)


def review_round(state, number, axis_keys):
    report, fix = state / f"review-{number}.md", state / f"review-{number}-fix.md"
    reported = reported_findings(report, axis_keys) if report.exists() else {}
    outcomes = fixer_outcomes(fix) if fix.exists() else {}
    mismatch = disagreement(reported, outcomes)
    if mismatch:
        raise UnreadableReport(f"{report}: findings do not match {fix.name}: {mismatch}")
    return [Finding(str(number), found.axis, found.location, found.text, outcomes[id].outcome)
            for id, found in reported.items()]


def user_round(state, number):
    outcomes = fixer_outcomes(state / f"user-{number}-fix.md")
    return [Finding(f"user-{number}", USER_AXIS, NO_LOCATION, outcome.note or id, outcome.outcome)
            for id, outcome in outcomes.items()]


def state_findings(state, axis_keys):
    state = Path(state)
    reads = [partial(review_round, state, number, axis_keys) for number in round_numbers(state, REVIEW_FILE)]
    reads += [partial(user_round, state, number) for number in round_numbers(state, USER_FIX_FILE)]
    findings, problems = [], []
    for read in reads:
        try:
            findings += read()
        except UnreadableReport as error:
            problems.append(str(error))
    return findings, problems
