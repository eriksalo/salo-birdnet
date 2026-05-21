from functools import lru_cache

import aiosqlite
from cachetools import TTLCache

from app.db import queries
from app.db.models import Detection, SpeciesSummary

# Cache for today's data (30s TTL) and historical (5min TTL)
_today_cache: TTLCache = TTLCache(maxsize=64, ttl=30)
_historical_cache: TTLCache = TTLCache(maxsize=256, ttl=300)


async def get_filtered_detections(
    db: aiosqlite.Connection,
    species: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    min_confidence: float = 0.0,
    last_id: int | None = None,
    limit: int = 50,
) -> list[Detection]:
    return await queries.get_detections_filtered(
        db, species=species, date_from=date_from, date_to=date_to,
        min_confidence=min_confidence, last_id=last_id, limit=limit,
    )


async def get_species_with_detections(
    db: aiosqlite.Connection, com_name: str, limit: int = 50, last_id: int | None = None
) -> tuple[SpeciesSummary | None, list[Detection]]:
    detail = await queries.get_species_detail(db, com_name)
    if not detail:
        return None, []
    detections = await queries.get_species_detections(db, com_name, limit=limit, last_id=last_id)
    return detail, detections
