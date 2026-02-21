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
    document_id: Optional[int] = None
    content_json: Optional[dict] = None
    reference_document_id: Optional[int] = None


class EvaluationResponse(BaseModel):
    """Evaluation response schema"""
    score: int = Field(..., ge=0, le=100)
    criteria_scores: list[CriteriaScore]
    passed: bool
    feedback: str
    model_used: str
