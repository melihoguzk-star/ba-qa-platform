"""Sayfa 2: Pipeline Sonuç — Görüntüleme & Export.

Export formatları:
- BA: DOCX
- TA: DOCX
- TC: CSV + Excel (23 kolon)
"""
import json
import io
import time
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pipeline Sonuç", page_icon="📊", layout="wide")
st.title("📊 Pipeline Sonuç")

# ── Veri kontrolü ──
# Önce session_state'ten, yoksa last_pipeline_result'tan al
ba_content = st.session_state.get("ba_content")
ta_content = st.session_state.get("ta_content")
tc_content = st.session_state.get("tc_content")
ba_qa = st.session_state.get("ba_qa_result", {})
ta_qa = st.session_state.get("ta_qa_result", {})
tc_qa = st.session_state.get("tc_qa_result", {})
ba_score = st.session_state.get("ba_score", 0)
ta_score = st.session_state.get("ta_score", 0)
tc_score = st.session_state.get("tc_score", 0)
project = st.session_state.get("project_name", "Proje")

# Fallback: last_pipeline_result
results = st.session_state.get("last_pipeline_result")
if results and not ba_content:
    ba_content = results.get("ba", {}).get("content")
    ta_content = results.get("ta", {}).get("content")
    tc_content = results.get("tc", {}).get("content")
    ba_qa = results.get("ba", {}).get("qa_result", {})
    ta_qa = results.get("ta", {}).get("qa_result", {})
    tc_qa = results.get("tc", {}).get("qa_result", {})
    ba_score = results.get("ba", {}).get("quality_score", 0)
    ta_score = results.get("ta", {}).get("quality_score", 0)
    tc_score = results.get("tc", {}).get("quality_score", 0)
    project = results.get("project_name", "Proje")

if not ba_content:
    st.info("Henüz pipeline çalıştırılmadı veya tamamlanmadı. Önce **BRD Pipeline** sayfasından çalıştırın.")
    st.stop()


# ════════════════════════════════════════════
# DOCX BUILD FONKSİYONLARI
# ════════════════════════════════════════════

def build_ba_docx(ba_content, project_name):
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)
    doc.add_heading(f'{project_name} — İş Analizi', level=0)
    doc.add_paragraph(f'Tarih: {time.strftime("%d.%m.%Y %H:%M")}')

    for i, e in enumerate(ba_content.get("ekranlar", []), 1):
        doc.add_heading(f'{i}. {e.get("ekran_adi", "")}', level=1)

        doc.add_heading(f'{i}.1. Açıklama', level=2)
        doc.add_paragraph(e.get("aciklama", ""))

        doc.add_heading(f'{i}.2. Gerekli Dokümanlar', level=2)
        doc.add_heading(f'{i}.2.1. Teknik Akış/Analiz', level=3)
        doc.add_paragraph(e.get("gerekli_dokumanlar", {}).get("teknik_akis", ""))
        doc.add_heading(f'{i}.2.2. Tasarım Dosyası', level=3)
        doc.add_paragraph(e.get("gerekli_dokumanlar", {}).get("tasarim_dosyasi", ""))

        doc.add_heading(f'{i}.3. İş Akışı Diyagramı', level=2)
        for adim in e.get("is_akisi_diyagrami", []):
            doc.add_paragraph(adim, style='List Number')

        frs = e.get("fonksiyonel_gereksinimler", [])
        doc.add_heading(f'{i}.4. Fonksiyonel Gereksinimler', level=2)
        for fr in frs:
            p = doc.add_paragraph()
            run = p.add_run(f'{fr.get("id","")}: ')
            run.bold = True
            p.add_run(fr.get("tanim", ""))

        kurallar = e.get("is_kurallari", [])
        doc.add_heading(f'{i}.5. İş Kuralları', level=2)
        for k in kurallar:
            p = doc.add_paragraph()
            run = p.add_run(k.get("kural", ""))
            run.bold = True
            if k.get("detay"):
                doc.add_paragraph(k["detay"])

        brs = e.get("kabul_kriterleri", [])
        doc.add_heading(f'{i}.6. Kabul Kriterleri', level=2)
        for br in brs:
            p = doc.add_paragraph()
            run = p.add_run(f'{br.get("id","")}: ')
            run.bold = True
            p.add_run(br.get("kriter", ""))

        vals = e.get("validasyonlar", [])
        doc.add_heading(f'{i}.7. Validasyonlar', level=2)
        for v in vals:
            doc.add_paragraph(
                f'{v.get("alan","")}: {v.get("kisit","")} → {v.get("hata_mesaji","")}',
                style='List Bullet'
            )

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def build_ta_docx(ta_content, project_name):
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal'].font.size = Pt(11)

    ta = ta_content.get("teknik_analiz", ta_content)
    doc.add_heading(f'{project_name} — Teknik Analiz', level=0)
    doc.add_paragraph(f'Oluşturma Tarihi: {time.strftime("%d.%m.%Y %H:%M")}')

    genel = ta.get("genel_tanim", {})
    if genel:
        doc.add_heading("Genel Tanım", level=1)
        doc.add_paragraph(f'Modül: {genel.get("modul_adi", "")}')
        doc.add_paragraph(f'Stack: {", ".join(genel.get("teknoloji_stack", []))}')
        doc.add_paragraph(f'Mimari: {genel.get("mimari_yaklasim", "")}')

    endpoints = ta.get("endpoint_detaylari", {})
    if endpoints:
        doc.add_heading("API Endpoint Detayları", level=1)
        for ep, detail in endpoints.items():
            doc.add_heading(f'{detail.get("method", "GET")} {ep}', level=2)
            doc.add_paragraph(detail.get("aciklama", ""))
            if detail.get("request_body"):
                doc.add_paragraph(f'Request: {json.dumps(detail["request_body"], ensure_ascii=False, indent=2)[:500]}')
            if detail.get("response_success"):
                doc.add_paragraph(f'Response: {json.dumps(detail["response_success"], ensure_ascii=False, indent=2)[:500]}')
            for err in detail.get("response_errors", []):
                doc.add_paragraph(f'{err.get("http_code", "")} — {err.get("error_code", "")}: {err.get("mesaj", "")}', style='List Bullet')

    dtos = ta.get("dto_veri_yapilari", [])
    if dtos:
        doc.add_heading("DTO Veri Yapıları", level=1)
        for dto in dtos:
            doc.add_heading(dto.get("dto_adi", ""), level=2)
            doc.add_paragraph(dto.get("aciklama", ""))
            for f in dto.get("fields", []):
                doc.add_paragraph(f'{f.get("field", "")}: {f.get("tip", "")} {"(zorunlu)" if f.get("zorunlu") else ""} — {f.get("validasyon", "")}', style='List Bullet')

    vrs = ta.get("validasyon_kurallari", [])
    if vrs:
        doc.add_heading("Validasyon Kuralları", level=1)
        for v in vrs:
            doc.add_paragraph(f'{v.get("id", "")} [{v.get("field", "")}]: {v.get("kural", "")} → {v.get("hata_mesaji", "")}', style='List Bullet')

    curls = ta.get("mock_curl_ornekleri", [])
    if curls:
        doc.add_heading("cURL Örnekleri", level=1)
        for c in curls:
            doc.add_heading(c.get("endpoint_adi", ""), level=2)
            doc.add_paragraph(c.get("curl", ""))

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def build_tc_excel(tc_content):
    """TC'yi 23-kolon Loodos şablonunda Excel'e çevir."""
    from utils.export import export_tc_excel
    return export_tc_excel(tc_content)


def build_tc_csv(tc_content):
    """TC'yi CSV'ye çevir."""
    tcs = tc_content.get("test_cases", [])
    if not tcs:
        return ""
    cols_23 = [
        "existance", "created_by", "date", "app_bundle", "test_case_id",
        "br_id", "tr_id", "priority", "channel", "testcase_type",
        "user_type", "test_area", "test_scenario", "testcase", "test_steps",
        "precondition", "test_data", "expected_result", "postcondition",
        "actual_result", "status", "regression_case", "comments"
    ]
    df = pd.DataFrame(tcs)
    for c in cols_23:
        if c not in df.columns:
            df[c] = ""
    df = df[cols_23]
    return df.to_csv(index=False, encoding="utf-8-sig")


# ════════════════════════════════════════════
# SKOR KARTLARI
# ════════════════════════════════════════════
col1, col2, col3 = st.columns(3)
with col1:
    color = "🟢" if ba_score >= 60 else "🟡" if ba_score >= 40 else "🔴"
    st.metric(f"{color} BA Skor", f"{ba_score:.0f}/100")
with col2:
    color = "🟢" if ta_score >= 60 else "🟡" if ta_score >= 40 else "🔴"
    st.metric(f"{color} TA Skor", f"{ta_score:.0f}/100")
with col3:
    tc_count = len(tc_content.get("test_cases", [])) if tc_content else 0
    color = "🟢" if tc_score >= 60 else "🟡" if tc_score >= 40 else "🔴"
    st.metric(f"{color} TC Skor ({tc_count} TC)", f"{tc_score:.0f}/100")

st.divider()

# ════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════
tab_ba, tab_ta, tab_tc, tab_qa, tab_export = st.tabs(
    ["📋 İş Analizi", "⚙️ Teknik Analiz", "🧪 Test Case", "🔍 QA Detay", "📥 Export"]
)

# ── BA TAB ──
with tab_ba:
    ekranlar = ba_content.get("ekranlar", [])
    st.subheader(f"İş Analizi — {len(ekranlar)} Ekran")
    for i, e in enumerate(ekranlar, 1):
        with st.expander(f"**{i}. {e.get('ekran_adi', '')}**", expanded=i == 1):
            st.markdown(e.get("aciklama", ""))
            akis = e.get("is_akisi_diyagrami", [])
            if akis:
                st.markdown("**İş Akışı:**")
                for a in akis:
                    st.markdown(f"- {a}")
            frs = e.get("fonksiyonel_gereksinimler", [])
            if frs:
                st.markdown(f"**Fonksiyonel Gereksinimler ({len(frs)}):**")
                for fr in frs:
                    st.markdown(f"- **{fr.get('id','')}** {fr.get('tanim','')}")
            kurallar = e.get("is_kurallari", [])
            if kurallar:
                st.markdown(f"**İş Kuralları ({len(kurallar)}):**")
                for k in kurallar:
                    st.markdown(f"- {k.get('kural','')}")
            brs = e.get("kabul_kriterleri", [])
            if brs:
                st.markdown(f"**Kabul Kriterleri ({len(brs)}):**")
                for br in brs:
                    st.markdown(f"- **{br.get('id','')}** {br.get('kriter','')}")
            vals = e.get("validasyonlar", [])
            if vals:
                st.markdown(f"**Validasyonlar ({len(vals)}):**")
                for v in vals:
                    st.markdown(f"- `{v.get('alan','')}`: {v.get('kisit','')} → {v.get('hata_mesaji','')}")

# ── TA TAB ──
with tab_ta:
    ta = ta_content.get("teknik_analiz", ta_content) if ta_content else {}
    st.subheader("Teknik Analiz")
    if ta.get("genel_tanim"):
        g = ta["genel_tanim"]
        st.markdown(f"**Modül:** {g.get('modul_adi', '')} | **Stack:** {', '.join(g.get('teknoloji_stack', []))}")
    if ta.get("endpoint_detaylari"):
        st.markdown(f"### API Endpoint'ler ({len(ta['endpoint_detaylari'])})")
        for ep, detail in ta["endpoint_detaylari"].items():
            with st.expander(f"`{detail.get('method', 'GET')} {ep}`"):
                st.markdown(detail.get("aciklama", ""))
                if detail.get("request_body"):
                    st.json(detail["request_body"])
                if detail.get("response_success"):
                    st.json(detail["response_success"])
    if ta.get("validasyon_kurallari"):
        st.markdown(f"### Validasyon Kuralları ({len(ta['validasyon_kurallari'])})")
        for v in ta["validasyon_kurallari"]:
            st.markdown(f"- **{v.get('id', '')}** `{v.get('field', '')}`: {v.get('kural', '')}")

# ── TC TAB ──
with tab_tc:
    test_cases = tc_content.get("test_cases", []) if tc_content else []
    st.subheader(f"Test Cases — {len(test_cases)} adet")
    if test_cases:
        df = pd.DataFrame(test_cases)
        display_cols = [c for c in ["test_case_id", "priority", "test_area", "testcase", "test_steps", "expected_result"] if c in df.columns]
        st.dataframe(df[display_cols] if display_cols else df, use_container_width=True, height=600)

# ── QA TAB ──
with tab_qa:
    st.subheader("QA Hakem Detayları")
    for stage_name, qa in [("BA", ba_qa), ("TA", ta_qa), ("TC", tc_qa)]:
        if not qa:
            continue
        with st.expander(f"**{stage_name} QA** — Puan: {qa.get('genel_puan', '?')}/100"):
            st.markdown(qa.get("genel_degerlendirme", ""))
            for s in qa.get("skorlar", []):
                puan = s.get("puan", 0)
                bar = "🟩" * puan + "⬜" * (10 - puan)
                st.markdown(f"**{s.get('kriter', '')}**: {bar} {puan}/10")
                st.caption(s.get("aciklama", ""))
            oneriler = qa.get("iyilestirme_onerileri", [])
            if oneriler:
                st.markdown("**İyileştirme Önerileri:**")
                for o in oneriler:
                    st.markdown(f"- {o}")

# ── EXPORT TAB ──
with tab_export:
    st.subheader("📥 Dokümanları İndir")

    col1, col2, col3 = st.columns(3)

    # BA → DOCX
    with col1:
        st.markdown("### 📋 İş Analizi")
        ba_docx = build_ba_docx(ba_content, project)
        st.download_button(
            "📥 İş Analizi (.docx)",
            data=ba_docx,
            file_name=f"{project}_is_analizi.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    # TA → DOCX
    with col2:
        st.markdown("### ⚙️ Teknik Analiz")
        if ta_content:
            ta_docx = build_ta_docx(ta_content, project)
            st.download_button(
                "📥 Teknik Analiz (.docx)",
                data=ta_docx,
                file_name=f"{project}_teknik_analiz.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.info("TA verisi mevcut değil.")

    # TC → CSV + Excel
    with col3:
        st.markdown("### 🧪 Test Cases")
        if tc_content and tc_content.get("test_cases"):
            tc_csv = build_tc_csv(tc_content)
            st.download_button(
                "📥 Test Cases (.csv)",
                data=tc_csv,
                file_name=f"{project}_test_cases.csv",
                mime="text/csv",
                use_container_width=True,
            )
            tc_xlsx = build_tc_excel(tc_content)
            st.download_button(
                "📥 Test Cases (.xlsx) — 23 kolon",
                data=tc_xlsx,
                file_name=f"{project}_test_cases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.info("TC verisi mevcut değil.")
