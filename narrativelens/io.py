from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from dateutil import parser as dateparser


@dataclass
class Item:
    id: str
    created_at: datetime
    source: str | None
    title: str
    text: str | None
    url: str | None

    @property
    def doc(self) -> str:
        parts = [self.title.strip()]
        if self.text:
            parts.append(self.text.strip())
        return "\n".join([p for p in parts if p])


def _parse_dt(v: Any) -> datetime:
    if isinstance(v, datetime):
        dt = v
    else:
        dt = dateparser.parse(str(v))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_jsonl(path: str | Path, time_field: str = "created_at") -> list[Item]:
    path = Path(path)
    items: list[Item] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            items.append(
                Item(
                    id=str(obj.get("id", line_no)),
                    created_at=_parse_dt(obj[time_field]),
                    source=obj.get("source"),
                    title=str(obj.get("title", "")).strip(),
                    text=obj.get("text"),
                    url=obj.get("url"),
                )
            )
    return items


def write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def read_json(path: str | Path) -> Any:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
