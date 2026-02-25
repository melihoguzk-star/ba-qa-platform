"""
Drive Router — Shared Drive search endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from api.services import search_service
from api.services.drive_service import MIME_TYPE_MAP

router = APIRouter()


class DriveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    mime_type_filter: Optional[str] = Field(
        default="",
        description="Filter: docs, sheets, docx, pdf, all (or empty)"
    )


class DriveFileResult(BaseModel):
    name: str = ""
    id: str = ""
    file_id: str = ""
    webViewLink: str = ""
    mimeType: str = ""
    modifiedTime: str = ""
    createdTime: str = ""
    size: Optional[str] = None
    lastModifiedBy: str = ""
    fileType: str = ""
    relevance_score: float = 0.0


class DriveSearchResponse(BaseModel):
    results: list[DriveFileResult]
    count: int
    query: str


@router.post("/search", response_model=DriveSearchResponse)
async def search_drive(request: DriveSearchRequest):
    """
    Search Google Shared Drive via n8n webhook proxy.
    Uses search_service for document filtering, dedup, and relevance scoring.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Resolve user-friendly mime filter to actual MIME type
    resolved_mime = MIME_TYPE_MAP.get(request.mime_type_filter or "", "")

    raw_results = await search_service.drive_search(
        query=request.query.strip(),
        mime_type=resolved_mime or None,
    )

    # Map raw dicts to response model
    results = []
    for item in raw_results:
        file_id = item.get("id", item.get("file_id", ""))
        web_link = item.get("webViewLink", "") or item.get("alternateLink", "")
        if not web_link and file_id:
            web_link = f"https://drive.google.com/file/d/{file_id}/view"

        results.append(DriveFileResult(
            name=item.get("name", ""),
            id=file_id,
            file_id=file_id,
            webViewLink=web_link,
            mimeType=item.get("mimeType", ""),
            modifiedTime=item.get("modifiedTime", item.get("modifiedDate", "")),
            createdTime=item.get("createdTime", ""),
            size=item.get("size"),
            lastModifiedBy=item.get("lastModifiedBy", ""),
            fileType=item.get("fileType", ""),
            relevance_score=item.get("_relevance_score", 0.0),
        ))

    return DriveSearchResponse(
        results=results,
        count=len(results),
        query=request.query,
    )
