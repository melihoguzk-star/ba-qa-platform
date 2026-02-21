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


def fetch_document_content_from_jira(task_key: str, prefer_sheets: bool = False) -> str:
    """
    Fetch Google Doc/Sheets content linked in JIRA task (uses config credentials)

    Args:
        task_key: JIRA task key
        prefer_sheets: If True, look for Sheets first (for TC), else Docs first (for BA)
    """
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

    # Extract doc ID - use description as string to detect Sheets vs Docs
    desc_str = str(description)

    # Try to detect if it's a Sheets or Docs link
    is_sheets = 'spreadsheets' in desc_str

    doc_id, doc_url = extract_doc_id_from_description(description)
    if not doc_id:
        raise HTTPException(
            status_code=404,
            detail=f"No Google Doc/Sheets link found in JIRA task {task_key}"
        )

    # Fetch content based on document type
    try:
        if is_sheets or prefer_sheets:
            # Try Sheets first
            from integrations.google_docs import fetch_google_sheets_as_text
            try:
                content = fetch_google_sheets_as_text(doc_id)
                return content
            except Exception as sheets_error:
                # Fallback to Docs if Sheets fails
                if not prefer_sheets:
                    raise
                try:
                    content = fetch_google_doc_via_proxy(doc_id)
                    return content
                except Exception:
                    raise sheets_error
        else:
            # Docs
            content = fetch_google_doc_via_proxy(doc_id)
            return content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Google Doc/Sheets {doc_id}: {str(e)}"
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
    from ..config import get_settings
    settings = get_settings()

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
            reference_content=reference_content,
            model=request.model or "gemini-2.5-flash"
        )

        # Check if evaluation actually succeeded (not a fallback error result)
        # Don't update JIRA if score is 0 and there are no criteria scores (indicates error)
        is_valid_result = result["score"] > 0 or len(result.get("criteria_scores", [])) > 0

        # Update JIRA only if this was from a JIRA task AND evaluation succeeded
        if request.jira_task_key and is_valid_result:
            from integrations.jira_client import jira_add_comment, jira_update_labels
            from agents.prompts import format_ba_report
            from data.database import save_analysis

            # Format report
            report_data = {
                "genel_puan": result["score"],
                "gecti_mi": result["passed"],
                "genel_degerlendirme": result["feedback"],
                "guclu_yanlar": result.get("strengths", []),
                "kritik_eksikler": result.get("weaknesses", []),
                "iyilestirme_onerileri": result.get("suggestions", []),
                "skorlar": [
                    {"kriter": c["criterion"], "puan": c["score"], "aciklama": c["feedback"]}
                    for c in result["criteria_scores"]
                ],
                "belirsiz_ifadeler": result.get("vague_expressions", []),
                "istatistikler": result.get("statistics", {})
            }
            report_text = format_ba_report(report_data)

            # Add JIRA comment
            jira_add_comment(settings.jira_email, settings.jira_api_token, request.jira_task_key, report_text)

            # Update JIRA labels
            new_label = "qa-gecti" if result["passed"] else "qa-gecmedi"
            jira_update_labels(
                settings.jira_email,
                settings.jira_api_token,
                request.jira_task_key,
                ["qa-devam-ediyor"],
                ["qa-tamamlandi", new_label]
            )

            # Save to database
            save_analysis(
                request.jira_task_key,
                "ba",
                result["score"],
                result["passed"],
                report_data,
                report_text
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
    from ..config import get_settings
    settings = get_settings()

    # Mode 1: JIRA task (auto-fetch Google Doc/Sheets)
    if request.jira_task_key:
        # Fetch document content from JIRA + Google Sheets (TC uses Sheets, uses config credentials)
        tc_text = fetch_document_content_from_jira(request.jira_task_key, prefer_sheets=True)

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
            reference_ba=reference_ba,
            model=request.model or "gemini-2.5-flash"
        )

        # Check if evaluation actually succeeded (not a fallback error result)
        # Don't update JIRA if score is 0 and there are no criteria scores (indicates error)
        is_valid_result = result["score"] > 0 or len(result.get("criteria_scores", [])) > 0

        # Update JIRA only if this was from a JIRA task AND evaluation succeeded
        if request.jira_task_key and is_valid_result:
            from integrations.jira_client import jira_add_comment, jira_update_labels
            from agents.prompts import format_tc_report
            from data.database import save_analysis

            # Format report
            report_data = {
                "genel_puan": result["score"],
                "gecti_mi": result["passed"],
                "genel_degerlendirme": result["feedback"],
                "guclu_yanlar": result.get("strengths", []),
                "kritik_eksikler": result.get("weaknesses", []),
                "iyilestirme_onerileri": result.get("suggestions", []),
                "skorlar": [
                    {"kriter": c["criterion"], "puan": c["score"], "aciklama": c["feedback"]}
                    for c in result["criteria_scores"]
                ],
                "istatistikler": result.get("statistics", {})
            }
            report_text = format_tc_report(report_data)

            # Add JIRA comment
            jira_add_comment(settings.jira_email, settings.jira_api_token, request.jira_task_key, report_text)

            # Update JIRA labels
            new_label = "tc-qa-gecti" if result["passed"] else "tc-qa-gecmedi"
            jira_update_labels(
                settings.jira_email,
                settings.jira_api_token,
                request.jira_task_key,
                ["tc-qa-devam-ediyor"],
                ["tc-qa-tamamlandi", new_label]
            )

            # Save to database
            save_analysis(
                request.jira_task_key,
                "tc",
                result["score"],
                result["passed"],
                report_data,
                report_text
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )
