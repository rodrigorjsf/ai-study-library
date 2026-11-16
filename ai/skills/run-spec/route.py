#!/usr/bin/env python3
import argparse
import re
import sys
from typing import NamedTuple

sys.dont_write_bytecode = True

COUNT_LINE = re.compile(r"COUNT: (.*)")
SECTION_HEADING = re.compile(r"## (.*)")
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


def read_counts(text):
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


def main():
    parser = argparse.ArgumentParser(prog="route.py")
    parser.add_argument("review")
    args = parser.parse_args()
    try:
        with open(args.review, encoding="utf-8") as review:
            counts, uxaix_skipped = read_counts(review.read())
    except (OSError, UnicodeDecodeError, MalformedReport) as error:
        print(f"route.py: {args.review}: {error}", file=sys.stderr)
        sys.exit(2)
    blocking, advisory = totals(counts)
    print(counts_line(counts, uxaix_skipped))
    print(f"blocking: {blocking}")
    print(f"advisory: {advisory}")
    print(f"route: {route_of(blocking, advisory)}")


if __name__ == "__main__":
    main()
