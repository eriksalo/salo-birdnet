# salo-birdnet

Modern web frontend for [BirdNET-Pi](https://github.com/mcguirepr89/BirdNET-Pi). Replaces the dated PHP GUI with a fast, dark-mode dashboard built on FastAPI and HTMX.

This is **not a fork** of BirdNET-Pi. It's a standalone consumer of BirdNET-Pi's data — it reads `birds.db` and serves audio from `BirdSongs/` via Docker volume mounts. The ML analysis pipeline is completely untouched.

## Stack

- **Backend**: FastAPI + Jinja2 + aiosqlite (read-only access to BirdNET-Pi's SQLite DB)
- **Frontend**: HTMX + Alpine.js + Tailwind CSS + Chart.js
- **Live updates**: Server-Sent Events (SSE)
- **Deployment**: Docker Compose on the Pi

## Features

- **Dashboard** — stat cards (total detections, today's count, species, hourly rate), live detection feed via SSE, new/rare species highlights, hourly activity chart
- **Detection history** — filterable by species, date range, and confidence with infinite scroll (keyset pagination)
- **Species browser** — searchable card grid, species detail pages with detection timeline and hourly distribution charts
- **Charts** — daily activity, hourly breakdown, weekly trends, top species heatmap
- **Audio playback** — inline play/pause on detection cards, served from the existing BirdSongs directory
- **System info** — hostname, uptime, CPU temp, memory, disk, DB stats, service status
- **Config viewer** — read-only display of `birdnet.conf` settings

## Running

```bash
# Docker (on the Pi)
docker compose up --build
# Browse to http://<pi-ip>:8081

# Local dev (with a sample or real DB)
BIRDNET_DB_PATH=./tests/fixtures/test.db uvicorn app.main:app --reload
```

## Docker Compose

Volume paths in `docker-compose.yml` map to BirdNET-Pi's default locations on the Pi:

```yaml
volumes:
  - /home/pi/BirdNET-Pi/scripts/birds.db:/data/birds.db:ro
  - /home/pi/BirdSongs:/data/birdsongs:ro
  - /etc/birdnet:/data/config:ro
```

Adjust these if your BirdNET-Pi install uses different paths.

## Tests

```bash
pip install -r requirements.txt pytest pytest-asyncio httpx
pytest tests/
```

## Branch info

Development happens on `feat/initial-implementation`. This branch contains the full initial build — all phases from core infrastructure through dashboard, history, species, charts, audio, config, and system pages.
