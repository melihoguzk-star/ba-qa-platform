"""
Search Router — Hybrid search, Drive proxy, reindex, stats
"""
import asyncio
import time

from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    DriveResult,
    DriveSearchRequest,
    ReindexStatusResponse,
    SearchStatsResponse,
)
from api.services import search_service

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Perform hybrid search across platform documents and/or Google Drive.

    - **source**: "platform" (default), "drive", or "both"
    """
    start_time = time.time()

    platform_results: list[SearchResult] = []
    drive_results: list[DriveResult] = []

    try:
        if request.source in ("platform", "both"):
            platform_results = search_service.hybrid_search_platform(
                query=request.query,
                doc_type_filter=request.doc_type_filter,
                project_filter=request.project_filter,
                limit=request.limit,
            )

        if request.source in ("drive", "both"):
            raw_drive = await search_service.drive_search(query=request.query)
            for item in raw_drive:
                file_id = item.get("id", item.get("file_id", ""))
                web_link = item.get("webViewLink", "") or item.get("alternateLink", "")
                if not web_link and file_id:
                    web_link = f"https://drive.google.com/file/d/{file_id}/view"
                drive_results.append(DriveResult(
                    name=item.get("name", ""),
                    file_id=file_id,
                    webViewLink=web_link,
                    mimeType=item.get("mimeType", ""),
                    modifiedTime=item.get("modifiedTime", item.get("modifiedDate", "")),
                    size=item.get("size"),
                ))

        execution_time = (time.time() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            platform_results=platform_results,
            drive_results=drive_results,
            total_found=len(platform_results) + len(drive_results),
            execution_time_ms=round(execution_time, 2),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/reindex")
async def trigger_reindex(background_tasks: BackgroundTasks):
    """
    Trigger full re-index of all platform documents into ChromaDB.
    Runs in background.
    """
    state = search_service.get_reindex_state()
    if state["status"] == "running":
        raise HTTPException(status_code=409, detail="Reindex already in progress")

    background_tasks.add_task(search_service.reindex_all_documents)
    return {"message": "Reindex started", "status": "running"}


@router.get("/reindex/status", response_model=ReindexStatusResponse)
async def reindex_status():
    """Get current reindex progress."""
    return ReindexStatusResponse(**search_service.get_reindex_state())


@router.get("/stats", response_model=SearchStatsResponse)
async def search_stats():
    """Get ChromaDB collection statistics."""
    try:
        from pipeline.vector_store import get_vector_store
        vs = get_vector_store()
        stats = vs.get_collection_stats()
        total = sum(s.get("chunk_count", 0) for s in stats.values())
        return SearchStatsResponse(**stats, total_chunks=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


@router.post("/drive", response_model=list[DriveResult])
async def drive_search_endpoint(request: DriveSearchRequest):
    """
    Search Google Drive via n8n webhook proxy.
    """
    try:
        raw = await search_service.drive_search(
            query=request.query,
            folder_id=request.folder_id,
            mime_type=request.mime_type,
        )
        results = []
        for item in raw:
            file_id = item.get("id", item.get("file_id", ""))
            web_link = item.get("webViewLink", "") or item.get("alternateLink", "")
            if not web_link and file_id:
                web_link = f"https://drive.google.com/file/d/{file_id}/view"
            results.append(DriveResult(
                name=item.get("name", ""),
                file_id=file_id,
                webViewLink=web_link,
                mimeType=item.get("mimeType", ""),
                modifiedTime=item.get("modifiedTime", item.get("modifiedDate", "")),
                size=item.get("size"),
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive search failed: {str(e)}")
