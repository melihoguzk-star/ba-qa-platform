"""
BA&QA Intelligence Platform — Evaluation Prompts
BA ve TC değerlendirme için LLM prompt'ları
"""
import json
import re


def build_ba_evaluation_prompt(ba_text: str, brd_text: str = "", has_brd: bool = False) -> str:
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

    return system_prompt + "\n\n" + user_content


def build_tc_evaluation_prompt(tc_text: str, ba_text: str = "", has_ba: bool = False) -> str:
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

    return system_prompt + "\n\n" + user_content


# ─────────────────────────────────────────────
# RESULT PARSERS & FORMATTERS
# ─────────────────────────────────────────────

def parse_json_response(text: str) -> dict:
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def format_ba_report(data: dict) -> str:
    from utils.config import BA_CRITERIA, emoji_score
    report = "📋 İŞ ANALİZİ KALİTE DEĞERLENDİRMESİ\n"
    report += "══════════════════════════════\n\n"
    report += f"📊 Genel Puan: {data.get('genel_puan', 0)}/100 {'✅ GEÇTİ' if data.get('gecti_mi') else '❌ GEÇMEDİ'}\n\n"
    report += "📈 Kriter Puanları:\n"
    for key, label in BA_CRITERIA:
        skor = next((s for s in data.get("skorlar", []) if s.get("kriter") == key), None)
        puan = skor["puan"] if skor else 0
        report += f"{emoji_score(puan)} {label}: {puan}/10\n"
    report += f"\n📝 Genel Değerlendirme:\n{data.get('genel_degerlendirme', '-')}\n"
    if data.get("guclu_yanlar"):
        report += "\n✅ Güçlü Yanlar:\n"
        for item in data["guclu_yanlar"]:
            report += f"• {item}\n"
    if data.get("kritik_eksikler"):
        report += "\n❌ Kritik Eksikler:\n"
        for item in data["kritik_eksikler"]:
            report += f"• {item}\n"
    if data.get("iyilestirme_onerileri"):
        report += "\n💡 İyileştirme Önerileri:\n"
        for i, item in enumerate(data["iyilestirme_onerileri"], 1):
            report += f"{i}. {item}\n"
    if data.get("belirsiz_ifadeler"):
        report += "\n⚠️ Belirsiz İfadeler:\n"
        for b in data["belirsiz_ifadeler"]:
            report += f"• [{b.get('konum', '')}] \"{b.get('ifade', '')}\" → {b.get('oneri', '')}\n"
    stats = data.get("istatistikler", {})
    report += f"\n📊 İstatistikler:\n"
    report += f"• Toplam Modül: {stats.get('toplam_modul', '-')}\n"
    report += f"• Wireframe Olan: {stats.get('wireframe_olan_modul', '-')}\n"
    report += f"• Akış Diyagramı Olan: {stats.get('akis_diyagrami_olan_modul', '-')}\n"
    report += f"• Toplam İş Kuralı: {stats.get('toplam_is_kurali', '-')}\n"
    report += f"• Kabul Kriteri Eksik: {stats.get('kabul_kriteri_eksik', '-')}\n"
    report += f"• Belirsiz İfade: {stats.get('belirsiz_ifade_sayisi', '-')}\n"
    return report


def format_tc_report(data: dict) -> str:
    from utils.config import TC_CRITERIA, emoji_score
    report = "🧪 TEST CASE KALİTE DEĞERLENDİRMESİ\n"
    report += "══════════════════════════════\n\n"
    report += f"📊 Genel Puan: {data.get('genel_puan', 0)}/100 {'✅ GEÇTİ' if data.get('gecti_mi') else '❌ GEÇMEDİ'}\n\n"
    report += "📈 Kriter Puanları:\n"
    for key, label in TC_CRITERIA:
        skor = next((s for s in data.get("skorlar", []) if s.get("kriter") == key), None)
        puan = skor["puan"] if skor else 0
        report += f"{emoji_score(puan)} {label}: {puan}/10\n"
    report += f"\n📝 Genel Değerlendirme:\n{data.get('genel_degerlendirme', '-')}\n"
    if data.get("guclu_yanlar"):
        report += "\n✅ Güçlü Yanlar:\n"
        for item in data["guclu_yanlar"]:
            report += f"• {item}\n"
    if data.get("kritik_eksikler"):
        report += "\n❌ Kritik Eksikler:\n"
        for item in data["kritik_eksikler"]:
            report += f"• {item}\n"
    if data.get("iyilestirme_onerileri"):
        report += "\n💡 İyileştirme Önerileri:\n"
        for i, item in enumerate(data["iyilestirme_onerileri"], 1):
            report += f"{i}. {item}\n"
    stats = data.get("istatistikler", {})
    report += f"\n📊 İstatistikler:\n"
    report += f"• Toplam TC: {stats.get('toplam_test_case', '-')}\n"
    report += f"• Boş Alan: {stats.get('bos_alan_sayisi', '-')}\n"
    report += f"• Negatif Senaryo: {stats.get('negatif_senaryo_sayisi', '-')} (%{stats.get('negatif_senaryo_orani', '-')})\n"
    report += f"• BR ID Eksik: {stats.get('br_id_eksik_sayisi', '-')}\n"
    report += f"• Test Data Eksik: {stats.get('test_data_eksik_sayisi', '-')}\n"
    report += f"• Regression: {stats.get('regression_case_sayisi', '-')}\n"
    report += f"• Öncelik: C={stats.get('critical_sayisi', 0)} H={stats.get('high_sayisi', 0)} M={stats.get('medium_sayisi', 0)} L={stats.get('low_sayisi', 0)}\n"
    if stats.get("kapsanmayan_ba_gereksinimleri"):
        report += f"• Kapsanmayan BA: {', '.join(stats['kapsanmayan_ba_gereksinimleri'])}\n"
    return report
