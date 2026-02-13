"""
BA&QA Intelligence Platform — 📈 Raporlar & Geçmiş
"""
import streamlit as st
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data.database import get_stats, get_recent_analyses
from utils.config import emoji_score

st.set_page_config(page_title="Raporlar — BA&QA", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;700&display=swap');
    .stApp { font-family: 'Outfit', sans-serif; }
    .stat-big { font-family: 'JetBrains Mono', monospace; font-size: 2.5rem; font-weight: 700; }
    .score-bar-bg { background: #1a1a2e; border-radius: 6px; height: 8px; overflow: hidden; margin: 4px 0; }
    .score-bar-fill { height: 100%; border-radius: 6px; }
    .score-green { background: linear-gradient(90deg, #00ff88, #00cc6a); }
    .score-red { background: linear-gradient(90deg, #ff4444, #cc0000); }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📈 Raporlar & Analiz Geçmişi")

stats = get_stats()

# ── KPI'lar ──
st.markdown("### 📊 Özet İstatistikler")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Toplam Analiz", stats["total"])

ba_s = next((s for s in stats["by_type"] if s["analysis_type"] == "ba"), {})
tc_s = next((s for s in stats["by_type"] if s["analysis_type"] == "tc"), {})
design_s = next((s for s in stats["by_type"] if s["analysis_type"] == "design"), {})

with col2:
    cnt = ba_s.get("c", 0)
    avg = ba_s.get("avg_puan", 0) or 0
    gecen = ba_s.get("gecen", 0)
    st.metric("BA Analiz", cnt, f"Ort: {avg:.0f} | Geçen: {gecen}")

with col3:
    cnt = tc_s.get("c", 0)
    avg = tc_s.get("avg_puan", 0) or 0
    gecen = tc_s.get("gecen", 0)
    st.metric("TC Analiz", cnt, f"Ort: {avg:.0f} | Geçen: {gecen}")

with col4:
    cnt = design_s.get("c", 0)
    st.metric("Design Analiz", cnt)

# ── 7 Günlük Trend ──
st.markdown("---")
st.markdown("### 📉 Son 7 Gün Trend")
trend_data = stats.get("recent_7_days", [])
if trend_data:
    import pandas as pd
    df = pd.DataFrame(trend_data)
    if not df.empty and "gun" in df.columns:
        pivot = df.pivot_table(index="gun", columns="analysis_type", values="avg_puan", aggfunc="mean")
        st.line_chart(pivot, height=300)
    else:
        st.info("Son 7 günde veri yok.")
else:
    st.info("Son 7 günde analiz yapılmadı.")

# ── Filtreli Geçmiş ──
st.markdown("---")
st.markdown("### 📋 Analiz Geçmişi")

col_f1, col_f2 = st.columns([1, 3])
with col_f1:
    filter_type = st.selectbox("Tip Filtre", ["Tümü", "BA", "TC", "Design"])

type_map = {"Tümü": None, "BA": "ba", "TC": "tc", "Design": "design"}
analyses = get_recent_analyses(limit=50, analysis_type=type_map[filter_type])

if analyses:
    for r in analyses:
        puan = r.get("genel_puan", 0)
        gecti = r.get("gecti_mi", 0)
        tip = {"ba": "📋 BA", "tc": "🧪 TC", "design": "🎨 Design"}.get(r["analysis_type"], "❓")
        color = "#00ff88" if gecti else "#ff4444"
        icon = "✅" if gecti else "❌"

        with st.expander(f"{tip} {r.get('jira_key', '—')} — {puan:.0f}/100 {icon} — {r.get('created_at', '')[:16]}"):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"**Puan:** {puan:.0f}/100 {icon}")
                st.markdown(f"**Tip:** {r['analysis_type'].upper()}")
                st.markdown(f"**Tetikleyen:** {r.get('triggered_by', 'manual')}")
                st.markdown(f"**Tarih:** {r.get('created_at', '')}")
            with c2:
                result = json.loads(r.get("result_json", "{}"))
                if result.get("skorlar"):
                    for s in result["skorlar"]:
                        p = s.get("puan", 0)
                        st.markdown(f"{emoji_score(p)} **{s['kriter']}**: {p}/10")

            if r.get("report_text"):
                st.text_area("Rapor", r["report_text"], height=200, disabled=True, key=f"rpt_{r['id']}")

    # CSV Export
    st.markdown("---")
    import csv, io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "jira_key", "analysis_type", "genel_puan", "gecti_mi", "created_at"])
    writer.writeheader()
    for r in analyses:
        writer.writerow({k: r.get(k, "") for k in ["id", "jira_key", "analysis_type", "genel_puan", "gecti_mi", "created_at"]})
    st.download_button("📥 CSV İndir", data=output.getvalue(), file_name="baqa_analyses.csv", mime="text/csv", use_container_width=True)
else:
    st.info("Henüz analiz kaydı yok.")
