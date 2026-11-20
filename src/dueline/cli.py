import argparse
import sys
from datetime import datetime

from . import __version__, parser, store


def _humanize(due, now=None):
    now = now or datetime.now()
    s = int((due - now).total_seconds())
    if s < 0:
        s = -s
        return f"OVERDUE by {s // 86400}d {s % 86400 // 3600}h"
    return f"in {s // 86400}d {s % 86400 // 3600}h {s % 3600 // 60}m"


def cmd_add(a):
    due = parser.parse_due(a.due)
    store.add(a.name, due.isoformat(), a.course, a.link)
    print(f"Added: {a.name}  due {due:%Y-%m-%d %H:%M}")


def cmd_list(a):
    items = store.list_all()
    if not items:
        print("No assignments yet.")
        return
    now = datetime.now()
    for it in items:
        mark = "⚠" if store.is_overdue(it) else " "
        state = "✓ done" if it["done"] else _humanize(datetime.fromisoformat(it["due"]), now)
        course = f" [{it['course']}]" if it.get("course") else ""
        print(f"{mark} - {it['name']}{course}  —  {state}")


def cmd_done(a):
    if store.mark_done(a.name):
        print(f"Marked as done: {a.name}")
    else:
        print(f"Not found: {a.name}")
        sys.exit(1)


def build_parser():
    p = argparse.ArgumentParser(prog="dueline")
    p.add_argument("--version", action="version", version=f"dueline {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    pa = sub.add_parser("add")
    pa.add_argument("name")
    pa.add_argument("--due", required=True)
    pa.add_argument("--course", default="")
    pa.add_argument("--link", default="")
    pa.set_defaults(func=cmd_add)

    pl = sub.add_parser("list")
    pl.set_defaults(func=cmd_list)

    pd = sub.add_parser("done")
    pd.add_argument("name")
    pd.set_defaults(func=cmd_done)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__&#8203;main__":
    main()
