from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates

import aiosqlite

from app.db import queries
from app.dependencies import get_db

router = APIRouter(prefix="/detections")
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def detection_history(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
    species: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0),
):
    all_species = await queries.get_all_species_names(db)
    detections = await queries.get_detections_filtered(
        db, species=species, date_from=date_from, date_to=date_to,
        min_confidence=min_confidence, limit=50,
    )
    return templates.TemplateResponse(request, "pages/detections.html", {
        "detections": detections,
        "all_species": all_species,
        "filters": {
            "species": species or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
            "min_confidence": min_confidence,
        },
    })


@router.get("/rows")
async def detection_rows(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
    species: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0),
    last_id: int | None = None,
):
    detections = await queries.get_detections_filtered(
        db, species=species, date_from=date_from, date_to=date_to,
        min_confidence=min_confidence, last_id=last_id, limit=50,
    )
    return templates.TemplateResponse(request, "partials/detection_rows.html", {
        "detections": detections,
        "filters": {
            "species": species or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
            "min_confidence": min_confidence,
        },
    })
