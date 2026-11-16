import subprocess
import sys


def run(*cmd, check=True):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result.stdout if result.returncode == 0 else ""


def default_refs():
    head = run("git", "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD", check=False).strip()
    for name in ([head.removeprefix("origin/")] if head else []) + ["main", "master"]:
        refs = [ref for ref in (f"refs/heads/{name}", f"refs/remotes/origin/{name}")
                if run("git", "rev-parse", "-q", "--verify", f"{ref}^{{commit}}", check=False).strip()]
        if refs:
            return refs
    return []
