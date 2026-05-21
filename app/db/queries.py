from datetime import date, datetime

import aiosqlite

from app.db.models import (
    DailyCount,
    DashboardStats,
    Detection,
    HourlyCount,
    SpeciesSummary,
)


async def get_dashboard_stats(db: aiosqlite.Connection) -> DashboardStats:
    today = date.today().isoformat()

    async with db.execute("SELECT COUNT(*) FROM detections") as cur:
        total_detections = (await cur.fetchone())[0]

    async with db.execute(
        "SELECT COUNT(*) FROM detections WHERE Date = ?", (today,)
    ) as cur:
        today_detections = (await cur.fetchone())[0]

    async with db.execute(
        "SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date = ?", (today,)
    ) as cur:
        species_today = (await cur.fetchone())[0]

    async with db.execute(
        "SELECT COUNT(DISTINCT Com_Name) FROM detections"
    ) as cur:
        total_species = (await cur.fetchone())[0]

    now = datetime.now()
    hours_elapsed = now.hour + now.minute / 60.0
    hourly_rate = today_detections / max(hours_elapsed, 0.1)

    return DashboardStats(
        total_detections=total_detections,
        today_detections=today_detections,
        species_today=species_today,
        total_species=total_species,
        hourly_rate=round(hourly_rate, 1),
    )


async def get_recent_detections(
    db: aiosqlite.Connection, limit: int = 20, after_id: int | None = None
) -> list[Detection]:
    if after_id:
        query = """
            SELECT rowid as id, Date, Time, Sci_Name, Com_Name, Confidence,
                   Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name
            FROM detections
            WHERE rowid > ?
            ORDER BY Date DESC, Time DESC
            LIMIT ?
        """
        params = (after_id, limit)
    else:
        query = """
            SELECT rowid as id, Date, Time, Sci_Name, Com_Name, Confidence,
                   Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name
            FROM detections
            ORDER BY Date DESC, Time DESC
            LIMIT ?
        """
        params = (limit,)

    async with db.execute(query, params) as cur:
        rows = await cur.fetchall()
        return [
            Detection(
                id=row[0], date=row[1], time=row[2], sci_name=row[3],
                com_name=row[4], confidence=row[5], lat=row[6], lon=row[7],
                cutoff=row[8], week=row[9], sens=row[10], overlap=row[11],
                file_name=row[12],
            )
            for row in rows
        ]


async def get_latest_detection_id(db: aiosqlite.Connection) -> int:
    async with db.execute(
        "SELECT MAX(rowid) FROM detections"
    ) as cur:
        result = await cur.fetchone()
        return result[0] or 0


async def get_detections_filtered(
    db: aiosqlite.Connection,
    species: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    min_confidence: float = 0.0,
    last_id: int | None = None,
    limit: int = 50,
) -> list[Detection]:
    conditions = []
    params: list = []

    if species:
        conditions.append("Com_Name = ?")
        params.append(species)
    if date_from:
        conditions.append("Date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("Date <= ?")
        params.append(date_to)
    if min_confidence > 0:
        conditions.append("Confidence >= ?")
        params.append(min_confidence)
    if last_id:
        conditions.append("rowid < ?")
        params.append(last_id)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT rowid as id, Date, Time, Sci_Name, Com_Name, Confidence,
               Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name
        FROM detections
        {where}
        ORDER BY rowid DESC
        LIMIT ?
    """
    params.append(limit)

    async with db.execute(query, params) as cur:
        rows = await cur.fetchall()
        return [
            Detection(
                id=row[0], date=row[1], time=row[2], sci_name=row[3],
                com_name=row[4], confidence=row[5], lat=row[6], lon=row[7],
                cutoff=row[8], week=row[9], sens=row[10], overlap=row[11],
                file_name=row[12],
            )
            for row in rows
        ]


async def get_species_list(db: aiosqlite.Connection) -> list[SpeciesSummary]:
    query = """
        SELECT Com_Name, Sci_Name,
               COUNT(*) as detection_count,
               ROUND(AVG(Confidence), 2) as avg_confidence,
               MAX(Date || ' ' || Time) as last_detected,
               MIN(Date || ' ' || Time) as first_detected
        FROM detections
        GROUP BY Com_Name, Sci_Name
        ORDER BY detection_count DESC
    """
    async with db.execute(query) as cur:
        rows = await cur.fetchall()
        return [
            SpeciesSummary(
                com_name=row[0], sci_name=row[1], detection_count=row[2],
                avg_confidence=row[3], last_detected=row[4], first_detected=row[5],
            )
            for row in rows
        ]


async def get_species_detail(
    db: aiosqlite.Connection, com_name: str
) -> SpeciesSummary | None:
    query = """
        SELECT Com_Name, Sci_Name,
               COUNT(*) as detection_count,
               ROUND(AVG(Confidence), 2) as avg_confidence,
               MAX(Date || ' ' || Time) as last_detected,
               MIN(Date || ' ' || Time) as first_detected
        FROM detections
        WHERE Com_Name = ?
        GROUP BY Com_Name, Sci_Name
    """
    async with db.execute(query, (com_name,)) as cur:
        row = await cur.fetchone()
        if not row:
            return None
        return SpeciesSummary(
            com_name=row[0], sci_name=row[1], detection_count=row[2],
            avg_confidence=row[3], last_detected=row[4], first_detected=row[5],
        )


async def get_species_detections(
    db: aiosqlite.Connection, com_name: str, limit: int = 50, last_id: int | None = None
) -> list[Detection]:
    return await get_detections_filtered(db, species=com_name, last_id=last_id, limit=limit)


async def get_daily_counts(
    db: aiosqlite.Connection, days: int = 30
) -> list[DailyCount]:
    query = """
        SELECT Date, COUNT(*) as count
        FROM detections
        WHERE Date >= date('now', ?)
        GROUP BY Date
        ORDER BY Date
    """
    async with db.execute(query, (f"-{days} days",)) as cur:
        rows = await cur.fetchall()
        return [DailyCount(date=row[0], count=row[1]) for row in rows]


async def get_hourly_counts(
    db: aiosqlite.Connection, target_date: str | None = None
) -> list[HourlyCount]:
    if target_date:
        query = """
            SELECT CAST(SUBSTR(Time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
            FROM detections
            WHERE Date = ?
            GROUP BY hour
            ORDER BY hour
        """
        params: tuple = (target_date,)
    else:
        query = """
            SELECT CAST(SUBSTR(Time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
            FROM detections
            WHERE Date = date('now')
            GROUP BY hour
            ORDER BY hour
        """
        params = ()

    async with db.execute(query, params) as cur:
        rows = await cur.fetchall()
        return [HourlyCount(hour=row[0], count=row[1]) for row in rows]


async def get_species_daily_counts(
    db: aiosqlite.Connection, com_name: str, days: int = 30
) -> list[DailyCount]:
    query = """
        SELECT Date, COUNT(*) as count
        FROM detections
        WHERE Com_Name = ? AND Date >= date('now', ?)
        GROUP BY Date
        ORDER BY Date
    """
    async with db.execute(query, (com_name, f"-{days} days")) as cur:
        rows = await cur.fetchall()
        return [DailyCount(date=row[0], count=row[1]) for row in rows]


async def get_species_hourly_distribution(
    db: aiosqlite.Connection, com_name: str
) -> list[HourlyCount]:
    query = """
        SELECT CAST(SUBSTR(Time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
        FROM detections
        WHERE Com_Name = ?
        GROUP BY hour
        ORDER BY hour
    """
    async with db.execute(query, (com_name,)) as cur:
        rows = await cur.fetchall()
        return [HourlyCount(hour=row[0], count=row[1]) for row in rows]


async def search_species(
    db: aiosqlite.Connection, query_str: str
) -> list[SpeciesSummary]:
    query = """
        SELECT Com_Name, Sci_Name,
               COUNT(*) as detection_count,
               ROUND(AVG(Confidence), 2) as avg_confidence,
               MAX(Date || ' ' || Time) as last_detected,
               MIN(Date || ' ' || Time) as first_detected
        FROM detections
        WHERE Com_Name LIKE ? OR Sci_Name LIKE ?
        GROUP BY Com_Name, Sci_Name
        ORDER BY detection_count DESC
    """
    pattern = f"%{query_str}%"
    async with db.execute(query, (pattern, pattern)) as cur:
        rows = await cur.fetchall()
        return [
            SpeciesSummary(
                com_name=row[0], sci_name=row[1], detection_count=row[2],
                avg_confidence=row[3], last_detected=row[4], first_detected=row[5],
            )
            for row in rows
        ]


async def get_new_species_today(db: aiosqlite.Connection) -> list[str]:
    """Species detected today that have never been seen before today."""
    query = """
        SELECT DISTINCT d1.Com_Name
        FROM detections d1
        WHERE d1.Date = date('now')
        AND NOT EXISTS (
            SELECT 1 FROM detections d2
            WHERE d2.Com_Name = d1.Com_Name AND d2.Date < date('now')
        )
    """
    async with db.execute(query) as cur:
        rows = await cur.fetchall()
        return [row[0] for row in rows]


async def get_rare_species_today(db: aiosqlite.Connection, threshold: int = 3) -> list[dict]:
    """Species seen today that have been detected fewer than `threshold` total days."""
    query = """
        SELECT d.Com_Name, COUNT(DISTINCT d.Date) as days_seen
        FROM detections d
        WHERE d.Com_Name IN (
            SELECT DISTINCT Com_Name FROM detections WHERE Date = date('now')
        )
        GROUP BY d.Com_Name
        HAVING days_seen <= ?
        ORDER BY days_seen
    """
    async with db.execute(query, (threshold,)) as cur:
        rows = await cur.fetchall()
        return [{"com_name": row[0], "days_seen": row[1]} for row in rows]


async def get_weekly_species_counts(
    db: aiosqlite.Connection, weeks: int = 8
) -> list[dict]:
    query = """
        SELECT
            strftime('%Y-W%W', Date) as week_label,
            COUNT(DISTINCT Com_Name) as species_count,
            COUNT(*) as detection_count
        FROM detections
        WHERE Date >= date('now', ?)
        GROUP BY week_label
        ORDER BY week_label
    """
    async with db.execute(query, (f"-{weeks * 7} days",)) as cur:
        rows = await cur.fetchall()
        return [
            {"week": row[0], "species_count": row[1], "detection_count": row[2]}
            for row in rows
        ]


async def get_top_species_heatmap(
    db: aiosqlite.Connection, limit: int = 15
) -> list[dict]:
    """Top N species with hourly detection counts for heatmap."""
    query = """
        SELECT Com_Name,
               CAST(SUBSTR(Time, 1, 2) AS INTEGER) as hour,
               COUNT(*) as count
        FROM detections
        WHERE Com_Name IN (
            SELECT Com_Name FROM detections
            GROUP BY Com_Name ORDER BY COUNT(*) DESC LIMIT ?
        )
        GROUP BY Com_Name, hour
        ORDER BY Com_Name, hour
    """
    async with db.execute(query, (limit,)) as cur:
        rows = await cur.fetchall()
        return [
            {"com_name": row[0], "hour": row[1], "count": row[2]}
            for row in rows
        ]


async def get_all_species_names(db: aiosqlite.Connection) -> list[str]:
    query = "SELECT DISTINCT Com_Name FROM detections ORDER BY Com_Name"
    async with db.execute(query) as cur:
        rows = await cur.fetchall()
        return [row[0] for row in rows]
