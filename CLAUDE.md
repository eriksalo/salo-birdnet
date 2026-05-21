# salo-birdnet

Modern web frontend for BirdNET-Pi. Reads the existing SQLite DB and audio files — does NOT modify the ML pipeline.

## Stack
- FastAPI + Jinja2 + aiosqlite (read-only)
- HTMX + Alpine.js + Tailwind CSS (CDN for dev)
- Chart.js for visualizations
- SSE for live detection feed

## Running locally
```bash
# With a sample DB
BIRDNET_DB_PATH=./tests/fixtures/test.db uvicorn app.main:app --reload

# Docker
docker compose up --build
```

## Project layout
- `app/main.py` — FastAPI app with lifespan (DB open/close)
- `app/config.py` — Pydantic Settings from env
- `app/db/` — aiosqlite connection, models, queries
- `app/routers/` — page routes (dashboard, detections, species, charts, system, config, audio, api)
- `app/services/` — business logic layer
- `app/templates/` — Jinja2 (base.html, pages/, partials/, components/)
- `app/static/` — CSS/JS assets

## Key patterns
- All DB access is read-only (`PRAGMA query_only=ON`)
- Keyset pagination (last_id) instead of OFFSET
- HTMX for partial page updates, Alpine.js for client state
- SSE endpoint at `/api/sse/detections` polls DB every 5s
- Audio served from mounted BirdSongs dir via `/audio/{path}`

## Testing
```bash
pytest tests/
```
