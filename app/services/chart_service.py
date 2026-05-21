import aiosqlite

from app.db import queries
from app.db.models import DailyCount, HourlyCount


async def get_daily_activity(
    db: aiosqlite.Connection, days: int = 30
) -> list[DailyCount]:
    return await queries.get_daily_counts(db, days)


async def get_hourly_activity(
    db: aiosqlite.Connection, target_date: str | None = None
) -> list[HourlyCount]:
    return await queries.get_hourly_counts(db, target_date)


async def get_species_timeline(
    db: aiosqlite.Connection, com_name: str, days: int = 30
) -> list[DailyCount]:
    return await queries.get_species_daily_counts(db, com_name, days)


async def get_species_hourly(
    db: aiosqlite.Connection, com_name: str
) -> list[HourlyCount]:
    return await queries.get_species_hourly_distribution(db, com_name)


async def get_weekly_summary(db: aiosqlite.Connection, weeks: int = 8) -> list[dict]:
    return await queries.get_weekly_species_counts(db, weeks)


async def get_heatmap_data(db: aiosqlite.Connection, limit: int = 15) -> list[dict]:
    return await queries.get_top_species_heatmap(db, limit)
