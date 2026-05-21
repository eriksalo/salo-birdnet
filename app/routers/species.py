from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import aiosqlite

from app.db import queries
from app.dependencies import get_db

router = APIRouter(prefix="/species")
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def species_list(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
):
    species = await queries.get_species_list(db)
    return templates.TemplateResponse(request, "pages/species.html", {
        "species_list": species,
    })


@router.get("/search")
async def species_search(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
    q: str = "",
):
    if q:
        species = await queries.search_species(db, q)
    else:
        species = await queries.get_species_list(db)
    return templates.TemplateResponse(request, "partials/species_grid.html", {
        "species_list": species,
    })


@router.get("/{com_name}")
async def species_detail(
    request: Request,
    com_name: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    detail = await queries.get_species_detail(db, com_name)
    if not detail:
        return HTMLResponse("Species not found", status_code=404)

    detections = await queries.get_species_detections(db, com_name, limit=20)
    daily_counts = await queries.get_species_daily_counts(db, com_name)
    hourly_dist = await queries.get_species_hourly_distribution(db, com_name)

    return templates.TemplateResponse(request, "pages/species_detail.html", {
        "species": detail,
        "detections": detections,
        "daily_counts": [c.model_dump() for c in daily_counts],
        "hourly_distribution": [h.model_dump() for h in hourly_dist],
    })
