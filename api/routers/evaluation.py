"""
Evaluation Router — BA/TC evaluation endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.schemas.evaluation import EvaluationRequest, EvaluationResponse
from api.services import evaluation_service, database_service

router = APIRouter()


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

    - **document_id**: Document ID to evaluate (optional)
    - **content_json**: Direct content to evaluate (optional)
    - **reference_document_id**: Reference BA for comparison (optional)
    """
    # Get content from document_id or direct content
    if request.document_id:
        document = database_service.get_document_by_id(request.document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {request.document_id} not found"
            )
        content_json = document.get('content_json', {})

    elif request.content_json:
        content_json = request.content_json

    else:
        raise HTTPException(
            status_code=400,
            detail="Either document_id or content_json must be provided"
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

    - **document_id**: Document ID to evaluate (optional)
    - **content_json**: Direct content to evaluate (optional)
    - **reference_document_id**: Reference BA for traceability check (optional)
    """
    # Get content from document_id or direct content
    if request.document_id:
        document = database_service.get_document_by_id(request.document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {request.document_id} not found"
            )
        content_json = document.get('content_json', {})

    elif request.content_json:
        content_json = request.content_json

    else:
        raise HTTPException(
            status_code=400,
            detail="Either document_id or content_json must be provided"
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
