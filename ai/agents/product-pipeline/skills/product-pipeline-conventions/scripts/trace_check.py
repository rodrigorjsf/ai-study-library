#!/usr/bin/env python3
"""Deterministic trace-check for the product pipeline (shared-traceability-keeper).

Usage:
  trace_check.py --run-dir docs/pipeline/<run-id> \
      --stage discovery|prd|architecture|tasks \
      --mode reserve|entry|exit|final [--out <path>] [--round N] [--now ISO]
      [--update-matrix] [--handoff-version N] [--revalidate FROM:TO ...]

Writes trace/report-<stage>-<mode>.json (or --out). Exit code 0 whenever the
check ran (blocking status is inside the JSON: summary.blocking), 2 on usage or
I/O errors.

Contracts implemented (product-pipeline-conventions §2, §3, §4, §6.1, §11.2 and
shared-traceability-keeper):
  * items: dicts with an `id` matching a registry regex in the stage machine
    artifacts (JSON/YAML/CSV; ADR-style markdown frontmatter; lens tables for
    cross-cutting prefixes; crosscutting/ledger.md rows).
  * links: explicit only. `traces_to` (list, dict-of-lists or string),
    `trace_links` [{from,to,type}], `supports`, `drivers`, keys named after a
    link type, `evidence_ids` (reverse: EVD -> item) and structural nesting
    (child item inside a parent item). A link goes from the item that declares
    the trace (downstream) to the traced item (upstream). Never inferred from text.
  * text hash: sha256 of the whitespace-normalised item text (statement, text,
    title, description, name, ... or the canonical JSON of the item without
    id/status/link fields; ADR markdown: the body).
Python 3 standard library only; PyYAML is used when importable, otherwise a
built-in YAML subset parser.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys

TOOL_VERSION = "1.0.0"

STAGES = ["discovery", "prd", "architecture", "tasks"]
STAGE_DIR = {"discovery": "01-discovery", "prd": "02-prd",
             "architecture": "03-architecture", "tasks": "04-tasks"}
STAGE_LETTER = {"discovery": "D", "prd": "P", "architecture": "A", "tasks": "T"}
STAGE_INFIX = {"prd": "P", "architecture": "A", "tasks": "T"}
CROSS = "crosscutting"

# Folders inside a stage that downstream readers never consume (§2: work/ drafts
# are not consumed downstream; gate/, briefs/, history/, rejections/ are process
# records). reviews/ is read separately (frontmatter trace_links, lens artifacts).
EXCLUDED_SUBDIRS = {"work", "gate", "reviews", "briefs", "history", "rejections"}
# Work files the keeper table names explicitly as machine artifacts of the stage.
NAMED_WORK_FILES = {"discovery": ["work/evidence-ledger.json"]}
MACHINE_EXT = (".json", ".yaml", ".yml", ".csv")

SHARED_PREFIXES_DEFAULT = ["RSK", "ASM", "Q", "NG", "CON", "TST", "SPK", "DL", "CND"]
CROSS_PREFIXES = {"THR", "SEC-NFR", "ABU", "LIN", "OBL", "SLO", "SLI"}

# Built-in registry (conventions §4), used only when trace/id-registry.json is absent.
_D3 = r"\d{3}"
DEFAULT_PREFIXES = (
    [(p, "^%s-%s$" % (p, _D3), "discovery") for p in
     ["OUT", "PRB", "FRM", "SEG", "JOB", "OPP", "SOL", "EVD", "MET", "KILL", "ALT",
      "TERM", "DEC", "LED"]]
    + [("FLAG", r"^FLAG-(FEAS|A11Y|SEC|PRIV)-\d{3}$", "discovery")]
    + [(p, r"^%s-(P-|A-|T-)?\d{2,3}$" % p, o) for p, o in
       [("RSK", "discovery"), ("ASM", "discovery"), ("Q", "discovery"), ("NG", "discovery"),
        ("CON", "prd"), ("TST", "discovery"), ("SPK", "architecture"), ("DL", "discovery"),
        ("CND", "discovery")]]
    + [(p, "^%s-%s$" % (p, _D3), "prd") for p in
       ["G", "J", "FL", "FR", "BR", "NFR", "M", "EV", "RC", "GL"]]
    + [("AC-FR", r"^AC-FR-\d{3}-\d+$", "prd")]
    + [(p, "^%s-%s$" % (p, _D3), "architecture") for p in
       ["QAS", "C", "CMP", "BC", "AGG", "EVT", "ENT", "OP", "MSG", "SAGA", "FF", "TD", "SP", "TP"]]
    + [("ADR", r"^ADR-\d{4}$", "architecture"), ("MS", r"^MS-\d+$", "tasks"),
       ("SL", r"^SL-\d{2}$", "tasks"), ("T", r"^T-S\d{2}-\d{2}$", "tasks"),
       ("FLG", r"^FLG-\d{2}$", "tasks"), ("MIG", r"^MIG-\d{2}$", "tasks"),
       ("TQ", r"^TQ-\d{2}$", "tasks"), ("AC-T", r"^AC-T-S\d{2}-\d{2}-\d+$", "tasks")]
    + [(p, "^%s-%s$" % (p, _D3), "cross-cutting") for p in sorted(CROSS_PREFIXES)]
)

LINK_TYPES = ["derives", "satisfies", "refines", "realizes", "verifies", "mitigates", "implements"]
TEXT_KEYS = ["statement", "text", "title", "description", "name", "summary", "decision",
             "scenario", "objective", "requirement", "item"]
NON_TEXT_KEYS = {"id", "status", "traces_to", "trace_links", "source", "history", "supports",
                 "evidence_ids", "drivers", "version", "sha256"} | set(LINK_TYPES)
INACTIVE = ("dropped", "deferred", "superseded", "withdrawn", "retired", "deleted", "rejected")
RATIONALE_KEYS = ["rationale", "reason", "drop_rationale", "justification", "note",
                  "duplicate_of", "superseded_by"]
APPROVER_KEYS = ["approved_by", "approver", "decision_ref", "approved_in", "decision"]
DROP_LIST_KEYS = ("dropped", "deferred", "drops", "drop_records")
ORPHAN_EXEMPT = {"OUT", "DEC", "DL", "Q", "TQ", "CND", "LED", "TERM", "GL", "RQ", "MS", "SL"}
LINK_COL_RE = re.compile(
    r"(trace|upstream|parent|verif|link|^fr|^ac|^nfr|^task|^t$|^t_id|^qas|^adr|^ff|^thr|"
    r"^lin|^obl|^slo|^risk|^req|^component|^contract|^ledger|^cmp|^op$|^spk|^g$|^goal)")

# Chain segments per stage: (name, parent families, child families, forward scope).
# Coverage is adjacency in either direction; forward scope says which parents are
# expected to have a child: "all", "must" (Must/target items only) or "none".
SEGMENTS = {
    "discovery": [("EVD->OPP/OUT", {"OPP", "OUT"}, {"EVD"}, "must"),
                  ("ASM/RSK->OPP", {"OPP"}, {"ASM", "RSK"}, "none"),
                  ("MET->OUT", {"OUT"}, {"MET"}, "all"),
                  ("SOL->OPP", {"OPP"}, {"SOL"}, "must")],
    "prd": [("OPP/OUT->G", {"OPP", "OUT"}, {"G"}, "must"),
            ("G->FR/NFR/BR", {"G"}, {"FR", "NFR", "BR"}, "all"),
            ("FR/NFR/BR->AC", {"FR", "NFR", "BR"}, {"AC"}, "must"),
            ("G->M", {"G"}, {"M"}, "must"),
            ("M->EV", {"M"}, {"EV"}, "all"),
            ("FR->FL/J", {"FR"}, {"FL", "J"}, "none")],
    "architecture": [("FR/NFR->QAS", {"FR", "NFR"}, {"QAS"}, "none"),
                     ("QAS->ADR", {"QAS"}, {"ADR"}, "all"),
                     ("ADR->C/CMP", {"ADR"}, {"C", "CMP"}, "none"),
                     ("C/CMP->OP/MSG", {"C", "CMP"}, {"OP", "MSG"}, "none"),
                     ("QAS->FF", {"QAS"}, {"FF"}, "all"),
                     ("RSK->ADR/SPK", {"RSK"}, {"ADR", "SPK"}, "none"),
                     ("THR/LIN->control", {"THR", "LIN"},
                      {"SEC-NFR", "NFR", "ADR", "C", "CMP", "OP", "MSG", "FF", "QAS"}, "all")],
    "tasks": [("FR/AC->T", {"FR", "AC"}, {"T"}, "must"),
              ("NFR/QAS/FF/THR/LIN/OBL/SLO/LED->T",
               {"NFR", "QAS", "FF", "THR", "LIN", "OBL", "SLO", "LED"}, {"T"}, "all"),
              ("T->TST", {"T"}, {"TST"}, "all")],
}
ADR_DRIVERS = {"FR", "NFR", "QAS", "CON", "BR", "RSK", "ASM", "THR", "LIN", "OBL", "SLO",
               "SEC-NFR", "G"}
CONTROL_FAMILIES = {"SEC-NFR", "NFR", "ADR", "C", "CMP", "OP", "MSG", "FF", "QAS", "T"}


class UsageError(Exception):
    pass


# --------------------------------------------------------------------------- utils

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def norm_text(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def text_hash(s):
    return sha256_bytes(norm_text(s).encode("utf-8"))


def jsonable(o):
    return json.loads(json.dumps(o, default=str, sort_keys=True))


def truthy(v):
    if v is True:
        return True
    return isinstance(v, str) and v.strip().lower() in ("true", "yes", "y", "1")


def pct(n, d):
    return None if not d else round(100.0 * n / d, 1)


def github_slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


# ------------------------------------------------------------------ YAML loading

try:  # optional
    import yaml as _pyyaml  # type: ignore
except Exception:  # pragma: no cover
    _pyyaml = None


def _strip_comment(line):
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q:
                q = None
        elif ch in ("'", '"'):
            q = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def _scalar(s):
    s = s.strip()
    if not s:
        return None
    if s[0] == '"' and s.endswith('"') and len(s) >= 2:
        try:
            return json.loads(s)
        except ValueError:
            return s[1:-1]
    if s[0] == "'" and s.endswith("'") and len(s) >= 2:
        return s[1:-1].replace("''", "'")
    low = s.lower()
    if low in ("null", "~"):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


class _Flow:
    def __init__(self, s):
        self.s, self.i = s, 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t\r\n":
            self.i += 1

    def value(self, in_map_key=False):
        self.ws()
        if self.i >= len(self.s):
            return None
        c = self.s[self.i]
        if c == "[":
            self.i += 1
            out = []
            while True:
                self.ws()
                if self.i >= len(self.s):
                    return out
                if self.s[self.i] == "]":
                    self.i += 1
                    return out
                out.append(self.value())
                self.ws()
                if self.i < len(self.s) and self.s[self.i] == ",":
                    self.i += 1
        if c == "{":
            self.i += 1
            out = {}
            while True:
                self.ws()
                if self.i >= len(self.s):
                    return out
                if self.s[self.i] == "}":
                    self.i += 1
                    return out
                k = self.value(in_map_key=True)
                self.ws()
                v = None
                if self.i < len(self.s) and self.s[self.i] == ":":
                    self.i += 1
                    v = self.value()
                out[str(k)] = v
                self.ws()
                if self.i < len(self.s) and self.s[self.i] == ",":
                    self.i += 1
        if c in ("'", '"'):
            j = self.i + 1
            while j < len(self.s):
                if self.s[j] == c and (c == "'" or self.s[j - 1] != "\\"):
                    if c == "'" and j + 1 < len(self.s) and self.s[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            tok = self.s[self.i:j + 1]
            self.i = j + 1
            return _scalar(tok)
        j = self.i
        stops = ",]}" + (":" if in_map_key else "")
        while j < len(self.s) and self.s[j] not in stops:
            j += 1
        tok = self.s[self.i:j]
        self.i = j
        return _scalar(tok)


class _MiniYaml:
    """Small YAML subset: block maps/sequences, flow collections, quoted and
    block scalars, comments. Enough for pipeline frontmatter and data files."""

    def __init__(self, text):
        self.lines = text.replace("\t", "  ").splitlines()
        self.i = 0

    def _next(self):
        while self.i < len(self.lines):
            st = self.lines[self.i].strip()
            if st and not st.startswith("#") and st not in ("---", "..."):
                return self.i
            self.i += 1
        return None

    def parse(self):
        idx = self._next()
        if idx is None:
            return None
        return self._block(_indent(self.lines[idx]))

    def _block(self, ind):
        idx = self._next()
        st = _strip_comment(self.lines[idx]).strip()
        if st == "-" or st.startswith("- "):
            return self._seq(ind)
        if st.startswith("[") or st.startswith("{"):
            self.i += 1
            return self._flow(st, ind)
        if not re.match(r"^[^:]+?:(\s|$)", st) and not re.match(r"^\"[^\"]*\":(\s|$)", st):
            self.i += 1
            return self._continue_scalar(st, ind - 1)
        return self._map(ind)

    def _flow(self, rest, ind):
        text = rest
        while text.count("[") + text.count("{") > text.count("]") + text.count("}") \
                and self.i < len(self.lines):
            text += " " + _strip_comment(self.lines[self.i]).strip()
            self.i += 1
        return _Flow(text).value()

    def _continue_scalar(self, rest, ind):
        parts = [rest]
        while True:
            idx = self._next()
            if idx is None or _indent(self.lines[idx]) <= ind:
                break
            nst = _strip_comment(self.lines[idx]).strip()
            if nst.startswith("- ") or re.match(r"^[\w\"'-]+:(\s|$)", nst):
                break
            parts.append(nst)
            self.i += 1
        return _scalar(" ".join(parts))

    def _value(self, rest, ind):
        if rest in ("|", ">", "|-", ">-", "|+", ">+"):
            return self._block_scalar(ind, rest[0])
        if rest.startswith("[") or rest.startswith("{"):
            return self._flow(rest, ind)
        if rest.startswith('"') or rest.startswith("'"):
            return _scalar(rest)
        return self._continue_scalar(rest, ind)

    def _block_scalar(self, ind, style):
        out = []
        while self.i < len(self.lines):
            line = self.lines[self.i]
            if line.strip() and _indent(line) <= ind:
                break
            out.append(line.strip())
            self.i += 1
        while out and not out[-1]:
            out.pop()
        return ("\n" if style == "|" else " ").join(out)

    def _seq(self, ind):
        out = []
        while True:
            idx = self._next()
            if idx is None:
                break
            line = self.lines[idx]
            st = _strip_comment(line).strip()
            if _indent(line) != ind or not (st == "-" or st.startswith("- ")):
                break
            rest = st[1:].strip()
            self.i += 1
            if not rest:
                nidx = self._next()
                if nidx is not None and _indent(self.lines[nidx]) > ind:
                    out.append(self._block(_indent(self.lines[nidx])))
                else:
                    out.append(None)
            elif rest[0] not in "[{\"'" and re.match(r"^[^:]+?:(\s|$)", rest):
                col = ind + 1 + (len(st[1:]) - len(st[1:].lstrip()))
                self.i -= 1
                self.lines[self.i] = " " * col + rest
                out.append(self._map(col))
            else:
                out.append(self._value(rest, ind))
        return out

    def _map(self, ind):
        out = {}
        while True:
            idx = self._next()
            if idx is None:
                break
            line = self.lines[idx]
            st = _strip_comment(line).strip()
            if _indent(line) != ind or st == "-" or st.startswith("- "):
                break
            m = re.match(r"^(\"[^\"]*\"|'[^']*'|[^:]+?)\s*:(?:\s+(.*)|$)", st)
            self.i += 1
            if not m:
                continue
            key = str(_scalar(m.group(1)))
            rest = (m.group(2) or "").strip()
            if rest == "":
                nidx = self._next()
                if nidx is not None:
                    nl = self.lines[nidx]
                    ni = _indent(nl)
                    nst = nl.strip()
                    if ni > ind or (ni == ind and (nst == "-" or nst.startswith("- "))):
                        out[key] = self._block(ni)
                        continue
                out[key] = None
            else:
                out[key] = self._value(rest, ind)
        return out


YAML_PARSER = "pyyaml" if _pyyaml is not None else "builtin"


def load_yaml(text):
    if _pyyaml is not None:
        try:
            return jsonable(_pyyaml.safe_load(text))
        except Exception:
            pass
    return jsonable(_MiniYaml(text).parse())


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines(True)
    for n in range(1, len(lines)):
        if lines[n].strip() == "---":
            return "".join(lines[1:n]), "".join(lines[n + 1:])
    return None, text


# ---------------------------------------------------------------------- registry

class Registry:
    def __init__(self, data, present):
        self.present = present
        self.problems = []
        self.entries = []  # (prefix, compiled regex, owner)
        prefixes = (data or {}).get("prefixes") if isinstance(data, dict) else None
        rows = []
        if isinstance(prefixes, list):
            for p in prefixes:
                if isinstance(p, dict) and p.get("prefix") and p.get("regex"):
                    rows.append((str(p["prefix"]), str(p["regex"]), str(p.get("owner_stage", ""))))
        elif isinstance(prefixes, dict):
            for k, v in prefixes.items():
                if isinstance(v, dict) and v.get("regex"):
                    rows.append((str(k), str(v["regex"]), str(v.get("owner_stage", ""))))
                elif isinstance(v, str):
                    rows.append((str(k), v, ""))
        if not rows:
            if present:
                self.problems.append({"kind": "registry_without_prefixes",
                                      "detail": "no usable prefixes[] {prefix, regex}; built-in §4 table used"})
            rows = list(DEFAULT_PREFIXES)
        seen = set()
        for prefix, rx, owner in sorted(rows):
            if prefix in seen:
                self.problems.append({"kind": "registry_duplicate_prefix", "detail": prefix})
                continue
            seen.add(prefix)
            try:
                self.entries.append((prefix, re.compile(rx), owner))
            except re.error as e:
                self.problems.append({"kind": "registry_bad_regex", "detail": "%s: %s" % (prefix, e)})
        known = {p for p, _, _ in self.entries}
        for p, _, _ in DEFAULT_PREFIXES:
            if p not in known:
                self.problems.append({"kind": "registry_missing_prefix", "detail": p})
        infix = (data or {}).get("stage_infix") if isinstance(data, dict) else None
        sp = infix.get("shared_prefixes") if isinstance(infix, dict) else None
        self.shared = set(sp) if isinstance(sp, list) and sp else set(SHARED_PREFIXES_DEFAULT)
        if present and not (isinstance(sp, list) and sp):
            self.problems.append({"kind": "registry_missing_stage_infix",
                                  "detail": "stage_infix.shared_prefixes absent; §4 default used"})
        self.owner = {p: o for p, _, o in self.entries}
        bodies = []
        for p, rx, _ in sorted(self.entries, key=lambda e: (-len(e[1].pattern), e[0])):
            body = rx.pattern
            body = body[1:] if body.startswith("^") else body
            body = body[:-1] if body.endswith("$") else body
            bodies.append("(?:%s)" % body)
        self.token_re = re.compile(r"(?<![A-Za-z0-9_\-])(?:%s)(?![A-Za-z0-9_]|-\d)" % "|".join(bodies))
        self.ids = (data or {}).get("ids") if isinstance(data, dict) else None

    def classify(self, s):
        """Return (prefix, valid). prefix None when no registry prefix applies."""
        if not isinstance(s, str):
            return None, False
        s = s.strip()
        best = None
        for p, rx, _ in self.entries:
            if rx.fullmatch(s) and (best is None or len(p) > len(best)):
                best = p
        if best:
            return best, True
        textual = None
        for p, _, _ in self.entries:
            if s.startswith(p + "-") and (textual is None or len(p) > len(textual)):
                textual = p
        return textual, False

    def is_item(self, s):
        return self.classify(s)[1]

    def tokens(self, text):
        return [m.group(0) for m in self.token_re.finditer(text or "")]


def family(prefix):
    if not prefix:
        return None
    if prefix.startswith("AC-"):
        return "AC"
    if prefix == "CON-P":
        return "CON"
    return prefix


def stage_index(stage):
    return STAGES.index(stage) if stage in STAGES else -1


# ----------------------------------------------------------------------- model

class Model:
    def __init__(self, reg):
        self.reg = reg
        self.defs = {}        # id -> list of definitions
        self.links = {}       # (from, to, type) -> set(sources)
        self.annotations = 0  # links with a non-item endpoint (finding/proposal IDs)
        self.dangling = {}    # (id, source) -> referencing item
        self.unknown_trace_items = []
        self.drop_refs = {}   # id -> {rationale, approver, source}
        self.no_interface = set()

    def add_def(self, item):
        self.defs.setdefault(item["id"], []).append(item)

    def add_link(self, frm, to, ltype, source, referrer=None):
        frm, to = str(frm).strip(), str(to).strip()
        if not frm or not to or frm == to:
            return
        ltype = ltype if ltype in LINK_TYPES else (ltype or "")
        fi, ti = self.reg.is_item(frm), self.reg.is_item(to)
        if not (fi and ti):
            self.annotations += 1
            return
        self.links.setdefault((frm, to, ltype), set()).add(source)


def default_link_type(from_id, reg):
    fam = family(reg.classify(from_id)[0])
    if fam == "TST":
        return "verifies"
    if fam == "T":
        return "implements"
    if fam == "AC":
        return "refines"
    return "derives"


def ids_in(value, reg):
    """Collect ID-like strings from a traces_to-like value."""
    out = []
    if value is None:
        return out
    if isinstance(value, str):
        for tok in re.split(r"[,;|\s]+", value):
            tok = tok.strip().strip("[](){}\"'`")
            if tok:
                out.append((tok, None))
    elif isinstance(value, list):
        for v in value:
            if isinstance(v, dict):
                tid = v.get("id") or v.get("to") or v.get("target") or v.get("ref")
                if tid:
                    out.append((str(tid), v.get("type")))
            else:
                out.extend(ids_in(v, reg))
    elif isinstance(value, dict):
        for k in sorted(value):
            sub = ids_in(value[k], reg)
            ktype = k if k in LINK_TYPES else None
            out.extend((t, ty or ktype) for t, ty in sub)
    else:
        out.append((str(value), None))
    return out


def item_text(obj):
    for k in TEXT_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v
    rest = {k: v for k, v in obj.items() if k not in NON_TEXT_KEYS}
    return json.dumps(rest, sort_keys=True, ensure_ascii=False)


def item_status(obj):
    st = obj.get("status")
    if isinstance(st, str):
        low = st.strip().lower()
        for s in INACTIVE:
            if low.startswith(s):
                return s
    return "active"


def item_must(obj, fam):
    for k in ("priority", "moscow", "must", "must_have", "priority_moscow"):
        v = obj.get(k)
        if v is True and k in ("must", "must_have"):
            return True
        if isinstance(v, str) and v.strip().lower() in ("must", "must-have", "must have", "m", "p0"):
            return True
    if fam == "OPP" and truthy(obj.get("target")):
        return True
    return False


def first_str(obj, keys):
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return k, v.strip()
        if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
            return k, ", ".join(v)
    return None, None


def make_item(obj, model, file_rel, stage, text=None, link_source=None):
    reg = model.reg
    iid = str(obj["id"]).strip()
    prefix, _ = reg.classify(iid)
    fam = family(prefix)
    txt = text if text is not None else item_text(obj)
    status = item_status(obj)
    kind = obj.get("kind") or obj.get("type")
    just = obj.get("justification")
    na = False
    for k in ("target", "applicability", "value"):
        v = obj.get(k)
        if isinstance(v, str) and v.strip().lower().startswith(("n/a", "not applicable")):
            na = True
    disp = " ".join(str(obj.get(k, "")) for k in ("disposition", "strategy", "treatment", "response"))
    item = {
        "id": iid, "prefix": prefix, "family": fam, "stage": stage, "file": file_rel,
        "sha256": text_hash(txt), "text_len": len(norm_text(txt)), "status": status, "must": item_must(obj, fam),
        "kind": str(kind).lower() if isinstance(kind, str) else None,
        "justification": just if isinstance(just, str) else None,
        "evidence_status": str(obj.get("evidence_status") or ""),
        "na": na, "mitigate": "mitigat" in disp.lower(),
        "target_stage": str(obj.get("target_stage") or ""),
        "rationale": first_str(obj, RATIONALE_KEYS)[1],
        "approver": None,
    }
    _, appr = first_str(obj, APPROVER_KEYS)
    if appr:
        m = re.search(r"\b(?:DEC-\d{3}|DL-[PAT]-\d{2,3})\b", appr)
        item["approver"] = m.group(0) if m else appr
    src = link_source or file_rel
    for key in sorted(obj):
        val = obj[key]
        if key in ("traces_to", "supports", "drivers") or (key in LINK_TYPES and key != "derives"):
            ktype = key if key in LINK_TYPES else ("satisfies" if key == "drivers" else None)
            for tid, ty in ids_in(val, reg):
                link_to(model, iid, tid, ty or ktype, src, file_rel)
        elif key == "evidence_ids":
            for tid, ty in ids_in(val, reg):
                link_to(model, tid, iid, ty or "derives", src, file_rel, reverse=True)
        elif key == "trace_links" and isinstance(val, list):
            add_trace_links(model, val, src)
    model.add_def(item)
    return item


def link_to(model, frm, to, ltype, source, file_rel, reverse=False):
    reg = model.reg
    probe = frm if reverse else to
    prefix, valid = reg.classify(probe)
    if not valid:
        if prefix:  # looks like a registry ID but malformed
            model.dangling[(probe, source)] = frm if not reverse else to
        return
    if ltype is None:
        ltype = default_link_type(frm, reg)
    model.add_link(frm, to, ltype, source)
    model.dangling.setdefault(("?check", probe, source, frm if not reverse else to), None)


def add_trace_links(model, links, source):
    for l in links:
        if isinstance(l, dict) and l.get("from") and l.get("to"):
            frm, to = str(l["from"]), str(l["to"])
            ltype = l.get("type") or default_link_type(frm, model.reg)
            model.add_link(frm, to, ltype, source)
            for end in (frm, to):
                if model.reg.is_item(end):
                    model.dangling.setdefault(("?check", end, source, frm), None)


def walk(obj, model, file_rel, stage, parent=None, depth=0):
    if depth > 60:
        return
    if isinstance(obj, dict):
        cur = parent
        iid = obj.get("id")
        if isinstance(iid, str):
            prefix, valid = model.reg.classify(iid)
            if valid:
                cur = make_item(obj, model, file_rel, stage)
                if parent is not None:
                    model.add_link(cur["id"], parent["id"], "refines", file_rel + " (nesting)")
            elif prefix or "traces_to" in obj:
                model.unknown_trace_items.append({"id": iid, "file": file_rel,
                                                  "kind": "bad_format" if prefix else "unknown_prefix"})
        # drop records held outside the item itself (e.g. scope.json dropped[])
        for key in DROP_LIST_KEYS:
            v = obj.get(key)
            if isinstance(v, list):
                for e in v:
                    rid = e if isinstance(e, str) else (
                        (e.get("id") or e.get("item") or e.get("ref")) if isinstance(e, dict) else None)
                    if isinstance(rid, str) and model.reg.is_item(rid):
                        rec = {"status": "deferred" if key == "deferred" else "dropped", "source": file_rel,
                               "rationale": first_str(e, RATIONALE_KEYS)[1] if isinstance(e, dict) else None,
                               "approver": first_str(e, APPROVER_KEYS)[1] if isinstance(e, dict) else None}
                        model.drop_refs.setdefault(rid, rec)
        flat = " ".join(str(v) for v in obj.values() if isinstance(v, (str, bool)))
        if re.search(r"no[\s_-]?interface", flat + " " + " ".join(obj.keys()), re.I):
            for v in obj.values():
                if isinstance(v, str):
                    for t in model.reg.tokens(v):
                        model.no_interface.add(t)
                elif isinstance(v, list):
                    for x in v:
                        if isinstance(x, str) and model.reg.is_item(x):
                            model.no_interface.add(x)
        for k in sorted(obj):
            if k in ("traces_to", "trace_links", "supports", "evidence_ids", "drivers") or \
                    k in DROP_LIST_KEYS:  # drop lists reference items, they do not define them
                continue
            walk(obj[k], model, file_rel, stage, cur, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, model, file_rel, stage, parent, depth + 1)


def load_csv(text, model, file_rel, stage):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return
    header = [h.strip() for h in rows[0]]
    low = [h.lower() for h in header]
    body = [r for r in rows[1:] if any(c.strip() for c in r)]
    id_col = low.index("id") if "id" in low else None
    if id_col is None:
        for c in range(len(header)):
            vals = [r[c].strip() for r in body if c < len(r) and r[c].strip()]
            if vals and all(model.reg.is_item(v) for v in vals):
                id_col = c
                break
    if id_col is None:
        return
    link_cols = [c for c, h in enumerate(low) if c != id_col and LINK_COL_RE.search(h)]
    text_cols = [c for c, h in enumerate(low) if h in TEXT_KEYS]
    for r in body:
        if id_col >= len(r) or not model.reg.is_item(r[id_col].strip()):
            continue
        obj = {"id": r[id_col].strip()}
        for c, h in enumerate(low):
            if c < len(r) and c not in link_cols and c != id_col:
                obj[h] = r[c]
        traces = []
        for c in link_cols:
            if c < len(r):
                traces.extend(t for t in re.split(r"[,;|\s]+", r[c]) if t)
        obj["traces_to"] = traces
        txt = r[text_cols[0]] if text_cols and text_cols[0] < len(r) else \
            " | ".join(r[c] for c in range(len(r)) if c not in link_cols and low[c] != "status")
        make_item(obj, model, file_rel, stage, text=txt)


def load_md_table_items(text, model, file_rel, stage, only_families):
    header = None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        first = cells[0].strip("`* ") if cells else ""
        prefix, valid = model.reg.classify(first)
        if not valid or family(prefix) not in only_families:
            continue
        obj = {"id": first}
        traces = []
        for c, h in enumerate(header):
            if c == 0 or c >= len(cells):
                continue
            if LINK_COL_RE.search(h):
                traces.extend(model.reg.tokens(cells[c]))
            else:
                obj[h] = cells[c]
        obj["traces_to"] = traces
        make_item(obj, model, file_rel, stage, text=" | ".join(cells[1:]))


def load_ledger(text, model, file_rel):
    header = None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        row = dict(zip(header, cells))
        lid = row.get("ledger_id", "")
        if not model.reg.is_item(lid):
            continue
        status = row.get("status", "").lower()
        # ledger `deferred` means carried to target_stage, not dropped: keep the row active
        obj = {"id": lid, "statement": row.get("item", ""), "target_stage": row.get("target_stage", "").lower(),
               "decision_ref": row.get("decision_ref", "")}
        it = make_item(obj, model, file_rel, CROSS)
        it["ledger_status"] = status


# ---------------------------------------------------------------- run context

class Ctx:
    def __init__(self, run_dir, stage, mode):
        self.run_dir = run_dir
        self.stage = stage
        self.mode = mode
        self.inputs = {}
        self.parse_errors = []
        parent = os.path.dirname(run_dir)
        if os.path.basename(parent) == "pipeline" and os.path.basename(os.path.dirname(parent)) == "docs":
            self.repo_root = os.path.dirname(os.path.dirname(parent))
        else:
            self.repo_root = os.getcwd()

    def rel(self, path):
        return os.path.relpath(path, self.run_dir).replace(os.sep, "/")

    def read(self, rel_path, record=True):
        path = os.path.join(self.run_dir, rel_path)
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError:
            return None
        if record:
            self.inputs[self.rel(path)] = sha256_bytes(data)
        return data.decode("utf-8", errors="replace")

    def exists(self, rel_path):
        return os.path.exists(os.path.join(self.run_dir, rel_path))


def list_files(ctx, stage, include_named_work):
    sdir = os.path.join(ctx.run_dir, STAGE_DIR[stage])
    machine, md = [], []
    if not os.path.isdir(sdir):
        return machine, md
    for root, dirs, files in os.walk(sdir):
        rel_root = os.path.relpath(root, sdir).replace(os.sep, "/")
        top = rel_root.split("/")[0] if rel_root != "." else ""
        if top in EXCLUDED_SUBDIRS:
            dirs[:] = []
            continue
        dirs.sort()
        for f in sorted(files):
            rel = ctx.rel(os.path.join(root, f))
            if f.endswith(MACHINE_EXT):
                machine.append(rel)
            elif f.endswith(".md"):
                md.append(rel)
    if include_named_work:
        for w in NAMED_WORK_FILES.get(stage, []):
            rel = STAGE_DIR[stage] + "/" + w
            if ctx.exists(rel):
                machine.append(rel)
    return sorted(set(machine)), sorted(set(md))


def review_files(ctx, stage):
    rdir = os.path.join(ctx.run_dir, STAGE_DIR[stage], "reviews")
    tops, lens = [], []
    if not os.path.isdir(rdir):
        return tops, lens
    for root, dirs, files in os.walk(rdir):
        dirs.sort()
        for f in sorted(files):
            rel = ctx.rel(os.path.join(root, f))
            if os.path.abspath(root) == os.path.abspath(rdir):
                if f.endswith(".md"):
                    tops.append(rel)
            else:
                lens.append(rel)
    return tops, lens


def parse_machine(ctx, model, rel, stage):
    text = ctx.read(rel)
    if text is None:
        ctx.parse_errors.append({"file": rel, "error": "unreadable"})
        return
    try:
        if rel.endswith(".json"):
            data = json.loads(text)
        elif rel.endswith((".yaml", ".yml")):
            data = load_yaml(text)
        else:
            load_csv(text, model, rel, stage)
            return
    except Exception as e:  # malformed artifact is a finding, not a crash
        ctx.parse_errors.append({"file": rel, "error": "%s: %s" % (type(e).__name__, str(e)[:160])})
        return
    walk(data, model, rel, stage)


def parse_md_item_file(ctx, model, rel, stage):
    text = ctx.read(rel, record=False)
    if text is None:
        return
    fm, body = split_frontmatter(text)
    if fm is None:
        return
    try:
        data = load_yaml(fm)
    except Exception as e:
        ctx.parse_errors.append({"file": rel, "error": "frontmatter: %s" % str(e)[:160]})
        return
    if isinstance(data, dict) and isinstance(data.get("id"), str) and model.reg.is_item(data["id"]):
        ctx.inputs[rel] = sha256_bytes(text.encode("utf-8"))
        txt = data.get("statement") or data.get("text") or body
        make_item(data, model, rel, stage, text=txt)


def parse_review(ctx, model, rel, review_findings):
    text = ctx.read(rel)
    if text is None:
        return
    fm, _ = split_frontmatter(text)
    if fm is None:
        return
    try:
        data = load_yaml(fm)
    except Exception as e:
        ctx.parse_errors.append({"file": rel, "error": "frontmatter: %s" % str(e)[:160]})
        return
    if not isinstance(data, dict):
        return
    if isinstance(data.get("trace_links"), list):
        add_trace_links(model, data["trace_links"], rel)
    for f in data.get("findings") or []:
        if isinstance(f, dict) and f.get("location"):
            review_findings.append((rel, str(f.get("id", "")), str(f["location"])))


# ------------------------------------------------------------ location resolution

def resolve_location(ctx, loc, cache):
    loc = (loc or "").strip().strip("`")
    if not loc:
        return False
    anchor = line = None
    path = loc
    m = re.match(r"^(.*?):(\d+)(?:-\d+)?$", loc)
    if "#" in loc:
        path, anchor = loc.split("#", 1)
    elif m:
        path, line = m.group(1), int(m.group(2))
    path = path.strip()
    cands = []
    if os.path.isabs(path):
        cands.append(path)
    else:
        cands += [os.path.join(ctx.repo_root, path), os.path.join(ctx.run_dir, path)]
        cands += [os.path.join(ctx.run_dir, STAGE_DIR[s], path) for s in STAGES]
    target = next((c for c in cands if os.path.isfile(c)), None)
    if target is None:
        return False
    if anchor is None and line is None:
        return True
    if target not in cache:
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as fh:
                cache[target] = fh.read()
        except OSError:
            cache[target] = ""
    text = cache[target]
    if line is not None:
        return len(text.splitlines()) >= line
    anchor = anchor.strip()
    if not anchor:
        return True
    lm = re.fullmatch(r"L(\d+)(?:-L?\d+)?", anchor)
    if lm:
        return len(text.splitlines()) >= int(lm.group(1))
    if anchor in text:
        return True
    for h in re.findall(r"^#{1,6}\s+(.*)$", text, re.M):
        if github_slug(h) == anchor.lower():
            return True
    return False


# ------------------------------------------------------------------- analysis

class Analysis:
    def __init__(self, ctx, reg, model, rule_stages, history, matrix):
        self.ctx, self.reg, self.model = ctx, reg, model
        self.rule_stages = rule_stages
        self.history, self.matrix = history, matrix
        self.items = {}
        self.id_errors, self.duplicates, self.renumbered = [], [], []
        self.adj = {}
        self.out_links = {}

    # canonical item per ID: earliest stage, then non-work file, then path
    def canonicalise(self):
        for iid, defs in self.model.defs.items():
            defs.sort(key=lambda d: (stage_index(d["stage"]) if d["stage"] in STAGES else -1,
                                     "/work/" in d["file"], d["file"]))
            self.items[iid] = defs[0]
        for iid in self.items:
            m = re.match(r"^AC-FR-(\d{3})-\d+$", iid)
            if m and self.items.get("FR-" + m.group(1), {}).get("must"):
                self.items[iid]["must"] = True

    def build_graph(self):
        for (frm, to, _t) in self.model.links:
            if frm in self.items and to in self.items:
                self.adj.setdefault(frm, set()).add(to)
                self.adj.setdefault(to, set()).add(frm)
                self.out_links.setdefault(frm, set()).add(to)

    def check_ids(self):
        reg = self.reg
        for u in self.model.unknown_trace_items:
            self.id_errors.append({"kind": u["kind"], "id": u["id"], "location": "%s#%s" % (u["file"], u["id"]),
                                   "detail": "item id does not match the registry"})
        for (k, *rest), _ in sorted(self.model.dangling.items(), key=lambda kv: json.dumps(kv[0])):
            if k == "?check":
                probe, source, frm = rest
                if probe not in self.items:
                    self.id_errors.append({"kind": "dangling_reference", "id": probe,
                                           "location": "%s#%s" % (source, frm if frm in self.items else probe),
                                           "detail": "%s references %s, which no parsed artifact defines" % (frm, probe)})
            else:
                probe, source = k, rest[0]
                self.id_errors.append({"kind": "malformed_reference", "id": probe,
                                       "location": "%s#%s" % (source, probe),
                                       "detail": "reference has a registry prefix but fails its regex"})
        for iid, defs in sorted(self.model.defs.items()):
            prefix = defs[0]["prefix"]
            first = self.items[iid]
            by_file = {}
            for d in defs:
                by_file.setdefault(d["file"], []).append(d)
            for f, ds in sorted(by_file.items()):
                if len(ds) > 1:
                    self.duplicates.append({"id": iid, "kind": "same_file", "severity": "BLOCKER",
                                            "locations": ["%s#%s" % (f, iid)], "count": len(ds)})
            by_stage = {}
            for d in defs:
                by_stage.setdefault(d["stage"], {}).setdefault(d["sha256"], set()).add(d["file"])
            for st, shas in sorted(by_stage.items()):
                if len(shas) > 1:
                    locs = sorted("%s#%s" % (f, iid) for fs in shas.values() for f in fs)
                    self.duplicates.append({"id": iid, "kind": "conflicting_definition", "severity": "BLOCKER",
                                            "locations": locs, "count": len(locs)})
            for d in defs:
                if d is first or d["stage"] == first["stage"] or d["stage"] == CROSS:
                    continue
                if d["sha256"] != first["sha256"]:
                    self.id_errors.append({"kind": "inherited_redefined", "id": iid,
                                           "location": "%s#%s" % (d["file"], iid),
                                           "detail": "upstream ID re-defined in %s with different text (first in %s)"
                                                     % (d["stage"], first["file"])})
            st = first["stage"]
            if st not in STAGES or prefix in CROSS_PREFIXES or prefix == "LED":
                continue
            fam_prefix = prefix.split("-")[0] if prefix not in reg.owner else prefix
            base = prefix.split("-")[0]
            if base in reg.shared:
                m = re.match(r"^%s-([PAT])-" % re.escape(base), iid)
                if st == "discovery" and m:
                    self.id_errors.append({"kind": "unexpected_stage_infix", "id": iid,
                                           "location": "%s#%s" % (first["file"], iid),
                                           "detail": "Discovery mints bare IDs for shared prefixes"})
                elif st != "discovery" and not m and not (base == "SPK" and st == "architecture"):
                    self.id_errors.append({"kind": "missing_stage_infix", "id": iid,
                                           "location": "%s#%s" % (first["file"], iid),
                                           "detail": "%s minted in %s without -%s- infix" % (base, st, STAGE_INFIX[st])})
                elif m and st != "discovery" and m.group(1) != STAGE_INFIX[st]:
                    self.id_errors.append({"kind": "wrong_stage_infix", "id": iid,
                                           "location": "%s#%s" % (first["file"], iid),
                                           "detail": "infix -%s- used in %s" % (m.group(1), st)})
                continue
            owner = reg.owner.get(fam_prefix, "")
            if owner in STAGES and owner != st:
                kind = "prefix_minted_early" if stage_index(owner) > stage_index(st) else "upstream_prefix_reminted"
                self.id_errors.append({"kind": kind, "id": iid, "location": "%s#%s" % (first["file"], iid),
                                       "detail": "prefix %s is owned by %s, minted in %s" % (prefix, owner, st)})
        # same text under two active IDs (possible silent copy or renumbering)
        by_sha = {}
        for iid, it in self.items.items():
            if it["status"] == "active" and it["text_len"] >= 20:
                by_sha.setdefault((it["family"], it["sha256"]), []).append(iid)
        for (_fam, sha), ids in sorted(by_sha.items()):
            if len(ids) > 1:
                self.duplicates.append({"id": sorted(ids)[0], "kind": "same_text_different_ids",
                                        "severity": "NOTE", "ids": sorted(ids),
                                        "locations": sorted("%s#%s" % (self.items[i]["file"], i) for i in ids),
                                        "count": len(ids)})

    def check_history(self):
        hist = self.history
        if not hist:
            return
        parsed_stages = {it["stage"] for it in self.items.values()}
        cur_by_sha = {}
        for iid, it in self.items.items():
            cur_by_sha.setdefault(it["sha256"], []).append(iid)
        for hid in sorted(hist):
            h = hist[hid]
            hstage = h.get("stage")
            if hstage in STAGES and stage_index(hstage) > stage_index(self.ctx.stage):
                continue
            if hstage and hstage not in parsed_stages:
                continue
            cur = self.items.get(hid)
            hsha = h.get("sha256")
            hstat = h.get("status", "active")
            if cur is None:
                movers = [i for i in cur_by_sha.get(hsha, []) if i not in hist] if hsha else []
                if movers:
                    for to in sorted(movers):
                        self.renumbered.append({"from": hid, "to": to, "kind": "text_moved_to_new_id",
                                                "sha256": hsha, "location": "%s#%s" % (self.items[to]["file"], to)})
                elif hstat == "active":
                    self.id_errors.append({"kind": "deleted_without_record", "id": hid,
                                           "location": "trace/matrix.json#%s" % hid,
                                           "detail": "ID recorded earlier is absent and has no dropped/superseded record"})
                continue
            if hsha and cur["sha256"] != hsha:
                others = [i for i in cur_by_sha.get(hsha, []) if i != hid]
                for to in sorted(others):
                    self.renumbered.append({"from": hid, "to": to, "kind": "text_moved_to_other_id",
                                            "sha256": hsha, "location": "%s#%s" % (self.items[to]["file"], to)})
                if hstat in ("dropped", "superseded") and cur["status"] == "active":
                    self.id_errors.append({"kind": "reused_after_drop", "id": hid,
                                           "location": "%s#%s" % (cur["file"], hid),
                                           "detail": "ID was %s and is active again with different text" % hstat})

    def suspects(self, revalidate):
        out = []
        mitems = {i.get("id"): i for i in (self.matrix.get("items") or []) if isinstance(i, dict)}
        for l in self.matrix.get("links") or []:
            if not isinstance(l, dict):
                continue
            to, frm = l.get("to"), l.get("from")
            if (frm, to) in revalidate:
                continue
            rec = l.get("to_sha256") or (mitems.get(to) or {}).get("sha256")
            cur = self.items.get(to)
            if not rec or cur is None or cur["sha256"] == rec:
                continue
            out.append({"link": {"from": frm, "to": to, "type": l.get("type")},
                        "upstream_change": {"id": to, "recorded_sha256": rec, "current_sha256": cur["sha256"],
                                            "recorded_at_version": l.get("recorded_at_version")},
                        "source": l.get("source"),
                        "location": "%s#%s" % (cur["file"], to)})
        return sorted(out, key=lambda s: (s["link"]["to"], s["link"]["from"] or "", s["link"]["type"] or ""))

    def has(self, iid, fams, filt=None):
        for n in self.adj.get(iid, ()):
            it = self.items[n]
            if it["family"] in fams and it["status"] != "superseded" and (filt is None or filt(it)):
                return True
        return False

    def dropped(self, iid):
        it = self.items.get(iid)
        return (it is not None and it["status"] in ("dropped", "deferred")) or iid in self.model.drop_refs

    def active(self, fams, stages=None):
        return sorted(i for i, it in self.items.items()
                      if it["family"] in fams and it["status"] == "active"
                      and (stages is None or it["stage"] in stages))

    def coverage_and_gaps(self):
        segs, fwd = {}, []
        for st in self.rule_stages:
            for name, parents, children, scope in SEGMENTS[st]:
                pids = self.active(parents)
                if "LED" in parents:
                    pids = [p for p in pids if self.items[p]["family"] != "LED"
                            or (self.items[p].get("target_stage") == st
                                and self.items[p].get("ledger_status", "open") in ("open", "deferred"))]
                cids = self.active(children)
                pc = [p for p in pids if self.has(p, children)]
                cc = [c for c in cids if self.has(c, parents)]
                segs[name] = {"stage": st, "parents": len(pids), "parents_covered": len(pc),
                              "forward_pct": pct(len(pc), len(pids)), "children": len(cids),
                              "children_linked": len(cc), "backward_pct": pct(len(cc), len(cids)),
                              "forward_scope": scope}
                if scope == "none":
                    continue
                for p in pids:
                    it = self.items[p]
                    if p in pc or (scope == "must" and not it["must"]):
                        continue
                    if self.dropped(p):
                        continue
                    fwd.append({"segment": name, "id": p, "must": it["must"], "missing": sorted(children),
                                "location": "%s#%s" % (it["file"], p)})
        return segs, sorted(fwd, key=lambda g: (g["segment"], g["id"]))

    def link_type_coverage(self):
        counts = {}
        total = 0
        for (frm, to, t) in self.model.links:
            if frm in self.items and to in self.items:
                counts[t or "untyped"] = counts.get(t or "untyped", 0) + 1
                total += 1
        return {t: {"count": c, "pct": pct(c, total)} for t, c in sorted(counts.items())}, total

    def orphans(self):
        out = []
        for iid in sorted(self.items):
            it = self.items[iid]
            if it["stage"] not in self.rule_stages or it["status"] != "active":
                continue
            if it["family"] in ORPHAN_EXEMPT:
                continue
            ups = [n for n in self.out_links.get(iid, ()) if not
                   (it["family"] == "FR" and self.items[n]["family"] == "AC")]
            if ups:
                continue
            just = None
            if it["kind"] in ("enabling", "technical"):
                just = "kind:" + it["kind"]
            elif it["justification"] and it["justification"].lower().startswith("new"):
                just = it["justification"]
            out.append({"id": iid, "stage": it["stage"], "family": it["family"], "justified": bool(just),
                        "justification": just, "location": "%s#%s" % (it["file"], iid)})
        return out

    def blocking(self, orphans):
        gaps, must = [], {}

        def gap(rule, iid, detail):
            it = self.items[iid]
            gaps.append({"rule": rule, "id": iid, "stage": it["stage"], "detail": detail,
                         "location": "%s#%s" % (it["file"], iid)})

        def mcheck(iid, ok):
            must[iid] = must.get(iid, True) and ok

        orphan_ids = {o["id"]: o for o in orphans}
        unverifiable = []
        for st in self.rule_stages:
            if st == "discovery":
                for o in self.active({"OPP"}):
                    it = self.items[o]
                    if not it["must"]:
                        continue
                    ok = self.has(o, {"EVD"}) or it["evidence_status"].lower().startswith("assumption-only") \
                        or self.dropped(o)
                    mcheck(o, ok)
                    if not ok:
                        gap("D-B1", o, "target OPP without >=1 EVD and without assumption-only status")
                for m in self.active({"MET"}):
                    if not self.has(m, {"OUT"}):
                        gap("D-B2", m, "MET without OUT")
            elif st == "prd":
                for o in self.active({"OPP"}):
                    if self.items[o]["must"]:
                        ok = self.has(o, {"G", "FR"}) or self.dropped(o)
                        mcheck(o, ok)
                        if not ok:
                            gap("P-B1", o, "Must OPP with no G/FR and no drop record")
                for f in self.active({"FR"}, {"prd"}):
                    o = orphan_ids.get(f)
                    if o and not o["justified"]:
                        gap("P-B2", f, "FR with no upstream link")
                    if self.items[f]["must"]:
                        ok = self.has(f, {"AC"})
                        mcheck(f, ok)
                        if not ok:
                            gap("P-B3", f, "Must FR without AC")
                for g in self.active({"G"}, {"prd"}):
                    if self.items[g]["must"]:
                        ok = self.has(g, {"M"})
                        mcheck(g, ok)
                        if not ok:
                            gap("P-B4", g, "Must G without M")
            elif st == "architecture":
                for f in self.active({"FR"}):
                    if self.items[f]["must"]:
                        ok = self.has(f, {"C", "CMP", "OP"}) or f in self.model.no_interface or self.dropped(f)
                        mcheck(f, ok)
                        if not ok:
                            gap("A-B1", f, "Must FR without C/CMP/OP or 'no interface' note")
                for n in self.active({"NFR"}):
                    if not self.items[n]["na"] and not self.has(n, {"QAS"}) and not self.dropped(n):
                        gap("A-B2", n, "NFR without QAS")
                for a in self.active({"ADR"}, {"architecture"}):
                    if not self.has(a, ADR_DRIVERS):
                        gap("A-B3", a, "ADR without driver ID")
                for c in self.active({"C", "CMP"}, {"architecture"}):
                    if not self.has(c, {"FR", "NFR", "ADR"}):
                        gap("A-B4", c, "component with no FR/NFR/ADR")
                for t in self.active({"THR"}):
                    if self.items[t]["mitigate"] and not self.has(t, CONTROL_FAMILIES - {"T"}):
                        gap("A-B5", t, "THR `mitigate` without control")
            elif st == "tasks":
                for f in self.active({"FR", "AC"}):
                    it = self.items[f]
                    if not it["must"] or it["stage"] not in ("prd",):
                        continue
                    tasks = [n for n in self.adj.get(f, ()) if self.items[n]["family"] == "T"]
                    verified = self.has(f, {"TST"}) or any(self.has(t, {"TST"}) for t in tasks)
                    ok = (bool(tasks) and verified) or self.dropped(f)
                    mcheck(f, ok)
                    if not verified and not self.dropped(f):
                        unverifiable.append({"id": f, "location": "%s#%s" % (it["file"], f)})
                    if not ok:
                        gap("T-B1", f, "Must %s without %s" % (it["family"], " and ".join(
                            x for x, miss in (("task", not tasks), ("test", not verified)) if miss)))
                for x in self.active({"THR", "OBL", "SLO", "LED"}):
                    it = self.items[x]
                    if it["family"] == "THR" and not it["mitigate"]:
                        continue
                    if it["family"] == "LED" and not (it.get("target_stage") == "tasks"
                                                      and it.get("ledger_status", "open") in ("open", "deferred")):
                        continue
                    if not self.has(x, {"T"}) and not self.dropped(x):
                        gap("T-B2", x, "%s targeted at Tasks without a task" % it["family"])
                for t in self.active({"T"}, {"tasks"}):
                    if t in orphan_ids:
                        gap("T-B3", t, "task with no upstream link" + (
                            " (enabling task must link an NFR/ADR)" if self.items[t]["kind"] == "enabling" else ""))
                for s in self.active({"TST"}, {"tasks"}):
                    if not self.has(s, {"T"}):
                        gap("T-B4", s, "test without task")
        gaps.sort(key=lambda g: (g["rule"], g["id"]))
        covered = sorted(i for i, ok in must.items() if ok)
        return gaps, {"total": len(must), "covered": len(covered),
                      "uncovered": sorted(i for i, ok in must.items() if not ok)}, \
            sorted(unverifiable, key=lambda u: u["id"])

    def drop_records(self, known_approvers):
        out = []
        for iid in sorted(self.items):
            it = self.items[iid]
            if it["status"] not in ("dropped", "deferred") and iid not in self.model.drop_refs:
                continue
            ref = self.model.drop_refs.get(iid, {})
            appr = it["approver"] or ref.get("approver")
            out.append({"id": iid, "status": it["status"] if it["status"] != "active" else ref.get("status"),
                        "rationale_present": bool(it["rationale"] or ref.get("rationale")),
                        "approver": appr, "approver_known": bool(appr and appr in known_approvers),
                        "location": "%s#%s" % (it["file"], iid)})
        return out


# ------------------------------------------------------------------ findings

def make_findings(rep, stage, round_no, prior_ids):
    letter = STAGE_LETTER[stage]
    crit_map = {
        "blocking_gap": "conventions §4 blocking gap; shared-traceability-keeper stage-depth table",
        "id_error": "conventions §4 ID scheme; TRC-ACC-03; R-TRC-X-06",
        "duplicate": "conventions §4 immutability; TRC-ACC-03",
        "renumbered": "conventions §4 immutability (no renumbering); TRC-ACC-03; R-TRC-X-06",
        "orphan": "TRC-ACC-02 (zero unjustified orphans)",
        "suspect": "conventions §4 suspect links; TRC-ACC-05",
        "forward_gap": "TRC-ACC-01 (forward coverage)",
        "drop_record": "conventions §4 immutability (dropped item: rationale + approver); TRC-ACC-01",
        "handoff": "conventions §3.1 version and hash; R-TRC-X-04",
        "parse_error": "conventions §3.1 machine files are the source of truth",
        "unresolved_location": "conventions §6.1 every finding location must resolve",
        "unverifiable": "TRC-ACC-07 (verifying test link for every Must)",
    }
    scen = {
        "blocking_gap": "The next stage starts without an upstream commitment carried forward, so it builds or "
                        "skips work nobody traced.",
        "id_error": "Downstream stages bind to an ID that does not mean what it meant, so links point at the "
                    "wrong item.",
        "duplicate": "Two definitions answer to one ID; downstream readers pick different ones.",
        "renumbered": "An item silently changed ID; downstream links to the old ID now point at different content.",
        "orphan": "Work exists without an upstream reason and cannot be justified or prioritised.",
        "suspect": "The upstream item changed after the link was recorded; the downstream item may no longer "
                   "satisfy it.",
        "drop_record": "A dropped commitment has no recorded approver, so the drop cannot be audited.",
        "handoff": "The stage reads a handoff that differs from the one the gate approved.",
        "parse_error": "Items in an unparseable artifact are invisible to the trace, so gaps go unreported.",
        "unresolved_location": "A reader cannot find the cited evidence, so the finding cannot be verified.",
        "unverifiable": "A Must ships with no test proving it.",
    }
    direction = {
        "blocking_gap": "Add the missing explicit traces_to link in the authoring artifact, or record a drop with "
                        "rationale and approver.",
        "id_error": "Restore the registered ID or add an explicit mapping in the decision log; do not re-mint.",
        "duplicate": "Keep one definition per ID; mirror files must carry identical text.",
        "renumbered": "Restore the original ID or record an explicit old-to-new mapping with an approver.",
        "orphan": "Add an explicit upstream traces_to link, or type the item enabling/technical with a link to an "
                  "NFR, ADR or risk.",
        "suspect": "Route to the owning author to revalidate the downstream item against the changed upstream text.",
        "forward_gap": "Confirm whether a downstream child is expected for this item.",
        "drop_record": "Record the rationale and a DEC-/DL- approver for the drop.",
        "handoff": "Re-issue the handoff or recompute the hashes; do not proceed on a mismatched version.",
        "parse_error": "Fix the artifact syntax so it parses.",
        "unresolved_location": "Point the location at an existing file and anchor.",
        "unverifiable": "Link a verifying test to the item or to its task.",
    }
    raw = []

    def add(cat, key, sev, refusal, location, evidence):
        raw.append({"cat": cat, "key": key, "severity": sev, "refusal_class": refusal,
                    "location": location, "evidence": evidence})

    for g in rep["blocking_gaps"]:
        add("blocking_gap", "blocking_gap:%s:%s" % (g["rule"], g["id"]), "BLOCKER", "rejected", g["location"],
            "%s %s: %s" % (g["rule"], g["id"], g["detail"]))
    for e in rep["id_errors"]:
        add("id_error", "id_error:%s:%s" % (e["kind"], e["id"]), "BLOCKER", "rejected", e["location"],
            "%s %s: %s" % (e["kind"], e["id"], e.get("detail", "")))
    for d in rep["duplicates"]:
        add("duplicate", "duplicate:%s:%s" % (d["kind"], d["id"]), d["severity"],
            "rejected" if d["severity"] == "BLOCKER" else None, d["locations"][0],
            "%s %s at %s" % (d["kind"], ", ".join(d.get("ids", [d["id"]])), "; ".join(d["locations"])))
    for r in rep["renumbered"]:
        add("renumbered", "renumbered:%s:%s" % (r["from"], r["to"]), "BLOCKER", "rejected", r["location"],
            "text of %s (sha256 %s...) now under %s" % (r["from"], r["sha256"][:12], r["to"]))
    blocking_ids = {g["id"] for g in rep["blocking_gaps"]}
    for o in rep["backward_orphans"]:
        if o["id"] in blocking_ids:
            continue
        if o["justified"]:
            add("orphan", "orphan:%s" % o["id"], "NOTE", None, o["location"],
                "%s has no upstream link; justification '%s' needs keeper review" % (o["id"], o["justification"]))
        else:
            add("orphan", "orphan:%s" % o["id"], "BLOCKER" if stage == "tasks" else "MAJOR", None,
                o["location"], "%s has no upstream traces_to link" % o["id"])
    for s in rep["suspect_links"]:
        add("suspect", "suspect:%s:%s" % (s["link"]["from"], s["link"]["to"]), "MAJOR", None, s["location"],
            "link %s -> %s: upstream text hash changed since version %s" % (
                s["link"]["from"], s["link"]["to"], s["upstream_change"].get("recorded_at_version")))
    for g in rep["forward_gaps"]:
        if g["id"] in blocking_ids:
            continue
        add("forward_gap", "forward_gap:%s:%s" % (g["segment"], g["id"]), "NOTE", None, g["location"],
            "%s has no child in segment %s" % (g["id"], g["segment"]))
    for u in rep["unverifiable"]:
        if u["id"] in blocking_ids:
            continue
        add("unverifiable", "unverifiable:%s" % u["id"], "BLOCKER", None, u["location"],
            "%s has no verifying test link" % u["id"])
    for d in rep["drop_records"]:
        if not d["rationale_present"] or not d["approver_known"]:
            add("drop_record", "drop_record:%s" % d["id"], "MAJOR", None, d["location"],
                "%s is %s; rationale %s; approver %s" % (d["id"], d["status"],
                                                          "present" if d["rationale_present"] else "missing",
                                                          d["approver"] or "missing"))
    hc = rep.get("handoff_check") or []
    for h in hc:
        for p in h["problems"]:
            add("handoff", "handoff:%s:%s" % (h["stage"], p["kind"] + ":" + p.get("path", "")), "BLOCKER",
                "blocked", p["location"], "%s: %s" % (p["kind"], p.get("detail", "")))
    for p in rep["parse_errors"]:
        add("parse_error", "parse_error:%s" % p["file"], "BLOCKER", "rejected", p["file"],
            "%s: %s" % (p["file"], p["error"]))
    for u in rep["unresolved_locations"]:
        add("unresolved_location", "unresolved_location:%s:%s" % (u["file"], u["finding"]), "MINOR", None,
            u["file"] + "#" + u["finding"] if u["finding"] else u["file"],
            "finding %s cites '%s', which does not resolve" % (u["finding"], u["location"]))

    raw.sort(key=lambda r: r["key"])
    used = {int(v.split("-")[-1]) for v in prior_ids.values() if re.match(r"^TRC-[DPAT]-\d+$", v)}
    nxt = max(used) + 1 if used else 1
    out = []
    for r in raw:
        fid = prior_ids.get(r["key"])
        if not fid:
            fid = "TRC-%s-%03d" % (letter, nxt)
            nxt += 1
        sev = r["severity"]
        out.append({
            "id": fid, "key": r["key"], "round_raised": round_no, "reviewer": "deterministic",
            "severity": sev, "criterion": crit_map[r["cat"]], "location": r["location"],
            "evidence": r["evidence"],
            "failure_scenario": scen.get(r["cat"], "") if sev in ("BLOCKER", "MAJOR") else "",
            "suggested_direction": direction[r["cat"]], "refusal_class": r["refusal_class"],
            "status": "open", "history": [{"round": round_no, "status": "open", "note": "raised by trace_check"}],
        })
    out.sort(key=lambda f: f["id"])
    return out


# ------------------------------------------------------------------ handoff check

def handoff_check(ctx, model, hstage, matrix):
    rel = STAGE_DIR[hstage] + "/handoff.md"
    res = {"stage": hstage, "path": rel, "handoff_version": None, "inputs_hash_recorded": None,
           "inputs_hash_recomputed": None, "verdict_inputs_hash": None,
           "matrix_records_version": None, "artifacts_checked": 0, "problems": []}
    text = ctx.read(rel)
    if text is None:
        res["problems"].append({"kind": "handoff_missing", "path": rel, "location": STAGE_DIR[hstage],
                                "detail": "no handoff.md"})
        return res
    fm, _ = split_frontmatter(text)
    try:
        data = load_yaml(fm) if fm else {}
    except Exception as e:
        data = {}
        res["problems"].append({"kind": "handoff_frontmatter_unparseable", "path": rel, "location": rel,
                                "detail": str(e)[:160]})
    data = data if isinstance(data, dict) else {}
    res["handoff_version"] = data.get("handoff_version")
    res["inputs_hash_recorded"] = data.get("inputs_hash")
    lines = []
    for a in data.get("artifacts") or []:
        if not isinstance(a, dict) or not a.get("path"):
            continue
        p, rec = str(a["path"]), str(a.get("sha256") or "").replace("sha256:", "")
        res["artifacts_checked"] += 1
        raw = None
        try:
            with open(os.path.join(ctx.run_dir, p), "rb") as fh:
                raw = fh.read()
        except OSError:
            res["problems"].append({"kind": "artifact_missing", "path": p, "location": "%s#%s" % (rel, p),
                                    "detail": "listed in artifacts but absent on disk"})
            lines.append("%s  %s\n" % (rec, p))
            continue
        cur = sha256_bytes(raw)
        lines.append("%s  %s\n" % (cur, p))
        if cur != rec:
            res["problems"].append({"kind": "artifact_hash_mismatch", "path": p, "location": "%s#%s" % (rel, p),
                                    "detail": "recorded %s..., on disk %s..." % (rec[:12], cur[:12])})
    res["inputs_hash_recomputed"] = "sha256:" + sha256_bytes("".join(lines).encode("utf-8"))
    res["inputs_hash_method"] = "sha256 over '<sha256>  <path>\\n' lines, artifacts in frontmatter order"
    if res["inputs_hash_recorded"] and res["inputs_hash_recorded"] != res["inputs_hash_recomputed"]:
        res["problems"].append({"kind": "inputs_hash_mismatch", "path": rel, "location": "%s#inputs_hash" % rel,
                                "detail": "frontmatter %s vs recomputed %s" % (
                                    res["inputs_hash_recorded"], res["inputs_hash_recomputed"])})
    vrel = STAGE_DIR[hstage] + "/gate/verdict.json"
    vtext = ctx.read(vrel)
    if vtext is not None:
        try:
            res["verdict_inputs_hash"] = json.loads(vtext).get("inputs_hash")
        except ValueError:
            pass
        if res["verdict_inputs_hash"] != res["inputs_hash_recorded"]:
            res["problems"].append({"kind": "verdict_hash_mismatch", "path": vrel,
                                    "location": "%s#inputs_hash" % vrel,
                                    "detail": "verdict.json %s vs handoff %s" % (
                                        res["verdict_inputs_hash"], res["inputs_hash_recorded"])})
    else:
        res["problems"].append({"kind": "verdict_missing", "path": vrel, "location": rel,
                                "detail": "gate/verdict.json absent"})
    hv = matrix.get("handoff_versions") if isinstance(matrix, dict) else None
    recv = None
    if isinstance(hv, dict):
        v = hv.get(hstage)
        recv = v.get("handoff_version") if isinstance(v, dict) else v
    elif isinstance(hv, list):
        for v in hv:
            if isinstance(v, dict) and v.get("stage") == hstage:
                recv = v.get("handoff_version")
    res["matrix_records_version"] = recv
    if recv != res["handoff_version"]:
        res["problems"].append({"kind": "matrix_version_mismatch", "path": "trace/matrix.json",
                                "location": "%s#handoff_version" % rel,
                                "detail": "trace/matrix.json records %s, handoff.md is %s" % (
                                    recv, res["handoff_version"])})
    res["problems"].sort(key=lambda p: (p["kind"], p.get("path", "")))
    return res


# ----------------------------------------------------------------------- main

def rule_stages_for(stage, mode):
    if mode in ("exit", "final"):
        return [stage]
    if stage == "discovery":
        return ["discovery"]
    if stage == "tasks":
        return ["prd", "architecture"]
    return [STAGES[STAGES.index(stage) - 1]]


def load_json_file(ctx, rel):
    text = ctx.read(rel)
    if text is None:
        return None, False
    try:
        return json.loads(text), True
    except ValueError as e:
        ctx.parse_errors.append({"file": rel, "error": "ValueError: %s" % str(e)[:160]})
        return None, True


def run(args):
    run_dir = os.path.abspath(args.run_dir)
    if not os.path.isdir(run_dir):
        raise UsageError("run dir not found: %s" % args.run_dir)
    stage, mode = args.stage, args.mode
    if mode == "reserve" and stage != "discovery":
        raise UsageError("reserve mode is Discovery-only")
    ctx = Ctx(run_dir, stage, mode)
    reg_data, reg_present = load_json_file(ctx, "trace/id-registry.json")
    reg = Registry(reg_data, reg_present)
    matrix, matrix_present = load_json_file(ctx, "trace/matrix.json")
    matrix = matrix if isinstance(matrix, dict) else {}
    model = Model(reg)
    rep = {"schema_version": "1.0", "tool": "trace_check.py", "tool_version": TOOL_VERSION,
           "yaml_parser": YAML_PARSER, "run_id": os.path.basename(run_dir), "stage": stage, "mode": mode,
           "round": args.round}
    if args.now:
        rep["generated_at"] = args.now
    registry_info = {"path": "trace/id-registry.json", "present": reg_present,
                     "prefix_count": len(reg.entries), "problems": sorted(reg.problems, key=lambda p: (p["kind"], p["detail"]))}
    rep["registry"] = registry_info

    rule_stages = [] if mode == "reserve" else rule_stages_for(stage, mode)
    rep["rule_stages"] = rule_stages
    cur_i = STAGES.index(stage)
    review_findings = []
    known_approvers = set()
    if mode != "reserve":
        for s in STAGES[:cur_i + 1]:
            machine, md = list_files(ctx, s, include_named_work=(s == stage))
            for rel in machine:
                parse_machine(ctx, model, rel, s)
            for rel in md:
                if rel.endswith("/handoff.md"):
                    continue
                parse_md_item_file(ctx, model, rel, s)
            # current-stage reviews are read in exit/final only (entry runs before the
            # lens reviewers), except when this stage's own handoff is being re-checked
            if STAGES.index(s) < cur_i or mode in ("exit", "final") or s in rule_stages:
                tops, lens = review_files(ctx, s)
                for rel in tops:
                    parse_review(ctx, model, rel, review_findings)
                for rel in lens:
                    if rel.endswith(MACHINE_EXT):
                        parse_machine(ctx, model, rel, s)
                    elif rel.endswith(".md"):
                        t = ctx.read(rel)
                        if t:
                            load_md_table_items(t, model, rel, s, CROSS_PREFIXES)
            dl = STAGE_DIR[s] + "/gate/decision-log.md"
            t = ctx.read(dl)
            if t:
                known_approvers.update(re.findall(r"\b(?:DEC-\d{3}|DL-[PAT]-\d{2,3})\b", t))
            ft = STAGE_DIR[s] + "/gate/findings.json"
            fj = ctx.read(ft)
            if fj:
                try:
                    fdata = json.loads(fj)
                    flist = fdata.get("findings", fdata) if isinstance(fdata, dict) else fdata
                    for f in flist if isinstance(flist, list) else []:
                        if isinstance(f, dict) and f.get("location"):
                            review_findings.append((ft, str(f.get("id", "")), str(f["location"])))
                except ValueError as e:
                    ctx.parse_errors.append({"file": ft, "error": "ValueError: %s" % str(e)[:160]})
        lt = ctx.read("crosscutting/ledger.md")
        if lt:
            load_ledger(lt, model, "crosscutting/ledger.md")

    an = Analysis(ctx, reg, model, rule_stages, {}, matrix)
    an.canonicalise()
    known_approvers.update(i for i in an.items if re.match(r"^(DEC|DL)-", i))
    an.build_graph()

    # history: registry ids[] then matrix items[] (matrix wins)
    hist = {}
    for src in (reg.ids if isinstance(reg.ids, list) else [], matrix.get("items") or []):
        for h in src:
            if isinstance(h, dict) and h.get("id"):
                hist[str(h["id"])] = {"sha256": h.get("sha256") or h.get("sha"), "status": h.get("status", "active"),
                                      "stage": h.get("stage") or h.get("owner_stage")}
    an.history = hist

    if mode == "reserve":
        rep.update({"inputs": [], "parse_errors": [], "id_errors": [], "duplicates": [], "renumbered": [],
                    "forward_gaps": [], "backward_orphans": [], "suspect_links": [], "blocking_gaps": [],
                    "unverifiable": [], "drop_records": [], "unresolved_locations": [], "handoff_check": None})
        for p in registry_info["problems"]:
            rep["id_errors"].append({"kind": p["kind"], "id": p["detail"], "location": "trace/id-registry.json",
                                     "detail": p["detail"]})
        if not reg_present:
            rep["id_errors"].append({"kind": "registry_missing", "id": "trace/id-registry.json",
                                     "location": "trace/report-%s-%s.json#id_errors" % (stage, mode),
                                     "detail": "reserve mode expects the keeper to have written the registry"})
        rep["coverage"] = {"must_pct": None, "coverage_must_pct": None,
                           "must": {"total": 0, "covered": 0, "uncovered": []}, "by_segment": {}, "by_link_type": {}}
    else:
        an.check_ids()
        an.check_history()
        if not reg_present:
            an.id_errors.append({"kind": "registry_missing", "id": "trace/id-registry.json",
                                 "location": "trace/report-%s-%s.json#id_errors" % (stage, mode),
                                 "detail": "no trace/id-registry.json; built-in §4 prefixes used"})
        if not matrix_present and stage != "discovery":
            an.id_errors.append({"kind": "matrix_missing", "id": "trace/matrix.json",
                                 "location": "trace/report-%s-%s.json#id_errors" % (stage, mode),
                                 "detail": "trace/matrix.json missing after Discovery (R-TRC-X-03)"})
        revalidate = set()
        for r in args.revalidate or []:
            if ":" in r:
                a, b = r.split(":", 1)
                revalidate.add((a.strip(), b.strip()))
        segs, fwd = an.coverage_and_gaps()
        orphans = an.orphans()
        gaps, must, unverifiable = an.blocking(orphans)
        by_type, total_links = an.link_type_coverage()
        must_pct = pct(must["covered"], must["total"])
        rep["inputs"] = []
        rep["parse_errors"] = sorted(ctx.parse_errors, key=lambda p: p["file"])
        rep["id_errors"] = sorted(an.id_errors, key=lambda e: (e["kind"], e["id"], e["location"]))
        rep["duplicates"] = sorted(an.duplicates, key=lambda d: (d["kind"], d["id"]))
        rep["renumbered"] = sorted(an.renumbered, key=lambda r: (r["from"], r["to"]))
        rep["forward_gaps"] = fwd
        rep["backward_orphans"] = orphans
        rep["coverage"] = {"must_pct": must_pct, "coverage_must_pct": must_pct, "must": must,
                           "by_segment": segs, "by_link_type": by_type, "links_total": total_links,
                           "annotation_links": model.annotations}
        rep["suspect_links"] = an.suspects(revalidate)
        rep["blocking_gaps"] = gaps
        rep["unverifiable"] = unverifiable
        rep["drop_records"] = an.drop_records(known_approvers)
        cache = {}
        unresolved = []
        for f, fid, loc in sorted(set(review_findings)):
            if not resolve_location(ctx, loc, cache):
                unresolved.append({"file": f, "finding": fid, "location": loc})
        rep["unresolved_locations"] = unresolved
        rep["handoff_check"] = None
        if mode == "entry":
            hstages = ["discovery"] if stage == "discovery" else rule_stages
            rep["handoff_check"] = [handoff_check(ctx, model, h, matrix) for h in hstages]

    out = args.out or os.path.join(run_dir, "trace", "report-%s-%s.json" % (stage, mode))
    out_rel = ctx.rel(os.path.abspath(out))
    # stable finding IDs across rounds: reuse IDs from earlier reports of this stage
    prior = {}
    tdir = os.path.join(run_dir, "trace")
    if os.path.isdir(tdir):
        names = sorted(n for n in os.listdir(tdir) if n.startswith("report-%s-" % stage) and n.endswith(".json"))
        for n in names:
            try:
                with open(os.path.join(tdir, n), "r", encoding="utf-8") as fh:
                    for f in json.load(fh).get("findings") or []:
                        if isinstance(f, dict) and f.get("key") and f.get("id"):
                            prior.setdefault(f["key"], f["id"])
            except (OSError, ValueError, AttributeError):
                continue
    rep["inputs"] = [{"path": p, "sha256": h} for p, h in sorted(ctx.inputs.items()) if p != out_rel]
    rep["findings"] = make_findings(rep, stage, args.round, prior)

    cache = {}
    bad_locs = [f["id"] for f in rep["findings"]
                if not resolve_location(ctx, f["location"], cache) and not f["location"].startswith(out_rel)]
    sev = {}
    for f in rep["findings"]:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    hc_problems = sum(len(h["problems"]) for h in (rep.get("handoff_check") or []))
    unjust = [o for o in rep["backward_orphans"] if not o["justified"]]
    blocking = bool(rep["blocking_gaps"] or rep["id_errors"] or rep["renumbered"] or rep["parse_errors"]
                    or hc_problems or any(d["severity"] == "BLOCKER" for d in rep["duplicates"])
                    or sev.get("BLOCKER"))
    rep["summary"] = {
        "items": len(an.items), "links": rep["coverage"].get("links_total", 0),
        "coverage_must_pct": rep["coverage"]["coverage_must_pct"],
        "blocking_gap_ids": sorted({g["id"] for g in rep["blocking_gaps"]}),
        "orphan_ids": sorted(o["id"] for o in unjust),
        "justified_orphan_ids": sorted(o["id"] for o in rep["backward_orphans"] if o["justified"]),
        "suspect_count": len(rep["suspect_links"]),
        "counts": {"id_errors": len(rep["id_errors"]), "duplicates": len(rep["duplicates"]),
                   "renumbered": len(rep["renumbered"]), "forward_gaps": len(rep["forward_gaps"]),
                   "backward_orphans": len(rep["backward_orphans"]), "blocking_gaps": len(rep["blocking_gaps"]),
                   "suspect_links": len(rep["suspect_links"]), "unverifiable": len(rep["unverifiable"]),
                   "parse_errors": len(rep["parse_errors"]), "unresolved_locations": len(rep["unresolved_locations"]),
                   "handoff_problems": hc_problems},
        "findings_by_severity": {k: sev.get(k, 0) for k in ("BLOCKER", "MAJOR", "MINOR", "NOTE")},
        "blocking": blocking,
        "self_check": {"finding_locations_resolve": not bad_locs, "unresolved_finding_ids": bad_locs},
    }
    if mode == "reserve":
        rep["summary"]["note"] = "reserve mode: registry validated only"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
    except OSError as e:
        raise UsageError("cannot write %s: %s" % (out, e))

    if args.update_matrix:
        if mode not in ("exit", "final"):
            raise UsageError("--update-matrix is allowed in exit/final mode only (report written)")
        write_matrix(ctx, an, matrix, rep, args, run_dir)
    return rep, out


def write_matrix(ctx, an, matrix, rep, args, run_dir):
    stage = args.stage
    hv = matrix.get("handoff_versions") if isinstance(matrix.get("handoff_versions"), dict) else {}
    prev = hv.get(stage)
    prev_v = prev.get("handoff_version") if isinstance(prev, dict) else prev
    version = args.handoff_version or (int(prev_v) + 1 if isinstance(prev_v, int) and args.mode == "final"
                                       else (prev_v or 1))
    revalidate = {tuple(r.split(":", 1)) for r in (args.revalidate or []) if ":" in r}
    old_links = {(l.get("from"), l.get("to"), l.get("type")): l for l in matrix.get("links") or []
                 if isinstance(l, dict)}
    suspect = {(s["link"]["from"], s["link"]["to"], s["link"]["type"]) for s in rep["suspect_links"]}
    items = []
    for iid in sorted(an.items):
        it = an.items[iid]
        items.append({"id": iid, "type": it["family"], "stage": it["stage"], "version": version,
                      "sha256": it["sha256"], "status": it["status"], "source": it["file"]})
    links = []
    for (frm, to, t), srcs in sorted(an.model.links.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or "")):
        if frm not in an.items or to not in an.items:
            continue
        old = old_links.get((frm, to, t))
        keep = old is not None and (frm, to) not in revalidate
        links.append({"from": frm, "to": to, "type": t, "source": sorted(srcs)[0],
                      "recorded_at_version": old.get("recorded_at_version", version) if keep else version,
                      "to_sha256": (old.get("to_sha256") or an.items[to]["sha256"]) if keep else an.items[to]["sha256"],
                      "status": "suspect" if (frm, to, t) in suspect else "valid"})
    new = dict(matrix)
    new["items"], new["links"] = items, links
    hv = dict(hv)
    if args.mode == "final":
        hv[stage] = {"handoff_version": version,
                     "artifacts": [i for i in rep["inputs"] if i["path"].startswith(STAGE_DIR[stage] + "/")]}
    new["handoff_versions"] = hv
    path = os.path.join(run_dir, "trace", "matrix.json")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(new, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
    except OSError as e:
        raise UsageError("cannot write %s: %s" % (path, e))


def main(argv=None):
    p = argparse.ArgumentParser(description="Deterministic trace-check (shared-traceability-keeper).")
    p.add_argument("--run-dir", required=True, help="docs/pipeline/<run-id>")
    p.add_argument("--stage", required=True, choices=STAGES)
    p.add_argument("--mode", required=True, choices=["reserve", "entry", "exit", "final"])
    p.add_argument("--out", help="report path (default <run-dir>/trace/report-<stage>-<mode>.json)")
    p.add_argument("--round", type=int, default=1, help="critic round, recorded in findings (default 1)")
    p.add_argument("--now", help="optional timestamp to record as generated_at (omitted by default)")
    p.add_argument("--update-matrix", action="store_true",
                   help="exit/final: rewrite trace/matrix.json items/links (final also records handoff_version)")
    p.add_argument("--handoff-version", type=int, help="handoff_version to record (final mode)")
    p.add_argument("--revalidate", action="append", metavar="FROM:TO",
                   help="link revalidated by its owner; clears its suspect status on --update-matrix")
    args = p.parse_args(argv)
    try:
        rep, out = run(args)
    except UsageError as e:
        sys.stderr.write("trace_check: %s\n" % e)
        return 2
    except OSError as e:
        sys.stderr.write("trace_check: I/O error: %s\n" % e)
        return 2
    s = rep["summary"]
    sys.stdout.write("trace_check %s/%s: items=%d links=%d coverage_must_pct=%s blocking_gaps=%d id_errors=%d "
                     "orphans=%d suspects=%d blocking=%s report=%s\n" % (
                         rep["stage"], rep["mode"], s["items"], s["links"], s["coverage_must_pct"],
                         s["counts"]["blocking_gaps"], s["counts"]["id_errors"], len(s["orphan_ids"]),
                         s["suspect_count"], str(s["blocking"]).lower(), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
