from __future__ import annotations
from pathlib import Path
from typing import Dict, List
from ..or_client import Conversation
from ..storage.paths import workspace_dir
from ..contracts.events import PromptSent, ResponseReceived


def ensure_workspace_index(rid: str) -> Path:
    root = workspace_dir(rid)
    idx = root / "index.html"
    if not idx.exists():
        idx.write_text("<!doctype html><title>Vibe</title><h1>Vibe</h1><div id='app'></div>", encoding="utf-8")
    return idx


async def agent_exchange(rid: str, iteration: int, route_to: str, parts: List[Dict]) -> List[dict]:
    """Emit prompt.sent/response.received (returns the 2 events as dicts)."""
    # Minimal: simulate local response to avoid external latency in v0
    # Build user content
    text = ""
    for p in parts:
        if p.get("type") == "text":
            text = p.get("text", "")
    # Emit prompt.sent
    sent = PromptSent(
        t="prompt.sent",
        actor="code" if route_to == "vision" else "vision",
        to=route_to,
        content=parts,
        iteration=iteration,
    ).model_dump()
    # Return a trivial echo without calling external APIs
    reply = text or "ok"
    recv = ResponseReceived(t="response.received", actor=route_to, text=reply, iteration=iteration).model_dump()
    return [sent, recv]


def deterministic_patch(rid: str, iteration: int) -> Path:
    """Trivial patch: append an iteration marker to workspace/index.html."""
    idx = ensure_workspace_index(rid)
    html = idx.read_text(encoding="utf-8")
    marker = f"\n<!-- iter:{iteration} -->\n"
    if marker not in html:
        idx.write_text(html + marker, encoding="utf-8")
    return idx


