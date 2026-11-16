#!/usr/bin/env python3
import argparse
import datetime
import pathlib
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gitcmd import default_refs, run
from route import UnreadableReport, read_reviews

REVIEW_FINDINGS = {
    "acceptance": ("Acceptance", "blocking"),
    "standards": ("Standards", "blocking"),
    "security": ("Security", "blocking"),
    "uxaix": ("UX/AIX", "advisory"),
    "design": ("Design", "blocking"),
    "hygiene": ("Hygiene", "blocking"),
}
AXES = tuple(REVIEW_FINDINGS)
COUNTS = ("rounds", *(f"findings.{axis}" for axis in AXES), "dismissals", "unverified", "done", "skipped", "stuck")
REQUIRED = ("at", "slug", "pr", "head", *COUNTS)
OPTIONAL_COUNTS = ("unproven",)
COMMIT_ID = re.compile(r"[0-9a-f]{7,40}")
DIGITS = re.compile(r"[0-9]+")
REVERT = re.compile(rf"This reverts commit ({COMMIT_ID.pattern})")


class Corrupt(Exception):
    pass


def metrics_path():
    common = pathlib.Path(run("git", "rev-parse", "--git-common-dir").strip()).resolve()
    return common / "run-spec" / "metrics.tsv"


def parse(line):
    fields = {}
    for field in line.split("\t"):
        key, sep, value = field.partition("=")
        if not sep or not key or key in fields:
            raise Corrupt(line)
        fields[key] = value
    if any(key not in fields for key in REQUIRED):
        raise Corrupt(line)
    present_counts = [*COUNTS, *(key for key in OPTIONAL_COUNTS if key in fields)]
    if not COMMIT_ID.fullmatch(fields["head"]) or not all(DIGITS.fullmatch(fields[key]) for key in present_counts):
        raise Corrupt(line)
    return fields


def load(path):
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise Corrupt(path.name)
    if text and not text.endswith("\n"):
        raise Corrupt(path.name)
    return [(line, parse(line)) for line in text.splitlines()]


def start_fresh(path):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    aside = path.with_name(f"{path.name}.corrupt-{stamp}")
    n = 0
    while aside.exists():
        n += 1
        aside = path.with_name(f"{path.name}.corrupt-{stamp}-{n}")
    path.rename(aside)
    path.touch()
    print(f"{path.name} was corrupt: moved to {aside}, started a new file")


def load_or_start_fresh(path):
    try:
        return load(path)
    except Corrupt:
        start_fresh(path)
        return []


def single_line_text(value):
    if re.search(r"[\t\r\n]", value):
        raise argparse.ArgumentTypeError("must not contain a tab or a newline")
    return value


def head_sha(value):
    if not COMMIT_ID.fullmatch(value):
        raise argparse.ArgumentTypeError("must be a 7 to 40 character lowercase hex commit id")
    return value


def count(value):
    if not DIGITS.fullmatch(value):
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return int(value)


def axis_count(value):
    axis, sep, number = value.partition("=")
    if axis not in AXES or not sep:
        raise argparse.ArgumentTypeError(f"must be AXIS=N with AXIS one of {', '.join(AXES)}")
    return axis, count(number)


def review_numbers(state):
    try:
        reviews = read_reviews(state)
    except UnreadableReport as error:
        print(f"runlog.py: {error}", file=sys.stderr)
        sys.exit(2)
    findings = [(axis, sum(getattr(counts[section], field) for counts in reviews))
                for axis, (section, field) in REVIEW_FINDINGS.items()]
    unverified = reviews[-1]["Acceptance"].unverified if reviews else 0
    return len(reviews), findings, unverified


def recorded_review_numbers(args):
    if args.state is not None:
        return review_numbers(args.state)
    return args.rounds or 0, args.findings or [], args.unverified or 0


def record(args):
    rounds, axis_findings, unverified = recorded_review_numbers(args)
    path = metrics_path()
    load_or_start_fresh(path)
    findings = dict.fromkeys(AXES, 0)
    findings.update(axis_findings)
    fields = [("at", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
              ("slug", args.slug), ("pr", args.pr), ("head", args.head), ("rounds", rounds),
              *((f"findings.{axis}", findings[axis]) for axis in AXES),
              ("dismissals", args.dismissals), ("unverified", unverified),
              ("done", args.done), ("skipped", args.skipped), ("stuck", args.stuck), ("unproven", args.unproven)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write("\t".join(f"{key}={value}" for key, value in fields) + "\n")


def same_commit(a, b):
    return a.startswith(b) or b.startswith(a)


def reverting_commits(refs):
    log = run("git", "log", *refs, "--grep=This reverts commit", "--format=%x1e%H%x1f%B")
    entries = [entry.partition("\x1f") for entry in log.split("\x1e") if entry]
    return [(sha.strip(), target) for sha, _, body in entries for target in REVERT.findall(body)]


def merge_commits_by_parent(refs):
    merged = {}
    for line in run("git", "log", "--merges", *refs, "--format=%H %P").splitlines():
        merge, *parents = line.split()
        for parent in parents[1:]:
            merged.setdefault(parent, []).append(merge)
    return merged


def reverts(args):
    path = metrics_path()
    records = load_or_start_fresh(path)
    refs = default_refs()
    pending = [i for i, (_, fields) in enumerate(records) if "reverted" not in fields]
    if not pending or not refs:
        return
    reverting = reverting_commits(refs)
    merged = merge_commits_by_parent(refs)
    marked = []
    for i in pending:
        line, fields = records[i]
        landed = {fields["head"]} | {merge for parent, merges in merged.items()
                                     if same_commit(parent, fields["head"]) for merge in merges}
        reverted_by = next((sha for sha, target in reverting if any(same_commit(c, target) for c in landed)), None)
        if reverted_by:
            records[i] = (f"{line}\treverted={reverted_by[:7]}", fields)
            marked.append(f"{fields['slug']} by {reverted_by[:7]}")
    if marked:
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text("".join(f"{line}\n" for line, _ in records), encoding="utf-8")
        temporary.replace(path)
        print(f"marked reverted: {'; '.join(marked)}")


def main():
    ap = argparse.ArgumentParser(prog="runlog.py")
    sub = ap.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--slug", required=True, type=single_line_text)
    rec.add_argument("--head", required=True, type=head_sha)
    rec.add_argument("--pr", default="none", type=single_line_text)
    for name in ("dismissals", "unproven", "done", "skipped", "stuck"):
        rec.add_argument(f"--{name}", default=0, type=count)
    for name in ("rounds", "unverified"):
        rec.add_argument(f"--{name}", type=count)
    rec.add_argument("--findings", nargs="*", type=axis_count)
    rec.add_argument("--state")
    rec.set_defaults(run=record)
    sub.add_parser("reverts").set_defaults(run=reverts)
    args = ap.parse_args()
    if args.command == "record":
        review_options = (args.rounds, args.findings, args.unverified)
        if args.state is not None and any(option is not None for option in review_options):
            rec.error("--state replaces --rounds, --findings and --unverified")
    args.run(args)


if __name__ == "__main__":
    main()
