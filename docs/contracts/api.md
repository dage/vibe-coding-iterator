# API (v0)

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
