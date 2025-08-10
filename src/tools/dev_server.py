from __future__ import annotations
import asyncio, uvicorn
from ..adapters.http.api import app
from ..engine.run_loop import RunLoop


async def main_async():
    loop = RunLoop()
    await loop.start()

    async def engine_task():
        # Start unpaused for harness to capture events quickly
        await loop.resume()
        await loop.step_forever()

    async def api_task():
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    await asyncio.gather(engine_task(), api_task())


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()


