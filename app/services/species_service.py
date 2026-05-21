import aiosqlite

from app.db import queries
from app.db.models import SpeciesSummary


async def list_species(db: aiosqlite.Connection) -> list[SpeciesSummary]:
    return await queries.get_species_list(db)


async def search_species(db: aiosqlite.Connection, query: str) -> list[SpeciesSummary]:
    return await queries.search_species(db, query)


async def get_species(db: aiosqlite.Connection, com_name: str) -> SpeciesSummary | None:
    return await queries.get_species_detail(db, com_name)
