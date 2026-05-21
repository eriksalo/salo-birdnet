import logging
from pathlib import Path

import httpx
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Cache bird image URLs for 24 hours
_image_cache: TTLCache = TTLCache(maxsize=500, ttl=86400)

WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary"


async def get_bird_image_url(sci_name: str) -> str | None:
    """Fetch a bird image URL from Wikipedia by scientific name."""
    if sci_name in _image_cache:
        return _image_cache[sci_name]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{WIKIPEDIA_API}/{sci_name.replace(' ', '_')}")
            if resp.status_code == 200:
                data = resp.json()
                thumbnail = data.get("thumbnail", {}).get("source")
                if thumbnail:
                    _image_cache[sci_name] = thumbnail
                    return thumbnail
    except Exception:
        logger.debug(f"Failed to fetch image for {sci_name}")

    _image_cache[sci_name] = None
    return None
