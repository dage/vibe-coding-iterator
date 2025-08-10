from __future__ import annotations
import asyncio, json
from pathlib import Path
from typing import AsyncIterator, Dict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from ...contracts.events import ControlPaused, ControlResumed, ErrorEv
from ...contracts.commands import ControlCommand, PromptCommand

app = FastAPI()

# Simple in-module subscriber set (will be replaced by engine.bus in branch 2)
_subs: "set[asyncio.Queue]" = set()


async def publish(ev: Dict):
    for q in list(_subs):
        await q.put(ev)


async def subscribe() -> AsyncIterator[Dict]:
    q: asyncio.Queue = asyncio.Queue()
    _subs.add(q)
    try:
        yield {"t": "hello", "ts": "bootstrap"}  # initial hello for UI
        while True:
            ev = await q.get()
            yield ev
    finally:
        _subs.discard(q)


@app.get("/api/events")
async def events(request: Request):
    async def gen():
        async for ev in subscribe():
            if await request.is_disconnected():
                break
            yield {"event": "message", "data": json.dumps(ev)}

    return EventSourceResponse(gen())


@app.post("/api/control")
async def control(cmd: ControlCommand):
    if cmd.action == "pause":
        await publish(ControlPaused(t="control.paused").model_dump())
    else:
        await publish(ControlResumed(t="control.resumed").model_dump())
    return {"ok": True}


@app.post("/api/prompt")
async def prompt(cmd: PromptCommand):
    # No routing in branch 1; validated only
    return {"ok": True}

# Serve /static from storage; / from web/
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="storage", html=False), name="static")
app.mount("/", StaticFiles(directory="web", html=True), name="web")


