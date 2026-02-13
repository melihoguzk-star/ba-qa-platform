"""
BA&QA Intelligence Platform — 🧪 Test Case Değerlendirme
"""
import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.sidebar import render_custom_sidebar
from utils.config import get_credentials, all_creds_available, TC_CRITERIA, emoji_score
from integrations.jira_client import (jira_search, jira_get_issue, jira_add_label,
                                       jira_update_labels, jira_add_comment)
from integrations.google_docs import (fetch_google_doc_via_proxy, fetch_google_sheets_as_text,
                                       extract_doc_id, extract_spreadsheet_id, find_linked_ba_key)
from agents.agent_definitions import create_tc_agents
from agents.prompts import build_tc_evaluation_prompt, parse_json_response, format_tc_report
from data.database import save_analysis

st.set_page_config(page_title="TC Değerlendirme — BA&QA", page_icon="🧪", layout="wide")

# Custom sidebar
render_custom_sidebar(active_page="tc")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;700&display=swap');
    .stApp { font-family: 'Outfit', sans-serif; }
    .score-bar-bg { background: #1a1a2e; border-radius: 6px; height: 8px; overflow: hidden; margin: 4px 0; }
    .score-bar-fill { height: 100%; border-radius: 6px; transition: width 0.5s; }
    .score-green { background: linear-gradient(90deg, #00ff88, #00cc6a); }
    .score-yellow { background: linear-gradient(90deg, #ffd700, #ffaa00); }
    .score-red { background: linear-gradient(90deg, #ff4444, #cc0000); }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🧪 Test Case (TC) Kalite Değerlendirme")
st.markdown("**4 Agent Pipeline:** JIRA & Sheet Tarayıcı → Doküman Birleştirici → TC Değerlendirici → Raporcu")

gemini_key, jira_email, jira_token = get_credentials()
if not all_creds_available():
    st.warning("⚠️ Ana sayfadan Gemini API Key ve JIRA bilgilerini gir.")
    st.stop()


def render_score_dashboard(data, criteria):
    genel_puan = data.get("genel_puan", 0)
    gecti = data.get("gecti_mi", False)
    score_color = "#00ff88" if gecti else "#ff4444"
    status_text = "✅ GEÇTİ" if gecti else "❌ GEÇMEDİ"
    st.markdown(f"""
    <div style="text-align:center; padding: 1.5rem; background: linear-gradient(145deg, #1a1a2e, #16213e);
         border-radius: 16px; border: 2px solid {score_color}; margin: 1rem 0;">
        <div style="font-size: 3rem; font-weight: 700; color: {score_color};
             font-family: 'JetBrains Mono', monospace;">{genel_puan}/100</div>
        <div style="font-size: 1.3rem; margin-top: 0.3rem; color: #e0e0e0;">{status_text}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("#### 📈 Kriter Puanları")
    cols = st.columns(3)
    for i, (key, label) in enumerate(criteria):
        skor = next((s for s in data.get("skorlar", []) if s.get("kriter") == key), None)
        puan = skor["puan"] if skor else 0
        bar_cls = "score-green" if puan >= 8 else ("score-yellow" if puan >= 6 else "score-red")
        with cols[i % 3]:
            st.markdown(f"""<div style="margin: 6px 0;">
                <div style="display:flex; justify-content:space-between; font-size:0.82rem;">
                    <span style="color:#ccc;">{emoji_score(puan)} {label}</span>
                    <span style="font-weight:700; color:#e0e0e0;">{puan}/10</span>
                </div>
                <div class="score-bar-bg"><div class="score-bar-fill {bar_cls}" style="width:{puan*10}%"></div></div>
            </div>""", unsafe_allow_html=True)
            if skor and skor.get("aciklama"):
                st.caption(skor["aciklama"][:150])
    col_l, col_r = st.columns(2)
    with col_l:
        if data.get("guclu_yanlar"):
            st.markdown("#### ✅ Güçlü Yanlar")
            for item in data["guclu_yanlar"]: st.markdown(f"- {item}")
    with col_r:
        if data.get("kritik_eksikler"):
            st.markdown("#### ❌ Kritik Eksikler")
            for item in data["kritik_eksikler"]: st.markdown(f"- {item}")
    if data.get("iyilestirme_onerileri"):
        st.markdown("#### 💡 İyileştirme Önerileri")
        for i, item in enumerate(data["iyilestirme_onerileri"], 1): st.markdown(f"{i}. {item}")


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
        if "tc-qa-tamamlandi" in labels or "tc-qa-devam-ediyor" in labels:
            continue
        desc = issue.get("fields", {}).get("description", "")
        tc_doc_id, tc_url = extract_spreadsheet_id(desc)
        if not tc_doc_id:
            tc_doc_id, tc_url = extract_doc_id(desc)
        if tc_doc_id:
            ba_key = find_linked_ba_key(issue)
            queue.append({
                "key": issue["key"],
                "summary": issue["fields"].get("summary", ""),
                "assignee": (issue["fields"].get("assignee") or {}).get("displayName", ""),
                "tc_doc_id": tc_doc_id, "tc_url": tc_url,
                "linked_ba_key": ba_key,
            })
    return queue


def run_tc_pipeline(selected_task: dict = None):
    _, _, agent3, _ = create_tc_agents(gemini_key)
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
            eval_data = None
            for attempt in range(3):
                try:
                    resp = agent3.run(eval_prompt)
                    content = resp.content if resp else ""
                    if "429" in content or "RESOURCE_EXHAUSTED" in content:
                        time.sleep(30 * (attempt + 1))
                        continue
                    eval_data = parse_json_response(content)
                    if eval_data and eval_data.get("skorlar"):
                        break
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        time.sleep(30 * (attempt + 1))
                    else:
                        st.error(f"AI hatası: {e}")
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
        st.markdown(f"### 🧪 Sonuç: {selected['key']} - {selected['summary']}")
        render_score_dashboard(eval_data, TC_CRITERIA)
        with st.expander("📄 JIRA Comment (Ham Rapor)"):
            st.text(report_text)
    return eval_data


# ── Task Kuyruğu ──
if st.button("🔍 TC Kuyruğunu Tara", use_container_width=True):
    with st.spinner("JIRA taranıyor..."):
        st.session_state["tc_queue"] = fetch_tc_queue()

if "tc_queue" in st.session_state and st.session_state["tc_queue"]:
    tc_queue = st.session_state["tc_queue"]
    st.markdown(f"**🧪 Kuyrukta {len(tc_queue)} task var:**")
    for task in tc_queue:
        c1, c2, c3, c4 = st.columns([1.5, 4, 2, 1.5])
        with c1: st.markdown(f"**{task['key']}**")
        with c2: st.caption(task["summary"][:60])
        with c3: st.caption(f"BA: {task.get('linked_ba_key', '—')}")
        with c4:
            if st.button("▶️", key=f"tc_run_{task['key']}"):
                st.session_state["tc_selected_task"] = task

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
