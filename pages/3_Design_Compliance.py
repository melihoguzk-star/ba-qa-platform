"""
BA&QA Intelligence Platform — 🎨 Design Compliance
Tasarım ↔ İş Analizi Uyumluluk Kontrolü
"""
import streamlit as st
import sys, os, tempfile, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.sidebar import render_custom_sidebar
from pathlib import Path
from agno.media import Image as AgnoImage
from utils.config import get_credentials, gemini_available
from integrations.google_docs import fetch_google_doc_direct
from agents.agent_definitions import create_design_agents
from data.database import save_analysis

st.set_page_config(page_title="Design Compliance — BA&QA", page_icon="🎨", layout="wide")

# Custom sidebar
render_custom_sidebar(active_page="design")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;700&display=swap');
    .stApp { font-family: 'Outfit', sans-serif; }
    .agent-step {
        padding: 0.9rem 1.2rem;
        background: linear-gradient(135deg, rgba(46,134,193,0.15), rgba(26,188,156,0.1));
        border-radius: 10px; margin-bottom: 0.8rem;
        border-left: 4px solid #2E86C1; color: #e0e0e0; font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🎨 Design Compliance — Tasarım ↔ BA Uyumluluk")
st.markdown("**4 Agent Pipeline:** Requirements Extractor → Screen Analyzer → Compliance Checker → Report Generator")

gemini_key, jira_email, jira_token = get_credentials()
if not gemini_available():
    st.warning("⚠️ Ana sayfadan Gemini API Key gir.")
    st.stop()

agents = create_design_agents(gemini_key)
if not all(agents):
    st.error("Agent'lar başlatılamadı.")
    st.stop()
requirements_agent, screen_agent, compliance_agent, report_agent = agents

# ── Input ──
col_doc, col_space, col_design = st.columns([1, 0.05, 1])

with col_doc:
    st.subheader("📄 İş Analizi Dokümanı")
    doc_url = st.text_input("Google Docs URL'si", placeholder="https://docs.google.com/document/d/...")
    doc_text_override = st.text_area("Veya metin yapıştır (opsiyonel)", height=200)

    if doc_url or doc_text_override:
        with st.expander("📋 Doküman Önizleme", expanded=False):
            if doc_text_override:
                st.text(doc_text_override[:2000] + ("..." if len(doc_text_override) > 2000 else ""))
            elif doc_url:
                with st.spinner("Çekiliyor..."):
                    fetched = fetch_google_doc_direct(doc_url)
                    if fetched:
                        st.session_state["doc_content"] = fetched
                        st.text(fetched[:2000])
                    else:
                        st.error("Doküman çekilemedi. Paylaşım ayarını kontrol et.")

with col_design:
    st.subheader("🎨 Tasarım Ekranları")
    design_files = st.file_uploader("Figma export / Ekran görüntüsü yükle",
                                     type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if design_files:
        for f in design_files:
            st.image(f, caption=f.name, use_container_width=True)

# ── Config ──
st.markdown("---")
col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    st.subheader("🎯 Kontrol Kapsamı")
    checks = st.multiselect("Yapılacak Kontroller", [
        "Gereksinim ↔ Tasarım Eşleştirme (Traceability)",
        "Eksik/Fazla Özellik Tespiti",
        "Acceptance Criteria Karşılaştırma",
        "UI Text/Label Doğrulama",
    ], default=[
        "Gereksinim ↔ Tasarım Eşleştirme (Traceability)",
        "Eksik/Fazla Özellik Tespiti",
        "Acceptance Criteria Karşılaştırma",
        "UI Text/Label Doğrulama",
    ])
with col_cfg2:
    st.subheader("📝 Ek Bilgi")
    project_name = st.text_input("Proje Adı", placeholder="Örn: Enliq Tenant Management")
    extra_context = st.text_area("Ek Bağlam", height=100)

# ── Run ──
if st.button("🚀 Uyumluluk Kontrolünü Çalıştır", type="primary", use_container_width=True):
    doc_content = doc_text_override or st.session_state.get("doc_content")
    if not doc_content and doc_url:
        with st.spinner("Doküman çekiliyor..."):
            doc_content = fetch_google_doc_direct(doc_url)
    if not doc_content:
        st.error("❌ İş analizi dokümanı sağla.")
        st.stop()
    if not design_files:
        st.error("❌ En az bir tasarım ekranı yükle.")
        st.stop()

    # Process images
    design_images = []
    for f in design_files:
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"tmp_{f.name}")
            with open(tmp, "wb") as fp:
                fp.write(f.getvalue())
            design_images.append(AgnoImage(filepath=Path(tmp)))
        except Exception:
            pass
    if not design_images:
        st.error("❌ Görseller işlenemedi.")
        st.stop()

    st.markdown("---")
    st.header("📊 Analiz Sonuçları" + (f" — {project_name}" if project_name else ""))
    progress = st.progress(0, text="Başlatılıyor...")

    checks_str = ", ".join(checks)
    context_str = f"Proje: {project_name}. {extra_context}" if project_name else extra_context

    # Step 1
    progress.progress(10, text="🧠 Adım 1/4 — Gereksinimler çıkarılıyor...")
    with st.expander("🧠 Adım 1: Gereksinim Çıkarma", expanded=True):
        req_prompt = f"Aşağıdaki iş analizi dokümanından tüm gereksinimleri çıkar.\nKontrol kapsamı: {checks_str}\n{f'Ek bağlam: {context_str}' if context_str else ''}\n\n--- İŞ ANALİZİ DOKÜMANI ---\n{doc_content}"
        req_response = requirements_agent.run(req_prompt)
        requirements_output = req_response.content
        st.markdown(requirements_output)

    # Step 2
    progress.progress(35, text="👁️ Adım 2/4 — Ekran analizi...")
    with st.expander("👁️ Adım 2: Ekran Analizi", expanded=True):
        screen_prompt = f"Bu tasarım ekranlarını detaylı analiz et.\n{f'Proje: {project_name}' if project_name else ''}\nEkran sayısı: {len(design_files)}"
        screen_response = screen_agent.run(screen_prompt, images=design_images)
        screen_output = screen_response.content
        st.markdown(screen_output)

    # Step 3
    progress.progress(60, text="⚖️ Adım 3/4 — Uyumluluk kontrolü...")
    with st.expander("⚖️ Adım 3: Uyumluluk Kontrolü", expanded=True):
        compliance_prompt = f"Karşılaştır:\nKontroller: {checks_str}\n\n--- GEREKSİNİMLER ---\n{requirements_output}\n\n--- EKRAN ANALİZİ ---\n{screen_output}"
        compliance_response = compliance_agent.run(compliance_prompt, images=design_images)
        compliance_output = compliance_response.content
        st.markdown(compliance_output)

    # Step 4
    progress.progress(85, text="📋 Adım 4/4 — Rapor oluşturuluyor...")
    with st.expander("📋 Adım 4: Uyumluluk Raporu", expanded=True):
        report_prompt = f"Rapor oluştur.\nProje: {project_name or 'Belirtilmedi'}\nEkran sayısı: {len(design_files)}\n\n--- UYUMLULUK ---\n{compliance_output}\n\n--- GEREKSİNİMLER ---\n{requirements_output}"
        report_response = report_agent.run(report_prompt)
        report_output = report_response.content
        st.markdown(report_output)

    progress.progress(100, text="✅ Analiz tamamlandı!")

    # DB'ye kaydet (skor olmadığı için 0 ile)
    save_analysis(project_name or "design", "design", 0, False, {"report": report_output})

    st.success(f"✅ Uyumluluk kontrolü tamamlandı! {len(design_files)} ekran analiz edildi.")

    # Download
    full_report = f"# Design Compliance Report\n## Proje: {project_name}\n## Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n# 1. Gereksinimler\n{requirements_output}\n\n---\n\n# 2. Ekran Analizi\n{screen_output}\n\n---\n\n# 3. Uyumluluk\n{compliance_output}\n\n---\n\n# 4. Rapor\n{report_output}"
    st.download_button("📥 Tam Raporu İndir (Markdown)", data=full_report,
                        file_name=f"compliance_{project_name or 'report'}.md",
                        mime="text/markdown", use_container_width=True)
