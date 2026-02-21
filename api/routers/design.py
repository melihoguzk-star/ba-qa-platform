"""
Design Compliance API Router
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json

from api.schemas.design import (
    DesignComplianceResponse,
    CheckType,
    DesignComplianceStreamEvent
)
from api.services.design_service import (
    analyze_design_compliance,
    analyze_design_compliance_stream
)

router = APIRouter(prefix="/design", tags=["Design Compliance"])


@router.post("/analyze", response_model=DesignComplianceResponse)
async def analyze_design(
    ba_document: str = Form(..., description="BA document text content"),
    project_name: Optional[str] = Form(None, description="Project name"),
    checks: str = Form(
        default=f"{CheckType.TRACEABILITY.value},{CheckType.MISSING_FEATURES.value}",
        description="Comma-separated list of checks"
    ),
    extra_context: Optional[str] = Form(None, description="Additional context"),
    model: str = Form(default="gemini-2.0-flash-exp", description="Vision model to use"),
    images: List[UploadFile] = File(..., description="Design screen images")
) -> DesignComplianceResponse:
    """
    Perform design compliance analysis using 4-agent vision AI pipeline.

    Analyzes uploaded design screens against BA document requirements.
    Returns detailed compliance report with all agent outputs.
    """
    try:
        # Validate inputs
        if not images:
            raise HTTPException(status_code=400, detail="At least one image is required")

        if len(images) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 images allowed")

        # Parse checks
        checks_list = [check.strip() for check in checks.split(",") if check.strip()]

        # Read image files
        image_files = []
        for img in images:
            # Validate image type
            if not img.content_type or not img.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {img.filename}. Only images allowed."
                )

            # Read bytes
            image_bytes = await img.read()
            image_files.append(image_bytes)

        # Perform analysis
        result = analyze_design_compliance(
            ba_document=ba_document,
            image_files=image_files,
            project_name=project_name,
            checks=checks_list,
            extra_context=extra_context,
            model=model
        )

        return DesignComplianceResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-stream")
async def analyze_design_stream(
    ba_document: str = Form(..., description="BA document text content"),
    project_name: Optional[str] = Form(None, description="Project name"),
    checks: str = Form(
        default=f"{CheckType.TRACEABILITY.value},{CheckType.MISSING_FEATURES.value}",
        description="Comma-separated list of checks"
    ),
    extra_context: Optional[str] = Form(None, description="Additional context"),
    model: str = Form(default="gemini-2.0-flash-exp", description="Vision model to use"),
    images: List[UploadFile] = File(..., description="Design screen images")
):
    """
    Streaming version of design compliance analysis.

    Returns Server-Sent Events (SSE) with progress updates as each agent completes.
    Enables real-time UI updates during long-running analysis.
    """
    try:
        # Validate inputs
        if not images:
            raise HTTPException(status_code=400, detail="At least one image is required")

        if len(images) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 images allowed")

        # Parse checks
        checks_list = [check.strip() for check in checks.split(",") if check.strip()]

        # Read image files
        image_files = []
        for img in images:
            if not img.content_type or not img.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {img.filename}. Only images allowed."
                )

            image_bytes = await img.read()
            image_files.append(image_bytes)

        # Create SSE generator
        async def event_generator():
            """Generate SSE events from analysis stream"""
            try:
                async for event in analyze_design_compliance_stream(
                    ba_document=ba_document,
                    image_files=image_files,
                    project_name=project_name,
                    checks=checks_list,
                    extra_context=extra_context,
                    model=model
                ):
                    # Validate and serialize event
                    event_obj = DesignComplianceStreamEvent(**event)
                    event_json = event_obj.model_dump_json()

                    # SSE format: data: {json}\n\n
                    yield f"data: {event_json}\n\n"

            except Exception as e:
                # Send error event
                error_event = DesignComplianceStreamEvent(
                    event_type="error",
                    message=str(e),
                    progress=0
                )
                yield f"data: {error_event.model_dump_json()}\n\n"

        # Return streaming response
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream setup failed: {str(e)}")


@router.get("/check-types")
async def get_check_types():
    """
    Get available compliance check types.

    Returns list of all supported compliance checks.
    """
    return {
        "check_types": [
            {"value": check.value, "name": check.name}
            for check in CheckType
        ]
    }


@router.get("/models")
async def get_supported_models():
    """
    Get list of supported vision models.

    Returns available models for design analysis.
    """
    return {
        "models": [
            {
                "id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash",
                "provider": "Google",
                "recommended": True
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "provider": "Google",
                "recommended": False
            },
            {
                "id": "gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "provider": "Google",
                "recommended": False
            },
            {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "recommended": False
            },
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "recommended": False
            }
        ]
    }
