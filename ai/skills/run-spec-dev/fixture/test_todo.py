import os
import subprocess
import sys
import tempfile
from pathlib import Path

TODO = Path(__file__).resolve().parent / "todo.py"


def todo(store, *args):
    env = {**os.environ, "TODO_STORE": str(store)}
    return subprocess.run([sys.executable, "-I", "-S", str(TODO), *args], env=env, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as tmp:
    store = Path(tmp) / "todo.json"

    empty = todo(store, "list")
    assert (empty.returncode, empty.stdout, empty.stderr) == (0, "", ""), empty

    first = todo(store, "add", "buy milk")
    assert (first.returncode, first.stdout, first.stderr) == (0, "added 1\n", ""), first
    second = todo(store, "add", "walk dog")
    assert (second.returncode, second.stdout) == (0, "added 2\n"), second

    listed = todo(store, "list")
    assert (listed.returncode, listed.stdout) == (0, "1 [ ] buy milk\n2 [ ] walk dog\n"), listed

    finished = todo(store, "done", "1")
    assert (finished.returncode, finished.stdout) == (0, "done 1\n"), finished
    after = todo(store, "list")
    assert after.stdout == "1 [x] buy milk\n2 [ ] walk dog\n", after

    missing = todo(store, "done", "9")
    assert (missing.returncode, missing.stdout, missing.stderr) == (1, "", "no such item: 9\n"), missing

    no_command = todo(store)
    assert no_command.returncode == 2, no_command

with tempfile.TemporaryDirectory() as tmp:
    blank_store = Path(tmp) / "todo.json"
    blank_store.write_text("")
    blank = todo(blank_store, "add", "water plants")
    assert (blank.returncode, blank.stdout) == (0, "added 1\n"), blank

print("ok")
