"""
Document Export Router - Download BA/TA/TC in DOCX/XLSX formats
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.services.document_export import (
    json_to_ba_docx,
    json_to_ta_docx,
    json_to_tc_xlsx
)
from api.services.pipeline_service import get_checkpoint
import api.db as database_service
from typing import Literal

router = APIRouter()


@router.get("/{run_id}/download/{doc_type}")
async def download_document(
    run_id: int,
    doc_type: Literal['ba', 'ta', 'tc']
):
    """
    Download generated document in appropriate format.

    - BA: DOCX
    - TA: DOCX
    - TC: XLSX

    Args:
        run_id: Pipeline run ID
        doc_type: Document type (ba, ta, or tc)

    Returns:
        StreamingResponse with document file
    """
    try:
        # Get pipeline run to get project name
        runs = database_service.get_recent_pipeline_runs(limit=1000)
        run = next((r for r in runs if r['id'] == run_id), None)

        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run {run_id} not found"
            )

        project_name = run['project_name']

        # Load checkpoint data
        stage = f"{doc_type}_gen"
        content = get_checkpoint(project_name, stage)

        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"No {doc_type.upper()} document found for run {run_id}"
            )

        # Add project name to content for document export
        content["_project_name"] = project_name

        # Generate appropriate file format
        if doc_type == 'ba':
            buffer = json_to_ba_docx(content)
            filename = f"BA_{project_name.replace(' ', '_')}.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        elif doc_type == 'ta':
            buffer = json_to_ta_docx(content)
            filename = f"TA_{project_name.replace(' ', '_')}.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        elif doc_type == 'tc':
            buffer = json_to_tc_xlsx(content)
            filename = f"TC_{project_name.replace(' ', '_')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type: {doc_type}. Must be ba, ta, or tc"
            )

        # Return file as streaming response
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate {doc_type.upper()} document: {str(e)}"
        )


@router.get("/{run_id}/preview/{doc_type}")
async def preview_document(
    run_id: int,
    doc_type: Literal['ba', 'ta', 'tc']
):
    """
    Get document content for preview (JSON format).

    Args:
        run_id: Pipeline run ID
        doc_type: Document type (ba, ta, or tc)

    Returns:
        JSON content of the document
    """
    try:
        # Get pipeline run to get project name
        runs = database_service.get_recent_pipeline_runs(limit=1000)
        run = next((r for r in runs if r['id'] == run_id), None)

        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run {run_id} not found"
            )

        project_name = run['project_name']

        # Load checkpoint data
        stage = f"{doc_type}_gen"
        content = get_checkpoint(project_name, stage)

        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"No {doc_type.upper()} document found for run {run_id}"
            )

        return {
            "doc_type": doc_type.upper(),
            "project_name": project_name,
            "content": content
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview {doc_type.upper()} document: {str(e)}"
        )
