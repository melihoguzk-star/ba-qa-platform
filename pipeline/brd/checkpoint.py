"""Checkpoint persistence — n8n staticData'nın SQLite karşılığı."""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/pipeline.db")


def _get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            stage TEXT NOT NULL,
            data_json TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(project_name, stage)
        )
    """)
    conn.commit()
    return conn


def save_checkpoint(project_name: str, stage: str, data: dict, ttl_hours: int = 24):
    conn = _get_conn()
    now = datetime.now()
    expires = now + timedelta(hours=ttl_hours)
    conn.execute(
        """INSERT OR REPLACE INTO checkpoints (project_name, stage, data_json, expires_at, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (project_name, stage, json.dumps(data, ensure_ascii=False), expires.isoformat(), now.isoformat()),
    )
    conn.commit()
    conn.close()


def load_checkpoint(project_name: str, stage: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT data_json, expires_at FROM checkpoints WHERE project_name = ? AND stage = ?",
        (project_name, stage),
    ).fetchone()
    conn.close()
    if not row:
        return None
    expires = datetime.fromisoformat(row[1])
    if datetime.now() > expires:
        clear_checkpoint(project_name, stage)
        return None
    return json.loads(row[0])


def clear_checkpoint(project_name: str, stage: str):
    conn = _get_conn()
    conn.execute("DELETE FROM checkpoints WHERE project_name = ? AND stage = ?", (project_name, stage))
    conn.commit()
    conn.close()


def clear_all_checkpoints(project_name: str):
    conn = _get_conn()
    conn.execute("DELETE FROM checkpoints WHERE project_name = ?", (project_name,))
    conn.commit()
    conn.close()
