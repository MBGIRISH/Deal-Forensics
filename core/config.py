"""
Application-wide configuration helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Typed view of environment configuration."""

    llm_provider: str
    openai_api_key: str | None
    google_api_key: str | None
    embedding_model: str
    vector_db_path: Path
    embedding_cache_path: Path
    mongodb_uri: str | None
    mongo_db: str
    mongo_collection: str
    report_output_dir: Path
    default_historical_data: Path


def _load_env() -> None:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    load_dotenv("env.example", override=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    _load_env()
    base_dir = Path(".")

    def _path(value: str, default: str) -> Path:
        return (base_dir / Path(value or default)).resolve()

    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "openai").lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"
        ),
        vector_db_path=_path(os.getenv("VECTOR_DB_PATH", ".cache/vector_index"), ".cache/vector_index"),
        embedding_cache_path=_path(
            os.getenv("EMBEDDING_CACHE_PATH", ".cache/embedding_cache.pkl"),
            ".cache/embedding_cache.pkl",
        ),
        mongodb_uri=os.getenv("MONGODB_URI"),
        mongo_db=os.getenv("MONGODB_DB", "deal_forensics"),
        mongo_collection=os.getenv("MONGODB_COLLECTION", "historical_deals"),
        report_output_dir=_path(os.getenv("REPORT_OUTPUT_DIR", "reports"), "reports"),
        default_historical_data=_path(
            os.getenv("DEFAULT_HISTORICAL_DATA", "data/historical_deals.json"),
            "data/historical_deals.json",
        ),
    )


def ensure_directories() -> None:
    """Create filesystem locations that the app relies on."""

    settings = get_settings()
    settings.vector_db_path.parent.mkdir(parents=True, exist_ok=True)
    settings.embedding_cache_path.parent.mkdir(parents=True, exist_ok=True)
    settings.report_output_dir.mkdir(parents=True, exist_ok=True)

