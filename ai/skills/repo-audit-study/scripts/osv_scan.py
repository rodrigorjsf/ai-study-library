"""Query OSV.dev for every (package, version) pinned in the given lockfiles.

WHAT: Parses lockfiles and sends one batched query per 500 packages to https://api.osv.dev/v1/querybatch,
      printing each package version that has known advisories (GHSA / RUSTSEC / PYSEC ids).
WHY:  Works without osv-scanner, cargo-audit or npm installed, and never executes anything from the
      audited repository: it only reads lockfile text.
WHEN: Supply-chain step of an audit, once per pinned commit. Run it on every lockfile the repo commits.
HOW:  python3 -I osv_scan.py <lockfile>...
      Supported: Cargo.lock, package-lock.json, bun.lock (text), uv.lock, poetry.lock.
      Then fetch details for a hit: curl -s https://api.osv.dev/v1/vulns/<ID>
      A hit is not a finding yet: check whether the package is dev-only and whether the vulnerable
      function is reachable from the code before you rate it.
"""
import json
import re
import sys
import tomllib
import urllib.request


def parse(path):
    pkgs = set()
    if path.endswith("Cargo.lock"):
        for p in tomllib.load(open(path, "rb")).get("package", []):
            if "registry" in p.get("source", ""):
                pkgs.add(("crates.io", p["name"], p["version"]))
    elif path.endswith("package-lock.json"):
        for key, val in json.load(open(path)).get("packages", {}).items():
            if key.startswith("node_modules/") and "version" in val:
                pkgs.add(("npm", key.split("node_modules/")[-1], val["version"]))
    elif path.endswith("bun.lock"):
        for m in re.finditer(r'\[\s*"((?:@[^/"]+/)?[^@"]+)@(\d[^"]*)"', open(path).read()):
            pkgs.add(("npm", m.group(1), m.group(2)))
    elif path.endswith(("uv.lock", "poetry.lock")):
        for p in tomllib.load(open(path, "rb")).get("package", []):
            if "name" in p and "version" in p:
                pkgs.add(("PyPI", p["name"], p["version"]))
    else:
        sys.exit(f"unsupported lockfile: {path}")
    return pkgs


def query(pkgs):
    pkgs = sorted(pkgs)
    hits = {}
    for i in range(0, len(pkgs), 500):
        chunk = pkgs[i:i + 500]
        body = {"queries": [{"package": {"ecosystem": e, "name": n}, "version": v} for e, n, v in chunk]}
        req = urllib.request.Request("https://api.osv.dev/v1/querybatch", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
        res = json.load(urllib.request.urlopen(req, timeout=60))
        for (_, n, v), r in zip(chunk, res["results"]):
            ids = [x["id"] for x in r.get("vulns", [])]
            if ids:
                hits[f"{n}@{v}"] = ids
    return hits


for lockfile in sys.argv[1:]:
    packages = parse(lockfile)
    found = query(packages)
    print(f"## {lockfile}: {len(packages)} packages, {len(found)} with known advisories")
    for pkg, ids in sorted(found.items()):
        print(f"  {pkg}: {', '.join(ids)}")
