from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

import aiosqlite

from app.db import queries
from app.services import chart_service
from app.dependencies import get_db

router = APIRouter(prefix="/charts")
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def charts_page(request: Request):
    return templates.TemplateResponse(request, "pages/charts.html")


@router.get("/data/daily")
async def daily_chart_data(
    db: aiosqlite.Connection = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
):
    counts = await chart_service.get_daily_activity(db, days)
    return JSONResponse({
        "labels": [c.date for c in counts],
        "data": [c.count for c in counts],
    })


@router.get("/data/hourly")
async def hourly_chart_data(
    db: aiosqlite.Connection = Depends(get_db),
    date: str | None = None,
):
    counts = await chart_service.get_hourly_activity(db, date)
    # Fill all 24 hours
    hour_map = {c.hour: c.count for c in counts}
    return JSONResponse({
        "labels": [f"{h:02d}:00" for h in range(24)],
        "data": [hour_map.get(h, 0) for h in range(24)],
    })


@router.get("/data/weekly")
async def weekly_chart_data(
    db: aiosqlite.Connection = Depends(get_db),
    weeks: int = Query(default=8, ge=1, le=52),
):
    data = await chart_service.get_weekly_summary(db, weeks)
    return JSONResponse({
        "labels": [d["week"] for d in data],
        "species_counts": [d["species_count"] for d in data],
        "detection_counts": [d["detection_count"] for d in data],
    })


@router.get("/data/heatmap")
async def heatmap_data(
    db: aiosqlite.Connection = Depends(get_db),
    limit: int = Query(default=15, ge=1, le=30),
):
    data = await chart_service.get_heatmap_data(db, limit)
    return JSONResponse(data)


@router.get("/data/species/{com_name}/daily")
async def species_daily_data(
    com_name: str,
    db: aiosqlite.Connection = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
):
    counts = await chart_service.get_species_timeline(db, com_name, days)
    return JSONResponse({
        "labels": [c.date for c in counts],
        "data": [c.count for c in counts],
    })


@router.get("/data/species/{com_name}/hourly")
async def species_hourly_data(
    com_name: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    counts = await chart_service.get_species_hourly(db, com_name)
    hour_map = {c.hour: c.count for c in counts}
    return JSONResponse({
        "labels": [f"{h:02d}:00" for h in range(24)],
        "data": [hour_map.get(h, 0) for h in range(24)],
    })
