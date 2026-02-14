"""
BA&QA Intelligence Platform — Database (SQLite)
Analiz sonuçlarını, skorları ve geçmiş verileri saklar.
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "baqa.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jira_key TEXT,
            project TEXT DEFAULT '',
            analysis_type TEXT CHECK(analysis_type IN ('ba', 'tc', 'design', 'full')),
            status TEXT DEFAULT 'done',
            genel_puan REAL DEFAULT 0,
            gecti_mi INTEGER DEFAULT 0,
            result_json TEXT DEFAULT '{}',
            report_text TEXT DEFAULT '',
            triggered_by TEXT DEFAULT 'manual',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS jira_sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            action TEXT,
            jira_key TEXT,
            success INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        );

        CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(analysis_type);
        CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at);
        CREATE INDEX IF NOT EXISTS idx_analyses_jira ON analyses(jira_key);

        -- BRD Pipeline Tables
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            jira_key TEXT,
            priority TEXT,
            brd_filename TEXT,
            status TEXT DEFAULT 'running',
            current_stage TEXT DEFAULT 'ba',
            ba_score REAL DEFAULT 0,
            ta_score REAL DEFAULT 0,
            tc_score REAL DEFAULT 0,
            ba_revisions INTEGER DEFAULT 0,
            ta_revisions INTEGER DEFAULT 0,
            tc_revisions INTEGER DEFAULT 0,
            total_time_sec INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS stage_outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_run_id INTEGER NOT NULL,
            stage TEXT NOT NULL,
            content_json TEXT,
            qa_result_json TEXT,
            revision_number INTEGER DEFAULT 0,
            forced_pass INTEGER DEFAULT 0,
            generation_time_sec INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(id)
        );

        CREATE INDEX IF NOT EXISTS idx_pipeline_runs_created ON pipeline_runs(created_at);
        CREATE INDEX IF NOT EXISTS idx_stage_outputs_run ON stage_outputs(pipeline_run_id);
    """)
    conn.commit()
    conn.close()


def save_analysis(jira_key: str, analysis_type: str, genel_puan: float,
                  gecti_mi: bool, result_data: dict, report_text: str = "",
                  project: str = "", triggered_by: str = "manual") -> int:
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO analyses (jira_key, project, analysis_type, genel_puan, gecti_mi,
                              result_json, report_text, triggered_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (jira_key, project, analysis_type, genel_puan, int(gecti_mi),
          json.dumps(result_data, ensure_ascii=False), report_text, triggered_by))
    analysis_id = cur.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def get_recent_analyses(limit: int = 20, analysis_type: str = None) -> list:
    conn = get_db()
    if analysis_type:
        rows = conn.execute(
            "SELECT * FROM analyses WHERE analysis_type=? ORDER BY created_at DESC LIMIT ?",
            (analysis_type, limit)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?",
            (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM analyses").fetchone()["c"]
    by_type = conn.execute(
        "SELECT analysis_type, COUNT(*) as c, AVG(genel_puan) as avg_puan, "
        "SUM(CASE WHEN gecti_mi=1 THEN 1 ELSE 0 END) as gecen "
        "FROM analyses GROUP BY analysis_type"
    ).fetchall()
    recent_7 = conn.execute(
        "SELECT date(created_at) as gun, analysis_type, COUNT(*) as c, AVG(genel_puan) as avg_puan "
        "FROM analyses WHERE created_at >= date('now', '-7 days') "
        "GROUP BY gun, analysis_type ORDER BY gun"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "by_type": [dict(r) for r in by_type],
        "recent_7_days": [dict(r) for r in recent_7],
    }


# ─────────────────────────────────────────────
# BRD Pipeline Functions
# ─────────────────────────────────────────────

def create_pipeline_run(project_name: str, jira_key: str, priority: str, brd_filename: str) -> int:
    """Create a new BRD pipeline run."""
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO pipeline_runs (project_name, jira_key, priority, brd_filename, created_at) VALUES (?, ?, ?, ?, ?)",
        (project_name, jira_key, priority, brd_filename, datetime.now().isoformat()),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def update_pipeline_run(run_id: int, **kwargs):
    """Update a BRD pipeline run."""
    conn = get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [run_id]
    conn.execute(f"UPDATE pipeline_runs SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def save_pipeline_stage_output(run_id: int, stage: str, content: dict, qa_result: dict,
                                revision: int = 0, forced_pass: bool = False, gen_time: int = 0):
    """Save BRD pipeline stage output."""
    conn = get_db()
    conn.execute(
        """INSERT INTO stage_outputs (pipeline_run_id, stage, content_json, qa_result_json,
           revision_number, forced_pass, generation_time_sec, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, stage, json.dumps(content, ensure_ascii=False),
         json.dumps(qa_result, ensure_ascii=False), revision, int(forced_pass), gen_time,
         datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_recent_pipeline_runs(limit: int = 20) -> list:
    """Get recent BRD pipeline runs."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pipeline_run_outputs(run_id: int) -> list:
    """Get all outputs for a specific pipeline run."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM stage_outputs WHERE pipeline_run_id = ? ORDER BY created_at", (run_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Initialize on import
init_db()
