"""
Mock orchestrator - Returns mock data for testing without API calls
"""
import json
import time
from agents.mock_data import (
    MOCK_BA_CHUNK1, MOCK_BA_CHUNK2,
    MOCK_TA, MOCK_TC,
    MOCK_BA_QA, MOCK_TA_QA, MOCK_TC_QA
)


def merge_ba_mock(chunk1: dict, chunk2: dict) -> dict:
    """Merge BA chunks (mock version)"""
    ekranlar = chunk1.get("ekranlar", [])
    detaylar = chunk2.get("ekran_detaylari", [])

    for e in ekranlar:
        matching = next(
            (d for d in detaylar if d.get("ekran_adi") == e.get("ekran_adi")),
            None
        )
        if matching:
            e.update(matching)

    return {
        "proje_bilgisi": chunk1.get("proje_bilgisi", {}),
        "ekranlar": ekranlar,
        "fonksiyonel_gereksinimler": chunk1.get("fonksiyonel_gereksinimler", []),
        "business_rules": chunk2.get("business_rules", []),
        "validasyonlar": chunk2.get("validasyonlar", [])
    }


def generate_ba_mock(brd_text, project_name, anthropic_key, gemini_key, log, previous_feedback="", model=None):
    """Generate BA document (mock version)"""
    log("  🤖 [MOCK] BA Chunk1 üretiliyor...")
    time.sleep(0.5)  # Simulate API delay

    log("  🤖 [MOCK] BA Chunk2 üretiliyor...")
    time.sleep(0.5)

    log("  🔗 BA birleştiriliyor...")
    result = merge_ba_mock(MOCK_BA_CHUNK1, MOCK_BA_CHUNK2)

    log("  ✅ BA dokümanı üretildi")
    return result


def generate_ta_mock(brd_text, ba_content, project_name, anthropic_key, gemini_key, log, previous_feedback="", model=None):
    """Generate TA document (mock version)"""
    log("  🤖 [MOCK] TA üretiliyor...")
    time.sleep(0.5)

    log("  ✅ TA dokümanı üretildi")
    return MOCK_TA


def generate_tc_mock(ba_content, ta_content, project_name, jira_key, anthropic_key, gemini_key, log, screen_analysis="", previous_feedback="", model=None):
    """Generate TC document (mock version)"""
    log("  🤖 [MOCK] TC üretiliyor...")
    time.sleep(0.5)

    log("  ✅ TC dokümanı üretildi")
    return MOCK_TC


def evaluate_ba_qa_mock(ba_content, anthropic_key, gemini_key, log=None, model=None):
    """Evaluate BA quality (mock version)"""
    if log:
        log("  🔍 [MOCK] BA QA değerlendiriliyor...")
    time.sleep(0.3)

    if log:
        log(f"  📊 Skor: {MOCK_BA_QA['score']}/100")

    return MOCK_BA_QA


def evaluate_ta_qa_mock(ta_content, anthropic_key, gemini_key, log=None, model=None):
    """Evaluate TA quality (mock version)"""
    if log:
        log("  🔍 [MOCK] TA QA değerlendiriliyor...")
    time.sleep(0.3)

    if log:
        log(f"  📊 Skor: {MOCK_TA_QA['score']}/100")

    return MOCK_TA_QA


def evaluate_tc_qa_mock(tc_content, anthropic_key, gemini_key, log=None, model=None):
    """Evaluate TC quality (mock version)"""
    if log:
        log("  🔍 [MOCK] TC QA değerlendiriliyor...")
    time.sleep(0.3)

    if log:
        log(f"  📊 Skor: {MOCK_TC_QA['score']}/100")

    return MOCK_TC_QA
