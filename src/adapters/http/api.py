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
from ...engine.bus import publish, subscribe

app = FastAPI()

async def _bootstrap_then_stream():
    # initial hello for UI, then stream engine bus
    yield {"t": "hello", "ts": "bootstrap"}
    async for ev in subscribe():
        yield ev


@app.get("/api/events")
async def events(request: Request):
    async def gen():
        async for ev in _bootstrap_then_stream():
            if await request.is_disconnected():
                break
            # compact separators to match harness greps (no spaces)
            yield {"event": "message", "data": json.dumps(ev, separators=(",", ":"))}

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


