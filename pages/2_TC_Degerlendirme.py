"""
BA&QA Intelligence Platform — 🧪 Test Case Değerlendirme
"""
import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.sidebar import render_custom_sidebar
from utils.config import get_credentials, all_creds_available, TC_CRITERIA, emoji_score, get_gemini_keys, get_anthropic_key, get_all_models, GEMINI_MODEL
from integrations.jira_client import (jira_search, jira_get_issue, jira_add_label,
                                       jira_update_labels, jira_add_comment)
from integrations.google_docs import (fetch_google_doc_via_proxy, fetch_google_sheets_as_text,
                                       extract_doc_id, extract_spreadsheet_id, find_linked_ba_key)
from agents.prompts import build_tc_evaluation_prompt, parse_json_response, format_tc_report
from agents.ai_client import call_ai
from data.database import save_analysis

st.set_page_config(page_title="TC Değerlendirme — BA&QA", page_icon="🧪", layout="wide")

# Custom sidebar
render_custom_sidebar(active_page="tc")

# ── Modern CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    .main {
        background: #0a0e17;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    /* Breadcrumb */
    .breadcrumb {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 0;
        margin-bottom: 24px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #64748b;
    }
    .breadcrumb a {
        color: #06b6d4;
        text-decoration: none;
        transition: color 0.2s;
    }
    .breadcrumb a:hover {
        color: #3b82f6;
    }
    .breadcrumb .separator {
        color: #475569;
    }
    .breadcrumb .current {
        color: #f1f5f9;
        font-weight: 500;
    }

    /* Header */
    .page-header {
        margin-bottom: 32px;
    }
    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }
    .page-subtitle {
        color: #94a3b8;
        font-size: 16px;
        line-height: 1.6;
        font-family: 'DM Sans', sans-serif;
    }
    .pipeline-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.2);
        border-radius: 20px;
        padding: 6px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #10b981;
        margin-top: 8px;
    }

    /* Queue Table */
    .queue-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: #f1f5f9;
        margin: 1.5rem 0 1rem 0;
    }
    .task-row {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.2s;
    }
    .task-row:hover {
        border-color: rgba(16,185,129,0.3);
        background: #1e2742;
    }
    .task-key {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: #10b981;
        font-size: 13px;
        flex: 0 0 110px;
    }
    .task-summary {
        flex: 1;
        font-size: 13px;
        color: #cbd5e1;
    }
    .task-ba {
        flex: 0 0 120px;
        font-size: 12px;
        color: #94a3b8;
    }

    /* Score Dashboard */
    .score-main {
        text-align: center;
        padding: 2rem;
        background: #1a2236;
        border-radius: 16px;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
    }
    .score-main::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    .score-main.pass::before {
        background: linear-gradient(135deg, #10b981, #06b6d4);
    }
    .score-main.fail::before {
        background: linear-gradient(135deg, #ef4444, #dc2626);
    }
    .score-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 64px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .score-status {
        font-size: 22px;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Criteria Grid */
    .criteria-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 1.5rem 0;
    }
    .criterion-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 16px;
    }
    .criterion-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .criterion-label {
        font-size: 13px;
        color: #cbd5e1;
        font-weight: 500;
    }
    .criterion-score {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 16px;
        color: #f1f5f9;
    }
    .criterion-desc {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.5;
        margin-top: 8px;
    }

    /* Progress Bar */
    .progress-container {
        background: #0f1624;
        border-radius: 6px;
        height: 6px;
        overflow: hidden;
        margin-top: 8px;
    }
    .progress-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s;
    }
    .progress-green { background: linear-gradient(90deg, #10b981, #06b6d4); }
    .progress-yellow { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
    .progress-red { background: linear-gradient(90deg, #ef4444, #dc2626); }

    /* Lists */
    .insights-section {
        margin: 1.5rem 0;
    }
    .insights-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .insight-item {
        background: #1a2236;
        border-left: 3px solid;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 13px;
        color: #cbd5e1;
        line-height: 1.6;
    }
    .insight-item.positive { border-color: #10b981; }
    .insight-item.negative { border-color: #ef4444; }
    .insight-item.neutral { border-color: #10b981; }

    @media (max-width: 768px) {
        .criteria-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ── Breadcrumb ──
st.markdown("""
<div class="breadcrumb">
    <a href="/">🏠 Ana Sayfa</a>
    <span class="separator">›</span>
    <span class="current">🧪 QA Değerlendirme</span>
</div>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="page-header">
    <div class="page-title">🧪 Test Case Kalite Değerlendirme</div>
    <div class="page-subtitle">Test Case dokümanlarını BA ile karşılaştırarak kalite analizi yapar</div>
    <div class="pipeline-badge">
        🤖 4-Agent Pipeline: JIRA & Sheet Scanner → Doc Merger → TC Evaluator → Reporter
    </div>
</div>
""", unsafe_allow_html=True)

# ── Model Selection ──
st.markdown("### ⚙️ Model Ayarları")
ALL_MODELS = get_all_models()

col1, col2 = st.columns(2)
with col1:
    # Get default model index
    current_model = st.session_state.get("tc_eval_model", GEMINI_MODEL)
    current_model_name = [k for k, v in ALL_MODELS.items() if v == current_model][0] if current_model in ALL_MODELS.values() else "Gemini 2.5 Flash"
    default_idx = list(ALL_MODELS.keys()).index(current_model_name) if current_model_name in ALL_MODELS.keys() else 4

    selected_model_name = st.selectbox(
        "Evaluation Model",
        options=list(ALL_MODELS.keys()),
        index=default_idx,
        help="TC değerlendirme için kullanılacak AI modeli"
    )
    selected_model = ALL_MODELS[selected_model_name]
    st.session_state["tc_eval_model"] = selected_model

with col2:
    st.info(f"🤖 **Seçili Model:** {selected_model_name}")

st.divider()

# ── Credential Check ──
gemini_keys = get_gemini_keys()
gemini_key = gemini_keys[0] if gemini_keys else ""
anthropic_key = get_anthropic_key()
_, jira_email, jira_token = get_credentials()

if not jira_email or not jira_token:
    st.warning("⚠️ Ana sayfadan JIRA bilgilerini girin.")
    st.stop()

# Check if we have the right API key for selected model
if selected_model.startswith("claude-") and not anthropic_key:
    st.warning("⚠️ Anthropic modeli seçtiniz ama API key girilmemiş. Ana sayfadan Anthropic API Key'i girin.")
    st.stop()
elif selected_model.startswith("gemini-") and not gemini_key:
    st.warning("⚠️ Gemini modeli seçtiniz ama API key girilmemiş. Ana sayfadan Gemini API Key'i girin.")
    st.stop()


def render_score_dashboard(data, criteria):
    genel_puan = data.get("genel_puan", 0)
    gecti = data.get("gecti_mi", False)
    score_color = "#10b981" if gecti else "#ef4444"
    status_text = "✅ GEÇTİ" if gecti else "❌ GEÇMEDİ"
    status_class = "pass" if gecti else "fail"

    st.markdown(f"""
    <div class="score-main {status_class}">
        <div class="score-value" style="color: {score_color};">{genel_puan}/100</div>
        <div class="score-status" style="color: {score_color};">{status_text}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="insights-title">📈 Kriter Puanları</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (key, label) in enumerate(criteria):
        skor = next((s for s in data.get("skorlar", []) if s.get("kriter") == key), None)
        puan = skor["puan"] if skor else 0
        progress_cls = "progress-green" if puan >= 8 else ("progress-yellow" if puan >= 6 else "progress-red")

        with cols[i % 3]:
            st.markdown(f"""
            <div class="criterion-card">
                <div class="criterion-header">
                    <span class="criterion-label">{emoji_score(puan)} {label}</span>
                    <span class="criterion-score">{puan}/10</span>
                </div>
                <div class="progress-container">
                    <div class="progress-fill {progress_cls}" style="width:{puan*10}%"></div>
                </div>
                <div class="criterion-desc">{skor.get('aciklama', '')[:120] if skor else ''}</div>
            </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        if data.get("guclu_yanlar"):
            st.markdown('<div class="insights-title">✅ Güçlü Yanlar</div>', unsafe_allow_html=True)
            for item in data["guclu_yanlar"]:
                st.markdown(f'<div class="insight-item positive">{item}</div>', unsafe_allow_html=True)

    with col_r:
        if data.get("kritik_eksikler"):
            st.markdown('<div class="insights-title">❌ Kritik Eksikler</div>', unsafe_allow_html=True)
            for item in data["kritik_eksikler"]:
                st.markdown(f'<div class="insight-item negative">{item}</div>', unsafe_allow_html=True)

    if data.get("iyilestirme_onerileri"):
        st.markdown('<div class="insights-title">💡 İyileştirme Önerileri</div>', unsafe_allow_html=True)
        for item in data["iyilestirme_onerileri"]:
            st.markdown(f'<div class="insight-item neutral">{item}</div>', unsafe_allow_html=True)


def fetch_tc_queue():
    jql = ("project = BAQA AND component = Test AND "
           "(labels not in (tc-qa-tamamlandi, tc-qa-devam-ediyor) OR labels is EMPTY) "
           "AND created >= startOfYear() AND status NOT IN (Cancelled,Done) ORDER BY updated DESC")
    try:
        issues = jira_search(jira_email, jira_token, jql, max_results=20)
    except Exception:
        return []
    queue = []
    for issue in issues:
        labels = issue.get("fields", {}).get("labels", [])
        summary = issue["fields"].get("summary", "")

        # Skip completed/in-progress tasks
        if "tc-qa-tamamlandi" in labels or "tc-qa-devam-ediyor" in labels:
            continue

        # Skip test/dummy tasks
        if "test" in labels or "test-task" in labels:
            continue
        if "TEST TEST" in summary or summary.endswith("(Test)"):
            continue

        desc = issue.get("fields", {}).get("description", "")
        tc_doc_id, tc_url = extract_spreadsheet_id(desc)
        if not tc_doc_id:
            tc_doc_id, tc_url = extract_doc_id(desc)
        if tc_doc_id:
            ba_key = find_linked_ba_key(issue)
            queue.append({
                "key": issue["key"],
                "summary": summary,
                "assignee": (issue["fields"].get("assignee") or {}).get("displayName", ""),
                "tc_doc_id": tc_doc_id, "tc_url": tc_url,
                "linked_ba_key": ba_key,
            })
    return queue


def run_tc_pipeline(selected_task: dict = None):
    status_container = st.container()
    result_container = st.container()

    with status_container:
        progress_bar = st.progress(0, text="🤖 Pipeline başlatılıyor...")

        with st.status("🔍 Adım 1: JIRA & Sheet Tarayıcı", expanded=True) as step1:
            selected = selected_task or (fetch_tc_queue() or [None])[0]
            if not selected:
                st.warning("Uygun TC task bulunamadı.")
                return None
            jira_add_label(jira_email, jira_token, selected["key"], "tc-qa-devam-ediyor")
            ba_text, has_ba = "", False
            if selected.get("linked_ba_key"):
                try:
                    ba_issue = jira_get_issue(jira_email, jira_token, selected["linked_ba_key"])
                    ba_doc_id, _ = extract_doc_id(ba_issue.get("fields", {}).get("description", ""))
                    if ba_doc_id:
                        ba_text = fetch_google_doc_via_proxy(ba_doc_id)
                        has_ba = True
                except Exception:
                    pass
            st.write(f"✅ **{selected['key']}** — BA: {'✅' if has_ba else '❌ Yok'}")
            step1.update(label=f"✅ Adım 1: {selected['key']}", state="complete", expanded=False)
        progress_bar.progress(25, text="🔄 Adım 2/4 — Sheet'ler okunuyor...")

        with st.status("📄 Adım 2: Doküman Birleştirici", expanded=True) as step2:
            try:
                tc_text = fetch_google_sheets_as_text(selected["tc_doc_id"])
            except Exception as e:
                st.error(f"Sheets hatası: {e}")
                return None
            if len(tc_text.strip()) < 50:
                st.error("TC dokümanı boş.")
                return None
            st.write(f"✅ **{len(tc_text):,}** karakter okundu")
            step2.update(label=f"✅ Adım 2: {len(tc_text):,} karakter", state="complete", expanded=False)
        progress_bar.progress(50, text="🔄 Adım 3/4 — AI değerlendiriyor...")

        with st.status("🧠 Adım 3: TC Kalite Değerlendirici", expanded=True) as step3:
            eval_prompt = build_tc_evaluation_prompt(tc_text, ba_text, has_ba)

            # Build system prompt
            system_prompt = """Sen son derece deneyimli bir test mühendisliği kalite kontrol uzmanısın.

STANDART: Loodos standart şablonu (23 sütun) beklenir.

PUANLAMA KURALLARI:
- Varsayılan başlangıç: 5/10
- 8+ puan = MÜKEMMEL kalite
- Sadece happy path varsa edge_cases için MAX 4/10
- Genel puan = (8 kriter ortalaması × 100) / 80
- Geçme eşiği = 60+

TÜM çıktılar TÜRKÇE olmalı.
Sadece JSON formatında yanıt ver."""

            eval_data = None
            for attempt in range(3):
                try:
                    result = call_ai(
                        system_prompt=system_prompt,
                        user_content=eval_prompt,
                        anthropic_key=anthropic_key,
                        gemini_key=gemini_key,
                        model=selected_model,
                        max_tokens=8000
                    )

                    if result.get("stop_reason") == "max_tokens":
                        st.warning("⚠️ Yanıt token limitine ulaştı, devam ediyor...")

                    eval_data = result
                    if eval_data and eval_data.get("skorlar"):
                        break
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "rate" in error_msg.lower() or "limit" in error_msg.lower():
                        wait = 30 * (attempt + 1)
                        st.warning(f"⏳ Rate limit — {wait}s bekleniyor...")
                        time.sleep(wait)
                    else:
                        st.error(f"AI hatası: {e}")
                        if attempt == 2:
                            return None

            if not eval_data or not eval_data.get("skorlar"):
                st.error("AI yanıtı parse edilemedi.")
                return None
            puan = eval_data.get('genel_puan', 0)
            gecti = eval_data.get('gecti_mi', False)
            st.write(f"✅ Puan: **{puan}/100** {'✅ GEÇTİ' if gecti else '❌ GEÇMEDİ'}")
            step3.update(label=f"✅ Adım 3: {puan}/100", state="complete", expanded=False)
        progress_bar.progress(75, text="🔄 Adım 4/4 — JIRA güncelleniyor...")

        with st.status("📝 Adım 4: TC Raporcu", expanded=True) as step4:
            report_text = format_tc_report(eval_data)
            jira_add_comment(jira_email, jira_token, selected["key"], report_text)
            new_label = "tc-qa-gecti" if gecti else "tc-qa-gecmedi"
            jira_update_labels(jira_email, jira_token, selected["key"],
                               ["tc-qa-devam-ediyor"], ["tc-qa-tamamlandi", new_label])
            save_analysis(selected["key"], "tc", puan, gecti, eval_data, report_text)
            st.write(f"✅ JIRA güncellendi — Label: **{new_label}**")
            step4.update(label="✅ Adım 4: JIRA güncellendi", state="complete", expanded=False)
        progress_bar.progress(100, text="✅ Pipeline tamamlandı!")

    with result_container:
        st.markdown("---")
        st.markdown(f'<div class="queue-header">🧪 Sonuç: {selected["key"]} - {selected["summary"]}</div>', unsafe_allow_html=True)
        render_score_dashboard(eval_data, TC_CRITERIA)
        with st.expander("📄 JIRA Comment (Ham Rapor)"):
            st.text(report_text)
    return eval_data


# ── Task Queue UI ──
if st.button("🔍 TC Kuyruğunu Tara", use_container_width=True):
    with st.spinner("JIRA taranıyor..."):
        st.session_state["tc_queue"] = fetch_tc_queue()

if "tc_queue" in st.session_state and st.session_state["tc_queue"]:
    tc_queue = st.session_state["tc_queue"]
    st.markdown(f'<div class="queue-header">🧪 Kuyrukta {len(tc_queue)} Task Var</div>', unsafe_allow_html=True)

    for task in tc_queue:
        col1, col2, col3, col4 = st.columns([1.5, 5, 1.5, 1])
        with col1:
            st.markdown(f'<span class="task-key">{task["key"]}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="task-summary">{task["summary"][:70]}</span>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<span class="task-ba">BA: {task.get("linked_ba_key", "—")}</span>', unsafe_allow_html=True)
        with col4:
            if st.button("▶️", key=f"tc_run_{task['key']}"):
                st.session_state["tc_selected_task"] = task

    st.markdown("---")

if "tc_selected_task" in st.session_state and st.session_state["tc_selected_task"]:
    task = st.session_state.pop("tc_selected_task")
    start = time.time()
    result = run_tc_pipeline(selected_task=task)
    if result:
        st.success(f"✅ {task['key']} tamamlandı! ({time.time()-start:.1f}s)")

if st.button("⚡ Sıradakini Otomatik Değerlendir", type="primary", use_container_width=True):
    start = time.time()
    result = run_tc_pipeline()
    if result:
        st.success(f"✅ Tamamlandı! ({time.time()-start:.1f}s)")
