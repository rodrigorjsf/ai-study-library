#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.dont_write_bytecode = True

COUNT_LINE = re.compile(r"COUNT: (.*)")
SECTION_HEADING = re.compile(r"## (.*)")
REVIEW_REPORT = re.compile(r"review-(\d+)\.md")
RUNLOG_FINDINGS = {
    "acceptance": ("Acceptance", "blocking"),
    "standards": ("Standards", "blocking"),
    "security": ("Security", "blocking"),
    "uxaix": ("UX/AIX", "advisory"),
    "design": ("Design", "blocking"),
    "hygiene": ("Hygiene", "blocking"),
}
COUNT_FORMS = {
    "Acceptance": "<blocking> blocking, <unverified> unverified",
    "Standards": "<blocking> proven, <advisory> unproven",
    "Security": "<blocking> blocking, <advisory> needs-human",
    "UX/AIX": "<advisory>",
    "Design": "<blocking> proven, <advisory> unproven",
    "Hygiene": "<blocking>",
}
AXES = tuple(COUNT_FORMS)
COUNT_SHAPES = {axis: re.compile(re.sub(r"<(\w+)>", r"(?P<\1>\\d+)", form)) for axis, form in COUNT_FORMS.items()}


class AxisCount(NamedTuple):
    blocking: int = 0
    advisory: int = 0
    unverified: int = 0


class MalformedReport(Exception):
    pass


def sections(text):
    found = {}
    current = None
    for line in text.splitlines():
        heading = SECTION_HEADING.fullmatch(line)
        if heading:
            current = heading.group(1).strip()
            if current in found:
                raise MalformedReport(f"{current}: section appears twice")
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return found


def counts_of(axis, body):
    count_lines = [match.group(1).strip() for match in map(COUNT_LINE.fullmatch, body) if match]
    if not count_lines:
        raise MalformedReport(f"{axis}: no COUNT line")
    shape = COUNT_SHAPES[axis].fullmatch(count_lines[-1])
    if not shape:
        raise MalformedReport(f"{axis}: COUNT line '{count_lines[-1]}' does not match COUNT: {COUNT_FORMS[axis]}")
    return AxisCount(**{field: int(number) for field, number in shape.groupdict().items()})


def read_report(text):
    found = sections(text)
    counts = {}
    for axis in AXES:
        if axis not in found:
            raise MalformedReport(f"{axis}: section missing")
        counts[axis] = counts_of(axis, found[axis])
    skipped = any(line.startswith("skipped") for line in found["UX/AIX"])
    return counts, skipped


def totals(counts):
    blocking = sum(count.blocking for count in counts.values())
    advisory = sum(count.advisory for count in counts.values())
    return blocking, advisory


def counts_line(counts, uxaix_skipped):
    acceptance, standards, design = counts["Acceptance"], counts["Standards"], counts["Design"]
    uxaix = "skipped" if uxaix_skipped else counts["UX/AIX"].advisory
    return (f"counts: Acceptance {acceptance.blocking}/{acceptance.unverified}, "
            f"Standards {standards.blocking} proven/{standards.advisory} unproven, "
            f"Security {counts['Security'].blocking}, UX/AIX {uxaix}, "
            f"Design {design.blocking} proven/{design.advisory} unproven, Hygiene {counts['Hygiene'].blocking}")


def route_of(blocking, advisory):
    if blocking:
        return "blocking"
    return "advisory-only" if advisory else "clean"


def review_reports(state):
    numbered = ((int(match.group(1)), path) for path in Path(state).iterdir()
                if (match := REVIEW_REPORT.fullmatch(path.name)))
    return [path for _, path in sorted(numbered)]


def read_review(path):
    try:
        return read_report(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, MalformedReport) as error:
        print(f"route.py: {path}: {error}", file=sys.stderr)
        sys.exit(2)


def runlog_line(state):
    try:
        reports = [read_review(path)[0] for path in review_reports(state)]
    except OSError as error:
        print(f"route.py: {state}: {error}", file=sys.stderr)
        sys.exit(2)
    findings = " ".join(f"{name}={sum(getattr(counts[axis], field) for counts in reports)}"
                        for name, (axis, field) in RUNLOG_FINDINGS.items())
    unverified = reports[-1]["Acceptance"].unverified if reports else 0
    return f"--rounds {len(reports)} --findings {findings} --unverified {unverified}"


def main():
    parser = argparse.ArgumentParser(prog="route.py")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("review", nargs="?")
    target.add_argument("--runlog", metavar="STATE")
    args = parser.parse_args()
    if args.runlog is not None:
        print(runlog_line(args.runlog))
        return
    counts, uxaix_skipped = read_review(args.review)
    blocking, advisory = totals(counts)
    print(counts_line(counts, uxaix_skipped))
    print(f"blocking: {blocking}")
    print(f"advisory: {advisory}")
    print(f"route: {route_of(blocking, advisory)}")


if __name__ == "__main__":
    main()
