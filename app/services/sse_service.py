import asyncio
import json
import logging
from collections.abc import AsyncGenerator

import aiosqlite

from app.db import queries

logger = logging.getLogger(__name__)


async def detection_event_generator(
    db: aiosqlite.Connection, poll_interval: float = 5.0
) -> AsyncGenerator[dict, None]:
    """Yield new detections as SSE events by polling for new rowids."""
    last_id = await queries.get_latest_detection_id(db)

    while True:
        await asyncio.sleep(poll_interval)
        try:
            new_detections = await queries.get_recent_detections(db, limit=10, after_id=last_id)
            if new_detections:
                last_id = max(d.id for d in new_detections)
                for detection in reversed(new_detections):
                    yield {
                        "event": "detection",
                        "data": json.dumps(detection.model_dump(), default=str),
                    }
                # Also send updated stats
                stats = await queries.get_dashboard_stats(db)
                yield {
                    "event": "stats",
                    "data": json.dumps(stats.model_dump()),
                }
        except Exception:
            logger.exception("Error polling for new detections")
            await asyncio.sleep(poll_interval)
