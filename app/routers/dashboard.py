from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

import aiosqlite

from app.db import queries
from app.dependencies import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def dashboard(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    stats = await queries.get_dashboard_stats(db)
    species, totals, hourly = await queries.get_todays_top_species_by_hour(db, limit=10)

    # Current hour for highlighting
    current_hour = datetime.now().hour

    return templates.TemplateResponse(request, "pages/dashboard.html", {
        "stats": stats,
        "species": species,
        "totals": totals,
        "hourly": hourly,
        "current_hour": current_hour,
        "hours": list(range(24)),
    })
