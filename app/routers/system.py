import asyncio
import os
import platform
import socket
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

import aiosqlite

from app.config import Settings
from app.dependencies import get_db, get_settings

router = APIRouter(prefix="/system")
templates = Jinja2Templates(directory="app/templates")


async def _run_cmd(cmd: str) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        return stdout.decode().strip()
    except Exception:
        return "N/A"


async def _check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def get_system_info(settings: Settings) -> dict:
    uptime = await _run_cmd("uptime -p")
    cpu_temp = await _run_cmd("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")
    if cpu_temp != "N/A" and cpu_temp.isdigit():
        cpu_temp = f"{int(cpu_temp) / 1000:.1f}C"

    db_path = settings.birdnet_db_path
    db_size = f"{db_path.stat().st_size / (1024*1024):.1f} MB" if db_path.exists() else "N/A"

    # Disk usage for data partition
    try:
        stat = os.statvfs(str(db_path.parent))
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        disk_info = f"{total_gb - free_gb:.1f} / {total_gb:.1f} GB"
    except Exception:
        disk_info = "N/A"

    # Memory
    mem_info = await _run_cmd("free -h | awk '/^Mem:/ {print $3 \"/\" $2}'")

    return {
        "hostname": socket.gethostname(),
        "platform": platform.machine(),
        "uptime": uptime,
        "cpu_temp": cpu_temp,
        "memory": mem_info,
        "disk": disk_info,
        "db_size": db_size,
    }


async def get_service_status() -> list[dict]:
    """Check BirdNET-Pi services by probing their expected ports."""
    services = [
        {"name": "BirdNET Analysis", "host": "10.0.0.19", "port": 80},
        {"name": "Icecast Stream", "host": "10.0.0.19", "port": 8000},
    ]
    results = []
    for svc in services:
        up = await _check_port(svc["host"], svc["port"])
        results.append({**svc, "status": "up" if up else "down"})
    return results


@router.get("/")
async def system_page(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    sys_info = await get_system_info(settings)
    svc_status = await get_service_status()

    # DB stats
    async with db.execute("SELECT COUNT(*) FROM detections") as cur:
        total_rows = (await cur.fetchone())[0]
    async with db.execute("SELECT MIN(Date), MAX(Date) FROM detections") as cur:
        row = await cur.fetchone()
        date_range = f"{row[0]} to {row[1]}" if row[0] else "No data"

    return templates.TemplateResponse(request, "pages/system.html", {
        "sys_info": sys_info,
        "services": svc_status,
        "db_stats": {"total_rows": total_rows, "date_range": date_range},
    })
