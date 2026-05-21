from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.config import Settings
from app.dependencies import get_settings

router = APIRouter(prefix="/audio")


@router.get("/{file_path:path}")
async def serve_audio(
    file_path: str,
    settings: Settings = Depends(get_settings),
):
    full_path = settings.birdnet_recs_dir / file_path
    # Prevent directory traversal
    try:
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(settings.birdnet_recs_dir.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except (ValueError, OSError):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    suffix = full_path.suffix.lower()
    media_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".png": "image/png",
        ".jpg": "image/jpeg",
    }
    media_type = media_types.get(suffix, "application/octet-stream")
    return FileResponse(full_path, media_type=media_type)
