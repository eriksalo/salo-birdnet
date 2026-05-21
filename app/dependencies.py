from typing import AsyncGenerator

import aiosqlite
from fastapi import Request

from app.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_db(request: Request) -> AsyncGenerator[aiosqlite.Connection, None]:
    yield request.app.state.db
