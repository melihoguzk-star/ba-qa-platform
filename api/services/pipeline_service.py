"""
Pipeline Service — BRD pipeline orchestration
"""
from typing import Dict, Any, List
from api.services import database_service
import time


async def start_pipeline(
    project_id: int,
    brd_content: Dict[str, Any],
    stages: List[str]
) -> int:
    """
    Start BRD pipeline execution in background.

    Args:
        project_id: Project ID
        brd_content: BRD document content
        stages: List of stages to execute (ba, ta, tc)

    Returns:
        Pipeline run ID
    """
    # Create pipeline run record
    project = database_service.get_project_by_id(project_id)
    project_name = project['name'] if project else f"Project {project_id}"

    run_id = database_service.create_pipeline_run(
        project_name=project_name,
        jira_key="",
        priority="normal",
        brd_filename=f"api_upload_{int(time.time())}"
    )

    # Update status to running
    database_service.update_pipeline_run(
        run_id,
        status="running",
        current_stage=stages[0] if stages else "ba"
    )

    return run_id


async def execute_pipeline(
    run_id: int,
    brd_content: Dict[str, Any],
    stages: List[str]
):
    """
    Execute pipeline stages sequentially.
    This runs as a background task.

    Args:
        run_id: Pipeline run ID
        brd_content: BRD document content
        stages: List of stages to execute
    """
    from pipeline.brd.orchestrator import run_full_pipeline
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting pipeline execution for run_id={run_id}, stages={stages}")

        # Import BRD pipeline orchestrator
        # Note: This is a long-running operation
        start_time = time.time()

        # Execute pipeline using existing orchestrator
        result = run_full_pipeline(
            brd_content=brd_content,
            project_name=f"Pipeline Run {run_id}",
            jira_key="",
            priority="normal",
            checkpoint_dir=f"data/checkpoints/run_{run_id}",
            enable_ba=("ba" in stages),
            enable_ta=("ta" in stages),
            enable_tc=("tc" in stages)
        )

        # Calculate total time
        total_time = int(time.time() - start_time)

        # Update pipeline run with results
        database_service.update_pipeline_run(
            run_id,
            status="completed",
            current_stage="completed",
            ba_score=result.get("ba_score", 0),
            ta_score=result.get("ta_score", 0),
            tc_score=result.get("tc_score", 0),
            total_time_sec=total_time
        )

        logger.info(f"Pipeline run {run_id} completed successfully in {total_time}s")

    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}")

        # Update status to failed
        database_service.update_pipeline_run(
            run_id,
            status="failed",
            current_stage="error"
        )


def get_pipeline_status(run_id: int) -> Dict[str, Any]:
    """
    Get pipeline run status.

    Args:
        run_id: Pipeline run ID

    Returns:
        Pipeline status information
    """
    # Get pipeline run from database
    runs = database_service.get_recent_pipeline_runs(limit=1000)
    run = next((r for r in runs if r['id'] == run_id), None)

    if not run:
        return {
            "run_id": run_id,
            "status": "not_found",
            "error": "Pipeline run not found"
        }

    # Get outputs
    outputs = database_service.get_pipeline_run_outputs(run_id)

    # Calculate progress
    total_stages = 3  # ba, ta, tc
    completed_stages = len([o for o in outputs if o.get('stage') in ['ba', 'ta', 'tc']])
    progress_pct = int((completed_stages / total_stages) * 100) if total_stages > 0 else 0

    # Determine stage statuses
    stages = []
    for stage_name in ['ba', 'ta', 'tc']:
        stage_outputs = [o for o in outputs if o.get('stage') == stage_name]

        if stage_outputs:
            stages.append({
                "stage": stage_name,
                "status": "completed",
                "started_at": stage_outputs[0].get('created_at'),
                "completed_at": stage_outputs[-1].get('created_at'),
                "error": None
            })
        elif run['current_stage'] == stage_name:
            stages.append({
                "stage": stage_name,
                "status": "running",
                "started_at": run.get('created_at'),
                "completed_at": None,
                "error": None
            })
        else:
            stages.append({
                "stage": stage_name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "error": None
            })

    return {
        "run_id": run_id,
        "status": run['status'],
        "current_stage": run.get('current_stage'),
        "progress_pct": progress_pct,
        "stages_completed": [s['stage'] for s in stages if s['status'] == 'completed'],
        "stages": stages,
        "error": None if run['status'] != 'failed' else "Pipeline execution failed",
        "created_at": run.get('created_at'),
        "updated_at": run.get('created_at')  # SQLite doesn't auto-update
    }
