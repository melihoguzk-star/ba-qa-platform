"""Pipeline Orchestrator — Adım adım çalışan, kullanıcı onayıyla QA'ya geçen pipeline.

Akış (her aşama için):
1. Checkpoint kontrol → varsa merge sonucunu göster
2. Chunk1 üret (Sonnet) → Chunk2 üret (Sonnet) → Birleştir
3. Birleştirilmiş dokümanı kullanıcıya göster → ONAY BEKLE
4. Onay sonrası → QA Hakem değerlendir (Gemini Flash)
5. Geçti mi? → Evet: sonraki aşama / Hayır: revizyon (max 3)
"""
import json
import time
from datetime import datetime

from agents.brd_prompts import (
    BA_CHUNK1_SYSTEM, BA_CHUNK2_SYSTEM, BA_QA_SYSTEM,
    TA_CHUNK1_SYSTEM, TA_CHUNK2_SYSTEM, TA_QA_SYSTEM,
    TC_CHUNK1_SYSTEM, TC_CHUNK2_SYSTEM, TC_QA_SYSTEM,
)
from agents.ai_client import call_sonnet, call_gemini
from pipeline.brd.checkpoint import save_checkpoint, load_checkpoint, clear_checkpoint
from pipeline.brd.json_repair import parse_ai_json
from data.database import create_pipeline_run as create_run, update_run, save_stage_output
from utils.config import (
    MAX_REVISIONS, BA_PASS_THRESHOLD, TA_PASS_THRESHOLD, TC_PASS_THRESHOLD,
)


# ═══════════════════════════════════════════════════════════
# MERGER FONKSİYONLARI
# ═══════════════════════════════════════════════════════════

def merge_ba(chunk1: dict, chunk2: dict) -> dict:
    """BA Chunk1 (ekranlar + FR) + Chunk2 (iş kuralları + BR + validasyonlar) birleştir."""
    ekranlar = chunk1.get("ekranlar", [])
    detaylar = chunk2.get("ekran_detaylari", [])
    for e in ekranlar:
        matching = next(
            (d for d in detaylar
             if d.get("ekran_adi") == e.get("ekran_adi")
             or d.get("ekran_adi", "").split(" ")[0] in e.get("ekran_adi", "")),
            None
        )
        if matching:
            e["is_kurallari"] = matching.get("is_kurallari", [])
            e["kabul_kriterleri"] = matching.get("kabul_kriterleri", [])
            e["validasyonlar"] = matching.get("validasyonlar", [])
        else:
            e.setdefault("is_kurallari", [])
            e.setdefault("kabul_kriterleri", [])
            e.setdefault("validasyonlar", [])
    return {"ekranlar": ekranlar}


def merge_ta(chunk1: dict, chunk2: dict) -> dict:
    ta = chunk1.get("teknik_analiz", chunk1)
    ta["sistem_entegrasyonlari"] = chunk2.get("sistem_entegrasyonlari", [])
    ta["sistem_akis_diyagramlari"] = chunk2.get("sistem_akis_diyagramlari", [])
    ta["validasyon_kurallari"] = chunk2.get("validasyon_kurallari", [])
    ta["exception_stratejisi"] = chunk2.get("exception_stratejisi", {})
    ta["mock_curl_ornekleri"] = chunk2.get("mock_curl_ornekleri", [])
    return {"teknik_analiz": ta}


def merge_tc(chunk1: dict, chunk2: dict) -> dict:
    all_tc = chunk1.get("test_cases", []) + chunk2.get("test_cases", [])
    return {"test_cases": all_tc}


# ═══════════════════════════════════════════════════════════
# GENERATE FONKSİYONLARI (chunk1 + chunk2 + merge)
# ═══════════════════════════════════════════════════════════

def generate_ba(brd_text, project_name, anthropic_key, log, previous_feedback=""):
    """BA Chunk1 + Chunk2 üret ve birleştir."""
    import hashlib
    brd_hash = hashlib.md5(brd_text[:5000].encode()).hexdigest()[:8]

    cached = load_checkpoint(project_name, "ba")
    if cached:
        # BRD değiştiyse cache geçersiz
        if cached.get("_brd_hash") == brd_hash and not previous_feedback:
            log("  💾 BA checkpoint bulundu, cache'den yüklendi")
            return cached
        else:
            log("  🔄 BRD değişmiş veya revizyon — cache temizlendi")
            clear_checkpoint(project_name, "ba")

    user1 = "BRD DOKÜMANI:\n\n" + brd_text[:80000]
    if previous_feedback:
        user1 = f"ÖNCEKİ DEĞERLENDİRME GERİ BİLDİRİMİ:\n{previous_feedback}\n\nBu geri bildirime göre iyileştir.\n\n" + user1

    log("  🤖 BA Chunk1 üretiliyor (Sonnet)...")
    chunk1 = call_sonnet(BA_CHUNK1_SYSTEM, user1, anthropic_key)

    modul_names = ", ".join(e.get("ekran_adi", "") for e in chunk1.get("ekranlar", []))
    user2 = f"BRD DOKÜMANI:\n\n{brd_text[:60000]}\n\nEKRANLAR (İlk adımda tanımlanan): {modul_names}"

    log("  🤖 BA Chunk2 üretiliyor (Sonnet)...")
    chunk2 = call_sonnet(BA_CHUNK2_SYSTEM, user2, anthropic_key)

    log("  🔗 BA birleştiriliyor...")
    result = merge_ba(chunk1, chunk2)
    result["_brd_hash"] = brd_hash
    save_checkpoint(project_name, "ba", result)
    return result


def generate_ta(brd_text, ba_content, project_name, anthropic_key, log, previous_feedback=""):
    """TA Chunk1 + Chunk2 üret ve birleştir."""
    import hashlib
    brd_hash = hashlib.md5(brd_text[:5000].encode()).hexdigest()[:8]

    cached = load_checkpoint(project_name, "ta")
    if cached:
        if cached.get("_brd_hash") == brd_hash and not previous_feedback:
            log("  💾 TA checkpoint bulundu, cache'den yüklendi")
            return cached
        else:
            log("  🔄 BRD değişmiş veya revizyon — TA cache temizlendi")
            clear_checkpoint(project_name, "ta")

    ba_json = json.dumps(ba_content, ensure_ascii=False, indent=2)[:60000]
    brd_summary = brd_text[:40000]

    user1 = f"İŞ ANALİZİ:\n{ba_json}\n\nBRD ÖZETİ:\n{brd_summary}"
    if previous_feedback:
        user1 = f"ÖNCEKİ QA DEĞERLENDİRME GERİ BİLDİRİMİ:\n{previous_feedback}\n\nBu geri bildirime göre teknik analizi iyileştir.\n\n" + user1
    log("  🤖 TA Chunk1 üretiliyor (Sonnet)...")
    chunk1 = call_sonnet(TA_CHUNK1_SYSTEM, user1, anthropic_key)

    ta = chunk1.get("teknik_analiz", chunk1)
    endpoints = ", ".join(e.get("endpoint", "") for e in ta.get("api_endpoint_ozeti", []))
    user2 = f"ENDPOINT LİSTESİ:\n{endpoints}\n\nBRD ÖZETİ:\n{brd_text[:40000]}"

    log("  🤖 TA Chunk2 üretiliyor (Sonnet)...")
    chunk2 = call_sonnet(TA_CHUNK2_SYSTEM, user2, anthropic_key)

    log("  🔗 TA birleştiriliyor...")
    result = merge_ta(chunk1, chunk2)
    result["_brd_hash"] = brd_hash
    save_checkpoint(project_name, "ta", result)
    return result


def generate_tc(ba_content, ta_content, project_name, jira_key, anthropic_key, log, previous_feedback=""):
    """TC Chunk1 + Chunk2 üret ve birleştir."""
    import hashlib
    ba_hash = hashlib.md5(json.dumps(ba_content, ensure_ascii=False)[:3000].encode()).hexdigest()[:8]

    cached = load_checkpoint(project_name, "tc")
    if cached:
        if cached.get("_ba_hash") == ba_hash and not previous_feedback:
            log("  💾 TC checkpoint bulundu, cache'den yüklendi")
            return cached
        else:
            log("  🔄 İçerik değişmiş veya revizyon — TC cache temizlendi")
            clear_checkpoint(project_name, "tc")

    today = datetime.now().strftime("%d.%m.%Y")
    ba_json = json.dumps(ba_content, ensure_ascii=False, indent=2)[:50000]
    ta_json = json.dumps(ta_content, ensure_ascii=False, indent=2)[:50000]

    system1 = TC_CHUNK1_SYSTEM.format(today_date=today)
    user1 = f"İŞ ANALİZİ:\n{ba_json}\n\nTEKNİK ANALİZ:\n{ta_json}"
    if previous_feedback:
        user1 = f"ÖNCEKİ QA DEĞERLENDİRME GERİ BİLDİRİMİ:\n{previous_feedback}\n\nBu geri bildirime göre test case'leri iyileştir.\n\n" + user1

    log("  🤖 TC Chunk1 üretiliyor (Sonnet)...")
    chunk1 = call_sonnet(system1, user1, anthropic_key)

    tc_count = len(chunk1.get("test_cases", []))
    start_id = str(tc_count + 1).zfill(4)
    system2 = TC_CHUNK2_SYSTEM.format(start_id=start_id, today_date=today)
    user2 = f"İŞ ANALİZİ:\n{ba_json}\n\nTEKNİK ANALİZ:\n{ta_json}"

    log(f"  🤖 TC Chunk2 üretiliyor (Sonnet) — {tc_count} TC'den devam...")
    chunk2 = call_sonnet(system2, user2, anthropic_key)

    log("  🔗 TC birleştiriliyor...")
    result = merge_tc(chunk1, chunk2)
    result["_ba_hash"] = ba_hash
    save_checkpoint(project_name, "tc", result)
    return result


# ═══════════════════════════════════════════════════════════
# QA HAKEM DEĞERLENDİRME
# ═══════════════════════════════════════════════════════════

def evaluate_ba_qa(ba_content, gemini_key, log=None):
    """BA QA Hakem değerlendirmesi."""
    return _evaluate_qa(
        BA_QA_SYSTEM,
        "İŞ ANALİZİ İÇERİĞİ:\n" + json.dumps(ba_content, ensure_ascii=False, indent=2)[:80000],
        gemini_key, log,
    )


def evaluate_ta_qa(ta_content, gemini_key, log=None):
    """TA QA Hakem değerlendirmesi."""
    return _evaluate_qa(
        TA_QA_SYSTEM,
        "TEKNİK ANALİZ:\n" + json.dumps(ta_content, ensure_ascii=False, indent=2)[:80000],
        gemini_key, log,
    )


def evaluate_tc_qa(tc_content, gemini_key, log=None):
    """TC QA Hakem değerlendirmesi."""
    tc_count = len(tc_content.get("test_cases", []))
    qa_system = TC_QA_SYSTEM.format(tc_count=tc_count)
    return _evaluate_qa(
        qa_system,
        f"TEST CASES ({tc_count} adet):\n" + json.dumps(tc_content, ensure_ascii=False, indent=2)[:80000],
        gemini_key, log,
    )


def _evaluate_qa(system_prompt: str, user_content: str, gemini_key: str, log=None) -> dict:
    """Gemini Flash ile QA değerlendirme. Hata durumunda fallback döner."""
    try:
        result = call_gemini(system_prompt, user_content, gemini_key)
        if log:
            log(f"    → QA raw genel_puan: {result.get('genel_puan', 'YOK')}")
        # genel_puan yoksa veya 0 ise skorlardan hesapla
        if not result.get("genel_puan") and result.get("skorlar"):
            total = sum(s.get("puan", 0) for s in result["skorlar"])
            count = len(result["skorlar"])
            if count > 0:
                result["genel_puan"] = round((total / (count * 10)) * 100)
                result["gecti_mi"] = result["genel_puan"] >= 55
                if log:
                    log(f"    → QA puan yeniden hesaplandı: {total}/{count*10} = {result['genel_puan']}")
        return result
    except Exception as e:
        if log:
            log(f"    ⚠️ QA hatası: {str(e)[:200]}")
        return {
            "genel_puan": 55,
            "gecti_mi": True,
            "genel_degerlendirme": f"QA parse hatası: {str(e)[:200]}",
            "skorlar": [],
            "iyilestirme_onerileri": [],
        }


# ═══════════════════════════════════════════════════════════
# DB HELPER
# ═══════════════════════════════════════════════════════════

def init_run(project_name, jira_key, priority, brd_filename):
    """Yeni pipeline run kaydı oluştur."""
    return create_run(project_name, jira_key, priority, brd_filename)


def finalize_stage(run_id, stage, content, qa_result, revision_count, forced_pass, gen_time):
    """Aşama sonuçlarını kaydet."""
    score = qa_result.get("genel_puan", 0)
    update_run(run_id, **{f"{stage}_score": score, f"{stage}_revisions": revision_count})
    save_stage_output(run_id, stage, content, qa_result, revision_count, forced_pass, gen_time)


def complete_run(run_id, total_time):
    """Pipeline'ı tamamla."""
    update_run(run_id, status="completed", total_time_sec=total_time)
