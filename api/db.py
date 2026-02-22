"""
Database Service — Simple SQLite operations for pipeline management
"""
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

BA_DB_PATH = Path("data/baqa.db")
PIPELINE_DB_PATH = Path("data/pipeline.db")


def get_connection(db_path: Path):
    """Get database connection"""
    db_path.parent.mkdir(exist_ok=True)
    return sqlite3.connect(str(db_path))


def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Get project by ID from baqa.db"""
    conn = get_connection(BA_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def create_pipeline_run(
    project_name: str,
    jira_key: str = "",
    priority: str = "normal",
    brd_filename: str = ""
) -> int:
    """Create a new pipeline run record"""
    conn = get_connection(BA_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pipeline_runs (project_name, jira_key, priority, brd_filename, status, current_stage)
        VALUES (?, ?, ?, ?, 'started', 'ba_generation')
    """, (project_name, jira_key, priority, brd_filename))

    run_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return run_id


def update_pipeline_run(run_id: int, **kwargs):
    """Update pipeline run fields"""
    conn = get_connection(BA_DB_PATH)
    cursor = conn.cursor()

    # Build SET clause dynamically
    valid_fields = ['status', 'current_stage', 'ba_score', 'ta_score', 'tc_score',
                    'ba_revisions', 'ta_revisions', 'tc_revisions', 'total_time_sec']

    updates = []
    values = []
    for key, value in kwargs.items():
        if key in valid_fields:
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        conn.close()
        return

    values.append(run_id)
    query = f"UPDATE pipeline_runs SET {', '.join(updates)} WHERE id = ?"

    cursor.execute(query, values)
    conn.commit()
    conn.close()


def get_recent_pipeline_runs(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent pipeline runs"""
    conn = get_connection(BA_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM pipeline_runs
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_pipeline_output(run_id: int, stage: str, output_json: Dict[str, Any]):
    """
    Create pipeline output record in stage_outputs table.
    """
    conn = get_connection(BA_DB_PATH)
    cursor = conn.cursor()

    # Insert into stage_outputs table
    cursor.execute("""
        INSERT INTO stage_outputs (
            pipeline_run_id,
            stage,
            content_json,
            revision_number,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        run_id,
        stage,
        json.dumps(output_json, ensure_ascii=False),
        1,  # Initial revision
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_pipeline_run_outputs(run_id: int) -> List[Dict[str, Any]]:
    """
    Get outputs for a pipeline run.
    Returns documents created by the pipeline.
    """
    conn = get_connection(BA_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get stage outputs for this pipeline run
    cursor.execute("""
        SELECT
            stage,
            content_json,
            qa_result_json,
            revision_number,
            forced_pass,
            created_at
        FROM stage_outputs
        WHERE pipeline_run_id = ?
        ORDER BY created_at ASC
    """, (run_id,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        result = dict(row)
        # Parse JSON content
        if result.get('content_json'):
            try:
                result['output_json'] = json.loads(result['content_json'])
            except:
                result['output_json'] = {}
        results.append(result)

    return results
