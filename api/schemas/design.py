"""
Design Compliance API Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CheckType(str, Enum):
    """Available compliance check types"""
    TRACEABILITY = "Gereksinim ↔ Tasarım Eşleştirme (Traceability)"
    MISSING_FEATURES = "Eksik/Fazla Özellik Tespiti"
    ACCEPTANCE_CRITERIA = "Acceptance Criteria Karşılaştırma"
    UI_TEXT = "UI Text/Label Doğrulama"


class DesignComplianceRequest(BaseModel):
    """Request schema for design compliance analysis"""
    ba_document: str = Field(..., description="BA document text content")
    project_name: Optional[str] = Field(None, description="Project name")
    checks: List[CheckType] = Field(
        default=[CheckType.TRACEABILITY, CheckType.MISSING_FEATURES],
        description="List of compliance checks to perform"
    )
    extra_context: Optional[str] = Field(None, description="Additional context or instructions")
    model: str = Field(default="gemini-2.0-flash-exp", description="Vision model to use")


class AgentStep(str, Enum):
    """Agent execution steps"""
    REQUIREMENTS = "requirements"
    SCREEN_ANALYSIS = "screen_analysis"
    COMPLIANCE = "compliance"
    REPORT = "report"


class AgentOutput(BaseModel):
    """Output from a single agent step"""
    step: AgentStep
    content: str
    status: str = Field(default="completed")


class DesignComplianceResponse(BaseModel):
    """Response schema for design compliance analysis"""
    project_name: Optional[str]
    num_screens: int
    checks: List[str]
    requirements_output: str
    screen_output: str
    compliance_output: str
    report_output: str
    timestamp: str
    full_report: str = Field(..., description="Complete markdown report")


class DesignComplianceStreamEvent(BaseModel):
    """Server-sent event for streaming progress"""
    event_type: str = Field(..., description="Event type: progress, agent_output, complete, error")
    step: Optional[AgentStep] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str] = None
    data: Optional[dict] = None
