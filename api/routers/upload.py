"""
Upload Router — File upload and parsing endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from api.services import document_service
from api.config import get_settings
import os

router = APIRouter()
settings = get_settings()


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    doc_type: Optional[str] = Form(None),
):
    """
    Upload and parse a document file (DOCX, PDF, TXT).

    Returns parsed content with metadata and confidence score.

    - **file**: File to upload (multipart/form-data)
    - **project_id**: Optional project ID to associate with
    - **doc_type**: Optional document type (ba/ta/tc)
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.allowed_extensions}"
        )

    # Validate file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size_mb:.2f}MB). Maximum size: {settings.max_upload_size_mb}MB"
        )

    try:
        # Parse file
        parsed_result = await document_service.parse_uploaded_file(
            file_content=content,
            filename=file.filename,
            file_extension=file_ext
        )

        # If project_id and doc_type provided, create document
        if project_id and doc_type:
            from api.services import database_service

            doc_id = database_service.create_document(
                project_id=project_id,
                doc_type=doc_type,
                title=parsed_result['metadata']['title'],
                content_json=parsed_result['content']
            )

            parsed_result['document_id'] = doc_id
            parsed_result['message'] = "File uploaded and document created successfully"
        else:
            parsed_result['message'] = "File parsed successfully. Use POST /documents to save."

        return parsed_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File parsing failed: {str(e)}"
        )
