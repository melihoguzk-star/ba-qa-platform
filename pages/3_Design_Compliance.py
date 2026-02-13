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

    /* Section Headers */
    h2 {
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        font-family: 'Space Grotesk', sans-serif;
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
        text-align: center;
        margin-bottom: 40px;
    }
    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 48px;
        font-weight: 700;
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }
    .page-subtitle {
        color: #94a3b8;
        font-size: 18px;
        line-height: 1.6;
    }
    .pipeline-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(139,92,246,0.1);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 20px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #8b5cf6;
        margin-top: 12px;
    }

    /* Input Cards */
    .input-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    .input-card:hover {
        border-color: rgba(139,92,246,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .input-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }
    .input-card.purple::before { background: linear-gradient(135deg, #8b5cf6, #ec4899); }
    .input-card.blue::before { background: linear-gradient(135deg, #3b82f6, #06b6d4); }
    .input-card.green::before { background: linear-gradient(135deg, #10b981, #06b6d4); }

    .input-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Step Indicator */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 32px 0;
        padding: 20px;
        background: #1a2236;
        border-radius: 12px;
        border: 1px solid #2a3654;
    }
    .step {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
    }
    .step-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 16px;
        background: rgba(59,130,246,0.1);
        border: 2px solid rgba(59,130,246,0.3);
        color: #3b82f6;
    }
    .step-number.active {
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        border-color: transparent;
        color: white;
        box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    }
    .step-number.completed {
        background: linear-gradient(135deg, #10b981, #06b6d4);
        border-color: transparent;
        color: white;
    }
    .step-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
    }
    .step-label.active {
        color: #3b82f6;
        font-weight: 600;
    }
    .step-label.completed {
        color: #10b981;
    }
    .step-arrow {
        color: #475569;
        font-size: 20px;
    }

    /* Agent Output */
    .agent-output {
        background: #1a1d2e;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border-left: 4px solid;
        font-family: 'DM Sans', sans-serif;
        line-height: 1.8;
        color: #e0e0e0;
    }
    .agent-output.requirements { border-color: #3b82f6; }
    .agent-output.screen { border-color: #8b5cf6; }
    .agent-output.compliance { border-color: #ec4899; }
    .agent-output.report { border-color: #10b981; }

    /* Scroll to Top */
    .scroll-top-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #ec4899, #8b5cf6);
        border: none;
        border-radius: 50%;
        color: white;
        font-size: 20px;
        cursor: pointer;
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 99;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(236,72,153,0.3);
    }
    .scroll-top-btn.visible {
        opacity: 1;
    }
    .scroll-top-btn:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(236,72,153,0.5);
    }

    /* Image Preview */
    .image-preview {
        border-radius: 12px;
        border: 2px solid #2a3654;
        overflow: hidden;
        margin: 8px 0;
        transition: all 0.2s;
    }
    .image-preview:hover {
        border-color: rgba(139,92,246,0.4);
        transform: scale(1.02);
    }

    /* Reduce Streamlit default spacing */
    .stTextInput, .stTextArea, .stMultiSelect {
        margin-bottom: 0.5rem !important;
    }
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    @media (max-width: 768px) {
        .step-indicator {
            flex-direction: column;
        }
        .step-arrow {
            transform: rotate(90deg);
        }
    }
</style>

<script>
    window.addEventListener('scroll', function() {
        const scrollBtn = document.getElementById('scrollTopBtn');
        if (scrollBtn) {
            if (window.pageYOffset > 300) {
                scrollBtn.classList.add('visible');
            } else {
                scrollBtn.classList.remove('visible');
            }
        }
    });

    function scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
</script>
""", unsafe_allow_html=True)

# ── Breadcrumb Navigation ──
st.markdown("""
<div class="breadcrumb">
    <a href="/">🏠 Ana Sayfa</a>
    <span class="separator">›</span>
    <span class="current">🎨 Design Compliance</span>
</div>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="page-header">
    <div class="page-title">🎨 Design Compliance</div>
    <div class="page-subtitle">Tasarım ↔ İş Analizi Uyumluluk Kontrolü</div>
    <div class="pipeline-badge">
        🤖 4-Agent Pipeline: Requirements → Screen Analysis → Compliance → Report
    </div>
</div>
""", unsafe_allow_html=True)

# ── Scroll to Top Button ──
st.markdown("""
<button id="scrollTopBtn" class="scroll-top-btn" onclick="scrollToTop()">
    ↑
</button>
""", unsafe_allow_html=True)

# ── Check API ──
gemini_key, jira_email, jira_token = get_credentials()
if not gemini_available():
    st.error("⚠️ Gemini API Key bulunamadı. Ana sayfadan API key'i girin.")
    st.stop()

agents = create_design_agents(gemini_key)
if not all(agents):
    st.error("Agent'lar başlatılamadı. Lütfen API ayarlarını kontrol edin.")
    st.stop()
requirements_agent, screen_agent, compliance_agent, report_agent = agents

# ── Input Section ──
st.markdown("## 📥 Giriş Verileri")

col_doc, col_design = st.columns(2)

with col_doc:
    st.markdown('<div class="input-card purple">', unsafe_allow_html=True)
    st.markdown('<div class="input-card-title">📄 İş Analizi Dokümanı</div>', unsafe_allow_html=True)

    doc_url = st.text_input("Google Docs URL", placeholder="https://docs.google.com/document/d/...", label_visibility="collapsed")
    st.caption("veya")
    doc_text_override = st.text_area("Doküman metnini yapıştır", height=100, label_visibility="collapsed", placeholder="İş analizi dokümanı metnini buraya yapıştırın...")

    if doc_url or doc_text_override:
        with st.expander("📋 Doküman Önizleme"):
            if doc_text_override:
                st.text(doc_text_override[:2000] + ("..." if len(doc_text_override) > 2000 else ""))
            elif doc_url:
                with st.spinner("Doküman çekiliyor..."):
                    fetched = fetch_google_doc_direct(doc_url)
                    if fetched:
                        st.session_state["doc_content"] = fetched
                        st.text(fetched[:2000] + ("..." if len(fetched) > 2000 else ""))
                    else:
                        st.error("Doküman çekilemedi. Paylaşım ayarlarını kontrol edin.")

    st.markdown('</div>', unsafe_allow_html=True)

with col_design:
    st.markdown('<div class="input-card blue">', unsafe_allow_html=True)
    st.markdown('<div class="input-card-title">🎨 Tasarım Ekranları</div>', unsafe_allow_html=True)

    design_files = st.file_uploader(
        "Figma export veya ekran görüntüsü yükle",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if design_files:
        st.success(f"✅ {len(design_files)} ekran yüklendi")
        cols = st.columns(min(len(design_files), 3))
        for idx, f in enumerate(design_files):
            with cols[idx % 3]:
                st.image(f, caption=f.name, use_column_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Configuration ──
st.markdown("## ⚙️ Kontrol Ayarları")

col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    st.markdown('<div class="input-card green">', unsafe_allow_html=True)
    st.markdown('<div class="input-card-title">🎯 Kontrol Kapsamı</div>', unsafe_allow_html=True)

    checks = st.multiselect(
        "Yapılacak Kontroller",
        [
            "Gereksinim ↔ Tasarım Eşleştirme (Traceability)",
            "Eksik/Fazla Özellik Tespiti",
            "Acceptance Criteria Karşılaştırma",
            "UI Text/Label Doğrulama",
        ],
        default=[
            "Gereksinim ↔ Tasarım Eşleştirme (Traceability)",
            "Eksik/Fazla Özellik Tespiti",
        ],
        label_visibility="collapsed"
    )

    st.markdown('</div>', unsafe_allow_html=True)

with col_cfg2:
    st.markdown('<div class="input-card green">', unsafe_allow_html=True)
    st.markdown('<div class="input-card-title">📝 Proje Bilgileri</div>', unsafe_allow_html=True)

    project_name = st.text_input("Proje Adı", placeholder="Örn: Enliq Tenant Management", label_visibility="collapsed")
    extra_context = st.text_area("Ek Bağlam (Opsiyonel)", height=60, label_visibility="collapsed", placeholder="Ek notlar veya özel talimatlar...")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Run Button ──
if st.button("🚀 Uyumluluk Kontrolünü Başlat", type="primary", use_container_width=True):
    # Validate inputs
    doc_content = doc_text_override or st.session_state.get("doc_content")
    if not doc_content and doc_url:
        with st.spinner("Doküman çekiliyor..."):
            doc_content = fetch_google_doc_direct(doc_url)

    if not doc_content:
        st.error("❌ İş analizi dokümanı sağlamalısınız (URL veya metin).")
        st.stop()

    if not design_files:
        st.error("❌ En az bir tasarım ekranı yüklemelisiniz.")
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
        st.error("❌ Görseller işlenemedi. Lütfen geçerli dosyalar yükleyin.")
        st.stop()

    # ── Analysis Pipeline ──
    st.markdown("---")
    st.markdown(f"## 📊 Analiz Sonuçları{f' — {project_name}' if project_name else ''}")

    progress = st.progress(0, text="Analiz başlatılıyor...")
    checks_str = ", ".join(checks)
    context_str = f"Proje: {project_name}. {extra_context}" if project_name else extra_context

    # Step 1: Requirements Extraction
    progress.progress(10, text="🧠 1/4 — Gereksinimler çıkarılıyor...")
    st.markdown("""
    <div class="step-indicator">
        <div class="step">
            <div class="step-number active">1</div>
            <div class="step-label active">Requirements</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number">2</div>
            <div class="step-label">Screen Analysis</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number">3</div>
            <div class="step-label">Compliance</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number">4</div>
            <div class="step-label">Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🧠 Adım 1: Gereksinim Çıkarma", expanded=True):
        req_prompt = f"Aşağıdaki iş analizi dokümanından tüm gereksinimleri çıkar.\nKontrol kapsamı: {checks_str}\n{f'Ek bağlam: {context_str}' if context_str else ''}\n\n--- İŞ ANALİZİ DOKÜMANI ---\n{doc_content}"
        req_response = requirements_agent.run(req_prompt)
        requirements_output = req_response.content
        st.markdown(f'<div class="agent-output requirements">{requirements_output}</div>', unsafe_allow_html=True)

    # Step 2: Screen Analysis
    progress.progress(35, text="👁️ 2/4 — Ekran analizi yapılıyor...")
    st.markdown("""
    <div class="step-indicator">
        <div class="step">
            <div class="step-number completed">1</div>
            <div class="step-label completed">Requirements</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number active">2</div>
            <div class="step-label active">Screen Analysis</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number">3</div>
            <div class="step-label">Compliance</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number">4</div>
            <div class="step-label">Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("👁️ Adım 2: Ekran Analizi", expanded=True):
        screen_prompt = f"Bu tasarım ekranlarını detaylı analiz et.\n{f'Proje: {project_name}' if project_name else ''}\nEkran sayısı: {len(design_files)}"
        screen_response = screen_agent.run(screen_prompt, images=design_images)
        screen_output = screen_response.content
        st.markdown(f'<div class="agent-output screen">{screen_output}</div>', unsafe_allow_html=True)

    # Step 3: Compliance Check
    progress.progress(60, text="⚖️ 3/4 — Uyumluluk kontrolü yapılıyor...")
    st.markdown("""
    <div class="step-indicator">
        <div class="step">
            <div class="step-number completed">1</div>
            <div class="step-label completed">Requirements</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number completed">2</div>
            <div class="step-label completed">Screen Analysis</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number active">3</div>
            <div class="step-label active">Compliance</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number">4</div>
            <div class="step-label">Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚖️ Adım 3: Uyumluluk Kontrolü", expanded=True):
        compliance_prompt = f"Karşılaştır:\nKontroller: {checks_str}\n\n--- GEREKSİNİMLER ---\n{requirements_output}\n\n--- EKRAN ANALİZİ ---\n{screen_output}"
        compliance_response = compliance_agent.run(compliance_prompt, images=design_images)
        compliance_output = compliance_response.content
        st.markdown(f'<div class="agent-output compliance">{compliance_output}</div>', unsafe_allow_html=True)

    # Step 4: Report Generation
    progress.progress(85, text="📋 4/4 — Rapor oluşturuluyor...")
    st.markdown("""
    <div class="step-indicator">
        <div class="step">
            <div class="step-number completed">1</div>
            <div class="step-label completed">Requirements</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number completed">2</div>
            <div class="step-label completed">Screen Analysis</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number completed">3</div>
            <div class="step-label completed">Compliance</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-number active">4</div>
            <div class="step-label active">Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Adım 4: Uyumluluk Raporu", expanded=True):
        report_prompt = f"Rapor oluştur.\nProje: {project_name or 'Belirtilmedi'}\nEkran sayısı: {len(design_files)}\n\n--- UYUMLULUK ---\n{compliance_output}\n\n--- GEREKSİNİMLER ---\n{requirements_output}"
        report_response = report_agent.run(report_prompt)
        report_output = report_response.content
        st.markdown(f'<div class="agent-output report">{report_output}</div>', unsafe_allow_html=True)

    progress.progress(100, text="✅ Analiz tamamlandı!")

    # Save to database
    save_analysis(project_name or "design", "design", 0, False, {"report": report_output})

    st.success(f"✅ Uyumluluk kontrolü başarıyla tamamlandı! {len(design_files)} ekran analiz edildi.")

    # Download Report
    st.markdown("---")
    st.markdown("### 📥 Rapor İndir")

    full_report = f"""# Design Compliance Report

## Proje: {project_name or 'Belirtilmedi'}
## Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
## Ekran Sayısı: {len(design_files)}
## Kontroller: {checks_str}

---

# 1. Gereksinimler
{requirements_output}

---

# 2. Ekran Analizi
{screen_output}

---

# 3. Uyumluluk Kontrolü
{compliance_output}

---

# 4. Final Rapor
{report_output}
"""

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "📥 Markdown Rapor İndir",
            data=full_report,
            file_name=f"compliance_{project_name or 'report'}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            "📄 Text Rapor İndir",
            data=full_report,
            file_name=f"compliance_{project_name or 'report'}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #64748b; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
    BA&QA Intelligence Platform v1.0 — Design Compliance — February 2026
</div>
""", unsafe_allow_html=True)
