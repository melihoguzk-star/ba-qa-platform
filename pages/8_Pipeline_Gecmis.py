"""Sayfa 3: Pipeline Geçmişi."""
import json
import streamlit as st
from components.sidebar import render_custom_sidebar

st.set_page_config(page_title="Geçmiş", page_icon="📜", layout="wide")
render_custom_sidebar(active_page="pipeline_gecmis")
st.title("📜 Pipeline Geçmişi")

try:
    from data.database import get_recent_pipeline_runs as get_recent_runs, get_pipeline_run_outputs as get_run_outputs

    runs = get_recent_runs(20)
    if not runs:
        st.info("Henüz pipeline çalıştırılmadı.")
        st.stop()

    st.metric("Toplam Çalıştırma", len(runs))

    for r in runs:
        status_icon = "✅" if r["status"] == "completed" else "🔄" if r["status"] == "running" else "❌"
        avg_score = (r["ba_score"] + r["ta_score"] + r["tc_score"]) / 3 if r["ba_score"] else 0

        with st.expander(
            f"{status_icon} **{r['project_name']}** — "
            f"BA:{r['ba_score']:.0f} | TA:{r['ta_score']:.0f} | TC:{r['tc_score']:.0f} | "
            f"Ort:{avg_score:.0f} — {r['created_at'][:16]}"
        ):
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("BA", f"{r['ba_score']:.0f}", delta=f"{r['ba_revisions']} rev")
            col2.metric("TA", f"{r['ta_score']:.0f}", delta=f"{r['ta_revisions']} rev")
            col3.metric("TC", f"{r['tc_score']:.0f}", delta=f"{r['tc_revisions']} rev")
            col4.metric("Süre", f"{r['total_time_sec']}s")
            col5.metric("Dosya", r.get("brd_filename", "-"))

            outputs = get_run_outputs(r["id"])
            if outputs:
                st.markdown("**Aşama Detayları:**")
                for o in outputs:
                    forced = " ⚠️ forced" if o["forced_pass"] else ""
                    st.caption(
                        f"**{o['stage'].upper()}** — Rev: {o['revision_number']} | "
                        f"Süre: {o['generation_time_sec']}s{forced}"
                    )

except Exception as e:
    st.error(f"Veritabanı hatası: {e}")
