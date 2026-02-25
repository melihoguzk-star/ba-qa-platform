"""
Drive Search Service — Shared Drive search via n8n webhook proxy
"""
import logging
from typing import Optional

import httpx

from api.config import get_settings

logger = logging.getLogger(__name__)

# Mime type filter mapping (user-friendly key → Google MIME type)
MIME_TYPE_MAP = {
    "docs": "application/vnd.google-apps.document",
    "sheets": "application/vnd.google-apps.spreadsheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
    "": "",
    "all": "",
}


async def search_drive(
    query: str,
    drive_id: Optional[str] = None,
    mime_type_filter: Optional[str] = None,
) -> list[dict]:
    """
    Search Google Shared Drive via n8n webhook proxy.

    Args:
        query: Search query text
        drive_id: Shared Drive ID (defaults to config value)
        mime_type_filter: User-friendly filter key (docs/sheets/docx/pdf/all)

    Returns:
        List of file result dicts from n8n
    """
    settings = get_settings()
    webhook_url = settings.n8n_drive_search_proxy

    if not webhook_url:
        logger.warning("n8n_drive_search_proxy URL not configured")
        return []

    # Resolve drive_id
    resolved_drive_id = drive_id or settings.shared_drive_id

    # Resolve mime_type
    mime_type = MIME_TYPE_MAP.get(mime_type_filter or "", "")

    payload = {
        "query": query,
        "drive_id": resolved_drive_id,
    }
    if mime_type:
        payload["mime_type"] = mime_type

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            logger.info(f"Drive search: PAYLOAD={payload!r}")
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            # n8n may return list or wrapped in a key
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict) and "results" in data:
                results = data["results"]
            else:
                results = [data] if data else []

            logger.info(f"Drive search: {len(results)} results for query={query!r}")
            return results

    except httpx.TimeoutException:
        logger.error(f"Drive search timeout for query={query!r}")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"Drive search HTTP error: {e.response.status_code} for query={query!r}")
        return []
    except Exception as e:
        logger.error(f"Drive search failed: {e}", exc_info=True)
        return []
