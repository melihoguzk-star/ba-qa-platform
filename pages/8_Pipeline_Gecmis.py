"""Sayfa 3: Pipeline Geçmişi."""
import json
import streamlit as st
from components.sidebar import render_custom_sidebar

st.set_page_config(page_title="Geçmiş", page_icon="📜", layout="wide")
render_custom_sidebar(active_page="pipeline_gecmis")
st.title("📜 Pipeline Geçmişi")

def show_qa_result(qa_result, stage_name):
    """QA hakem sonuçlarını gösterir."""
    if not qa_result:
        st.info(f"{stage_name} QA sonucu mevcut değil.")
        return

    score = qa_result.get("genel_puan", 0)
    passed = qa_result.get("gecti_mi", False)

    # Genel değerlendirme
    if passed:
        st.success(f"✅ {stage_name} QA Geçti — Puan: {score}/100")
    else:
        st.warning(f"⚠️ {stage_name} QA Geçmedi — Puan: {score}/100")

    # Genel değerlendirme metni
    if qa_result.get("genel_degerlendirme"):
        st.markdown(f"**Genel Değerlendirme:** {qa_result.get('genel_degerlendirme')}")

    # Kriter skorları
    st.markdown("**Kriter Skorları:**")
    for s in qa_result.get("skorlar", []):
        puan = s.get("puan", 0)
        bar = "🟩" * puan + "⬜" * (10 - puan)
        kriter = s.get("kriter", "")
        aciklama = s.get("aciklama", "")

        # Fix: Convert dict/list to string
        if isinstance(aciklama, dict):
            aciklama = str(aciklama)
        elif isinstance(aciklama, list):
            aciklama = ', '.join(str(x) for x in aciklama)

        st.markdown(f"**{kriter}**: {bar} {puan}/10")
        if aciklama:
            st.caption(aciklama)

    # İyileştirme önerileri
    oneriler = qa_result.get("iyilestirme_onerileri", [])
    if oneriler:
        st.markdown("**İyileştirme Önerileri:**")
        for o in oneriler:
            st.markdown(f"- {o}")


try:
    from data.database import get_recent_pipeline_runs as get_recent_runs, get_pipeline_run_outputs as get_run_outputs

    runs = get_recent_runs(50)
    if not runs:
        st.info("Henüz pipeline çalıştırılmadı.")
        st.stop()

    # İstatistikler
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Çalıştırma", len(runs))
    with col2:
        completed = sum(1 for r in runs if r["status"] == "completed")
        st.metric("Tamamlanan", completed)
    with col3:
        if runs:
            avg_ba = sum(r["ba_score"] for r in runs) / len(runs)
            st.metric("Ort. BA Skoru", f"{avg_ba:.0f}")
    with col4:
        if runs:
            total_time = sum(r["total_time_sec"] for r in runs)
            st.metric("Toplam Süre", f"{total_time//60}dk")

    st.divider()

    for r in runs:
        status_icon = "✅" if r["status"] == "completed" else "🔄" if r["status"] == "running" else "❌"
        avg_score = (r["ba_score"] + r["ta_score"] + r["tc_score"]) / 3 if r["ba_score"] else 0

        with st.expander(
            f"{status_icon} **{r['project_name']}** — "
            f"BA:{r['ba_score']:.0f} | TA:{r['ta_score']:.0f} | TC:{r['tc_score']:.0f} | "
            f"Ort:{avg_score:.0f} — {r['created_at'][:16]}"
        ):
            # Özet metrikleri
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("BA Skor", f"{r['ba_score']:.0f}", delta=f"{r['ba_revisions']} rev")
            col2.metric("TA Skor", f"{r['ta_score']:.0f}", delta=f"{r['ta_revisions']} rev")
            col3.metric("TC Skor", f"{r['tc_score']:.0f}", delta=f"{r['tc_revisions']} rev")
            col4.metric("Süre", f"{r['total_time_sec']}s")
            col5.metric("Dosya", r.get("brd_filename", "-"))

            st.divider()

            # Stage output'larını al
            outputs = get_run_outputs(r["id"])

            # En son BA, TA, TC çıktılarını bul
            ba_output = next((o for o in reversed(outputs) if o["stage"] == "ba"), None)
            ta_output = next((o for o in reversed(outputs) if o["stage"] == "ta"), None)
            tc_output = next((o for o in reversed(outputs) if o["stage"] == "tc"), None)

            # QA sonuçlarını parse et
            ba_qa = json.loads(ba_output["qa_result_json"]) if ba_output and ba_output["qa_result_json"] else {}
            ta_qa = json.loads(ta_output["qa_result_json"]) if ta_output and ta_output["qa_result_json"] else {}
            tc_qa = json.loads(tc_output["qa_result_json"]) if tc_output and tc_output["qa_result_json"] else {}

            # Tab'lar ile hakem değerlendirmelerini göster
            if ba_qa or ta_qa or tc_qa:
                tab_ba, tab_ta, tab_tc = st.tabs(["📋 BA Hakem", "⚙️ TA Hakem", "🧪 TC Hakem"])

                with tab_ba:
                    if ba_output:
                        forced_badge = " ⚡ QA Atlandı (Force Pass)" if ba_output.get("forced_pass") else ""
                        st.caption(f"Revizyon: {ba_output['revision_number']} | Süre: {ba_output['generation_time_sec']}s{forced_badge}")
                        if ba_output.get("forced_pass"):
                            st.info("Bu aşamada QA atlandı ve otomatik olarak 100 puan verildi.")
                        else:
                            show_qa_result(ba_qa, "BA")
                    else:
                        st.info("BA hakem sonucu mevcut değil.")

                with tab_ta:
                    if ta_output:
                        forced_badge = " ⚡ QA Atlandı (Force Pass)" if ta_output.get("forced_pass") else ""
                        st.caption(f"Revizyon: {ta_output['revision_number']} | Süre: {ta_output['generation_time_sec']}s{forced_badge}")
                        if ta_output.get("forced_pass"):
                            st.info("Bu aşamada QA atlandı ve otomatik olarak 100 puan verildi.")
                        else:
                            show_qa_result(ta_qa, "TA")
                    else:
                        st.info("TA hakem sonucu mevcut değil.")

                with tab_tc:
                    if tc_output:
                        forced_badge = " ⚡ QA Atlandı (Force Pass)" if tc_output.get("forced_pass") else ""
                        st.caption(f"Revizyon: {tc_output['revision_number']} | Süre: {tc_output['generation_time_sec']}s{forced_badge}")
                        if tc_output.get("forced_pass"):
                            st.info("Bu aşamada QA atlandı ve otomatik olarak 100 puan verildi.")
                        else:
                            show_qa_result(tc_qa, "TC")
                    else:
                        st.info("TC hakem sonucu mevcut değil.")
            else:
                st.info("Bu pipeline çalıştırmasına ait QA sonuçları bulunamadı.")

except Exception as e:
    st.error(f"Veritabanı hatası: {e}")
    import traceback
    st.code(traceback.format_exc())
