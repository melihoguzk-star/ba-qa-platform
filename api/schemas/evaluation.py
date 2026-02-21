"""
Evaluation Schemas — Pydantic models for BA/TC evaluation
"""
from pydantic import BaseModel, Field
from typing import Optional


class CriteriaScore(BaseModel):
    """Individual criteria score"""
    criterion: str
    score: int = Field(..., ge=0, le=100)
    feedback: str
    passed: bool


class EvaluationRequest(BaseModel):
    """Evaluation request schema"""
    # Option 1: Evaluate from database document
    document_id: Optional[int] = None

    # Option 2: Evaluate direct content
    content_json: Optional[dict] = None

    # Option 3: Evaluate from JIRA task (auto-fetch Google Doc)
    # Uses JIRA credentials from environment variables
    jira_task_key: Optional[str] = None

    # Optional reference document
    reference_document_id: Optional[int] = None

    # Model selection (optional, defaults to Gemini 2.5 Flash)
    model: Optional[str] = "gemini-2.5-flash"


class EvaluationResponse(BaseModel):
    """Evaluation response schema"""
    score: int = Field(..., ge=0, le=100)
    criteria_scores: list[CriteriaScore]
    passed: bool
    feedback: str
    model_used: str
