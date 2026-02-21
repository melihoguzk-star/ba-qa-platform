"""
Documents Router — CRUD endpoints for documents
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from api.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentVersion
from api.schemas.common import SuccessResponse
from api.services import database_service

router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    doc_type: Optional[str] = Query(None, description="Filter by document type (ba/ta/tc)"),
    status: str = Query("active", description="Filter by status (active/archived/draft)"),
    search: Optional[str] = Query(None, description="Search in title and JIRA keys"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
):
    """
    Get all documents with optional filters.

    - **project_id**: Filter by project ID
    - **doc_type**: Filter by document type (ba, ta, tc)
    - **status**: Filter by status (active/archived/draft)
    - **search**: Search term for title and JIRA keys
    - **limit**: Maximum number of results (1-500)
    """
    documents = database_service.get_documents(
        project_id=project_id,
        doc_type=doc_type,
        status=status,
        search=search,
        limit=limit
    )
    return documents


@router.post("", response_model=DocumentResponse, status_code=201)
def create_document(document: DocumentCreate):
    """
    Create a new document.

    - **project_id**: Project ID (required)
    - **doc_type**: Document type (ba/ta/tc, required)
    - **title**: Document title (required)
    - **content_json**: Document content as JSON (optional)
    """
    # Validate project exists
    if document.project_id is not None:
        project = database_service.get_project_by_id(document.project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project with ID {document.project_id} not found"
            )

    try:
        doc_id = database_service.create_document(
            project_id=document.project_id,
            doc_type=document.doc_type,
            title=document.title,
            content_json=document.content_json or {}
        )

        created_doc = database_service.get_document_by_id(doc_id)
        if not created_doc:
            raise HTTPException(status_code=500, detail="Failed to retrieve created document")

        return created_doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int):
    """
    Get a specific document by ID with its latest content.

    - **document_id**: Document ID
    """
    document = database_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found"
        )

    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, document: DocumentUpdate):
    """
    Update a document's metadata (not content - use versions for content changes).

    - **document_id**: Document ID
    - **project_id**: New project ID (optional)
    - **doc_type**: New document type (optional)
    - **title**: New title (optional)
    """
    existing_doc = database_service.get_document_by_id(document_id)
    if not existing_doc:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found"
        )

    update_data = {}
    if document.project_id is not None:
        # Validate new project exists
        project = database_service.get_project_by_id(document.project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project with ID {document.project_id} not found"
            )
        update_data['project_id'] = document.project_id

    if document.doc_type is not None:
        update_data['doc_type'] = document.doc_type
    if document.title is not None:
        update_data['title'] = document.title
    if document.content_json is not None:
        # Create new version if content changes
        database_service.create_document_version(
            doc_id=document_id,
            content_json=document.content_json,
            change_summary="Content updated via API"
        )

    if update_data:
        try:
            database_service.update_document(document_id, **update_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    updated_doc = database_service.get_document_by_id(document_id)
    return updated_doc


@router.delete("/{document_id}", response_model=SuccessResponse)
def delete_document(document_id: int):
    """
    Soft delete a document (sets status to 'deleted').

    - **document_id**: Document ID
    """
    existing_doc = database_service.get_document_by_id(document_id)
    if not existing_doc:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found"
        )

    database_service.delete_document(document_id)

    return SuccessResponse(
        message=f"Document '{existing_doc['title']}' deleted successfully",
        data={"document_id": document_id}
    )


@router.get("/{document_id}/versions", response_model=list[DocumentVersion])
def get_document_versions(document_id: int):
    """
    Get all versions of a document.

    - **document_id**: Document ID
    """
    # Validate document exists
    document = database_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found"
        )

    versions = database_service.get_document_versions(document_id)
    return versions
