"""
Evaluation Service — BA/TC evaluation business logic
EXACTLY matches Streamlit agents/prompts.py implementation
"""
from typing import Dict, Any, List, Optional
from api.services import database_service
from agents.ai_client import call_ai
from agents.prompts import parse_json_response
import json
import re
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# BA Evaluation Criteria (from utils/config.py)
BA_CRITERIA = [
    ("completeness", "Tamlık"),
    ("wireframes", "Wireframe / Ekran Tasarımları"),
    ("flow_diagrams", "Akış Diyagramları"),
    ("requirement_quality", "Gereksinim Kalitesi"),
    ("acceptance_criteria", "Kabul Kriterleri"),
    ("consistency", "Tutarlılık"),
    ("business_rules", "İş Kuralları Derinliği"),
    ("error_handling", "Hata Yönetimi"),
    ("documentation_quality", "Dokümantasyon Kalitesi"),
]

# TC Evaluation Criteria
TC_CRITERIA = [
    ("coverage", "Kapsam"),
    ("test_structure", "Test Case Yapısı"),
    ("edge_cases", "Sınır Değer & Negatif Senaryolar"),
    ("data_quality", "Test Verisi Kalitesi"),
    ("priority_classification", "Öncelik Sınıflandırması"),
    ("regression_scope", "Regresyon Kapsamı"),
    ("traceability", "İzlenebilirlik"),
    ("readability", "Okunabilirlik & Uygulanabilirlik"),
]


def emoji_score(puan: int) -> str:
    """Score emoji helper"""
    return "🟢" if puan >= 8 else "🟡" if puan >= 6 else "🔴"


def build_ba_evaluation_prompt(ba_text: str, brd_text: str = "", has_brd: bool = False) -> tuple[str, str]:
    """
    Build BA evaluation prompt EXACTLY as in Streamlit agents/prompts.py
    Returns: (system_prompt, user_content)
    """
    ref_block = (
        'A REFERENCE DOCUMENT (BRD / Scope Document) has been provided. Evaluate the Business Analysis by COMPARING it against THIS REFERENCE.\n'
        'Every requirement, every module, every business rule in the reference document MUST be covered in the Business Analysis.\n'
        'Each missing requirement severely reduces the score.'
        if has_brd else
        'No reference document was provided. Evaluate the Business Analysis independently on its own merits, but still apply rigorous criteria.'
    )

    completeness_check = (
        'Are ALL requirements from the BRD/Scope document covered? Which ones are missing?'
        if has_brd else 'Are all modules defined?'
    )

    system_prompt = f"""You are an extremely experienced business analysis quality control expert.
Your task is to evaluate the quality of a Business Analysis document.

IMPORTANT: This is a BUSINESS ANALYSIS document, NOT a TECHNICAL DESIGN document.
A business analyst is NOT responsible for technical requirements, performance criteria, or infrastructure decisions.
Evaluate within the BUSINESS ANALYST'S RESPONSIBILITIES scope.

{ref_block}

===== SCORING RULES =====

WARNING: DEFAULT SCORE IS 5/10. Only increase if there is EVIDENCE of quality.
WARNING: 8/10 and above = EXCELLENT. Very hard to earn.
WARNING: Missing module = that criterion gets MAX 3/10.
WARNING: Vague expressions ("appropriate", "when needed", "fast", "sufficient") = each deducts 0.5 points.
WARNING: Overall score = average of 9 criteria multiplied by 100/90 (out of 100).
WARNING: Pass threshold: 60 and above = PASSED, below = FAILED.

===== 9 CRITERIA (each scored 1-10) =====

1. completeness (Completeness) - {completeness_check}
2. wireframes (Wireframes / Screen Designs) - Links = 9-10, descriptions = 7-8, none = MAX 3
3. flow_diagrams (Flow Diagrams) - Links = 9-10, text descriptions = 7-8, none = MAX 3
4. requirement_quality (Requirement Quality) - Vague expressions each deduct 0.5
5. acceptance_criteria (Acceptance Criteria) - Missing criteria each deduct 0.3
6. consistency (Consistency) - Terminology, ID numbering, contradictions
7. business_rules (Business Rules Depth) - Edge cases, validation rules
8. error_handling (Error Handling) - Error scenarios, fallback behaviors
9. documentation_quality (Documentation Quality) - Structure, readability, TOC

===== JSON OUTPUT FORMAT =====

LANGUAGE: ALL output text MUST be in Turkish.
Return ONLY the following JSON format. No other text.

{{"skorlar": [
    {{"kriter": "completeness", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "wireframes", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "flow_diagrams", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "requirement_quality", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "acceptance_criteria", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "consistency", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "business_rules", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "error_handling", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "documentation_quality", "puan": 5, "aciklama": "aciklama"}}
  ],
  "genel_puan": 56,
  "gecti_mi": false,
  "genel_degerlendirme": "Genel degerlendirme",
  "guclu_yanlar": ["guclu yan 1"],
  "kritik_eksikler": ["eksik 1"],
  "iyilestirme_onerileri": ["oneri 1"],
  "belirsiz_ifadeler": [{{"konum": "IK-005", "ifade": "uygun surede", "oneri": "5 is gunu icinde"}}],
  "istatistikler": {{
    "toplam_modul": 8, "wireframe_olan_modul": 0, "akis_diyagrami_olan_modul": 2,
    "toplam_is_kurali": 45, "kabul_kriteri_eksik": 20, "belirsiz_ifade_sayisi": 12
  }}
}}

Return ONLY JSON, no other text. Be FAIR in scoring but not generous."""

    user_content = "EVALUATE THE BUSINESS ANALYSIS DOCUMENT:\n\n" + ba_text[:500000]
    if has_brd and brd_text:
        user_content = "REFERENCE DOCUMENT (BRD / Scope):\n\n" + brd_text[:100000] + "\n\n---\n\nEVALUATE THE BUSINESS ANALYSIS DOCUMENT:\n\n" + ba_text[:400000]

    return system_prompt, user_content


def evaluate_ba_document(
    content_json: Dict[str, Any],
    reference_content: Optional[Dict[str, Any]] = None,
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Evaluate BA document quality using AI.
    EXACTLY matches Streamlit evaluation flow.

    Args:
        content_json: BA document content (contains "text" key)
        reference_content: Optional reference BRD for comparison
        model: AI model to use

    Returns:
        Evaluation result with scores and feedback (Streamlit-compatible format)
    """
    from ..config import get_settings
    settings = get_settings()

    # Extract text from content_json
    ba_text = content_json.get("text", "")
    brd_text = reference_content.get("text", "") if reference_content else ""
    has_brd = bool(brd_text)

    # Build prompt using exact Streamlit logic
    system_prompt, user_content = build_ba_evaluation_prompt(ba_text, brd_text, has_brd)

    try:
        # Call AI with retry logic (3 attempts) - EXACTLY like Streamlit
        result = None
        for attempt in range(3):
            try:
                result = call_ai(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    anthropic_key=settings.anthropic_api_key,
                    gemini_key=settings.gemini_api_key or "",
                    model=model,
                    max_tokens=8000,
                    use_caching=True
                )
                if result and result.get("skorlar"):
                    break
            except Exception as e:
                error_msg = str(e)
                if attempt == 2:
                    raise
                if "429" in error_msg or "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    import time
                    wait = 30 * (attempt + 1)
                    time.sleep(wait)
                else:
                    raise

        if not result or not result.get("skorlar"):
            raise Exception("AI yanıtı parse edilemedi.")

        # Return Streamlit-compatible format
        return {
            "score": result.get("genel_puan", 0),
            "criteria_scores": [
                {
                    "criterion": s.get("kriter", ""),
                    "score": s.get("puan", 0),
                    "feedback": s.get("aciklama", ""),
                    "passed": s.get("puan", 0) >= 6
                }
                for s in result.get("skorlar", [])
            ],
            "passed": result.get("gecti_mi", False),
            "feedback": result.get("genel_degerlendirme", ""),
            "strengths": result.get("guclu_yanlar", []),
            "weaknesses": result.get("kritik_eksikler", []),
            "suggestions": result.get("iyilestirme_onerileri", []),
            "vague_expressions": result.get("belirsiz_ifadeler", []),
            "statistics": result.get("istatistikler", {}),
            "model_used": model
        }

    except Exception as e:
        # Fallback response on error
        return {
            "score": 0,
            "criteria_scores": [],
            "passed": False,
            "feedback": f"Evaluation failed: {str(e)}",
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "vague_expressions": [],
            "statistics": {},
            "model_used": model
        }


def build_tc_evaluation_prompt(tc_text: str, ba_text: str = "", has_ba: bool = False) -> tuple[str, str]:
    """
    Build TC evaluation prompt EXACTLY as in Streamlit agents/prompts.py
    Returns: (system_prompt, user_content)
    """
    ref_block = (
        'A REFERENCE DOCUMENT (Business Analysis) has been provided. Evaluate the test case document by COMPARING it against the BUSINESS ANALYSIS.\n'
        'Every module, every business rule, every acceptance criterion in the BA must have test cases.\n'
        'Missing coverage severely reduces the score.'
        if has_ba else
        'No Business Analysis reference document was provided. Evaluate the test case document independently on its own merits.'
    )

    system_prompt = f"""You are an extremely experienced test engineering quality control expert.
Your task is to evaluate the quality of a Test Case document.

EXPECTED TEMPLATE STRUCTURE (23 Columns):
EXISTANCE, CREATED By, DATE, APP BUNDLE, TEST CASE ID, BR ID, TR ID, PRIORITY,
CHANNEL, TESTCASE TYPE, USER TYPE, TEST AREA, TEST SCENARIO, TESTCASE, TEST STEPS,
PRECONDITION, TEST DATA, EXPECTED RESULT, POSTCONDITION, ACTUAL RESULT, STATUS,
REGRESSION CASE, COMMENTS

{ref_block}

===== SCORING RULES =====

WARNING: DEFAULT SCORE IS 5/10. Only increase if there is EVIDENCE of quality.
WARNING: 8/10 and above = EXCELLENT.
WARNING: Overall score = average of 8 criteria multiplied by 100/80 (out of 100).
WARNING: Pass threshold: 60 and above = PASSED, below = FAILED.

===== 8 CRITERIA (each scored 1-10) =====

1. coverage - BA coverage, module coverage
2. test_structure - Template fields, ID format, steps, expected results
3. edge_cases - Negative scenarios (30%+ ratio needed), boundary values
4. data_quality - Specific test data, realistic values
5. priority_classification - CRITICAL/HIGH/MEDIUM/LOW distribution
6. regression_scope - 20-40% regression set ideal
7. traceability - BR ID mapping, requirement links
8. readability - Executability, step clarity, consistent terminology

===== JSON OUTPUT FORMAT =====

LANGUAGE: ALL output text MUST be in Turkish. Return ONLY JSON.

{{"skorlar": [
    {{"kriter": "coverage", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "test_structure", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "edge_cases", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "data_quality", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "priority_classification", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "regression_scope", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "traceability", "puan": 5, "aciklama": "aciklama"}},
    {{"kriter": "readability", "puan": 5, "aciklama": "aciklama"}}
  ],
  "genel_puan": 56,
  "gecti_mi": false,
  "genel_degerlendirme": "degerlendirme",
  "guclu_yanlar": ["guclu yan"],
  "kritik_eksikler": ["eksik"],
  "iyilestirme_onerileri": ["oneri"],
  "istatistikler": {{
    "toplam_test_case": 45, "bos_alan_sayisi": 12,
    "negatif_senaryo_sayisi": 8, "negatif_senaryo_orani": 18,
    "br_id_eksik_sayisi": 20, "test_data_eksik_sayisi": 15,
    "regression_case_sayisi": 10,
    "critical_sayisi": 5, "high_sayisi": 15, "medium_sayisi": 20, "low_sayisi": 5,
    "kapsanmayan_ba_gereksinimleri": ["modul"]
  }}
}}

Return ONLY JSON, no other text."""

    user_content = "EVALUATE THE TEST CASE DOCUMENT:\n\n" + tc_text[:500000]
    if has_ba and ba_text:
        user_content = "REFERENCE DOCUMENT (Business Analysis):\n\n" + ba_text[:100000] + "\n\n---\n\nEVALUATE THE TEST CASE DOCUMENT:\n\n" + tc_text[:400000]

    return system_prompt, user_content


def evaluate_tc_document(
    content_json: Dict[str, Any],
    reference_ba: Optional[Dict[str, Any]] = None,
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Evaluate TC document quality using AI.
    EXACTLY matches Streamlit evaluation flow.

    Args:
        content_json: TC document content (contains "text" key)
        reference_ba: Optional BA document for traceability check
        model: AI model to use

    Returns:
        Evaluation result with scores and feedback (Streamlit-compatible format)
    """
    from ..config import get_settings
    settings = get_settings()

    # Extract text from content_json
    tc_text = content_json.get("text", "")
    ba_text = reference_ba.get("text", "") if reference_ba else ""
    has_ba = bool(ba_text)

    # Build prompt using exact Streamlit logic
    system_prompt, user_content = build_tc_evaluation_prompt(tc_text, ba_text, has_ba)

    try:
        # Call AI with retry logic (3 attempts) - EXACTLY like Streamlit
        result = None
        for attempt in range(3):
            try:
                result = call_ai(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    anthropic_key=settings.anthropic_api_key,
                    gemini_key=settings.gemini_api_key or "",
                    model=model,
                    max_tokens=8000,
                    use_caching=True
                )
                if result and result.get("skorlar"):
                    break
            except Exception as e:
                error_msg = str(e)
                if attempt == 2:
                    raise
                if "429" in error_msg or "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    import time
                    wait = 30 * (attempt + 1)
                    time.sleep(wait)
                else:
                    raise

        if not result or not result.get("skorlar"):
            raise Exception("AI yanıtı parse edilemedi.")

        # Return Streamlit-compatible format
        return {
            "score": result.get("genel_puan", 0),
            "criteria_scores": [
                {
                    "criterion": s.get("kriter", ""),
                    "score": s.get("puan", 0),
                    "feedback": s.get("aciklama", ""),
                    "passed": s.get("puan", 0) >= 6
                }
                for s in result.get("skorlar", [])
            ],
            "passed": result.get("gecti_mi", False),
            "feedback": result.get("genel_degerlendirme", ""),
            "strengths": result.get("guclu_yanlar", []),
            "weaknesses": result.get("kritik_eksikler", []),
            "suggestions": result.get("iyilestirme_onerileri", []),
            "statistics": result.get("istatistikler", {}),
            "model_used": model
        }

    except Exception as e:
        # Fallback response on error
        return {
            "score": 0,
            "criteria_scores": [],
            "passed": False,
            "feedback": f"Evaluation failed: {str(e)}",
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "statistics": {},
            "model_used": model
        }
