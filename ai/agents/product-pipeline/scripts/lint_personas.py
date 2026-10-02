#!/usr/bin/env python3
"""Lint the product-pipeline persona set (Claude Code subagent files).

Usage: python3 lint_personas.py [--strict]

Paths are resolved relative to this script: ../{discovery,prd,architecture,tasks,shared}/*.md
and ../skills/product-pipeline-conventions/SKILL.md.

Exit code 1 if any ERROR is found (or any WARN with --strict), else 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGES = ["discovery", "prd", "architecture", "tasks", "shared"]
ORCH = {
    "discovery": "discovery-orchestrator",
    "prd": "prd-orchestrator",
    "architecture": "arch-orchestrator",
    "tasks": "tasks-orchestrator",
}
SKILL_NAME = "product-pipeline-conventions"
SKILL_PATH = ROOT / "skills" / SKILL_NAME / "SKILL.md"

REQUIRED_FIELDS = ["name", "description", "model", "tools", "skills"]
FIELD_ORDER = ["name", "description", "tools", "disallowedTools", "model", "permissionMode",
               "maxTurns", "effort", "skills", "mcpServers", "hooks", "memory", "background",
               "isolation"]
KNOWN_FIELDS = set(FIELD_ORDER)
ALLOWED_MODELS = {"opus", "sonnet"}

BASE_SECTIONS = [
    "Identity and mindset", "Mission", "Scope", "Inputs", "Process", "Output contract",
    "Acceptance criteria", "Refusal criteria", "Anti-patterns", "Collaboration and handoffs",
]
ORCH_SECTIONS = [
    "Session start", "Entry gate", "Roster and activation rules", "Delegation plan",
    "Consolidation and conflict resolution", "Exit gate", "Handoff writing", "Human checkpoints",
]
SCOPE_SUBSECTIONS = ["You own", "You do not own"]
REFUSAL_TAGS = ["blocked", "rejected", "out_of_scope"]

# Least-privilege tool policy (warnings; documented exceptions listed below).
WORKER_TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "WebSearch", "WebFetch"}
CRITIC_TOOLS = {"Read", "Grep", "Glob", "Write"}
REVIEWER_TOOLS = {"Read", "Grep", "Glob", "Write"}
ORCH_TOOLS = {"Read", "Write", "Edit", "Grep", "Glob", "Bash", "AskUserQuestion"}
# Exceptions justified by the syntheses (persona -> extra tools allowed).
TOOL_EXCEPTIONS = {
    "arch-domain-data-modeler": {"Bash"},          # schema/contract validation
    "arch-interface-designer": {"Bash"},           # OpenAPI/AsyncAPI linting
    "shared-traceability-keeper": {"Bash"},        # deterministic trace-check script
    "shared-finops-analyst": {"WebSearch", "WebFetch"},  # pricing pages only
    "discovery-critic": {"WebFetch"},              # citation spot-check only
}
# Only personas whose job includes desk research (or a sanctioned fetch) may use the web.
WEB_SANCTIONED = {
    "discovery-evidence-synthesizer", "discovery-market-analyst", "discovery-critic",
    "arch-solution-designer", "prd-feasibility-reviewer", "shared-finops-analyst",
}

WORD_RANGES = {"worker": (1000, 2800), "orchestrator": (2300, 4600)}

errors: list[str] = []
warns: list[str] = []


def err(f: str, msg: str) -> None:
    errors.append(f"ERROR {f}: {msg}")


def warn(f: str, msg: str) -> None:
    warns.append(f"WARN  {f}: {msg}")


# ---------------------------------------------------------------- frontmatter
try:
    import yaml  # type: ignore

    def parse_yaml(text: str) -> dict:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("frontmatter is not a mapping")
        return data
except ImportError:  # minimal parser: scalars, quoted scalars, block lists
    def _scalar(v: str):
        v = v.strip()
        if not v:
            return None
        if (v[0] == v[-1]) and v[0] in "\"'" and len(v) >= 2:
            inner = v[1:-1]
            return inner.replace('\\"', '"') if v[0] == '"' else inner.replace("''", "'")
        if re.fullmatch(r"-?\d+", v):
            return int(v)
        if v in ("true", "false"):
            return v == "true"
        return v

    def parse_yaml(text: str) -> dict:
        data: dict = {}
        key = None
        for ln, line in enumerate(text.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$", line)
            if m:
                key = m.group(1)
                if key in data:
                    raise ValueError(f"duplicate key {key}")
                val = m.group(2)
                data[key] = _scalar(val) if val is not None else []
                continue
            m = re.match(r"^\s+-\s+(.*)$", line)
            if m and key is not None and isinstance(data[key], list):
                data[key].append(_scalar(m.group(1)))
                continue
            raise ValueError(f"cannot parse frontmatter line {ln}: {line!r}")
        return data


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, None, text
    raw = text[4:end]
    return raw, raw, text[end + 5:]


def parse_tools(tools) -> tuple[list[str], list[str]]:
    """Return (plain tools, Agent(...) entries)."""
    if isinstance(tools, list):
        tools = ", ".join(str(t) for t in tools)
    tools = str(tools or "")
    agents: list[str] = []
    m = re.search(r"Agent\(([^)]*)\)", tools)
    if m:
        agents = [a.strip() for a in m.group(1).split(",") if a.strip()]
        tools = tools[:m.start()] + tools[m.end():]
    plain = [t.strip() for t in tools.split(",") if t.strip()]
    if m:
        plain.append("Agent")
    return plain, agents


def sections(body: str) -> list[tuple[int, str, int]]:
    """List of (level, title, line_index) for markdown headings outside code fences."""
    out, fence = [], False
    for i, line in enumerate(body.splitlines()):
        if line.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,3})\s+(.*?)\s*$", line)
        if m:
            out.append((len(m.group(1)), m.group(2), i))
    return out


def section_text(body: str, title: str) -> str:
    lines = body.splitlines()
    heads = sections(body)
    for idx, (lvl, t, i) in enumerate(heads):
        if lvl == 2 and t == title:
            j = next((h[2] for h in heads[idx + 1:] if h[0] <= 2), len(lines))
            return "\n".join(lines[i + 1:j])
    return ""


# ---------------------------------------------------------------- main checks
def role_of(name: str, stage: str) -> str:
    if name.endswith("-orchestrator"):
        return "orchestrator"
    if name.endswith("-critic"):
        return "critic"
    if stage == "shared":
        return "reviewer"
    return "worker"


def main() -> int:
    strict = "--strict" in sys.argv
    personas: dict[str, dict] = {}

    skill_sections: set[str] = set()
    if SKILL_PATH.exists():
        skill_sections = set(re.findall(r"^#{2,3} §(\d+(?:\.\d+)?)\b",
                                        SKILL_PATH.read_text(encoding="utf-8"), re.M))
    if not SKILL_PATH.exists():
        err(str(SKILL_PATH), "conventions skill missing")
    else:
        raw, _, _ = split_frontmatter(SKILL_PATH.read_text(encoding="utf-8"))
        try:
            fm = parse_yaml(raw or "")
            if fm.get("name") != SKILL_NAME:
                err("skills/.../SKILL.md", f"skill name {fm.get('name')!r} != {SKILL_NAME}")
            if not fm.get("description"):
                err("skills/.../SKILL.md", "skill description missing")
        except Exception as e:  # noqa: BLE001
            err("skills/.../SKILL.md", f"frontmatter does not parse: {e}")

    for stage in STAGES:
        d = ROOT / stage
        if not d.is_dir():
            err(stage, "stage folder missing")
            continue
        for p in sorted(d.glob("*.md")):
            rel = f"{stage}/{p.name}"
            text = p.read_text(encoding="utf-8")
            raw, _, body = split_frontmatter(text)
            if raw is None:
                err(rel, "no YAML frontmatter")
                continue
            try:
                fm = parse_yaml(raw)
            except Exception as e:  # noqa: BLE001
                err(rel, f"frontmatter does not parse: {e}")
                continue
            name = fm.get("name")
            personas[str(name)] = {"fm": fm, "body": body, "stage": stage, "rel": rel,
                                    "raw": raw, "text": text}

            # name / filename
            if name != p.stem:
                err(rel, f"name {name!r} != filename {p.stem!r}")
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(name)):
                err(rel, f"name {name!r} is not lowercase-hyphen")
            if stage != "shared" and not str(name).startswith(
                    {"architecture": "arch-"}.get(stage, stage + "-")):
                err(rel, "name does not carry the stage prefix")
            if stage == "shared" and not str(name).startswith("shared-"):
                err(rel, "shared persona name must start with shared-")

            for f in REQUIRED_FIELDS:
                if f not in fm or fm[f] in (None, "", []):
                    err(rel, f"missing required field {f}")
            unknown = set(fm) - KNOWN_FIELDS
            if unknown:
                err(rel, f"unknown frontmatter fields {sorted(unknown)}")
            if "memory" in fm:
                err(rel, "memory field is forbidden (conventions §1 rule 5)")
            order = [k for k in re.findall(r"^([A-Za-z_]\w*):", raw, re.M) if k in KNOWN_FIELDS]
            expected = [k for k in FIELD_ORDER if k in order]
            if order != expected:
                warn(rel, f"frontmatter field order {order} != {expected}")

            model = fm.get("model")
            if model not in ALLOWED_MODELS:
                err(rel, f"model {model!r} not in {sorted(ALLOWED_MODELS)}")
            if re.search(r"\bhaiku\b", text, re.I):
                err(rel, "mentions 'haiku'")
            skills = fm.get("skills") or []
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",")]
            if SKILL_NAME not in skills:
                err(rel, f"skills does not include {SKILL_NAME}")
            mt = fm.get("maxTurns")
            if mt is not None and not isinstance(mt, int):
                err(rel, f"maxTurns {mt!r} is not an integer")
            if fm.get("effort") not in (None, "low", "medium", "high", "xhigh", "max"):
                err(rel, f"effort {fm.get('effort')!r} invalid")

            role = role_of(str(name), stage)
            personas[str(name)]["role"] = role
            desc = str(fm.get("description") or "")
            if role in ("worker", "critic") and f"Invoked by {ORCH.get(stage, '')}" not in desc:
                err(rel, f"description lacks 'Invoked by {ORCH.get(stage)}'")
            if role == "reviewer" and "Invoked by any stage orchestrator" not in desc:
                err(rel, "description lacks 'Invoked by any stage orchestrator'")
            if role == "orchestrator" and f"claude --agent {name}" not in desc:
                warn(rel, "orchestrator description does not name its session command")

            # tools policy
            plain, agents = parse_tools(fm.get("tools"))
            personas[str(name)]["agents"] = agents
            personas[str(name)]["plain"] = plain
            allowed = {"orchestrator": ORCH_TOOLS | {"Agent"}, "critic": CRITIC_TOOLS,
                       "reviewer": REVIEWER_TOOLS, "worker": WORKER_TOOLS}[role]
            allowed = allowed | TOOL_EXCEPTIONS.get(str(name), set())
            extra = [t for t in plain if t not in allowed]
            if extra:
                warn(rel, f"tools beyond least-privilege policy for {role}: {extra}")
            web = [t for t in plain if t in ("WebSearch", "WebFetch")]
            if web and str(name) not in WEB_SANCTIONED:
                err(rel, f"web tools {web} on a persona whose job is not desk research")
            if role != "orchestrator" and ("Agent" in plain or agents):
                err(rel, "non-orchestrator has Agent tool (subagents cannot spawn subagents)")
            if role == "orchestrator" and not agents:
                err(rel, "orchestrator has no Agent(...) list")
            if role in ("critic", "reviewer") and "Edit" in plain:
                err(rel, "critic/reviewer must not have Edit (never rewrite)")
            for base in ("Read", "Write"):
                if base not in plain:
                    err(rel, f"tools lack {base}")

            # body structure
            heads = sections(body)
            h1 = [h for h in heads if h[0] == 1]
            if len(h1) != 1:
                err(rel, f"expected exactly one H1 title, found {len(h1)}")
            elif heads[0][0] != 1:
                err(rel, "body must start with the H1 title")
            h2 = [t for lvl, t, _ in heads if lvl == 2]
            missing = [s for s in BASE_SECTIONS if s not in h2]
            if missing:
                err(rel, f"missing sections {missing}")
            else:
                pos = [h2.index(s) for s in BASE_SECTIONS]
                if pos != sorted(pos):
                    err(rel, "base sections out of order")
            if role == "orchestrator":
                m2 = [s for s in ORCH_SECTIONS if s not in h2]
                if m2:
                    err(rel, f"missing orchestrator sections {m2}")
            if len(set(h2)) != len(h2):
                err(rel, "duplicate H2 headings")
            scope = section_text(body, "Scope")
            for sub in SCOPE_SUBSECTIONS:
                if not re.search(rf"^### {re.escape(sub)}\s*$", scope, re.M):
                    err(rel, f"Scope lacks ### {sub}")

            ref = section_text(body, "Refusal criteria")
            bullets = [l for l in ref.splitlines() if re.match(r"^\s*[-*]\s", l)]
            if not bullets:
                err(rel, "Refusal criteria has no bullets")
            for b in bullets:
                if not re.match(r"^\s*[-*]\s+\*\*(blocked|rejected|out_of_scope)\*\*", b):
                    err(rel, f"refusal bullet does not start with a status tag: {b.strip()[:70]}")
            for tag in REFUSAL_TAGS:
                if not any(re.match(rf"^\s*[-*]\s+\*\*{tag}\*\*", b) for b in bullets):
                    warn(rel, f"Refusal criteria has no **{tag}** bullet")

            acc = section_text(body, "Acceptance criteria")
            if not re.search(r"^\s*- \[ \] ", acc, re.M):
                err(rel, "Acceptance criteria has no '- [ ]' checklist items")
            proc = section_text(body, "Process")
            if not re.search(r"^\s*\d+\.\s", proc, re.M):
                err(rel, "Process has no numbered steps")
            if not re.search(r"self-check|self_check", body, re.I):
                warn(rel, "body never mentions a self-check")
            if SKILL_NAME not in body:
                err(rel, f"body does not cite {SKILL_NAME}")
            for sec in re.findall(rf"{SKILL_NAME} §(\d+(?:\.\d+)?)", body):
                if skill_sections and sec not in skill_sections:
                    err(rel, f"cites {SKILL_NAME} §{sec}, which does not exist")
            if not re.search(r"^You are\b", body, re.M):
                warn(rel, "body has no second-person 'You are ...' line")

            words = len(re.findall(r"\S+", body))
            lo, hi = WORD_RANGES["orchestrator" if role == "orchestrator" else "worker"]
            if not lo <= words <= hi:
                warn(rel, f"body length {words} words outside {lo}-{hi}")

    # ---------------------------------------------------------- cross-file
    names = [p for p in personas]
    if len(names) != len(set(names)):
        err("set", "duplicate persona names")
    for stage, orch in ORCH.items():
        if orch not in personas:
            err("set", f"missing orchestrator {orch}")
            continue
        agents = personas[orch]["agents"]
        if len(agents) != len(set(agents)):
            err(personas[orch]["rel"], "duplicate entries in Agent(...)")
        for a in agents:
            if a not in personas:
                err(personas[orch]["rel"], f"Agent({a}) names no existing persona")
            elif personas[a]["stage"] not in (stage, "shared"):
                err(personas[orch]["rel"], f"Agent({a}) belongs to another stage")
            elif personas[a]["role"] == "orchestrator":
                err(personas[orch]["rel"], f"Agent({a}) is an orchestrator")
        for n, p in personas.items():
            if p["stage"] == stage and n != orch and n not in agents:
                err(personas[orch]["rel"], f"stage worker {n} is not in Agent(...)")
            if n in agents and n not in personas[orch]["body"]:
                warn(personas[orch]["rel"], f"{n} is in Agent(...) but never named in the body")
    for n, p in personas.items():
        if p["stage"] == "shared":
            users = [o for o in ORCH.values() if o in personas and n in personas[o]["agents"]]
            if not users:
                err(p["rel"], "shared persona is listed by no orchestrator")

    for line in errors + warns:
        print(line)
    print(f"\n{len(personas)} personas checked: {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
