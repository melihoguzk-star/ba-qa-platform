"""
FastAPI Dependencies — Dependency Injection
"""
from typing import Generator
from contextlib import contextmanager
from api.config import get_settings
import sqlite3


settings = get_settings()


@contextmanager
def get_db_context() -> Generator[sqlite3.Connection, None, None]:
    """
    Database connection context manager with automatic cleanup.
    Prevents connection leaks on exceptions.

    Usage:
        with get_db_context() as conn:
            cursor = conn.cursor()
            # ... database operations
    """
    conn = None
    try:
        # Extract path from SQLite URI
        db_path = settings.database_url.replace("sqlite:///", "").split("?")[0]
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for concurrent reads
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def get_ai_client():
    """
    Returns AI client instance (agents/ai_client.py).
    """
    from api.services.ai_service import get_ai_service
    return get_ai_service()
