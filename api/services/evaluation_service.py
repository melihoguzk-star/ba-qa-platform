"""
Evaluation Service — BA/TC evaluation business logic
"""
from typing import Dict, Any, List, Optional
from api.services.ai_service import get_ai_service
from api.services import database_service
import json


# BA Evaluation Criteria (from agents/agent_definitions.py)
BA_CRITERIA = [
    ("completeness", "Tamlık", "Tüm gereksinimler detaylı şekilde tanımlanmış mı?"),
    ("wireframes", "Wireframe / Ekran Tasarımları", "Her ekran için wireframe veya mockup var mı?"),
    ("flow_diagrams", "Akış Diyagramları", "İş akışları görselleştirilmiş mi?"),
    ("requirement_quality", "Gereksinim Kalitesi", "Gereksinimler açık, ölçülebilir ve test edilebilir mi?"),
    ("acceptance_criteria", "Kabul Kriterleri", "Her gereksinim için kabul kriteri tanımlı mı?"),
    ("consistency", "Tutarlılık", "Doküman içinde tutarlılık var mı?"),
    ("business_rules", "İş Kuralları Derinliği", "İş kuralları detaylı açıklanmış mı?"),
    ("error_handling", "Hata Yönetimi", "Hata senaryoları ve çözümleri belirtilmiş mi?"),
    ("documentation_quality", "Dokümantasyon Kalitesi", "Doküman okunabilir ve profesyonel mi?"),
]

# TC Evaluation Criteria
TC_CRITERIA = [
    ("coverage", "Kapsam", "Tüm gereksinimler test case'ler ile kapsanmış mı?"),
    ("test_structure", "Test Case Yapısı", "Test case'ler doğru formatta yazılmış mı?"),
    ("edge_cases", "Sınır Değer & Negatif Senaryolar", "Edge case'ler ve negatif senaryolar var mı?"),
    ("data_quality", "Test Verisi Kalitesi", "Test verileri gerçekçi ve yeterli mi?"),
    ("priority_classification", "Öncelik Sınıflandırması", "Test case'ler önceliklendirilmiş mi?"),
    ("regression_scope", "Regresyon Kapsamı", "Regresyon test case'leri tanımlı mı?"),
    ("traceability", "İzlenebilirlik", "Test case'ler gereksinimlere bağlı mı?"),
    ("readability", "Okunabilirlik & Uygulanabilirlik", "Test case'ler net ve uygulanabilir mi?"),
]


def evaluate_ba_document(
    content_json: Dict[str, Any],
    reference_content: Optional[Dict[str, Any]] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Dict[str, Any]:
    """
    Evaluate BA document quality using AI.

    Args:
        content_json: BA document content
        reference_content: Optional reference BA for comparison
        model: AI model to use

    Returns:
        Evaluation result with scores and feedback
    """
    ai_service = get_ai_service()

    # Build evaluation prompt
    system_prompt = """Sen bir Business Analyst quality assurance uzmanısın.
BA dokümanlarını aşağıdaki kriterlere göre değerlendiriyorsun.
Her kriter için 0-100 arası puan ver ve detaylı feedback sun."""

    criteria_text = "\n".join([
        f"{i+1}. {name} ({desc}): {question}"
        for i, (code, name, question) in enumerate(BA_CRITERIA)
    ])

    prompt = f"""Aşağıdaki BA dokümanını değerlendir:

Doküman İçeriği:
{json.dumps(content_json, ensure_ascii=False, indent=2)}

Değerlendirme Kriterleri:
{criteria_text}

Lütfen JSON formatında yanıt ver:
{{
    "overall_score": <0-100 arası genel puan>,
    "criteria_scores": [
        {{"criterion": "<kriter kodu>", "score": <0-100>, "feedback": "<detaylı açıklama>"}},
        ...
    ],
    "passed": <true/false (60+ puan geçer)>,
    "summary": "<genel değerlendirme özeti>"
}}"""

    try:
        result = ai_service.generate_with_json(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=0.3,
            max_tokens=4000
        )

        # Parse and structure response
        criteria_scores = []
        for criterion_result in result.get("criteria_scores", []):
            criteria_scores.append({
                "criterion": criterion_result.get("criterion", ""),
                "score": criterion_result.get("score", 0),
                "feedback": criterion_result.get("feedback", ""),
                "passed": criterion_result.get("score", 0) >= 60
            })

        return {
            "score": result.get("overall_score", 0),
            "criteria_scores": criteria_scores,
            "passed": result.get("overall_score", 0) >= 60,
            "feedback": result.get("summary", ""),
            "model_used": model
        }

    except Exception as e:
        # Fallback response on error
        return {
            "score": 0,
            "criteria_scores": [],
            "passed": False,
            "feedback": f"Evaluation failed: {str(e)}",
            "model_used": model
        }


def evaluate_tc_document(
    content_json: Dict[str, Any],
    reference_ba: Optional[Dict[str, Any]] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Dict[str, Any]:
    """
    Evaluate TC document quality using AI.

    Args:
        content_json: TC document content
        reference_ba: Optional BA document for traceability check
        model: AI model to use

    Returns:
        Evaluation result with scores and feedback
    """
    ai_service = get_ai_service()

    # Build evaluation prompt
    system_prompt = """Sen bir Test Engineer quality assurance uzmanısın.
Test Case dokümanlarını aşağıdaki kriterlere göre değerlendiriyorsun.
Her kriter için 0-100 arası puan ver ve detaylı feedback sun."""

    criteria_text = "\n".join([
        f"{i+1}. {name} ({desc}): {question}"
        for i, (code, name, question) in enumerate(TC_CRITERIA)
    ])

    prompt = f"""Aşağıdaki TC dokümanını değerlendir:

Doküman İçeriği:
{json.dumps(content_json, ensure_ascii=False, indent=2)}

Değerlendirme Kriterleri:
{criteria_text}

Lütfen JSON formatında yanıt ver:
{{
    "overall_score": <0-100 arası genel puan>,
    "criteria_scores": [
        {{"criterion": "<kriter kodu>", "score": <0-100>, "feedback": "<detaylı açıklama>"}},
        ...
    ],
    "passed": <true/false (60+ puan geçer)>,
    "summary": "<genel değerlendirme özeti>"
}}"""

    try:
        result = ai_service.generate_with_json(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=0.3,
            max_tokens=4000
        )

        # Parse and structure response
        criteria_scores = []
        for criterion_result in result.get("criteria_scores", []):
            criteria_scores.append({
                "criterion": criterion_result.get("criterion", ""),
                "score": criterion_result.get("score", 0),
                "feedback": criterion_result.get("feedback", ""),
                "passed": criterion_result.get("score", 0) >= 60
            })

        return {
            "score": result.get("overall_score", 0),
            "criteria_scores": criteria_scores,
            "passed": result.get("overall_score", 0) >= 60,
            "feedback": result.get("summary", ""),
            "model_used": model
        }

    except Exception as e:
        # Fallback response on error
        return {
            "score": 0,
            "criteria_scores": [],
            "passed": False,
            "feedback": f"Evaluation failed: {str(e)}",
            "model_used": model
        }
