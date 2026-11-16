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


class Section(NamedTuple):
    log_key: str
    id_prefix: str
    counted: str
    count_form: str


SECTIONS = {
    "Acceptance": Section("acceptance", "A", "blocking", "<blocking> blocking, <unverified> unverified"),
    "Standards": Section("standards", "S", "blocking", "<blocking> proven, <advisory> unproven"),
    "Security": Section("security", "SEC", "blocking", "<blocking> blocking, <advisory> needs-human"),
    "UX/AIX": Section("uxaix", "UX", "advisory", "<advisory>"),
    "Design": Section("design", "D", "blocking", "<blocking> proven, <advisory> unproven"),
    "Hygiene": Section("hygiene", "H", "blocking", "<blocking>"),
}
AXES = tuple(SECTIONS)
COUNT_SHAPES = {name: re.compile(re.sub(r"<(\w+)>", r"(?P<\1>\\d+)", section.count_form))
                for name, section in SECTIONS.items()}


class AxisCount(NamedTuple):
    blocking: int = 0
    advisory: int = 0
    unverified: int = 0


class MalformedReport(Exception):
    pass


class UnreadableReport(Exception):
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
        raise MalformedReport(f"{axis}: COUNT line '{count_lines[-1]}' does not match COUNT: {SECTIONS[axis].count_form}")
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


def round_numbers(state, pattern):
    return sorted({int(match[1]) for path in Path(state).iterdir() if (match := pattern.fullmatch(path.name))})


def review_reports(state):
    return [Path(state) / f"review-{number}.md" for number in round_numbers(state, REVIEW_REPORT)]


def read_review(path):
    try:
        return read_report(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, MalformedReport) as error:
        raise UnreadableReport(f"{path}: {error}") from error


def read_reviews(state):
    try:
        paths = review_reports(state)
    except OSError as error:
        raise UnreadableReport(f"{state}: {error}") from error
    return [read_review(path)[0] for path in paths]


def main():
    parser = argparse.ArgumentParser(prog="route.py")
    parser.add_argument("review")
    args = parser.parse_args()
    try:
        counts, uxaix_skipped = read_review(args.review)
    except UnreadableReport as error:
        print(f"route.py: {error}", file=sys.stderr)
        sys.exit(2)
    blocking, advisory = totals(counts)
    print(counts_line(counts, uxaix_skipped))
    print(f"blocking: {blocking}")
    print(f"advisory: {advisory}")
    print(f"route: {route_of(blocking, advisory)}")


if __name__ == "__main__":
    main()
