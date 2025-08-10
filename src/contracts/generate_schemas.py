from __future__ import annotations
import json, os
from pathlib import Path
from pydantic import TypeAdapter
from .events import Event
from .commands import ControlCommand, PromptCommand

OUT = Path("docs/contracts")
OUT.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    events_schema = TypeAdapter(Event).json_schema()
    cmds_schema = {
        "oneOf": [
            TypeAdapter(ControlCommand).json_schema(),
            TypeAdapter(PromptCommand).json_schema(),
        ]
    }
    write_json(OUT / "events.schema.json", events_schema)
    write_json(OUT / "commands.schema.json", cmds_schema)

    api_md = """# API (v0)

## Endpoints
- `GET /api/events` — SSE stream of events (JSON per message)
- `POST /api/control` — `{ "action":"pause"|"resume" }` → `{"ok":true}`
- `POST /api/prompt` — `{ "actor":"user","route_to":"vision"|"code","content":[...]}`
- `GET /static/...` — artifacts (screenshots, workspace)
- `GET /` — serves `web/index.html`

## Events
Discriminator: `t` (see `events.schema.json`).

## Notes
- Timestamps are ISO-8601 with Z.
- Exactly 1 `screenshot.captured` per iteration.
"""
    (OUT / "api.md").write_text(api_md, encoding="utf-8")
    print("Wrote:", OUT)


if __name__ == "__main__":
    main()


