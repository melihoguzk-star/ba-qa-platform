"""
Background Tasks — Pipeline execution, embedding generation
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


async def execute_pipeline_task(
    run_id: int,
    project_name: str,
    brd_content: str,
    stages: List[str],
    figma_url: str = None
):
    """
    Background task for pipeline execution.

    Args:
        run_id: Pipeline run ID
        project_name: Project name
        brd_content: BRD content (plain text)
        stages: Stages to execute
        figma_url: Optional Figma design URL
    """
    from api.services import pipeline_service

    logger.info(f"Background task started: Pipeline run {run_id}")

    try:
        await pipeline_service.execute_pipeline(
            run_id=run_id,
            project_name=project_name,
            brd_content=brd_content,
            stages=stages,
            figma_url=figma_url
        )
        logger.info(f"Background task completed: Pipeline run {run_id}")

    except Exception as e:
        logger.error(f"Background task failed: Pipeline run {run_id}, error: {e}")
        raise


async def index_document_task(
    document_id: int,
    content_json: Dict[str, Any],
    doc_type: str
):
    """
    Background task for document embedding and indexing.

    Args:
        document_id: Document ID
        content_json: Document content
        doc_type: Document type
    """
    logger.info(f"Background task started: Index document {document_id}")

    try:
        from pipeline.embedding_pipeline import index_document_async

        index_document_async(
            doc_id=document_id,
            content=content_json,
            doc_type=doc_type,
            metadata={}
        )

        logger.info(f"Background task completed: Document {document_id} indexed")

    except Exception as e:
        logger.error(f"Background task failed: Document indexing {document_id}, error: {e}")
        # Don't raise - indexing failure shouldn't block document creation
