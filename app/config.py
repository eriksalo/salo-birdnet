from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    birdnet_db_path: Path = Path("/data/birds.db")
    birdnet_recs_dir: Path = Path("/data/birdsongs")
    birdnet_conf_path: Path = Path("/data/config/birdnet.conf")
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    db_cache_size: int = 8000  # in KB
    db_mmap_size: int = 67108864  # 64MB

    model_config = {"env_prefix": "", "env_file": ".env"}
