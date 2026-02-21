"""
Document Schemas — Pydantic models for documents
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document schema"""
    project_id: Optional[int] = None
    doc_type: str = Field(..., pattern="^(brd|ba|ta|tc)$")
    title: str = Field(..., min_length=1, max_length=255)
    content_json: Optional[dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    pass


class DocumentUpdate(BaseModel):
    """Document update schema"""
    project_id: Optional[int] = None
    doc_type: Optional[str] = Field(None, pattern="^(brd|ba|ta|tc)$")
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content_json: Optional[dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """Document response schema"""
    id: int
    current_version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentVersion(BaseModel):
    """Document version schema"""
    id: int
    document_id: int
    version_number: int
    content_json: dict[str, Any]
    created_at: datetime
    created_by: Optional[str] = None
