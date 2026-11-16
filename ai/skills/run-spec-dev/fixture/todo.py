import argparse
import json
import os
import sys

STORE = os.environ.get("TODO_STORE", ".todo.json")


def load_items():
    try:
        with open(STORE) as store:
            text = store.read()
    except FileNotFoundError:
        return []
    return json.loads(text) if text.strip() else []


def save_items(items):
    with open(STORE, "w") as store:
        json.dump(items, store)


def add(text):
    items = load_items()
    item_id = max((item["id"] for item in items), default=0) + 1
    items.append({"id": item_id, "text": text, "done": False})
    save_items(items)
    print(f"added {item_id}")
    return 0


def list_items():
    for item in load_items():
        mark = "x" if item["done"] else " "
        print(f"{item['id']} [{mark}] {item['text']}")
    return 0


def finish(item_id):
    items = load_items()
    match = next((item for item in items if item["id"] == item_id), None)
    if match is None:
        print(f"no such item: {item_id}", file=sys.stderr)
        return 1
    match["done"] = True
    save_items(items)
    print(f"done {item_id}")
    return 0


def parse(argv):
    parser = argparse.ArgumentParser(prog="todo.py")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("add").add_argument("text")
    commands.add_parser("list")
    commands.add_parser("done").add_argument("id", type=int)
    return parser.parse_args(argv)


def main(argv):
    args = parse(argv)
    if args.command == "add":
        return add(args.text)
    if args.command == "list":
        return list_items()
    return finish(args.id)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
