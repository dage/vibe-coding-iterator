from __future__ import annotations
import asyncio
from typing import AsyncIterator, Dict

_subs: "set[asyncio.Queue]" = set()


async def publish(ev: Dict):
    for q in list(_subs):
        await q.put(ev)


async def subscribe() -> AsyncIterator[Dict]:
    q: asyncio.Queue = asyncio.Queue()
    _subs.add(q)
    try:
        while True:
            yield await q.get()
    finally:
        _subs.discard(q)


