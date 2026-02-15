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
            openapi_spec_json TEXT DEFAULT NULL,
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


def get_recent_analyses(limit: int = 20, analysis_type: str = None, time_range: str = "all") -> list:
    """Get recent analyses with optional time range filter.

    Args:
        limit: Maximum number of records to return
        analysis_type: Filter by analysis type (ba, tc, design, full)
        time_range: Time range filter - "7days", "30days", "90days", or "all"
    """
    conn = get_db()

    # Build time filter
    time_filter = ""
    if time_range == "7days":
        time_filter = "AND created_at >= date('now', '-7 days')"
    elif time_range == "30days":
        time_filter = "AND created_at >= date('now', '-30 days')"
    elif time_range == "90days":
        time_filter = "AND created_at >= date('now', '-90 days')"

    if analysis_type:
        query = f"SELECT * FROM analyses WHERE analysis_type=? {time_filter} ORDER BY created_at DESC LIMIT ?"
        rows = conn.execute(query, (analysis_type, limit)).fetchall()
    else:
        query = f"SELECT * FROM analyses WHERE 1=1 {time_filter} ORDER BY created_at DESC LIMIT ?"
        rows = conn.execute(query, (limit,)).fetchall()

    conn.close()
    return [dict(r) for r in rows]


def get_stats(time_range: str = "all") -> dict:
    """Get statistics with optional time range filter.

    Args:
        time_range: Time range filter - "7days", "30days", "90days", or "all"
    """
    conn = get_db()

    # Build time filter
    time_filter = ""
    if time_range == "7days":
        time_filter = "WHERE created_at >= date('now', '-7 days')"
    elif time_range == "30days":
        time_filter = "WHERE created_at >= date('now', '-30 days')"
    elif time_range == "90days":
        time_filter = "WHERE created_at >= date('now', '-90 days')"

    total = conn.execute(f"SELECT COUNT(*) as c FROM analyses {time_filter}").fetchone()["c"]

    by_type = conn.execute(
        f"SELECT analysis_type, COUNT(*) as c, AVG(genel_puan) as avg_puan, "
        f"SUM(CASE WHEN gecti_mi=1 THEN 1 ELSE 0 END) as gecen "
        f"FROM analyses {time_filter} {'WHERE' if not time_filter else 'AND'} 1=1 GROUP BY analysis_type"
    ).fetchall()

    recent_7 = conn.execute(
        f"SELECT date(created_at) as gun, analysis_type, COUNT(*) as c, AVG(genel_puan) as avg_puan "
        f"FROM analyses {time_filter} "
        f"GROUP BY gun, analysis_type ORDER BY gun"
    ).fetchall()

    conn.close()
    return {
        "total": total,
        "by_type": [dict(r) for r in by_type],
        "recent_7_days": [dict(r) for r in recent_7],
    }


def get_dashboard_alerts() -> list:
    """Get dashboard alerts based on analysis metrics.

    Returns list of alerts with level (error/warning) and message.
    """
    conn = get_db()
    alerts = []

    # Get stats for last 30 days
    stats_30d = conn.execute(
        "SELECT analysis_type, COUNT(*) as c, AVG(genel_puan) as avg_puan, "
        "SUM(CASE WHEN gecti_mi=1 THEN 1 ELSE 0 END) as gecen "
        "FROM analyses WHERE created_at >= date('now', '-30 days') "
        "GROUP BY analysis_type"
    ).fetchall()

    for stat in stats_30d:
        analysis_type = stat["analysis_type"]
        count = stat["c"]
        avg_puan = stat["avg_puan"] or 0
        gecen = stat["gecen"]
        pass_rate = (gecen / count * 100) if count > 0 else 0

        type_label = {"ba": "BA", "tc": "TC", "design": "Design"}.get(analysis_type, analysis_type)

        # Alert: Low pass rate
        if pass_rate < 70 and count >= 5:
            alerts.append({
                "level": "error",
                "message": f"{type_label} geçme oranı düşük: %{pass_rate:.0f} (<70%)",
                "action": f"{type_label} değerlendirme kriterlerini gözden geçirin",
                "metric": "pass_rate",
                "value": pass_rate
            })

        # Alert: Low average score
        if avg_puan < 65 and count >= 5:
            alerts.append({
                "level": "warning",
                "message": f"{type_label} ortalama puan düşük: {avg_puan:.0f}/100",
                "action": f"{type_label} kalitesini artırmak için iyileştirme yapın",
                "metric": "avg_score",
                "value": avg_puan
            })

        # Alert: Low volume
        if count < 5 and count > 0:
            alerts.append({
                "level": "info",
                "message": f"{type_label} analiz sayısı düşük: Sadece {count} analiz (son 30 gün)",
                "action": f"Daha fazla {type_label} değerlendirmesi yapın",
                "metric": "volume",
                "value": count
            })

    conn.close()
    return alerts


def get_quality_trend_data(time_range: str = "30days") -> dict:
    """Get quality score trends over time.

    Args:
        time_range: Time range filter - "7days", "30days", "90days", or "all"

    Returns:
        Dictionary with dates and scores by analysis type
    """
    conn = get_db()

    # Build time filter
    time_filter = ""
    if time_range == "7days":
        time_filter = "WHERE created_at >= date('now', '-7 days')"
    elif time_range == "30days":
        time_filter = "WHERE created_at >= date('now', '-30 days')"
    elif time_range == "90days":
        time_filter = "WHERE created_at >= date('now', '-90 days')"

    # Get daily averages by type
    query = f"""
        SELECT
            date(created_at) as date,
            analysis_type,
            AVG(genel_puan) as avg_score,
            COUNT(*) as count
        FROM analyses
        {time_filter}
        GROUP BY date(created_at), analysis_type
        ORDER BY date(created_at)
    """

    rows = conn.execute(query).fetchall()
    conn.close()

    # Organize by type
    result = {
        "dates": [],
        "ba_scores": [],
        "tc_scores": [],
        "design_scores": []
    }

    # Group by date
    from collections import defaultdict
    by_date = defaultdict(dict)

    for row in rows:
        date = row["date"]
        atype = row["analysis_type"]
        score = row["avg_score"]

        by_date[date][atype] = score

    # Build arrays
    all_dates = sorted(by_date.keys())
    result["dates"] = all_dates

    for date in all_dates:
        result["ba_scores"].append(by_date[date].get("ba", None))
        result["tc_scores"].append(by_date[date].get("tc", None))
        result["design_scores"].append(by_date[date].get("design", None))

    return result


def get_score_distribution(time_range: str = "30days") -> dict:
    """Get score distribution for histogram.

    Args:
        time_range: Time range filter - "7days", "30days", "90days", or "all"

    Returns:
        Dictionary with scores by analysis type
    """
    conn = get_db()

    # Build time filter
    time_filter = ""
    if time_range == "7days":
        time_filter = "WHERE created_at >= date('now', '-7 days')"
    elif time_range == "30days":
        time_filter = "WHERE created_at >= date('now', '-30 days')"
    elif time_range == "90days":
        time_filter = "WHERE created_at >= date('now', '-90 days')"

    query = f"""
        SELECT analysis_type, genel_puan
        FROM analyses
        {time_filter}
        ORDER BY created_at DESC
    """

    rows = conn.execute(query).fetchall()
    conn.close()

    result = {
        "ba_scores": [],
        "tc_scores": [],
        "design_scores": []
    }

    for row in rows:
        score = row["genel_puan"]
        atype = row["analysis_type"]

        if atype == "ba":
            result["ba_scores"].append(score)
        elif atype == "tc":
            result["tc_scores"].append(score)
        elif atype == "design":
            result["design_scores"].append(score)

    return result


def get_sparkline_data(analysis_type: str, days: int = 7) -> list:
    """Get recent scores for sparkline chart.

    Args:
        analysis_type: Type of analysis (ba, tc, design)
        days: Number of days to look back

    Returns:
        List of scores
    """
    conn = get_db()

    query = """
        SELECT genel_puan
        FROM analyses
        WHERE analysis_type = ?
        AND created_at >= date('now', '-' || ? || ' days')
        ORDER BY created_at ASC
        LIMIT 10
    """

    rows = conn.execute(query, (analysis_type, days)).fetchall()
    conn.close()

    return [row["genel_puan"] for row in rows]


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


def save_openapi_spec(run_id: int, stage: str, openapi_json: str):
    """Save OpenAPI spec for a specific pipeline stage.
    
    Args:
        run_id: Pipeline run ID
        stage: Stage name ('ta' typically)
        openapi_json: OpenAPI spec as JSON string
    """
    conn = get_db()
    # SQLite doesn't support ORDER BY in UPDATE, so we need to find the ID first
    row = conn.execute(
        """SELECT id FROM stage_outputs 
           WHERE pipeline_run_id = ? AND stage = ? 
           ORDER BY created_at DESC LIMIT 1""",
        (run_id, stage)
    ).fetchone()
    
    if row:
        conn.execute(
            "UPDATE stage_outputs SET openapi_spec_json = ? WHERE id = ?",
            (openapi_json, row[0])  # Use index instead of key
        )
        conn.commit()
    conn.close()


def get_openapi_spec(run_id: int, stage: str = 'ta') -> str:
    """Get OpenAPI spec for a specific pipeline stage.
    
    Args:
        run_id: Pipeline run ID
        stage: Stage name (default: 'ta')
    
    Returns:
        OpenAPI spec as JSON string, or None if not found
    """
    conn = get_db()
    row = conn.execute(
        """SELECT openapi_spec_json FROM stage_outputs 
           WHERE pipeline_run_id = ? AND stage = ? 
           ORDER BY created_at DESC LIMIT 1""",
        (run_id, stage)
    ).fetchone()
    conn.close()
    return row["openapi_spec_json"] if row else None


# Initialize on import
init_db()
