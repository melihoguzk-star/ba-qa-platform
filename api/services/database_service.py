"""
Database Service — Wraps data/database.py with connection safety

All database operations use the get_db_context() context manager
to prevent connection leaks on exceptions.
"""
from typing import Optional, Any
from api.dependencies import get_db_context
import json
from datetime import datetime


# ─────────────────────────────────────────────
# ANALYSIS OPERATIONS (Legacy)
# ─────────────────────────────────────────────

def save_analysis(
    jira_key: str,
    analysis_type: str,
    genel_puan: float,
    gecti_mi: bool,
    result_json: dict,
    report_text: str = "",
    project: str = "",
    triggered_by: str = "manual"
) -> int:
    """Save analysis result to database"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analyses (jira_key, project, analysis_type, genel_puan, gecti_mi,
                                  result_json, report_text, triggered_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'done')
            """,
            (jira_key, project, analysis_type, genel_puan, int(gecti_mi),
             json.dumps(result_json, ensure_ascii=False), report_text, triggered_by)
        )
        return cursor.lastrowid


def get_recent_analyses(limit: int = 20, analysis_type: Optional[str] = None, time_range: str = "all") -> list:
    """Get recent analyses with optional filters"""
    with get_db_context() as conn:
        from data.database import get_recent_analyses as _get_recent_analyses
        return _get_recent_analyses(limit, analysis_type, time_range)


def get_stats(time_range: str = "all") -> dict:
    """Get analysis statistics"""
    with get_db_context() as conn:
        from data.database import get_stats as _get_stats
        return _get_stats(time_range)


def get_dashboard_alerts() -> list:
    """Get dashboard alerts"""
    with get_db_context() as conn:
        from data.database import get_dashboard_alerts as _get_dashboard_alerts
        return _get_dashboard_alerts()


def get_quality_trend_data(time_range: str = "30days") -> dict:
    """Get quality trend data"""
    with get_db_context() as conn:
        from data.database import get_quality_trend_data as _get_quality_trend_data
        return _get_quality_trend_data(time_range)


def get_score_distribution(time_range: str = "30days") -> dict:
    """Get score distribution"""
    with get_db_context() as conn:
        from data.database import get_score_distribution as _get_score_distribution
        return _get_score_distribution(time_range)


def get_sparkline_data(analysis_type: str, days: int = 7) -> list:
    """Get sparkline data"""
    with get_db_context() as conn:
        from data.database import get_sparkline_data as _get_sparkline_data
        return _get_sparkline_data(analysis_type, days)


# ─────────────────────────────────────────────
# PIPELINE OPERATIONS
# ─────────────────────────────────────────────

def create_pipeline_run(project_name: str, jira_key: str, priority: str, brd_filename: str) -> int:
    """Create new pipeline run"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO pipeline_runs (project_name, jira_key, priority, brd_filename, status, current_stage)
            VALUES (?, ?, ?, ?, 'running', 'ba')
            """,
            (project_name, jira_key, priority, brd_filename)
        )
        return cursor.lastrowid


def update_pipeline_run(run_id: int, **kwargs):
    """Update pipeline run with arbitrary fields"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [run_id]
        cursor.execute(f"UPDATE pipeline_runs SET {set_clause} WHERE id = ?", values)


def save_pipeline_stage_output(
    run_id: int,
    stage: str,
    content: dict,
    qa_result: dict,
    revision: int = 0,
    forced_pass: bool = False,
    generation_time: int = 0,
    openapi_spec: Optional[dict] = None
):
    """Save pipeline stage output"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO stage_outputs (pipeline_run_id, stage, content_json, qa_result_json,
                                       revision_number, forced_pass, generation_time_sec, openapi_spec_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id, stage,
                json.dumps(content, ensure_ascii=False),
                json.dumps(qa_result, ensure_ascii=False),
                revision, int(forced_pass), generation_time,
                json.dumps(openapi_spec, ensure_ascii=False) if openapi_spec else None
            )
        )


def get_recent_pipeline_runs(limit: int = 20) -> list:
    """Get recent pipeline runs"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_pipeline_run_outputs(run_id: int) -> list:
    """Get all outputs for a pipeline run"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM stage_outputs WHERE pipeline_run_id = ? ORDER BY stage, revision_number",
            (run_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def save_openapi_spec(run_id: int, stage: str, openapi_json: str):
    """Save OpenAPI spec for a stage"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE stage_outputs
            SET openapi_spec_json = ?
            WHERE pipeline_run_id = ? AND stage = ?
            ORDER BY revision_number DESC
            LIMIT 1
            """,
            (openapi_json, run_id, stage)
        )


def get_openapi_spec(run_id: int, stage: str = 'ta') -> Optional[str]:
    """Get OpenAPI spec for a stage"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT openapi_spec_json FROM stage_outputs
            WHERE pipeline_run_id = ? AND stage = ?
            ORDER BY revision_number DESC
            LIMIT 1
            """,
            (run_id, stage)
        )
        row = cursor.fetchone()
        return row[0] if row else None


# ─────────────────────────────────────────────
# PROJECT OPERATIONS
# ─────────────────────────────────────────────

def create_project(name: str, description: str = "", jira_project_key: str = "", tags: list = None) -> int:
    """Create new project"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (name, description, jira_project_key, tags)
            VALUES (?, ?, ?, ?)
            """,
            (name, description, jira_project_key, json.dumps(tags or []))
        )
        return cursor.lastrowid


def get_projects(status: Optional[str] = None, search: Optional[str] = None) -> list:
    """Get all projects with optional filters"""
    with get_db_context() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM projects WHERE 1=1"
        params = []

        if status == "active":
            query += " AND status = 'active'"

        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY updated_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        projects = []
        for row in rows:
            p = dict(row)
            p['tags'] = json.loads(p.get('tags', '[]'))
            projects.append(p)

        return projects


def get_project_by_id(project_id: int) -> Optional[dict]:
    """Get project by ID"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()

        if row:
            p = dict(row)
            p['tags'] = json.loads(p.get('tags', '[]'))
            return p
        return None


def update_project(project_id: int, **kwargs):
    """Update project with arbitrary fields"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        kwargs['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [project_id]
        cursor.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)


def delete_project(project_id: int):
    """Soft delete project"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET status = 'deleted' WHERE id = ?", (project_id,))


# ─────────────────────────────────────────────
# DOCUMENT OPERATIONS
# ─────────────────────────────────────────────

def create_document(
    project_id: int,
    doc_type: str,
    title: str,
    content_json: dict,
    description: str = "",
    tags: list = None,
    jira_keys: list = None,
    created_by: str = "system"
) -> int:
    """Create new document"""
    with get_db_context() as conn:
        cursor = conn.cursor()

        # Create document
        cursor.execute(
            """
            INSERT INTO documents (project_id, doc_type, title, description, current_version, tags, jira_keys, created_by)
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (
                project_id, doc_type, title, description,
                json.dumps(tags or []),
                json.dumps(jira_keys or []),
                created_by
            )
        )
        doc_id = cursor.lastrowid

        # Create initial version
        cursor.execute(
            """
            INSERT INTO document_versions (document_id, version_number, content_json, change_summary, created_by)
            VALUES (?, 1, ?, 'Initial version', ?)
            """,
            (doc_id, json.dumps(content_json, ensure_ascii=False), created_by)
        )

        return doc_id


def get_documents(
    project_id: Optional[int] = None,
    doc_type: Optional[str] = None,
    status: str = "active",
    search: Optional[str] = None,
    limit: int = 100
) -> list:
    """Get documents with filters"""
    with get_db_context() as conn:
        cursor = conn.cursor()

        query = """
            SELECT d.*, dv.content_json
            FROM documents d
            LEFT JOIN document_versions dv ON d.id = dv.document_id AND d.current_version = dv.version_number
            WHERE d.status = ?
        """
        params = [status]

        if project_id is not None:
            query += " AND d.project_id = ?"
            params.append(project_id)

        if doc_type:
            query += " AND d.doc_type = ?"
            params.append(doc_type)

        if search:
            query += " AND (d.title LIKE ? OR d.jira_keys LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY d.updated_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        documents = []
        for row in rows:
            doc = dict(row)
            if doc.get('content_json'):
                doc['content_json'] = json.loads(doc['content_json'])
            if doc.get('tags'):
                doc['tags'] = json.loads(doc['tags'])
            if doc.get('jira_keys'):
                doc['jira_keys'] = json.loads(doc['jira_keys'])
            documents.append(doc)

        return documents


def get_document_by_id(doc_id: int) -> Optional[dict]:
    """Get document by ID with latest content"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT d.*, dv.content_json
            FROM documents d
            LEFT JOIN document_versions dv ON d.id = dv.document_id AND d.current_version = dv.version_number
            WHERE d.id = ?
            """,
            (doc_id,)
        )
        row = cursor.fetchone()

        if row:
            doc = dict(row)
            if doc.get('content_json'):
                doc['content_json'] = json.loads(doc['content_json'])
            if doc.get('tags'):
                doc['tags'] = json.loads(doc['tags'])
            if doc.get('jira_keys'):
                doc['jira_keys'] = json.loads(doc['jira_keys'])
            return doc
        return None


def update_document(doc_id: int, **kwargs):
    """Update document metadata"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        kwargs['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [doc_id]
        cursor.execute(f"UPDATE documents SET {set_clause} WHERE id = ?", values)


def delete_document(doc_id: int):
    """Soft delete document"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE documents SET status = 'deleted' WHERE id = ?", (doc_id,))


def create_document_version(
    doc_id: int,
    content_json: dict,
    change_summary: str = "",
    created_by: str = "system"
) -> int:
    """Create new document version"""
    with get_db_context() as conn:
        cursor = conn.cursor()

        # Get current version
        cursor.execute("SELECT current_version FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        current_version = row[0] if row else 0
        new_version = current_version + 1

        # Create new version
        cursor.execute(
            """
            INSERT INTO document_versions (document_id, version_number, content_json, change_summary, created_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (doc_id, new_version, json.dumps(content_json, ensure_ascii=False), change_summary, created_by)
        )
        version_id = cursor.lastrowid

        # Update document version pointer
        cursor.execute("UPDATE documents SET current_version = ? WHERE id = ?", (new_version, doc_id))

        return version_id


def get_document_versions(doc_id: int) -> list:
    """Get all versions of a document"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM document_versions WHERE document_id = ? ORDER BY version_number DESC",
            (doc_id,)
        )
        rows = cursor.fetchall()

        versions = []
        for row in rows:
            v = dict(row)
            if v.get('content_json'):
                v['content_json'] = json.loads(v['content_json'])
            versions.append(v)

        return versions


def get_latest_version(doc_id: int) -> Optional[dict]:
    """Get latest version of a document"""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM document_versions
            WHERE document_id = ?
            ORDER BY version_number DESC
            LIMIT 1
            """,
            (doc_id,)
        )
        row = cursor.fetchone()

        if row:
            v = dict(row)
            if v.get('content_json'):
                v['content_json'] = json.loads(v['content_json'])
            return v
        return None


def get_document_stats() -> dict:
    """Get document statistics"""
    with get_db_context() as conn:
        cursor = conn.cursor()

        stats = {}

        # Total documents by type
        cursor.execute("""
            SELECT doc_type, COUNT(*) as count
            FROM documents
            WHERE status = 'active'
            GROUP BY doc_type
        """)
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

        # Total documents
        stats['total'] = sum(stats['by_type'].values())

        # Documents by project
        cursor.execute("""
            SELECT p.name, COUNT(d.id) as count
            FROM projects p
            LEFT JOIN documents d ON p.id = d.project_id AND d.status = 'active'
            GROUP BY p.id
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['by_project'] = [{'project': row[0], 'count': row[1]} for row in cursor.fetchall()]

        return stats


# ─────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────

def init_db():
    """Initialize database schema"""
    from data.database import init_db as _init_db
    _init_db()
