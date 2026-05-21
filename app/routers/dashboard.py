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
    recent = await queries.get_recent_detections(db, limit=15)
    new_species = await queries.get_new_species_today(db)
    rare_species = await queries.get_rare_species_today(db)
    hourly = await queries.get_hourly_counts(db)

    return templates.TemplateResponse(request, "pages/dashboard.html", {
        "stats": stats,
        "recent_detections": recent,
        "new_species": new_species,
        "rare_species": rare_species,
        "hourly_counts": [h.model_dump() for h in hourly],
    })
