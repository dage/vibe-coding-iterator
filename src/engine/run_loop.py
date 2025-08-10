from __future__ import annotations
import asyncio
from typing import Optional, Dict
from ..contracts.events import RunStarted, IterationStarted, ScreenshotCaptured
from ..storage.paths import run_id as mk_run_id, events_path, snap_path
from ..storage.events_log import append as log_append
from ..engine.bus import publish
from ..adapters.playwright.browser import capture_html
from .handlers import deterministic_patch, agent_exchange


class RunLoop:
    def __init__(self):
        self.paused = True
        self.iteration = 0
        self.run_id: Optional[str] = None

    async def start(self):
        self.run_id = mk_run_id()
        ev = RunStarted(t="run.started", run_id=self.run_id).model_dump()
        log_append(events_path(self.run_id), ev)
        await publish(ev)

    async def resume(self):
        self.paused = False

    async def pause(self):
        self.paused = True

    async def step_forever(self, delay_sec: float = 2.0):
        assert self.run_id, "call start() first"
        while True:
            if not self.paused:
                self.iteration += 1
                it = self.iteration
                rid = self.run_id
                # iteration.started
                i_ev = IterationStarted(t="iteration.started", run_id=rid, n=it).model_dump()
                log_append(events_path(rid), i_ev)
                await publish(i_ev)
                # prompt/response (minimal, route_to 'code' for v0)
                sent, recv = await agent_exchange(rid, it, route_to="code", parts=[{"type": "text", "text": "iterate"}])
                for ev in (sent, recv):
                    ev["run_id"] = rid
                    log_append(events_path(rid), ev)
                    await publish(ev)
                # patch → capture
                html = deterministic_patch(rid, it)
                out = snap_path(rid, it)
                # Run screenshot capture in a worker thread to avoid sync Playwright in event loop
                await asyncio.to_thread(capture_html, html, out)
                s_ev = ScreenshotCaptured(t="screenshot.captured", run_id=rid, url=f"/static/runs/{rid}/screenshots/{out.name}", iteration=it).model_dump()
                log_append(events_path(rid), s_ev)
                await publish(s_ev)
            await asyncio.sleep(delay_sec)


