import json

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

import aiosqlite

from app.db import queries
from app.dependencies import get_db
from app.services.sse_service import detection_event_generator

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")


@router.get("/sse/detections")
async def sse_detections(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
):
    async def event_stream():
        async for event in detection_event_generator(db):
            if await request.is_disconnected():
                break
            yield event

    return EventSourceResponse(event_stream())


@router.get("/stats")
async def get_stats(db: aiosqlite.Connection = Depends(get_db)):
    stats = await queries.get_dashboard_stats(db)
    return stats.model_dump()


@router.get("/partials/detection-card")
async def detection_card_partial(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Return the latest detection as an HTML partial for HTMX."""
    detections = await queries.get_recent_detections(db, limit=1)
    if not detections:
        return ""
    return templates.TemplateResponse(request, "components/detection_card.html", {
        "detection": detections[0],
    })
