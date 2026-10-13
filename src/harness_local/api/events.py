"""SSE entrega solo filas confirmadas. Las transacciones no viven durante la espera."""
import asyncio
import json
import time

from harness_local.api.schemas import LegacyEventRead


async def event_frames(repository, after, disconnected, interval=0.5, duration=15.0):
    yield "retry: 1000\n\n"
    idle = 0
    deadline = time.monotonic() + duration
    # Finite connections also bound graceful shutdown while EventSource reconnects by id.
    while time.monotonic() < deadline and not await disconnected():
        try:
            batch = await asyncio.to_thread(repository.events, after, 100)
        except ValueError as error:
            yield f"event: reset\ndata: {json.dumps({'diagnostic': str(error)})}\n\n"
            return
        for item in batch["items"]:
            if await disconnected():
                return
            event = LegacyEventRead.model_validate(item)
            yield f"id: {event.id}\nevent: legacy_update\ndata: {event.model_dump_json()}\n\n"
            after = event.id
        if batch["has_more"]:
            continue
        idle = 0 if batch["items"] else idle + 1
        if idle >= 30:
            yield ": keepalive\n\n"
            idle = 0
        await asyncio.sleep(interval)
