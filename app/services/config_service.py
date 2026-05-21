import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_birdnet_conf(conf_path: Path) -> dict[str, dict[str, str]]:
    """Parse birdnet.conf into categorized settings."""
    if not conf_path.exists():
        return {}

    settings: dict[str, dict[str, str]] = {}
    current_category = "General"

    for line in conf_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            # Use comments as category hints
            if line.startswith("# ") and line.endswith(":"):
                current_category = line[2:-1]
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if current_category not in settings:
                settings[current_category] = {}
            settings[current_category][key] = value

    return settings
