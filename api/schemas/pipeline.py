"""
Pipeline Schemas — Pydantic models for BRD pipeline
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class PipelineStartRequest(BaseModel):
    """Pipeline start request"""
    project_id: int
    brd_content: dict
    stages: list[Literal["ba", "ta", "tc"]] = Field(default=["ba", "ta", "tc"])


class PipelineStageStatus(BaseModel):
    """Pipeline stage status"""
    stage: str
    status: Literal["pending", "running", "completed", "failed"]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class PipelineStatus(BaseModel):
    """Pipeline status response"""
    run_id: int
    status: Literal["started", "running", "completed", "failed"]
    current_stage: Optional[str] = None
    progress_pct: int = Field(..., ge=0, le=100)
    stages_completed: list[str] = []
    stages: list[PipelineStageStatus] = []
    error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PipelineStartResponse(BaseModel):
    """Pipeline start response"""
    pipeline_run_id: int
    status: str = "started"
