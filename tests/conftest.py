import asyncio
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest
import pytest_asyncio
import aiosqlite
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import app


FIXTURE_DB = Path(__file__).parent / "fixtures" / "test.db"


def create_test_db():
    """Create a test SQLite database with sample data."""
    if FIXTURE_DB.exists():
        FIXTURE_DB.unlink()

    conn = sqlite3.connect(str(FIXTURE_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            Date TEXT,
            Time TEXT,
            Sci_Name TEXT,
            Com_Name TEXT,
            Confidence REAL,
            Lat REAL,
            Lon REAL,
            Cutoff REAL,
            Week INT,
            Sens REAL,
            Overlap REAL,
            File_Name TEXT
        )
    """)

    today = date.today()
    yesterday = today - timedelta(days=1)
    sample_data = [
        (today.isoformat(), "08:30:00", "Turdus merula", "Eurasian Blackbird", 0.92, 60.0, 24.0, 0.7, 20, 1.0, 0.0, "By_Date/2025-05-21/blackbird_08-30.mp3"),
        (today.isoformat(), "09:15:00", "Parus major", "Great Tit", 0.85, 60.0, 24.0, 0.7, 20, 1.0, 0.0, "By_Date/2025-05-21/tit_09-15.mp3"),
        (today.isoformat(), "10:00:00", "Turdus merula", "Eurasian Blackbird", 0.78, 60.0, 24.0, 0.7, 20, 1.0, 0.0, "By_Date/2025-05-21/blackbird_10-00.mp3"),
        (today.isoformat(), "11:45:00", "Erithacus rubecula", "European Robin", 0.95, 60.0, 24.0, 0.7, 20, 1.0, 0.0, "By_Date/2025-05-21/robin_11-45.mp3"),
        (yesterday.isoformat(), "06:00:00", "Turdus merula", "Eurasian Blackbird", 0.88, 60.0, 24.0, 0.7, 20, 1.0, 0.0, "By_Date/2025-05-20/blackbird_06-00.mp3"),
        (yesterday.isoformat(), "07:30:00", "Fringilla coelebs", "Common Chaffinch", 0.72, 60.0, 24.0, 0.7, 20, 1.0, 0.0, "By_Date/2025-05-20/chaffinch_07-30.mp3"),
        ((today - timedelta(days=5)).isoformat(), "12:00:00", "Parus major", "Great Tit", 0.91, 60.0, 24.0, 0.7, 19, 1.0, 0.0, "By_Date/2025-05-16/tit_12-00.mp3"),
    ]

    conn.executemany(
        "INSERT INTO detections VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        sample_data,
    )
    conn.commit()
    conn.close()
    return FIXTURE_DB


@pytest.fixture(scope="session", autouse=True)
def test_db_path():
    path = create_test_db()
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture(autouse=True)
def override_settings(test_db_path, tmp_path):
    settings = Settings(
        birdnet_db_path=test_db_path,
        birdnet_recs_dir=tmp_path / "birdsongs",
        birdnet_conf_path=tmp_path / "birdnet.conf",
    )
    (tmp_path / "birdsongs").mkdir(exist_ok=True)
    app.state.settings = settings


@pytest_asyncio.fixture
async def db(test_db_path):
    conn = await aiosqlite.connect(str(test_db_path))
    conn.row_factory = aiosqlite.Row
    yield conn
    await conn.close()


@pytest_asyncio.fixture
async def client(test_db_path, override_settings):
    conn = await aiosqlite.connect(str(test_db_path))
    conn.row_factory = aiosqlite.Row
    app.state.db = conn
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await conn.close()
