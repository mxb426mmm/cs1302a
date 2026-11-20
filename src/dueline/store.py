import json
import os
from pathlib import Path
from datetime import datetime


def _data_path():
    home = os.environ.get("DUELINE_HOME") or str(Path.home() / ".dueline")
    return Path(home) / "assignments.json"


def _load():
    p = _data_path()
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def _save(items):
    p = _data_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def add(name, due_iso, course="", link=""):
    items = _load()
    items.append({"name": name, "course": course, "due": due_iso,
                  "link": link, "done": False})
    _save(items)


def list_all():
    items = _load()
    items.sort(key=lambda x: x.get("due", ""))
    return items


def mark_done(name):
    items = _load()
    for it in items:
        if it["name"] == name and not it["done"]:
            it["done"] = True
            _save(items)
            return True
    return False


def is_overdue(item):
    if item.get("done"):
        return False
    return datetime.fromisoformat(item["due"]) < datetime.now()
