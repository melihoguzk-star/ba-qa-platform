"""
Evaluation Router — BA/TC evaluation endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.schemas.evaluation import EvaluationRequest, EvaluationResponse
from api.services import evaluation_service, database_service
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from integrations.google_docs import fetch_google_doc_via_proxy
from integrations.jira_client import jira_get_issue
import re

router = APIRouter()


def extract_doc_id_from_description(description: str) -> tuple[str, str]:
    """Extract Google Doc ID from JIRA description"""
    if not description:
        return "", ""

    desc_str = str(description)
    patterns = [
        r'docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
        r'https://docs\.google\.com/.*?/d/([a-zA-Z0-9_-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, desc_str)
        if match:
            doc_id = match.group(1)
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            return doc_id, doc_url

    return "", ""


def fetch_document_content_from_jira(task_key: str) -> str:
    """Fetch Google Doc content linked in JIRA task (uses config credentials)"""
    from ..config import get_settings
    settings = get_settings()

    if not settings.jira_email or not settings.jira_api_token:
        raise HTTPException(
            status_code=500,
            detail="JIRA credentials not configured. Set JIRA_EMAIL and JIRA_API_TOKEN in .env"
        )

    # Get JIRA task
    issue = jira_get_issue(settings.jira_email, settings.jira_api_token, task_key, fields="description")
    description = issue.get("fields", {}).get("description", "")

    # Extract doc ID
    doc_id, _ = extract_doc_id_from_description(description)
    if not doc_id:
        raise HTTPException(
            status_code=404,
            detail=f"No Google Doc link found in JIRA task {task_key}"
        )

    # Fetch Google Doc content
    try:
        content = fetch_google_doc_via_proxy(doc_id)
        return content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Google Doc {doc_id}: {str(e)}"
        )


@router.post("/ba", response_model=EvaluationResponse)
async def evaluate_ba(request: EvaluationRequest):
    """
    Evaluate a BA document using AI.

    Evaluates against 9 criteria:
    - Tamlık (Completeness)
    - Wireframe / Ekran Tasarımları
    - Akış Diyagramları
    - Gereksinim Kalitesi
    - Kabul Kriterleri
    - Tutarlılık
    - İş Kuralları Derinliği
    - Hata Yönetimi
    - Dokümantasyon Kalitesi

    Pass threshold: 60/100

    Three evaluation modes:
    1. **jira_task_key** + credentials: Auto-fetch from JIRA + Google Docs
    2. **document_id**: Evaluate from database
    3. **content_json**: Evaluate direct content
    """
    # Mode 1: JIRA task (auto-fetch Google Doc)
    if request.jira_task_key:
        # Fetch document content from JIRA + Google Docs (uses config credentials)
        ba_text = fetch_document_content_from_jira(request.jira_task_key)

        # Convert text to content_json (simple structure for now)
        content_json = {"text": ba_text}

    # Mode 2: Database document
    elif request.document_id:
        document = database_service.get_document_by_id(request.document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {request.document_id} not found"
            )
        content_json = document.get('content_json', {})

    # Mode 3: Direct content
    elif request.content_json:
        content_json = request.content_json

    else:
        raise HTTPException(
            status_code=400,
            detail="One of jira_task_key, document_id, or content_json must be provided"
        )

    # Get reference content if provided
    reference_content = None
    if request.reference_document_id:
        ref_doc = database_service.get_document_by_id(request.reference_document_id)
        if ref_doc:
            reference_content = ref_doc.get('content_json')

    try:
        # Perform evaluation
        result = evaluation_service.evaluate_ba_document(
            content_json=content_json,
            reference_content=reference_content
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/tc", response_model=EvaluationResponse)
async def evaluate_tc(request: EvaluationRequest):
    """
    Evaluate a TC document using AI.

    Evaluates against 8 criteria:
    - Kapsam (Coverage)
    - Test Case Yapısı
    - Sınır Değer & Negatif Senaryolar
    - Test Verisi Kalitesi
    - Öncelik Sınıflandırması
    - Regresyon Kapsamı
    - İzlenebilirlik
    - Okunabilirlik & Uygulanabilirlik

    Pass threshold: 60/100

    Three evaluation modes:
    1. **jira_task_key** + credentials: Auto-fetch from JIRA + Google Docs
    2. **document_id**: Evaluate from database
    3. **content_json**: Evaluate direct content
    """
    # Mode 1: JIRA task (auto-fetch Google Doc/Sheets)
    if request.jira_task_key:
        # Fetch document content from JIRA + Google Docs/Sheets (uses config credentials)
        tc_text = fetch_document_content_from_jira(request.jira_task_key)

        # Convert text to content_json
        content_json = {"text": tc_text}

    # Mode 2: Database document
    elif request.document_id:
        document = database_service.get_document_by_id(request.document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {request.document_id} not found"
            )
        content_json = document.get('content_json', {})

    # Mode 3: Direct content
    elif request.content_json:
        content_json = request.content_json

    else:
        raise HTTPException(
            status_code=400,
            detail="One of jira_task_key, document_id, or content_json must be provided"
        )

    # Get reference BA if provided
    reference_ba = None
    if request.reference_document_id:
        ref_doc = database_service.get_document_by_id(request.reference_document_id)
        if ref_doc:
            reference_ba = ref_doc.get('content_json')

    try:
        # Perform evaluation
        result = evaluation_service.evaluate_tc_document(
            content_json=content_json,
            reference_ba=reference_ba
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )
