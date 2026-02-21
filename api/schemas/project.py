"""
Project Schemas — Pydantic models for projects
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(ProjectBase):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
