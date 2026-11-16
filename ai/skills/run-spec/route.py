#!/usr/bin/env python3
import argparse
import re
import sys

sys.dont_write_bytecode = True

COUNT_LINE = re.compile(r"COUNT: (.*)")
SECTION_HEADING = re.compile(r"## (.*)")
NUMBER = r"(\d+)"
PROVEN_UNPROVEN = re.compile(rf"{NUMBER} proven, {NUMBER} unproven")
BLOCKING_UNVERIFIED = re.compile(rf"{NUMBER} blocking, {NUMBER} unverified")
BLOCKING_NEEDS_HUMAN = re.compile(rf"{NUMBER} blocking, {NUMBER} needs-human")
SINGLE = re.compile(NUMBER)
AXES = ("Acceptance", "Standards", "Security", "UX/AIX", "Design", "Hygiene")
COUNT_SHAPES = {
    "Acceptance": BLOCKING_UNVERIFIED,
    "Standards": PROVEN_UNPROVEN,
    "Security": BLOCKING_NEEDS_HUMAN,
    "UX/AIX": SINGLE,
    "Design": PROVEN_UNPROVEN,
    "Hygiene": SINGLE,
}


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
        raise MalformedReport(f"{axis}: COUNT line '{count_lines[-1]}' does not match {COUNT_SHAPES[axis].pattern}")
    return tuple(int(number) for number in shape.groups())


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
    blocking = (counts["Acceptance"][0] + counts["Security"][0] + counts["Hygiene"][0]
                + counts["Standards"][0] + counts["Design"][0])
    advisory = (counts["Security"][1] + counts["UX/AIX"][0]
                + counts["Standards"][1] + counts["Design"][1])
    return blocking, advisory


def counts_line(counts, uxaix_skipped):
    uxaix = "skipped" if uxaix_skipped else counts["UX/AIX"][0]
    acceptance, standards, security, design = (counts[axis] for axis in ("Acceptance", "Standards", "Security", "Design"))
    return (f"counts: Acceptance {acceptance[0]}/{acceptance[1]}, Standards {standards[0]} proven/{standards[1]} unproven, "
            f"Security {security[0]}, UX/AIX {uxaix}, Design {design[0]} proven/{design[1]} unproven, "
            f"Hygiene {counts['Hygiene'][0]}")


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
