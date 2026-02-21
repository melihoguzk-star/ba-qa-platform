"""
Pipeline Router — BRD pipeline orchestration endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.schemas.pipeline import PipelineStartRequest, PipelineStartResponse, PipelineStatus
from api.services import pipeline_service, database_service
from api.tasks.background import execute_pipeline_task

router = APIRouter()


@router.post("/start", response_model=PipelineStartResponse, status_code=202)
async def start_pipeline(
    request: PipelineStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start BRD pipeline execution in background.

    This is a long-running operation (2-5 minutes) that generates:
    1. BA (Business Analysis) document
    2. TA (Technical Analysis) document
    3. TC (Test Cases) document

    Each stage includes:
    - AI-powered generation
    - Quality assessment (QA)
    - Revision loop (max 3 attempts)

    The pipeline runs asynchronously. Use GET /pipeline/{run_id}/status to poll progress.

    - **project_id**: Project ID to associate documents with
    - **brd_content**: BRD document content (JSON)
    - **stages**: List of stages to execute (default: ["ba", "ta", "tc"])

    Returns:
    - **pipeline_run_id**: Use this ID to check status
    - **status**: "started"
    """
    # Validate project exists
    project = database_service.get_project_by_id(request.project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {request.project_id} not found"
        )

    try:
        # Create pipeline run and get ID
        run_id = await pipeline_service.start_pipeline(
            project_id=request.project_id,
            brd_content=request.brd_content,
            stages=request.stages
        )

        # Schedule background task for pipeline execution
        background_tasks.add_task(
            execute_pipeline_task,
            run_id=run_id,
            brd_content=request.brd_content,
            stages=request.stages
        )

        return PipelineStartResponse(
            pipeline_run_id=run_id,
            status="started"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start pipeline: {str(e)}"
        )


@router.get("/{run_id}/status", response_model=PipelineStatus)
async def get_pipeline_status(run_id: int):
    """
    Get pipeline execution status.

    Poll this endpoint every 2-5 seconds while pipeline is running.

    - **run_id**: Pipeline run ID (from start response)

    Returns:
    - **status**: "started", "running", "completed", or "failed"
    - **current_stage**: Current stage being executed (ba/ta/tc)
    - **progress_pct**: Progress percentage (0-100)
    - **stages_completed**: List of completed stages
    - **stages**: Detailed status for each stage
    - **error**: Error message if failed
    """
    try:
        status = pipeline_service.get_pipeline_status(run_id)

        if status.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run with ID {run_id} not found"
            )

        return status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline status: {str(e)}"
        )
