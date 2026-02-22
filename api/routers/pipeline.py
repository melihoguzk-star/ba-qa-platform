"""
Pipeline Router — BRD pipeline orchestration endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from api.schemas.pipeline import (
    PipelineStartRequest,
    PipelineStartResponse,
    PipelineStatus,
    PipelineStageApproval,
    PipelineCheckpoint
)
from api.services import pipeline_service
import api.db as database_service
from api.tasks.background import execute_pipeline_task
from pathlib import Path
import tempfile

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
            project_name=request.project_name,
            brd_content=request.brd_content,
            stages=request.stages,
            figma_url=request.figma_url
        )

        # Step-by-step workflow: Do NOT auto-execute
        # User will manually trigger each stage via /execute-stage endpoint
        # Commented out automatic execution:
        # background_tasks.add_task(
        #     execute_pipeline_task,
        #     run_id=run_id,
        #     project_name=request.project_name,
        #     brd_content=request.brd_content,
        #     stages=request.stages,
        #     figma_url=request.figma_url
        # )

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


@router.get("/{run_id}/results")
async def get_pipeline_results(run_id: int):
    """
    Get pipeline results (generated documents).

    Returns the generated BA, TA, TC documents if pipeline completed successfully.
    """
    try:
        results = pipeline_service.get_pipeline_results(run_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No results found for pipeline run {run_id}"
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline results: {str(e)}"
        )


@router.post("/{run_id}/execute-stage")
async def execute_stage(
    run_id: int,
    stage: str,
    background_tasks: BackgroundTasks,
    feedback: str = ""
):
    """
    Execute a single pipeline stage (ba_gen, ta_gen, tc_gen).

    This enables step-by-step execution with user approval between stages.
    Optionally accepts feedback from QA evaluation for regeneration.
    """
    try:
        # Validate stage
        valid_stages = ['ba_gen', 'ta_gen', 'tc_gen']
        if stage not in valid_stages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stage. Must be one of: {valid_stages}"
            )

        # Execute stage in background using threading
        import threading
        thread = threading.Thread(
            target=pipeline_service.execute_single_stage,
            args=(run_id, stage, feedback),
            daemon=True
        )
        thread.start()

        return {"status": "started", "stage": stage, "has_feedback": bool(feedback)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute stage: {str(e)}"
        )


@router.post("/{run_id}/evaluate-qa")
async def evaluate_qa(
    run_id: int,
    stage: str,
    content: dict,
    force_pass: bool = False
):
    """
    Evaluate QA for a stage (ba_qa, ta_qa, tc_qa).

    User can edit content before QA or force pass.
    """
    try:
        # Validate stage
        valid_stages = ['ba_qa', 'ta_qa', 'tc_qa']
        if stage not in valid_stages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stage. Must be one of: {valid_stages}"
            )

        result = await pipeline_service.evaluate_stage_qa(
            run_id=run_id,
            stage=stage,
            content=content,
            force_pass=force_pass
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate QA: {str(e)}"
        )


@router.get("/{run_id}/checkpoint/{stage}")
async def get_checkpoint(run_id: int, stage: str):
    """
    Get checkpoint data for a stage.

    Returns generated content for user review/editing.
    """
    try:
        # Get pipeline run to get project name
        runs = database_service.get_recent_pipeline_runs(limit=1000)
        run = next((r for r in runs if r['id'] == run_id), None)

        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run {run_id} not found"
            )

        checkpoint = pipeline_service.get_checkpoint(
            project_name=run['project_name'],
            stage=stage
        )

        if not checkpoint:
            raise HTTPException(
                status_code=404,
                detail=f"No checkpoint found for stage {stage}"
            )

        return checkpoint

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get checkpoint: {str(e)}"
        )


@router.post("/{run_id}/checkpoint/{stage}")
async def save_checkpoint(run_id: int, stage: str, data: dict):
    """
    Save user-edited checkpoint data.

    Allows user to edit generated content before QA.
    """
    try:
        # Get pipeline run to get project name
        runs = database_service.get_recent_pipeline_runs(limit=1000)
        run = next((r for r in runs if r['id'] == run_id), None)

        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline run {run_id} not found"
            )

        pipeline_service.save_checkpoint(
            project_name=run['project_name'],
            stage=stage,
            data=data
        )

        return {"status": "saved"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save checkpoint: {str(e)}"
        )
