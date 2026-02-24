"""
Search Service — Hybrid search logic + Drive proxy
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any, List

import httpx

from api.schemas.search import SearchResult

logger = logging.getLogger(__name__)

# ── Reindex state (in-memory) ────────────────────────────────────────────
_reindex_state: Dict[str, Any] = {
    "status": "idle",  # idle | running | completed | failed
    "total": 0,
    "processed": 0,
    "errors": 0,
    "error_message": "",
}


def get_reindex_state() -> Dict[str, Any]:
    return dict(_reindex_state)


def hybrid_search_platform(
    query: str,
    doc_type_filter: Optional[str] = None,
    project_filter: Optional[int] = None,
    limit: int = 10,
) -> list[SearchResult]:
    """
    Perform hybrid semantic + keyword search on platform documents.
    """
    try:
        from pipeline.hybrid_search import hybrid_search as _hybrid_search

        raw_results = _hybrid_search(
            query_text=query,
            doc_type=doc_type_filter.lower() if doc_type_filter else None,
            top_k=limit,
        )

        results = []
        for r in raw_results:
            score = r.get("hybrid_score", r.get("similarity", r.get("tfidf_score", 0.0)))
            results.append(SearchResult(
                document_id=r["document_id"],
                title=r.get("title", "Untitled"),
                doc_type=r.get("doc_type", r.get("metadata", {}).get("doc_type", "unknown")),
                score=round(score, 4),
                snippet=r.get("chunk_text", r.get("snippet", ""))[:500],
                metadata=r.get("metadata", {}),
            ))

        return results

    except Exception as e:
        logger.error(f"Platform hybrid search failed: {e}")
        return []


# Extensions to exclude from Drive results (non-document files)
_EXCLUDED_EXTENSIONS = {
    # Web / code
    '.svg', '.css', '.html', '.htm', '.js', '.min.js', '.ts', '.jsx', '.tsx',
    '.py', '.java', '.c', '.cpp', '.h', '.rb', '.go', '.rs', '.cs', '.swift',
    '.kt', '.m', '.mm', '.r', '.scala', '.pl', '.lua', '.php',
    # Config / data
    '.json', '.xml', '.yaml', '.yml', '.csv', '.env', '.toml', '.ini', '.cfg',
    '.lock', '.log', '.map', '.sql',
    # Images / media
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.bmp', '.tiff', '.psd',
    '.mp4', '.mp3', '.wav', '.avi', '.mov', '.mkv', '.flv', '.ogg',
    # Archives
    '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
    # Executables / binaries
    '.exe', '.dmg', '.app', '.sh', '.bat', '.bin', '.dll', '.so', '.dylib',
    # Fonts
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    # Design / tool-specific
    '.sketch', '.fig', '.xd', '.ai', '.eps', '.key', '.drawio',
    # Test / perf tools
    '.jmx', '.har', '.pcap',
}

# Google Workspace document mimeTypes (always allowed)
_DOCUMENT_MIMETYPES = {
    'application/vnd.google-apps.document',
    'application/vnd.google-apps.spreadsheet',
    'application/vnd.google-apps.presentation',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint',
    'text/plain',
}


def _is_document_file(item: Dict[str, Any]) -> bool:
    """Check if a Drive file is a document (not code/asset/media)."""
    mime = item.get("mimeType", "")
    if mime and mime in _DOCUMENT_MIMETYPES:
        return True

    name = item.get("name", "")
    if not name:
        return False

    # Check extension
    name_lower = name.lower()
    for ext in _EXCLUDED_EXTENSIONS:
        if name_lower.endswith(ext):
            return False

    # Google Workspace files have no extension — allow them
    if "." not in name_lower:
        return True

    return True


async def drive_search(
    query: str,
    folder_id: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search Google Drive via n8n webhook proxy.
    Filters out non-document files (svg, css, html, js, etc.)
    """
    from api.config import get_settings
    settings = get_settings()

    webhook_url = settings.n8n_drive_search_proxy
    if not webhook_url:
        logger.warning("n8n_drive_search_proxy URL not configured")
        return []

    payload: Dict[str, Any] = {"query": query}
    if folder_id:
        payload["folder_id"] = folder_id
    if mime_type:
        payload["mime_type"] = mime_type

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # n8n may return a list or wrapped in a key
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict) and "results" in data:
                results = data["results"]
            else:
                results = [data] if data else []

            # Filter: only document files
            return [r for r in results if _is_document_file(r)]
    except Exception as e:
        logger.error(f"Drive search failed: {e}")
        return []


def reindex_all_documents() -> None:
    """
    Re-index all platform documents into ChromaDB (runs in background).
    """
    global _reindex_state

    if _reindex_state["status"] == "running":
        return

    _reindex_state.update(status="running", total=0, processed=0, errors=0, error_message="")

    try:
        from data.database import get_db
        from pipeline.vector_store import get_vector_store

        conn = get_db()
        rows = conn.execute(
            "SELECT id, doc_type, title, description, tags, jira_keys, project_id FROM documents WHERE status='active'"
        ).fetchall()
        conn.close()

        _reindex_state["total"] = len(rows)
        vs = get_vector_store()

        for row in rows:
            try:
                doc_type = (row["doc_type"] or "ba").lower()
                if doc_type not in ("ba", "ta", "tc"):
                    _reindex_state["processed"] += 1
                    continue

                # Build minimal content_json from title + description
                content_json = {
                    "title": row.get("title", ""),
                    "description": row.get("description", ""),
                }

                metadata = {
                    "project_id": row.get("project_id"),
                    "tags": row.get("tags", ""),
                    "jira_keys": row.get("jira_keys", ""),
                }

                vs.index_document(
                    doc_id=row["id"],
                    doc_type=doc_type,
                    content_json=content_json,
                    metadata=metadata,
                )
                _reindex_state["processed"] += 1
            except Exception as e:
                logger.error(f"Reindex doc {row['id']} failed: {e}")
                _reindex_state["errors"] += 1
                _reindex_state["processed"] += 1

        _reindex_state["status"] = "completed"

    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        _reindex_state.update(status="failed", error_message=str(e))
