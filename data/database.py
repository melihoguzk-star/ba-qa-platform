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

        -- Document Repository Tables (Phase 1)
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            jira_project_key TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            doc_type TEXT CHECK(doc_type IN ('ba', 'ta', 'tc')) NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            current_version INTEGER DEFAULT 1,
            tags TEXT DEFAULT '[]',
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'draft')),
            jira_keys TEXT DEFAULT '[]',
            created_by TEXT DEFAULT 'system',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_document_id INTEGER DEFAULT NULL REFERENCES documents(id) ON DELETE SET NULL,
            adaptation_notes TEXT DEFAULT '',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            content_json TEXT NOT NULL,
            change_summary TEXT DEFAULT '',
            created_by TEXT DEFAULT 'system',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            UNIQUE(document_id, version_number)
        );

        CREATE TABLE IF NOT EXISTS document_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER NOT NULL,
            section_type TEXT NOT NULL,
            section_title TEXT NOT NULL,
            content_json TEXT NOT NULL,
            order_index INTEGER DEFAULT 0,
            FOREIGN KEY (version_id) REFERENCES document_versions(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
        CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type);
        CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
        CREATE INDEX IF NOT EXISTS idx_document_versions_doc ON document_versions(document_id);
        CREATE INDEX IF NOT EXISTS idx_document_sections_version ON document_sections(version_id);
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


# ─────────────────────────────────────────────
# Document Repository Functions (Phase 1)
# ─────────────────────────────────────────────

def create_project(name: str, description: str = "", jira_project_key: str = "", tags: list = None) -> int:
    """Create a new project."""
    conn = get_db()
    tags_json = json.dumps(tags or [], ensure_ascii=False)
    cur = conn.execute(
        "INSERT INTO projects (name, description, jira_project_key, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, jira_project_key, tags_json, datetime.now().isoformat(), datetime.now().isoformat())
    )
    project_id = cur.lastrowid
    conn.commit()
    conn.close()
    return project_id


def get_projects(status: str = None, search: str = None) -> list:
    """Get all projects with optional filters."""
    conn = get_db()

    query = "SELECT * FROM projects WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    query += " ORDER BY updated_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for row in rows:
        project = dict(row)
        project['tags'] = json.loads(project.get('tags', '[]'))
        result.append(project)

    return result


def get_project_by_id(project_id: int) -> dict:
    """Get a project by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()

    if row:
        project = dict(row)
        project['tags'] = json.loads(project.get('tags', '[]'))
        return project
    return None


def create_document(project_id: int, doc_type: str, title: str, content_json: dict,
                   description: str = "", tags: list = None, jira_keys: list = None,
                   created_by: str = "system", source_document_id: int = None,
                   adaptation_notes: str = "") -> int:
    """Create a new document with initial version.

    Args:
        project_id: Project ID
        doc_type: Document type (ba, ta, tc)
        title: Document title
        content_json: Document content as JSON dict
        description: Document description
        tags: List of tags
        jira_keys: List of JIRA keys
        created_by: Creator name
        source_document_id: ID of source document if adapted (Phase 3)
        adaptation_notes: Notes about adaptation (Phase 3)

    Returns:
        Created document ID
    """
    conn = get_db()

    # Create document record
    tags_json = json.dumps(tags or [], ensure_ascii=False)
    jira_keys_json = json.dumps(jira_keys or [], ensure_ascii=False)

    cur = conn.execute(
        """INSERT INTO documents (project_id, doc_type, title, description, current_version,
           tags, jira_keys, created_by, created_at, updated_at, source_document_id, adaptation_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (project_id, doc_type, title, description, 1, tags_json, jira_keys_json,
         created_by, datetime.now().isoformat(), datetime.now().isoformat(),
         source_document_id, adaptation_notes)
    )
    doc_id = cur.lastrowid

    # Create initial version
    change_summary = "Initial version"
    if source_document_id:
        change_summary = f"Adapted from document ID {source_document_id}"

    conn.execute(
        """INSERT INTO document_versions (document_id, version_number, content_json,
           change_summary, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
        (doc_id, 1, json.dumps(content_json, ensure_ascii=False),
         change_summary, created_by, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    # Phase 2A: Auto-index in ChromaDB
    if os.getenv('ENABLE_AUTO_INDEXING', 'true').lower() == 'true':
        try:
            from pipeline.embedding_pipeline import index_document_async
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Auto-indexing document {doc_id} in vector store")

            # Extract metadata for indexing
            metadata = {
                'project_id': project_id,
                'title': title,
                'description': description,
                'tags': tags or [],
                'jira_keys': jira_keys or [],
                'created_by': created_by
            }

            index_document_async(doc_id, content_json, doc_type, metadata)
        except Exception as e:
            # Don't fail document creation if indexing fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to auto-index document {doc_id}: {e}")

    return doc_id


def get_documents(project_id: int = None, doc_type: str = None, status: str = "active",
                 search: str = None, tags: list = None) -> list:
    """Get documents with optional filters."""
    conn = get_db()

    query = "SELECT * FROM documents WHERE 1=1"
    params = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)

    if doc_type:
        query += " AND doc_type = ?"
        params.append(doc_type)

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    query += " ORDER BY updated_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for row in rows:
        doc = dict(row)
        doc['tags'] = json.loads(doc.get('tags', '[]'))
        doc['jira_keys'] = json.loads(doc.get('jira_keys', '[]'))

        # Filter by tags if provided
        if tags:
            if not any(tag in doc['tags'] for tag in tags):
                continue

        result.append(doc)

    return result


def get_document_by_id(doc_id: int) -> dict:
    """Get a document by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    conn.close()

    if row:
        doc = dict(row)
        doc['tags'] = json.loads(doc.get('tags', '[]'))
        doc['jira_keys'] = json.loads(doc.get('jira_keys', '[]'))
        return doc
    return None


def update_document(doc_id: int, **kwargs):
    """Update document metadata."""
    conn = get_db()

    # Add updated_at timestamp
    kwargs['updated_at'] = datetime.now().isoformat()

    # Handle JSON fields
    if 'tags' in kwargs and isinstance(kwargs['tags'], list):
        kwargs['tags'] = json.dumps(kwargs['tags'], ensure_ascii=False)
    if 'jira_keys' in kwargs and isinstance(kwargs['jira_keys'], list):
        kwargs['jira_keys'] = json.dumps(kwargs['jira_keys'], ensure_ascii=False)

    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [doc_id]

    conn.execute(f"UPDATE documents SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def create_document_version(doc_id: int, content_json: dict, change_summary: str = "",
                            created_by: str = "system") -> int:
    """Create a new version of a document."""
    conn = get_db()

    # Get current version number
    current_doc = conn.execute("SELECT current_version FROM documents WHERE id = ?", (doc_id,)).fetchone()
    if not current_doc:
        conn.close()
        raise ValueError(f"Document {doc_id} not found")

    new_version = current_doc["current_version"] + 1

    # Insert new version
    cur = conn.execute(
        """INSERT INTO document_versions (document_id, version_number, content_json,
           change_summary, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
        (doc_id, new_version, json.dumps(content_json, ensure_ascii=False),
         change_summary, created_by, datetime.now().isoformat())
    )
    version_id = cur.lastrowid

    # Update document's current version
    conn.execute(
        "UPDATE documents SET current_version = ?, updated_at = ? WHERE id = ?",
        (new_version, datetime.now().isoformat(), doc_id)
    )

    # Get document info for indexing
    doc_row = conn.execute(
        "SELECT doc_type, project_id, title, description, tags, jira_keys FROM documents WHERE id = ?",
        (doc_id,)
    ).fetchone()

    conn.commit()
    conn.close()

    # Phase 2A: Re-index in ChromaDB on version update
    if doc_row and os.getenv('ENABLE_AUTO_INDEXING', 'true').lower() == 'true':
        try:
            from pipeline.embedding_pipeline import index_document_async
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Re-indexing document {doc_id} (new version: {new_version})")

            # Extract metadata for indexing
            metadata = {
                'project_id': doc_row['project_id'],
                'title': doc_row['title'],
                'description': doc_row['description'],
                'tags': json.loads(doc_row.get('tags', '[]')),
                'jira_keys': json.loads(doc_row.get('jira_keys', '[]')),
                'created_by': created_by,
                'version_number': new_version
            }

            index_document_async(doc_id, content_json, doc_row['doc_type'], metadata)
        except Exception as e:
            # Don't fail version creation if indexing fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to re-index document {doc_id}: {e}")

    return version_id


def get_document_versions(doc_id: int) -> list:
    """Get all versions of a document."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM document_versions WHERE document_id = ? ORDER BY version_number DESC",
        (doc_id,)
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        version = dict(row)
        version['content_json'] = json.loads(version['content_json'])
        result.append(version)

    return result


def get_latest_version(doc_id: int) -> dict:
    """Get the latest version of a document."""
    conn = get_db()
    row = conn.execute(
        """SELECT * FROM document_versions WHERE document_id = ?
           ORDER BY version_number DESC LIMIT 1""",
        (doc_id,)
    ).fetchone()
    conn.close()

    if row:
        version = dict(row)
        version['content_json'] = json.loads(version['content_json'])
        return version
    return None


def get_documents_with_content(project_id: int = None, doc_type: str = None,
                                status: str = "active", limit: int = 100) -> list:
    """
    Get documents WITH their latest version content.
    Useful for document matching and similarity analysis.

    Args:
        project_id: Filter by project ID (optional)
        doc_type: Filter by document type (optional)
        status: Filter by status (default: 'active')
        limit: Maximum number of documents to return (default: 100)

    Returns:
        List of documents with 'content_json' field populated
    """
    conn = get_db()

    query = """
        SELECT
            d.*,
            v.content_json
        FROM documents d
        LEFT JOIN (
            SELECT document_id, content_json,
                   ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY version_number DESC) as rn
            FROM document_versions
        ) v ON d.id = v.document_id AND v.rn = 1
        WHERE 1=1
    """
    params = []

    if project_id:
        query += " AND d.project_id = ?"
        params.append(project_id)

    if doc_type:
        query += " AND d.doc_type = ?"
        params.append(doc_type)

    if status:
        query += " AND d.status = ?"
        params.append(status)

    query += " ORDER BY d.updated_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for row in rows:
        doc = dict(row)
        doc['tags'] = json.loads(doc.get('tags', '[]'))
        doc['jira_keys'] = json.loads(doc.get('jira_keys', '[]'))

        # Parse content_json if exists
        if doc.get('content_json'):
            try:
                doc['content_json'] = json.loads(doc['content_json'])
            except (json.JSONDecodeError, TypeError):
                doc['content_json'] = {}
        else:
            doc['content_json'] = {}

        result.append(doc)

    return result


def create_document_sections(version_id: int, sections: list):
    """Create document sections for a version.

    Args:
        version_id: Version ID
        sections: List of dicts with {section_type, section_title, content_json, order_index}
    """
    conn = get_db()

    for section in sections:
        conn.execute(
            """INSERT INTO document_sections (version_id, section_type, section_title,
               content_json, order_index) VALUES (?, ?, ?, ?, ?)""",
            (version_id, section['section_type'], section['section_title'],
             json.dumps(section['content_json'], ensure_ascii=False), section.get('order_index', 0))
        )

    conn.commit()
    conn.close()


def get_document_sections(version_id: int) -> list:
    """Get all sections for a document version."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM document_sections WHERE version_id = ? ORDER BY order_index",
        (version_id,)
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        section = dict(row)
        section['content_json'] = json.loads(section['content_json'])
        result.append(section)

    return result


def get_document_stats() -> dict:
    """Get document repository statistics."""
    conn = get_db()

    total_projects = conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()["c"]
    total_docs = conn.execute("SELECT COUNT(*) as c FROM documents WHERE status='active'").fetchone()["c"]

    docs_by_type = conn.execute(
        "SELECT doc_type, COUNT(*) as c FROM documents WHERE status='active' GROUP BY doc_type"
    ).fetchall()

    recent_docs = conn.execute(
        """SELECT d.*, p.name as project_name FROM documents d
           LEFT JOIN projects p ON d.project_id = p.id
           WHERE d.status='active'
           ORDER BY d.updated_at DESC LIMIT 10"""
    ).fetchall()

    conn.close()

    return {
        "total_projects": total_projects,
        "total_documents": total_docs,
        "by_type": [dict(r) for r in docs_by_type],
        "recent_documents": [dict(r) for r in recent_docs]
    }


# ═══════════════════════════════════════════════════════════════
# PHASE 3: DOCUMENT LINEAGE & ADAPTATION
# ═══════════════════════════════════════════════════════════════

def get_document_lineage(doc_id: int) -> dict:
    """
    Get document lineage information (source and derived documents).

    Args:
        doc_id: Document ID

    Returns:
        Dict with source document and list of derived documents
    """
    conn = get_db()

    # Get the document
    doc = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()

    if not doc:
        conn.close()
        return None

    doc = dict(doc)

    # Get source document (if this was adapted from another)
    source_doc = None
    if doc.get('source_document_id'):
        source = conn.execute(
            "SELECT * FROM documents WHERE id = ?",
            (doc['source_document_id'],)
        ).fetchone()
        if source:
            source_doc = dict(source)
            source_doc['tags'] = json.loads(source_doc.get('tags', '[]'))
            source_doc['jira_keys'] = json.loads(source_doc.get('jira_keys', '[]'))

    # Get derived documents (documents adapted from this one)
    derived = conn.execute(
        "SELECT * FROM documents WHERE source_document_id = ? ORDER BY created_at DESC",
        (doc_id,)
    ).fetchall()

    derived_docs = []
    for row in derived:
        derived_doc = dict(row)
        derived_doc['tags'] = json.loads(derived_doc.get('tags', '[]'))
        derived_doc['jira_keys'] = json.loads(derived_doc.get('jira_keys', '[]'))
        derived_docs.append(derived_doc)

    conn.close()

    return {
        'document': doc,
        'source': source_doc,
        'derived': derived_docs,
        'lineage_depth': 1 if source_doc else 0,
        'has_descendants': len(derived_docs) > 0
    }


def get_template_candidates(doc_type: str = None, project_id: int = None,
                            exclude_id: int = None, limit: int = 20) -> list:
    """
    Get documents that can be used as templates.

    Args:
        doc_type: Filter by document type
        project_id: Filter by project
        exclude_id: Exclude specific document ID
        limit: Maximum results

    Returns:
        List of documents suitable as templates
    """
    conn = get_db()

    query = """
        SELECT d.*, p.name as project_name,
               (SELECT COUNT(*) FROM documents WHERE source_document_id = d.id) as times_used_as_template
        FROM documents d
        LEFT JOIN projects p ON d.project_id = p.id
        WHERE d.status = 'active'
    """
    params = []

    if doc_type:
        query += " AND d.doc_type = ?"
        params.append(doc_type)

    if project_id:
        query += " AND d.project_id = ?"
        params.append(project_id)

    if exclude_id:
        query += " AND d.id != ?"
        params.append(exclude_id)

    query += " ORDER BY times_used_as_template DESC, d.updated_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for row in rows:
        doc = dict(row)
        doc['tags'] = json.loads(doc.get('tags', '[]'))
        doc['jira_keys'] = json.loads(doc.get('jira_keys', '[]'))
        result.append(doc)

    return result


# Initialize on import
init_db()
