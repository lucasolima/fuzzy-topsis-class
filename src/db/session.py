import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
from src.db.config import build_database_url


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


engine = create_engine(
    build_database_url(),
    pool_pre_ping=True,
    pool_size=_int_env("DB_POOL_SIZE", 5),
    max_overflow=_int_env("DB_MAX_OVERFLOW", 10),
    pool_recycle=_int_env("DB_POOL_RECYCLE", 1800),
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
