from __future__ import annotations
import asyncio, uvicorn
from ..adapters.http.api import app
from ..engine.run_loop import RunLoop
from ..engine.bus import subscribe, publish
from ..contracts.events import ControlResumed


async def main_async():
    loop = RunLoop()
    await loop.start()

    async def engine_task():
        # Start unpaused for harness to capture events quickly
        await loop.resume()
        # Emit initial control.resumed so UI reflects the running state
        await publish(ControlResumed(t="control.resumed").model_dump())
        await loop.step_forever()

    async def api_task():
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def control_listener():
        async for ev in subscribe():
            t = ev.get("t")
            if t == "control.pause" or t == "control.paused":
                await loop.pause()
            elif t == "control.resume" or t == "control.resumed":
                await loop.resume()

    await asyncio.gather(engine_task(), api_task(), control_listener())


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()


