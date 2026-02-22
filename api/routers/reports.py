"""
Reports & Analytics API Router
"""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import csv
import io
from datetime import datetime

from data.database import get_stats, get_recent_analyses
from api.db import get_recent_pipeline_runs, get_pipeline_run_outputs

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/stats")
async def get_statistics(
    time_range: str = Query("all", description="Time range filter: 7days, 30days, 90days, all")
):
    """
    Get platform statistics.

    Returns aggregated stats by analysis type with optional time range filter.
    """
    stats = get_stats(time_range=time_range)
    return stats


@router.get("/analyses")
async def get_analyses(
    limit: int = Query(25, ge=1, le=100, description="Maximum number of records"),
    analysis_type: Optional[str] = Query(None, description="Filter by type: ba, tc, design, full"),
    time_range: str = Query("all", description="Time range filter: 7days, 30days, 90days, all")
):
    """
    Get recent analyses with filters.

    Returns list of analyses with details, scores, and reports.
    """
    analyses = get_recent_analyses(
        limit=limit,
        analysis_type=analysis_type,
        time_range=time_range
    )
    return {
        "total": len(analyses),
        "analyses": analyses
    }


@router.get("/export/csv")
async def export_analyses_csv(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    analysis_type: Optional[str] = Query(None, description="Filter by type: ba, tc, design, full"),
    time_range: str = Query("all", description="Time range filter: 7days, 30days, 90days, all")
):
    """
    Export analyses as CSV file.

    Returns CSV file with analysis summary data.
    """
    analyses = get_recent_analyses(
        limit=limit,
        analysis_type=analysis_type,
        time_range=time_range
    )

    # Create CSV in memory
    output = io.StringIO()
    fieldnames = [
        "id",
        "jira_key",
        "analysis_type",
        "genel_puan",
        "gecti_mi",
        "created_at",
        "triggered_by"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for analysis in analyses:
        writer.writerow({
            "id": analysis.get("id", ""),
            "jira_key": analysis.get("jira_key", ""),
            "analysis_type": analysis.get("analysis_type", ""),
            "genel_puan": analysis.get("genel_puan", ""),
            "gecti_mi": "Yes" if analysis.get("gecti_mi") else "No",
            "created_at": analysis.get("created_at", ""),
            "triggered_by": analysis.get("triggered_by", "manual")
        })

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    type_filter = analysis_type or "all"
    filename = f"baqa_analyses_{type_filter}_{timestamp}.csv"

    # Return as streaming response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/pipeline-runs")
async def get_pipeline_runs(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of pipeline runs")
):
    """
    Get recent BRD pipeline runs with available document info.

    Returns list of pipeline runs with scores and available document types.
    """
    runs = get_recent_pipeline_runs(limit=limit)

    results = []
    for run in runs:
        # Determine which documents are available from stage outputs
        outputs = get_pipeline_run_outputs(run["id"])
        available_docs = set()
        for output in outputs:
            stage = output.get("stage", "")
            if stage in ("ba", "ba_gen"):
                available_docs.add("ba")
            elif stage in ("ta", "ta_gen"):
                available_docs.add("ta")
            elif stage in ("tc", "tc_gen"):
                available_docs.add("tc")
        available_docs = list(available_docs)

        results.append({
            "id": run["id"],
            "project_name": run.get("project_name", ""),
            "status": run.get("status", ""),
            "current_stage": run.get("current_stage", ""),
            "ba_score": run.get("ba_score"),
            "ta_score": run.get("ta_score"),
            "tc_score": run.get("tc_score"),
            "created_at": run.get("created_at", ""),
            "available_docs": available_docs,
        })

    return results
