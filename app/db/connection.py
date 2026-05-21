import aiosqlite

from app.config import Settings


async def open_db(settings: Settings) -> aiosqlite.Connection:
    db_path = str(settings.birdnet_db_path)
    db = await aiosqlite.connect(f"file:{db_path}?mode=ro", uri=True)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute(f"PRAGMA cache_size=-{settings.db_cache_size}")
    await db.execute(f"PRAGMA mmap_size={settings.db_mmap_size}")
    await db.execute("PRAGMA query_only=ON")
    return db
