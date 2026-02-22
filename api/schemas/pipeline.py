"""
Pipeline Schemas — Pydantic models for BRD pipeline
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, Any, Dict
from datetime import datetime


class PipelineStartRequest(BaseModel):
    """Pipeline start request"""
    project_id: int
    project_name: str
    brd_content: str  # Changed to str - accepts plain text BRD
    stages: list[Literal["ba", "ta", "tc"]] = Field(default=["ba", "ta", "tc"])
    figma_url: Optional[str] = None


class PipelineStageStatus(BaseModel):
    """Pipeline stage status"""
    stage: str
    status: Literal["pending", "running", "completed", "failed", "waiting_approval"]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class PipelineStatus(BaseModel):
    """Pipeline status response"""
    run_id: int
    status: Literal["started", "running", "completed", "failed", "waiting_approval"]
    current_stage: Optional[str] = None
    progress_pct: int = Field(..., ge=0, le=100)
    stages_completed: list[str] = []
    stages: list[PipelineStageStatus] = []
    error: Optional[str] = None
    logs: list[str] = []
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PipelineStartResponse(BaseModel):
    """Pipeline start response"""
    pipeline_run_id: int
    status: str = "started"


class PipelineStageApproval(BaseModel):
    """Stage approval request"""
    run_id: int
    stage: Literal["ba", "ta", "tc"]
    approved_content: Optional[Dict[str, Any]] = None  # User-edited content
    skip_qa: bool = False


class PipelineCheckpoint(BaseModel):
    """Pipeline checkpoint data"""
    project_name: str
    stage: str
    data: Dict[str, Any]
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
