"""
Pipeline Service — BRD pipeline orchestration
"""
from typing import Dict, Any, List
import api.db as database_service
import time
from utils.config import SONNET_MODEL, GEMINI_MODEL


async def start_pipeline(
    project_id: int,
    project_name: str,
    brd_content: str,
    stages: List[str],
    figma_url: str = None
) -> int:
    """
    Start BRD pipeline (step-by-step mode).

    Saves BRD content and creates pipeline run, then waits for user to trigger first stage.

    Args:
        project_id: Project ID
        project_name: Project name
        brd_content: BRD document content (plain text)
        stages: List of stages to execute (ba, ta, tc)
        figma_url: Optional Figma design URL

    Returns:
        Pipeline run ID
    """
    from pipeline.brd.checkpoint import save_checkpoint

    # Save BRD content as checkpoint
    save_checkpoint(project_name, 'brd_content', {'content': brd_content})

    # Save Figma URL if provided
    if figma_url:
        save_checkpoint(project_name, 'figma_url', {'url': figma_url})

    # Save requested stages
    save_checkpoint(project_name, 'stages', {'stages': stages})

    # Create pipeline run record
    run_id = database_service.create_pipeline_run(
        project_name=project_name,
        jira_key="",
        priority="normal",
        brd_filename=f"api_upload_{int(time.time())}"
    )

    # Set initial state - waiting for user to start BA generation
    database_service.update_pipeline_run(
        run_id,
        status="waiting_approval",
        current_stage="ba_gen"
    )

    return run_id


async def execute_pipeline(
    run_id: int,
    project_name: str,
    brd_content: str,
    stages: List[str],
    figma_url: str = None
):
    """
    Execute pipeline stages sequentially.
    This runs as a background task.

    Args:
        run_id: Pipeline run ID
        project_name: Project name
        brd_content: BRD document content (plain text)
        stages: List of stages to execute
        figma_url: Optional Figma design URL
    """
    import logging
    from api.config import get_settings

    # Check if mock mode is enabled
    settings = get_settings()
    mock_mode = settings.mock_mode

    if mock_mode:
        from pipeline.brd.orchestrator_mock import (
            generate_ba_mock as generate_ba,
            generate_ta_mock as generate_ta,
            generate_tc_mock as generate_tc,
            evaluate_ba_qa_mock as evaluate_ba_qa,
            evaluate_ta_qa_mock as evaluate_ta_qa,
            evaluate_tc_qa_mock as evaluate_tc_qa
        )
    else:
        from pipeline.brd.orchestrator import generate_ba, generate_ta, generate_tc
        from pipeline.brd.orchestrator import evaluate_ba_qa, evaluate_ta_qa, evaluate_tc_qa

    logger = logging.getLogger(__name__)

    try:
        mode_label = "[MOCK]" if mock_mode else "[LIVE]"
        logger.info(f"{mode_label} Starting pipeline execution for run_id={run_id}, stages={stages}")

        start_time = time.time()
        results = {}

        # Get API keys from settings
        anthropic_key = settings.anthropic_api_key
        gemini_key = settings.gemini_api_key

        # Create log callback
        def log_callback(message):
            logger.info(f"Run {run_id}: {message}")

        # Execute BA generation if requested
        if "ba" in stages:
            logger.info(f"Run {run_id}: Generating BA...")
            database_service.update_pipeline_run(run_id, current_stage="ba_generation")

            ba_result = generate_ba(
                brd_text=brd_content,
                project_name=project_name,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                model=SONNET_MODEL
            )
            results["ba"] = ba_result

            # QA evaluation
            logger.info(f"Run {run_id}: Evaluating BA...")
            database_service.update_pipeline_run(run_id, current_stage="ba_qa")
            qa_result = evaluate_ba_qa(
                ba_content=ba_result,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                model=GEMINI_MODEL
            )
            results["ba_qa"] = qa_result
            database_service.update_pipeline_run(run_id, ba_score=qa_result.get("score", 0))

        # Execute TA generation if requested
        if "ta" in stages:
            logger.info(f"Run {run_id}: Generating TA...")
            database_service.update_pipeline_run(run_id, current_stage="ta_generation")

            ba_data = results.get("ba", {})
            ta_result = generate_ta(
                brd_text=brd_content,
                ba_content=ba_data,
                project_name=project_name,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                model=SONNET_MODEL
            )
            results["ta"] = ta_result

            # QA evaluation
            logger.info(f"Run {run_id}: Evaluating TA...")
            database_service.update_pipeline_run(run_id, current_stage="ta_qa")
            qa_result = evaluate_ta_qa(
                ta_content=ta_result,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                model=GEMINI_MODEL
            )
            results["ta_qa"] = qa_result
            database_service.update_pipeline_run(run_id, ta_score=qa_result.get("score", 0))

        # Execute TC generation if requested
        if "tc" in stages:
            logger.info(f"Run {run_id}: Generating TC...")
            database_service.update_pipeline_run(run_id, current_stage="tc_generation")

            ba_data = results.get("ba", {})
            ta_data = results.get("ta", {})

            # Get Figma screen analysis if URL provided
            screen_analysis = ""
            if figma_url:
                logger.info(f"Run {run_id}: Analyzing Figma designs...")
                # This would call Figma analysis - placeholder for now
                screen_analysis = f"Figma URL: {figma_url}"

            tc_result = generate_tc(
                ba_content=ba_data,
                ta_content=ta_data,
                project_name=project_name,
                jira_key="",
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                screen_analysis=screen_analysis,
                model=SONNET_MODEL
            )
            results["tc"] = tc_result

            # QA evaluation
            logger.info(f"Run {run_id}: Evaluating TC...")
            database_service.update_pipeline_run(run_id, current_stage="tc_qa")
            qa_result = evaluate_tc_qa(
                tc_content=tc_result,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                model=GEMINI_MODEL
            )
            results["tc_qa"] = qa_result
            database_service.update_pipeline_run(run_id, tc_score=qa_result.get("score", 0))

        # Calculate total time
        total_time = int(time.time() - start_time)

        # Save results as outputs
        for stage in stages:
            if stage in results:
                database_service.create_pipeline_output(
                    run_id=run_id,
                    stage=stage,
                    output_json=results[stage]
                )

        # Update pipeline run with completion
        database_service.update_pipeline_run(
            run_id,
            status="completed",
            current_stage="completed",
            total_time_sec=total_time
        )

        logger.info(f"Pipeline run {run_id} completed successfully in {total_time}s")

    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}", exc_info=True)

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

    # Calculate progress based on current stage
    stage_progress = {
        "ba_generation": 14,
        "ba_qa": 28,
        "ta_generation": 42,
        "ta_qa": 57,
        "tc_generation": 71,
        "tc_qa": 85,
        "completed": 100,
        "error": 0
    }
    progress_pct = stage_progress.get(run.get('current_stage', 'ba_generation'), 0)

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
        elif run.get('current_stage', '').startswith(stage_name):
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

    # Generate logs based on current progress
    logs = []
    logs.append(f"[{run.get('created_at')}] Pipeline started")

    for stage in stages:
        if stage['status'] == 'completed':
            logs.append(f"✓ {stage['stage'].upper()} generation completed")
            logs.append(f"✓ {stage['stage'].upper()} QA evaluation completed")
        elif stage['status'] == 'running':
            logs.append(f"⏳ {stage['stage'].upper()} in progress...")

    if run['status'] == 'completed':
        logs.append(f"✓ Pipeline completed successfully")
    elif run['status'] == 'failed':
        logs.append(f"✗ Pipeline failed")

    return {
        "run_id": run_id,
        "status": run['status'],
        "current_stage": run.get('current_stage'),
        "progress_pct": progress_pct,
        "stages_completed": [s['stage'] for s in stages if s['status'] == 'completed'],
        "stages": stages,
        "error": None if run['status'] != 'failed' else "Pipeline execution failed",
        "logs": logs,
        "created_at": run.get('created_at'),
        "updated_at": run.get('created_at')  # SQLite doesn't auto-update
    }


def get_pipeline_results(run_id: int) -> Dict[str, Any]:
    """
    Get pipeline results (generated documents).

    Args:
        run_id: Pipeline run ID

    Returns:
        Dictionary with BA, TA, TC documents and QA scores
    """
    outputs = database_service.get_pipeline_run_outputs(run_id)

    if not outputs:
        return None

    results = {}
    for output in outputs:
        stage = output.get('stage')
        if stage in ['ba', 'ta', 'tc']:
            results[stage] = output.get('output_json', {})

    # Get QA scores from pipeline run
    runs = database_service.get_recent_pipeline_runs(limit=1000)
    run = next((r for r in runs if r['id'] == run_id), None)

    if run:
        results['scores'] = {
            'ba': run.get('ba_score', 0),
            'ta': run.get('ta_score', 0),
            'tc': run.get('tc_score', 0)
        }

    return results


def execute_single_stage(run_id: int, stage: str, feedback: str = ""):
    """
    Execute a single pipeline stage (ba_gen, ta_gen, tc_gen).

    This is for step-by-step execution with user approval.

    Note: This is a synchronous function to work properly with FastAPI BackgroundTasks.

    Args:
        run_id: Pipeline run ID
        stage: Stage to execute (ba_gen, ta_gen, tc_gen)
        feedback: Optional QA feedback for regeneration
    """
    import logging
    from api.config import get_settings

    # Check if mock mode is enabled
    settings = get_settings()
    mock_mode = settings.mock_mode

    if mock_mode:
        from pipeline.brd.orchestrator_mock import (
            generate_ba_mock as generate_ba,
            generate_ta_mock as generate_ta,
            generate_tc_mock as generate_tc
        )
    else:
        from pipeline.brd.orchestrator import generate_ba, generate_ta, generate_tc

    logger = logging.getLogger(__name__)

    try:
        mode_label = "[MOCK]" if mock_mode else "[LIVE]"
        logger.info(f"{mode_label} Run {run_id}: Executing stage {stage}")

        # Get pipeline run
        runs = database_service.get_recent_pipeline_runs(limit=1000)
        run = next((r for r in runs if r['id'] == run_id), None)

        if not run:
            logger.error(f"Pipeline run {run_id} not found")
            return

        project_name = run['project_name']

        # Get BRD content from checkpoint
        from pipeline.brd.checkpoint import load_checkpoint
        brd_checkpoint = load_checkpoint(project_name, 'brd_content')
        brd_content = brd_checkpoint.get('content', '') if brd_checkpoint else ''

        # Get API keys
        anthropic_key = settings.anthropic_api_key
        gemini_key = settings.gemini_api_key

        # Create log callback
        def log_callback(message):
            logger.info(f"Run {run_id}: {message}")

        logger.info(f"Run {run_id}: Executing stage {stage}")
        database_service.update_pipeline_run(run_id, current_stage=stage, status='running')

        result = None

        if stage == 'ba_gen':
            result = generate_ba(
                brd_text=brd_content,
                project_name=project_name,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                previous_feedback=feedback,
                model=SONNET_MODEL
            )
        elif stage == 'ta_gen':
            # Load BA from checkpoint
            ba_checkpoint = load_checkpoint(project_name, 'ba_gen')
            ba_content = ba_checkpoint if ba_checkpoint else {}

            result = generate_ta(
                brd_text=brd_content,
                ba_content=ba_content,
                project_name=project_name,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                previous_feedback=feedback,
                model=SONNET_MODEL
            )
        elif stage == 'tc_gen':
            # Load BA and TA from checkpoints
            ba_checkpoint = load_checkpoint(project_name, 'ba_gen')
            ta_checkpoint = load_checkpoint(project_name, 'ta_gen')

            ba_content = ba_checkpoint if ba_checkpoint else {}
            ta_content = ta_checkpoint if ta_checkpoint else {}

            # Check for Figma URL
            figma_checkpoint = load_checkpoint(project_name, 'figma_url')
            screen_analysis = ""
            if figma_checkpoint and figma_checkpoint.get('url'):
                screen_analysis = f"Figma URL: {figma_checkpoint['url']}"

            result = generate_tc(
                ba_content=ba_content,
                ta_content=ta_content,
                project_name=project_name,
                jira_key="",
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                log=log_callback,
                screen_analysis=screen_analysis,
                previous_feedback=feedback,
                model=SONNET_MODEL
            )

        # Save result to checkpoint for review
        from pipeline.brd.checkpoint import save_checkpoint
        save_checkpoint(project_name, stage, result)
        logger.info(f"Run {run_id}: Checkpoint saved for stage {stage}")

        # Stage completed - wait for user review
        # Convert ba_gen -> ba_review, ta_gen -> ta_review, tc_gen -> tc_review
        review_stage = stage.replace('_gen', '_review')
        database_service.update_pipeline_run(
            run_id,
            current_stage=review_stage,
            status='waiting_approval'
        )

        logger.info(f"Run {run_id}: Stage {stage} completed, waiting for user review")

    except Exception as e:
        logger.error(f"Stage {stage} execution failed: {e}", exc_info=True)
        database_service.update_pipeline_run(
            run_id,
            status='failed',
            current_stage='error'
        )


async def evaluate_stage_qa(
    run_id: int,
    stage: str,
    content: Dict[str, Any],
    force_pass: bool = False
) -> Dict[str, Any]:
    """
    Evaluate QA for a stage.

    Args:
        run_id: Pipeline run ID
        stage: QA stage (ba_qa, ta_qa, tc_qa)
        content: User-edited content to evaluate
        force_pass: Force pass QA regardless of score

    Returns:
        QA evaluation result
    """
    import logging
    from api.config import get_settings

    # Check if mock mode is enabled
    settings = get_settings()
    mock_mode = settings.mock_mode

    if mock_mode:
        from pipeline.brd.orchestrator_mock import (
            evaluate_ba_qa_mock as evaluate_ba_qa,
            evaluate_ta_qa_mock as evaluate_ta_qa,
            evaluate_tc_qa_mock as evaluate_tc_qa
        )
    else:
        from pipeline.brd.orchestrator import evaluate_ba_qa, evaluate_ta_qa, evaluate_tc_qa

    logger = logging.getLogger(__name__)

    try:
        mode_label = "[MOCK]" if mock_mode else "[LIVE]"
        logger.info(f"{mode_label} Run {run_id}: Evaluating QA for stage {stage}")

        # Get pipeline run
        runs = database_service.get_recent_pipeline_runs(limit=1000)
        run = next((r for r in runs if r['id'] == run_id), None)

        if not run:
            raise Exception(f"Pipeline run {run_id} not found")

        project_name = run['project_name']
        anthropic_key = settings.anthropic_api_key
        gemini_key = settings.gemini_api_key

        # Create log callback
        def log_callback(message):
            logger.info(f"Run {run_id}: {message}")

        logger.info(f"Run {run_id}: Evaluating {stage}, force_pass={force_pass}")
        database_service.update_pipeline_run(run_id, current_stage=stage, status='running')

        qa_result = {}

        if force_pass:
            qa_result = {
                "score": 100,
                "assessment": "Force passed by user",
                "suggestions": [],
                "passed": True
            }
        else:
            if stage == 'ba_qa':
                qa_result = evaluate_ba_qa(
                    ba_content=content,
                    anthropic_key=anthropic_key,
                    gemini_key=gemini_key,
                    log=log_callback,
                    model=GEMINI_MODEL
                )
            elif stage == 'ta_qa':
                qa_result = evaluate_ta_qa(
                    ta_content=content,
                    anthropic_key=anthropic_key,
                    gemini_key=gemini_key,
                    log=log_callback,
                    model=GEMINI_MODEL
                )
            elif stage == 'tc_qa':
                qa_result = evaluate_tc_qa(
                    tc_content=content,
                    anthropic_key=anthropic_key,
                    gemini_key=gemini_key,
                    log=log_callback,
                    model=GEMINI_MODEL
                )

        # Update score
        score = qa_result.get('score', 0)
        stage_prefix = stage.replace('_qa', '')

        database_service.update_pipeline_run(
            run_id,
            **{f"{stage_prefix}_score": score}
        )

        # Determine if passed (60+ threshold)
        passed = score >= 60 or force_pass
        qa_result['passed'] = passed

        if passed:
            # Save to outputs
            database_service.create_pipeline_output(
                run_id=run_id,
                stage=stage_prefix,
                output_json=content
            )

            # Only transition to next stage if force_pass (user explicitly approved)
            # Otherwise, stay on QA stage to show results
            if force_pass:
                # Update to next stage or completed
                next_stage_map = {
                    'ba_qa': 'ta_gen',
                    'ta_qa': 'figma_upload',
                    'tc_qa': 'completed'
                }

                next_stage = next_stage_map.get(stage, 'completed')
                next_status = 'completed' if next_stage == 'completed' else 'waiting_approval'

                database_service.update_pipeline_run(
                    run_id,
                    current_stage=next_stage,
                    status=next_status
                )
                logger.info(f"Run {run_id}: Force pass - transitioning to {next_stage}")
            else:
                # Stay on QA stage, just mark as evaluated
                logger.info(f"Run {run_id}: QA evaluated, staying on {stage} for user review")

        logger.info(f"Run {run_id}: QA {stage} completed, score={score}, passed={passed}")

        return qa_result

    except Exception as e:
        logger.error(f"QA evaluation failed: {e}", exc_info=True)
        database_service.update_pipeline_run(
            run_id,
            status='failed',
            current_stage='error'
        )
        raise


def get_checkpoint(project_name: str, stage: str) -> Dict[str, Any]:
    """Get checkpoint data for a stage"""
    from pipeline.brd.checkpoint import load_checkpoint
    return load_checkpoint(project_name, stage)


def save_checkpoint(project_name: str, stage: str, data: Dict[str, Any]):
    """Save checkpoint data"""
    from pipeline.brd.checkpoint import save_checkpoint
    save_checkpoint(project_name, stage, data)
