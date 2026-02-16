"""
BA&QA Intelligence Platform — 🏗️ Mimari
Platform mimari dokümanını Streamlit native bileşenleriyle gösterir
"""
import streamlit as st
import json
from datetime import datetime
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.sidebar import render_custom_sidebar

st.set_page_config(page_title="Mimari — BA&QA", page_icon="🏗️", layout="wide")

# Custom sidebar
render_custom_sidebar(active_page="architecture")

# ── CSS Styling ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    .main {
        background: #0a0e17;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1600px;
    }

    /* Header Badge */
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 100px;
        padding: 6px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #06b6d4;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .header-badge .dot {
        width: 6px; height: 6px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    /* Platform Title */
    .platform-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }
    .platform-subtitle {
        color: #94a3b8;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Agent Cards */
    .agent-detail-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .agent-detail-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
    }
    .agent-detail-card.blue::before { background: linear-gradient(180deg, #3b82f6, #06b6d4); }
    .agent-detail-card.green::before { background: linear-gradient(180deg, #10b981, #06b6d4); }
    .agent-detail-card.purple::before { background: linear-gradient(180deg, #8b5cf6, #ec4899); }

    .agent-detail-card:hover {
        border-color: rgba(59,130,246,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .agent-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .agent-role {
        font-size: 13px;
        color: #64748b;
        font-style: italic;
        margin-bottom: 12px;
    }
    .agent-description {
        font-size: 14px;
        color: #cbd5e1;
        line-height: 1.7;
        margin-bottom: 12px;
    }
    .agent-instructions {
        background: rgba(0,0,0,0.2);
        border-radius: 8px;
        padding: 12px;
        margin-top: 12px;
    }
    .agent-instructions-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #06b6d4;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .agent-instruction-item {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.6;
        padding: 4px 0 4px 16px;
        position: relative;
    }
    .agent-instruction-item::before {
        content: '→';
        position: absolute;
        left: 0;
        color: #3b82f6;
        font-weight: 700;
    }

    /* Integration Cards */
    .integration-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 14px;
        transition: all 0.3s;
    }
    .integration-card:hover {
        border-color: rgba(139,92,246,0.3);
        transform: translateY(-2px);
    }
    .integration-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    .integration-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        background: rgba(139,92,246,0.1);
        border: 1px solid rgba(139,92,246,0.2);
    }
    .integration-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: #f1f5f9;
    }
    .integration-endpoint {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #06b6d4;
        margin-top: 4px;
    }
    .integration-desc {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.6;
    }
    .integration-methods {
        margin-top: 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    .method-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.2);
        color: #3b82f6;
    }

    /* Pipeline Flow */
    .pipeline-flow {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .pipeline-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .pipeline-steps {
        display: flex;
        align-items: stretch;
        gap: 12px;
        overflow-x: auto;
    }
    .pipeline-step {
        flex: 1;
        min-width: 180px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        position: relative;
    }
    .pipeline-step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 14px;
    }
    .pipeline-step-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 6px;
    }
    .pipeline-step-desc {
        font-size: 11px;
        color: #64748b;
        line-height: 1.5;
    }
    .pipeline-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3b82f6;
        font-size: 24px;
        font-weight: 300;
    }

    /* Breadcrumb Navigation */
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

    /* Scroll to Top Button */
    .scroll-top-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
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
        box-shadow: 0 4px 12px rgba(59,130,246,0.3);
    }
    .scroll-top-btn.visible {
        opacity: 1;
    }
    .scroll-top-btn:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(59,130,246,0.5);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    html {
        scroll-behavior: smooth;
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

# ── Scroll to Top Button ──
st.markdown("""
<button id="scrollTopBtn" class="scroll-top-btn" onclick="scrollToTop()">
    ↑
</button>
""", unsafe_allow_html=True)

# ── Breadcrumb Navigation ──
st.markdown("""
<div class="breadcrumb">
    <a href="/">🏠 Ana Sayfa</a>
    <span class="separator">›</span>
    <span class="current">🏗️ Mimari</span>
</div>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align: center; margin-bottom: 32px;">
    <div class="header-badge">
        <span class="dot"></span>
        Architecture Document
    </div>
    <div class="platform-title">🏗️ Platform Mimarisi</div>
    <div class="platform-subtitle">Birleşik BA değerlendirme, QA test analizi, design compliance ve JIRA otomasyon platformu</div>
</div>
""", unsafe_allow_html=True)

# ── Quick Stats ──
st.markdown("""
<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 24px;">
    <div style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(59,130,246,0.05)); border: 1px solid rgba(59,130,246,0.3); border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">15</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">AI Agents</div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(139,92,246,0.05)); border: 1px solid rgba(139,92,246,0.3); border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #8b5cf6; margin-bottom: 4px;">8</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Entegrasyonlar</div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05)); border: 1px solid rgba(16,185,129,0.3); border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #10b981; margin-bottom: 4px;">13</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Sayfalar</div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.05)); border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #f59e0b; margin-bottom: 4px;">4</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Pipeline</div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(6,182,212,0.1), rgba(6,182,212,0.05)); border: 1px solid rgba(6,182,212,0.3); border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #06b6d4; margin-bottom: 4px;">571</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Doc Chunks</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tab Navigation ──
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Agents", "📚 Document Intelligence", "🔗 Entegrasyonlar", "🔄 Pipeline Akışları", "⚙️ Tech Stack"])

# ═══════════════════════════════════════════════════════════
# TAB 1: AI AGENTS
# ═══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">AI Agents (Gemini 2.5 Flash)</div>', unsafe_allow_html=True)

    st.markdown("### 📋 BA (İş Analizi) Agents")
    st.caption("4 adet specialized agent ile İş Analizi doküman kalite değerlendirmesi yapar")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">🔍 Agent 1: JIRA Tarayıcı</div>
            <div class="agent-role">JIRA Task Discovery & Link Extraction</div>
            <div class="agent-description">
                JIRA'dan iş analizi task'larını tarar, Google Docs linklerini tespit eder ve task bilgilerini analiz eder.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">JIRA task'larını tarar ve filtreler</div>
                <div class="agent-instruction-item">Google Docs URL'lerini description'dan çıkarır</div>
                <div class="agent-instruction-item">Task bilgilerini özetler ve yapılandırır</div>
                <div class="agent-instruction-item">qa-devam-ediyor label'ını ekler</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">🧠 Agent 3: Kalite Değerlendirici</div>
            <div class="agent-role">Quality Assessment & Scoring Engine</div>
            <div class="agent-description">
                İş analizi dokümanını 9 kriter üzerinden detaylı değerlendirir. Platform'un en kritik AI agent'ıdır.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Değerlendirme Kriterleri (9 Kriter)</div>
                <div class="agent-instruction-item">Tamlık (Completeness)</div>
                <div class="agent-instruction-item">Wireframe / Ekran Tasarımları</div>
                <div class="agent-instruction-item">Akış Diyagramları (Flow Diagrams)</div>
                <div class="agent-instruction-item">Gereksinim Kalitesi</div>
                <div class="agent-instruction-item">Kabul Kriterleri (Acceptance Criteria)</div>
                <div class="agent-instruction-item">Tutarlılık (Consistency)</div>
                <div class="agent-instruction-item">İş Kuralları Derinliği</div>
                <div class="agent-instruction-item">Hata Yönetimi (Error Handling)</div>
                <div class="agent-instruction-item">Dokümantasyon Kalitesi</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">Puanlama Sistemi:</strong><br>
                    • Her kriter: 1-10 puan<br>
                    • Varsayılan başlangıç: 5/10<br>
                    • 8+ = Mükemmel, 6-7 = İyi, 5 = Orta, <5 = Eksik<br>
                    • Genel Puan = (9 kriter ortalaması × 100) / 90<br>
                    • Geçme Notu: 60/100
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">📄 Agent 2: Doküman Okuyucu</div>
            <div class="agent-role">Document Parser & Structure Analyzer</div>
            <div class="agent-description">
                Google Docs'tan çekilen BA dokümanını okur, yapısını analiz eder ve içeriği parçalara ayırır.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">Doküman yapısını analiz eder (başlıklar, bölümler)</div>
                <div class="agent-instruction-item">İçeriği parçalara ayırır</div>
                <div class="agent-instruction-item">Eksik bölümleri tespit eder</div>
                <div class="agent-instruction-item">Metrik bilgiler çıkarır (karakter sayısı, bölüm sayısı)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">📝 Agent 4: Raporcu</div>
            <div class="agent-role">Report Formatter & JIRA Commenter</div>
            <div class="agent-description">
                Değerlendirme sonuçlarını JIRA comment formatına dönüştürür ve okunabilir rapor oluşturur.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">JSON sonuçlarını Markdown formatına çevirir</div>
                <div class="agent-instruction-item">Emoji ve görsel elementler ekler</div>
                <div class="agent-instruction-item">JIRA comment'i oluşturur</div>
                <div class="agent-instruction-item">qa-gecti/qa-gecmedi label'larını yönetir</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧪 TC (Test Case) Agents")
    st.caption("4 adet specialized agent ile Test Case doküman kalite değerlendirmesi yapar")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">🔍 Agent 1: JIRA & Sheet Tarayıcı</div>
            <div class="agent-role">Test Task Discovery & BA Linking</div>
            <div class="agent-description">
                JIRA'dan TC task'larını tarar, linked BA task'ı bulur ve Google Sheets URL'lerini tespit eder.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">JIRA component = Test filtresiyle TC task'larını bulur</div>
                <div class="agent-instruction-item">Linked BA task key'ini tespit eder</div>
                <div class="agent-instruction-item">Google Sheets URL'sini çıkarır</div>
                <div class="agent-instruction-item">tc-qa-devam-ediyor label'ını ekler</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">🧠 Agent 3: TC Kalite Değerlendirici</div>
            <div class="agent-role">Test Case Quality Assessor</div>
            <div class="agent-description">
                Test case dokümanını 8 kriter üzerinden değerlendirir. Loodos standart şablonunu (23 sütun) bekler.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Değerlendirme Kriterleri (8 Kriter)</div>
                <div class="agent-instruction-item">Kapsam (Coverage) - BA gereksinimlerini kapsama oranı</div>
                <div class="agent-instruction-item">Test Case Yapısı (Structure)</div>
                <div class="agent-instruction-item">Sınır Değer & Negatif Senaryolar (Edge Cases)</div>
                <div class="agent-instruction-item">Test Verisi Kalitesi (Data Quality)</div>
                <div class="agent-instruction-item">Öncelik Sınıflandırması (Priority)</div>
                <div class="agent-instruction-item">Regresyon Kapsamı (Regression Scope)</div>
                <div class="agent-instruction-item">İzlenebilirlik (Traceability)</div>
                <div class="agent-instruction-item">Okunabilirlik & Uygulanabilirlik</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(16,185,129,0.1); border-radius: 6px; border-left: 3px solid #10b981;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #10b981;">Özel Kurallar:</strong><br>
                    • Sadece happy path varsa edge_cases MAX 4/10<br>
                    • Loodos şablonu yoksa (23 sütun) test_structure MAX 5/10<br>
                    • Genel Puan = (8 kriter ortalaması × 100) / 80<br>
                    • Geçme Notu: 60/100
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">📑 Agent 2: Doküman Birleştirici</div>
            <div class="agent-role">Document Merger & Metrics Extractor</div>
            <div class="agent-description">
                BA dokümanı ve TC sheet'lerini birleştirip analiz için hazırlar. BA ile TC karşılaştırması yapar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">BA dokümanı ile TC sheet'i birleştirir</div>
                <div class="agent-instruction-item">Test case sayısını ve coverage metriklerini çıkarır</div>
                <div class="agent-instruction-item">BA gereksinimlerini TC'lerle eşleştirir</div>
                <div class="agent-instruction-item">Eksik coverage alanlarını tespit eder</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">📝 Agent 4: TC Raporcu</div>
            <div class="agent-role">Test Report Generator</div>
            <div class="agent-description">
                TC değerlendirme sonuçlarını rapor formatına dönüştürür ve JIRA'ya yazar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">TC sonuçlarını Markdown formatına çevirir</div>
                <div class="agent-instruction-item">Coverage metrikleri ekler</div>
                <div class="agent-instruction-item">JIRA comment'i oluşturur</div>
                <div class="agent-instruction-item">tc-qa-gecti/tc-qa-gecmedi label'larını yönetir</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎨 Design Compliance Agents")
    st.caption("4 adet specialized agent ile Tasarım ↔ BA uyumluluk kontrolü yapar")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">📋 Agent 1: Requirements Extractor</div>
            <div class="agent-role">Requirement ID Generator & Parser</div>
            <div class="agent-description">
                BA dokümanından gereksinimleri yapılandırılmış biçimde çıkarır ve her birine benzersiz ID verir (REQ-001, REQ-002...).
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">Her fonksiyonel gereksinimi tanımlar ve ID verir</div>
                <div class="agent-instruction-item">Kabul kriterlerini çıkarır</div>
                <div class="agent-instruction-item">UI bileşeni beklentilerini belirler</div>
                <div class="agent-instruction-item">UI metinleri/label'ları aynen korur</div>
                <div class="agent-instruction-item">İş kurallarını ve doğrulama koşullarını listeler</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">⚖️ Agent 3: Compliance Checker</div>
            <div class="agent-role">Requirement ↔ Design Validator</div>
            <div class="agent-description">
                İş analizi gereksinimlerini tasarım ekranı analiziyle karşılaştırarak uyumluluk kontrolü yapar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Kontrol Türleri</div>
                <div class="agent-instruction-item">Gereksinim ↔ Tasarım Eşleştirme (✅ UYUMLU / ⚠️ KISMİ / ❌ EKSİK)</div>
                <div class="agent-instruction-item">Eksik/Fazla Özellik Tespiti</div>
                <div class="agent-instruction-item">Acceptance Criteria Karşılaştırma</div>
                <div class="agent-instruction-item">UI Text/Label Doğrulama</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(139,92,246,0.1); border-radius: 6px; border-left: 3px solid #8b5cf6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #8b5cf6;">Ciddiyet Seviyeleri:</strong><br>
                    🔴 KRİTİK - İş akışı etkileniyor<br>
                    🟡 ORTA - UX sorunu var<br>
                    🟢 DÜŞÜK - Minör iyileştirme
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">👁️ Agent 2: Screen Analyzer</div>
            <div class="agent-role">UI/UX Vision Analyzer</div>
            <div class="agent-description">
                Figma ekran görüntüsünü detaylı biçimde analiz eder. Multimodal Gemini ile görsel analiz yapar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">TÜM UI bileşenlerini tespit eder ve listeler</div>
                <div class="agent-instruction-item">Her bileşenin üzerindeki metni/label'ı AYNEN yazar</div>
                <div class="agent-instruction-item">Sayfa yapısını ve navigasyon öğelerini tanımlar</div>
                <div class="agent-instruction-item">Form alanlarının tipini belirtir (text, dropdown, checkbox, radio)</div>
                <div class="agent-instruction-item">Görünür iş kurallarını tespit eder (zorunlu alan, validasyon)</div>
                <div class="agent-instruction-item">Kullanıcı akışı ve etkileşim kalıplarını değerlendirir</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">📊 Agent 4: Report Generator</div>
            <div class="agent-role">Compliance Report Formatter</div>
            <div class="agent-description">
                Uyumluluk kontrol sonuçlarını yapılandırılmış rapora dönüştürür. JIRA ticket oluşturulabilecek netlikte yazar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Rapor Bölümleri</div>
                <div class="agent-instruction-item">📊 Uyumluluk Özet Tablosu</div>
                <div class="agent-instruction-item">🔴 Kritik Bulgular</div>
                <div class="agent-instruction-item">🟡 Orta Bulgular</div>
                <div class="agent-instruction-item">🟢 Düşük Bulgular</div>
                <div class="agent-instruction-item">✅ Uyumlu Gereksinimler</div>
                <div class="agent-instruction-item">📝 Genel Değerlendirme</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 BRD Pipeline Agents (Dual AI System)")
    st.caption("3 adet generation agent (Anthropic Claude) + QA referee agents (Gemini 2.5 Flash)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">📋 WF1: İş Analizi Generator</div>
            <div class="agent-role">Business Requirements → BA Document</div>
            <div class="agent-description">
                BRD dokümanından ekran bazlı İş Analizi üretir. 2-chunk strategy ile büyük dokümanları işler, sonra merge eder.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Çıktı Yapısı</div>
                <div class="agent-instruction-item">Her ekran için: Açıklama, Gerekli Dokümanlar</div>
                <div class="agent-instruction-item">İş Akışı Diyagramı (adım adım)</div>
                <div class="agent-instruction-item">Fonksiyonel Gereksinimler (FR-001, FR-002...)</div>
                <div class="agent-instruction-item">İş Kuralları (BR-001, BR-002...)</div>
                <div class="agent-instruction-item">Kabul Kriterleri</div>
                <div class="agent-instruction-item">Validasyonlar (alan, kısıt, hata mesajı)</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">QA Referee (Gemini Flash):</strong><br>
                    • 6 kriter: Eksiksizlik, FR/BR Kalitesi, Akış Netliği, Tutarlılık, Doğrulama Kuralları, Doküman Yapısı<br>
                    • Geçme eşiği: 60/100<br>
                    • Max 3 revizyon
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">🧪 WF3: Test Case Generator</div>
            <div class="agent-role">BA + TA → Test Cases</div>
            <div class="agent-description">
                BA ve TA dokümanlarından 23-kolonlu Loodos şablonunda detaylı test case'ler üretir. Happy path + edge cases.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Test Case Şablonu (23 Kolon)</div>
                <div class="agent-instruction-item">test_case_id, br_id, tr_id, priority, channel</div>
                <div class="agent-instruction-item">testcase_type, user_type, test_area, test_scenario</div>
                <div class="agent-instruction-item">testcase, test_steps, precondition, test_data</div>
                <div class="agent-instruction-item">expected_result, postcondition, regression_case</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">QA Referee (Gemini Flash):</strong><br>
                    • 6 kriter: Kapsam, Sınır/Negatif Senaryolar, Test Adımları, Test Verisi, Öncelik, İzlenebilirlik<br>
                    • Hedef: 56+ test case<br>
                    • Geçme eşiği: 60/100
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">⚙️ WF2: Teknik Analiz Generator</div>
            <div class="agent-role">BA → Technical Analysis</div>
            <div class="agent-description">
                İş analizinden teknik analiz üretir. API endpoint, DTO, validasyon kuralları, cURL örnekleri ile developer-ready çıktı verir.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Çıktı Yapısı</div>
                <div class="agent-instruction-item">Genel Tanım (modül, stack, mimari)</div>
                <div class="agent-instruction-item">API Endpoint Detayları (method, path, request/response)</div>
                <div class="agent-instruction-item">DTO Veri Yapıları (field, tip, zorunlu, validasyon)</div>
                <div class="agent-instruction-item">Validasyon Kuralları (VR-001, VR-002...)</div>
                <div class="agent-instruction-item">Response Error Scenarios (HTTP code, error code, mesaj)</div>
                <div class="agent-instruction-item">Mock cURL Örnekleri</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">QA Referee (Gemini Flash):</strong><br>
                    • 6 kriter: Endpoint Eksiksizlik, DTO Kalitesi, Validasyon, Error Handling, Mock Data, Doküman Netliği<br>
                    • Geçme eşiği: 60/100<br>
                    • Max 3 revizyon
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">🔍 Checkpoint & Revision System</div>
            <div class="agent-role">State Management & Quality Control</div>
            <div class="agent-description">
                Her aşamada checkpoint kaydeder, kullanıcı onayı bekler. QA geçmezse max 3 kez revizyon yapar veya kullanıcı manuel düzeltme yapabilir.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Özellikler</div>
                <div class="agent-instruction-item">Session state + database checkpoint</div>
                <div class="agent-instruction-item">Manuel edit mode (kullanıcı JSON düzeltir)</div>
                <div class="agent-instruction-item">Skip QA option (force pass, API tasarrufu)</div>
                <div class="agent-instruction-item">Revizyon tracking (ba_revisions, ta_revisions, tc_revisions)</div>
                <div class="agent-instruction-item">Export ready: BA/TA (DOCX), TC (CSV/Excel)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 2: DOCUMENT INTELLIGENCE (Phase 2)
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">📚 Document Intelligence System (Phase 2)</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(6,182,212,0.1), rgba(16,185,129,0.1)); border: 1px solid rgba(6,182,212,0.3); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
        <div style="font-size: 14px; color: #cbd5e1; line-height: 1.7;">
            <strong style="color: #06b6d4;">🚀 Phase 2 Özellikleri:</strong> Doküman depolama, akıllı arama, AI-destekli eşleştirme ve doküman yönetimi özellikleri içeren kapsamlı bir doküman repository sistemi.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Document Repository
    st.markdown("### 📁 Document Repository")
    st.caption("Merkezi doküman depolama ve yönetim sistemi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">📚 Document Library</div>
            <div class="agent-role">Centralized Document Management</div>
            <div class="agent-description">
                Tüm BA, TA ve TC dokümanlarını merkezi bir yerde depolar, versiyonlar ve kategorize eder.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Özellikler</div>
                <div class="agent-instruction-item">Multi-tab arayüz (Dashboard, Upload, Search, Edit, Analytics)</div>
                <div class="agent-instruction-item">Doküman tipi bazlı filtreleme (BA/TA/TC)</div>
                <div class="agent-instruction-item">Proje ve JIRA entegrasyonu</div>
                <div class="agent-instruction-item">Versiyon yönetimi ve tarihçe</div>
                <div class="agent-instruction-item">Google Docs/Sheets import</div>
                <div class="agent-instruction-item">Doküman önizleme ve indirme</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">Veri Modeli:</strong><br>
                    • documents table: metadata, versioning, JIRA linking<br>
                    • document_content table: full text + enriched chunks<br>
                    • Automatic chunking with field extraction
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">🔀 Import & Merge</div>
            <div class="agent-role">Batch Operations & Deduplication</div>
            <div class="agent-description">
                Google Drive klasörlerinden toplu doküman import eder, duplicate detection yapar ve mevcut dokümanları günceller.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Görevler</div>
                <div class="agent-instruction-item">Folder ID ile batch import</div>
                <div class="agent-instruction-item">Akıllı duplicate detection (başlık, proje, tip)</div>
                <div class="agent-instruction-item">Merge stratejileri (yeni versiyon/üzerine yaz/atla)</div>
                <div class="agent-instruction-item">Import sonuç raporları</div>
                <div class="agent-instruction-item">ChromaDB otomatik reindexing</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(16,185,129,0.1); border-radius: 6px; border-left: 3px solid #10b981;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #10b981;">n8n Entegrasyonu:</strong><br>
                    • Google Drive folder listing webhook<br>
                    • Automated content fetch<br>
                    • Batch processing support
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Hybrid Search System
    st.markdown("### 🔍 Hybrid Search System")
    st.caption("Semantic + Keyword dual search engine")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">🧠 ChromaDB Vector Store</div>
            <div class="agent-role">Semantic Embedding & Similarity Search</div>
            <div class="agent-description">
                Claude 3.5 Sonnet embeddings kullanarak dokümanları vektör uzayında depolar ve semantic similarity araması yapar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Teknik Detaylar</div>
                <div class="agent-instruction-item">Embedding Model: voyage-3 (1024 dimensions)</div>
                <div class="agent-instruction-item">Collection: ba_qa_documents (571 chunks)</div>
                <div class="agent-instruction-item">Chunking Strategy: doc-type specific</div>
                <div class="agent-instruction-item">Metadata: doc_id, type, project, JIRA key</div>
                <div class="agent-instruction-item">Cosine similarity ranking</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(139,92,246,0.1); border-radius: 6px; border-left: 3px solid #8b5cf6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #8b5cf6;">Enriched Chunks:</strong><br>
                    BA: fonksiyonel_gereksinimler, is_kurallari, kabul_kriterleri, validasyonlar<br>
                    TA: request_body, response_body, hata_kodlari<br>
                    TC: precondition, test_data
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card purple">
            <div class="agent-name">📝 TF-IDF Keyword Search</div>
            <div class="agent-role">Term Frequency Exact Match</div>
            <div class="agent-description">
                scikit-learn TF-IDF vectorizer ile keyword-based arama yapar. Exact match ve technical term detection için optimize edilmiş.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Özellikler</div>
                <div class="agent-instruction-item">TF-IDF vectorization (max_features=5000)</div>
                <div class="agent-instruction-item">Cosine similarity ranking</div>
                <div class="agent-instruction-item">N-gram support (1-2)</div>
                <div class="agent-instruction-item">Stop words filtering</div>
                <div class="agent-instruction-item">Fast exact match (technical terms, IDs)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 20px; margin-top: 16px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600; color: #f1f5f9; margin-bottom: 12px;">
            ⚡ Hybrid Fusion Algorithm
        </div>
        <div style="font-size: 13px; color: #94a3b8; line-height: 1.7;">
            <strong>Formül:</strong> <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: #06b6d4;">hybrid_score = 0.4 × keyword_score + 0.6 × semantic_score</code><br><br>
            <strong>Alpha Weighting:</strong> %40 keyword (exact match) + %60 semantic (intent match)<br>
            <strong>Result Deduplication:</strong> Chunk-level → Document-level aggregation (best chunk per document)<br>
            <strong>Ortalama Performans:</strong> <2s response time, 85%+ relevance
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Smart Matching System
    st.markdown("### 🎯 Smart Matching System")
    st.caption("AI-powered task-to-document matching")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">🧪 Rule-Based Analyzer (Tier 1)</div>
            <div class="agent-role">Fast, Free Task Analysis</div>
            <div class="agent-description">
                NLP heuristikleri ile görev açıklamalarını analiz eder. Basit sorgular için AI maliyeti olmadan çalışır (%70 maliyet tasarrufu).
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Complexity Metrics</div>
                <div class="agent-instruction-item">Sentence count, word count, technical terms</div>
                <div class="agent-instruction-item">Ambiguous words, conditional statements</div>
                <div class="agent-instruction-item">Intent detection (ADD_FEATURE/UPDATE/FIX_BUG)</div>
                <div class="agent-instruction-item">Keyword extraction with TF-IDF</div>
                <div class="agent-instruction-item">Scope identification</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">Tiered Approach:</strong><br>
                    • Confidence >0.7 → Use rule-based (free)<br>
                    • Confidence <0.7 → Fall back to AI (costs $0.002)
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">📊 Match Explainer</div>
            <div class="agent-role">Human-Readable Reasoning Generator</div>
            <div class="agent-description">
                Eşleşme nedenlerini açıklar ve kullanıcıya aksiyon önerisi sunar (GÜNCELLE/YENİ OLUŞTUR/DEĞERLENDİR).
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Explanation Modes</div>
                <div class="agent-instruction-item">Template-based (high confidence, free)</div>
                <div class="agent-instruction-item">AI-generated (low confidence, detailed)</div>
                <div class="agent-instruction-item">Action suggestions with reasoning</div>
                <div class="agent-instruction-item">Score breakdown (semantic/keyword/metadata)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-detail-card blue">
            <div class="agent-name">🤖 AI Task Analyzer (Tier 2)</div>
            <div class="agent-role">Deep Semantic Analysis</div>
            <div class="agent-description">
                Karmaşık görevler için Claude Sonnet ile detaylı analiz yapar. Keywords, intent, scope, entities ve doc_type_relevance çıkarır.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">AI Features</div>
                <div class="agent-instruction-item">Deep intent classification</div>
                <div class="agent-instruction-item">Entity extraction (özellikler, bileşenler)</div>
                <div class="agent-instruction-item">Doc type relevance scoring (BA/TA/TC)</div>
                <div class="agent-instruction-item">Optimized search query generation</div>
                <div class="agent-instruction-item">Prompt caching (90% cost reduction)</div>
            </div>
            <div style="margin-top: 12px; padding: 8px 12px; background: rgba(59,130,246,0.1); border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="font-size: 11px; color: #94a3b8; line-height: 1.6;">
                    <strong style="color: #3b82f6;">Output Schema:</strong><br>
                    keywords, intent, scope, entities,<br>
                    doc_type_relevance, complexity, search_query
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="agent-detail-card green">
            <div class="agent-name">🎯 Smart Matcher Orchestrator</div>
            <div class="agent-role">End-to-End Matching Pipeline</div>
            <div class="agent-description">
                Tüm bileşenleri birleştirerek görevden eşleşen dokümanları bulur, skorlar ve sıralar.
            </div>
            <div class="agent-instructions">
                <div class="agent-instructions-title">Workflow</div>
                <div class="agent-instruction-item">Task analysis (tiered: rule-based → AI)</div>
                <div class="agent-instruction-item">Hybrid search (semantic + keyword)</div>
                <div class="agent-instruction-item">Document-level deduplication</div>
                <div class="agent-instruction-item">Confidence scoring & ranking</div>
                <div class="agent-instruction-item">Match explanation generation</div>
                <div class="agent-instruction-item">Analytics tracking (acceptance rate)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 20px; margin-top: 16px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600; color: #f1f5f9; margin-bottom: 12px;">
            📈 Smart Matching Metrics
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
            <div style="text-align: center; padding: 12px; background: rgba(59,130,246,0.05); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: #3b82f6;">85%</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">MATCH ACCURACY</div>
            </div>
            <div style="text-align: center; padding: 12px; background: rgba(16,185,129,0.05); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: #10b981;">73%</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">ACCEPTANCE RATE</div>
            </div>
            <div style="text-align: center; padding: 12px; background: rgba(245,158,11,0.05); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: #f59e0b;"><2s</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">RESPONSE TIME</div>
            </div>
            <div style="text-align: center; padding: 12px; background: rgba(139,92,246,0.05); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: #8b5cf6;">$0.007</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">COST/QUERY</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 3: INTEGRATIONS
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Platform Entegrasyonları</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">🔗</div>
                <div>
                    <div class="integration-name">1. n8n Webhook Proxy (Google Docs)</div>
                    <div class="integration-endpoint">https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy</div>
                </div>
            </div>
            <div class="integration-desc">
                Google Docs API authentication bypass için n8n workflow kullanır. BA dokümanlarını proxy üzerinden çeker.
            </div>
            <div class="integration-methods">
                <span class="method-badge">GET</span>
                <span class="method-badge">?doc_id={id}</span>
                <span class="method-badge">timeout: 120s</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Kullanım:</strong> BA Değerlendirme ve QA Değerlendirme pipeline'larında
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">📊</div>
                <div>
                    <div class="integration-name">2. n8n Webhook Proxy (Google Sheets)</div>
                    <div class="integration-endpoint">https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy</div>
                </div>
            </div>
            <div class="integration-desc">
                Google Sheets API authentication bypass için n8n workflow kullanır. TC dokümanlarını (23 sütun) proxy üzerinden çeker.
            </div>
            <div class="integration-methods">
                <span class="method-badge">GET</span>
                <span class="method-badge">?spreadsheet_id={id}</span>
                <span class="method-badge">timeout: 120s</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Kullanım:</strong> QA Değerlendirme pipeline'ında
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">🔑</div>
                <div>
                    <div class="integration-name">3. JIRA REST API v3</div>
                    <div class="integration-endpoint">https://loodos.atlassian.net/rest/api/3/</div>
                </div>
            </div>
            <div class="integration-desc">
                JIRA Cloud REST API ile task yönetimi. Basic Auth (email + API token) kullanır.
            </div>
            <div class="integration-methods">
                <span class="method-badge">jira_search()</span>
                <span class="method-badge">jira_get_issue()</span>
                <span class="method-badge">jira_add_label()</span>
                <span class="method-badge">jira_update_labels()</span>
                <span class="method-badge">jira_add_comment()</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Fonksiyonlar:</strong><br>
                • JQL ile task arama<br>
                • Issue detaylarını çekme<br>
                • Label yönetimi (qa-devam-ediyor, qa-tamamlandi, qa-gecti/gecmedi)<br>
                • Comment ekleme (Atlassian Document Format)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">📄</div>
                <div>
                    <div class="integration-name">4. Google Docs Direct Export</div>
                    <div class="integration-endpoint">https://docs.google.com/document/d/{id}/export?format=txt</div>
                </div>
            </div>
            <div class="integration-desc">
                Public paylaşılan Google Docs'u doğrudan export endpoint ile çeker. n8n proxy'ye alternatif.
            </div>
            <div class="integration-methods">
                <span class="method-badge">GET</span>
                <span class="method-badge">Public Sharing Required</span>
                <span class="method-badge">timeout: 30s</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Kullanım:</strong> Design Compliance page'de manuel BA upload için
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">🧠</div>
                <div>
                    <div class="integration-name">5. Gemini 2.5 Flash API</div>
                    <div class="integration-endpoint">Google Generative AI API</div>
                </div>
            </div>
            <div class="integration-desc">
                Tüm AI agent'ların backend'i. Agno Framework üzerinden Gemini 2.5 Flash modeli kullanır. 1M token context window.
            </div>
            <div class="integration-methods">
                <span class="method-badge">Model: gemini-2.5-flash</span>
                <span class="method-badge">Context: 1M tokens</span>
                <span class="method-badge">Multimodal</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Özellikler:</strong><br>
                • Text generation (BA/TC değerlendirme)<br>
                • Vision (Figma ekran analizi)<br>
                • Structured output (JSON response)<br>
                • Markdown formatting
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">🤖</div>
                <div>
                    <div class="integration-name">6. Anthropic Claude API</div>
                    <div class="integration-endpoint">Anthropic Messages API</div>
                </div>
            </div>
            <div class="integration-desc">
                BRD Pipeline'da doküman generation için kullanılır. Anthropic Claude modeli ile BA, TA, TC üretimi yapar. 200k token context window.
            </div>
            <div class="integration-methods">
                <span class="method-badge">Provider: Anthropic</span>
                <span class="method-badge">Context: 200k tokens</span>
                <span class="method-badge">Max Output: 16k tokens</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Kullanım:</strong><br>
                • BRD → BA generation (chunk-based)<br>
                • BA → TA generation<br>
                • BA + TA → TC generation<br>
                • Structured JSON output
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">💾</div>
                <div>
                    <div class="integration-name">7. SQLite Database</div>
                    <div class="integration-endpoint">Local File: data/baqa.db</div>
                </div>
            </div>
            <div class="integration-desc">
                Platform'un ana veri deposu. Analiz sonuçları, skorlar, raporlar, pipeline runs ve geçmiş veriler saklanır.
            </div>
            <div class="integration-methods">
                <span class="method-badge">analyses</span>
                <span class="method-badge">pipeline_runs</span>
                <span class="method-badge">documents</span>
                <span class="method-badge">task_matches</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Tablolar:</strong> 9 ana tablo (analyses, ba_results, tc_results, design_results, pipeline_runs, stage_outputs, documents, document_content, task_matches)
            </div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="integration-card">
            <div class="integration-header">
                <div class="integration-icon">🧠</div>
                <div>
                    <div class="integration-name">8. ChromaDB Vector Database</div>
                    <div class="integration-endpoint">Local Persist: data/chroma_db/</div>
                </div>
            </div>
            <div class="integration-desc">
                Doküman embedding'lerini depolar ve semantic similarity araması yapar. Voyage-3 embeddings kullanır (1024 dimensions).
            </div>
            <div class="integration-methods">
                <span class="method-badge">Collection: ba_qa_documents</span>
                <span class="method-badge">571 chunks</span>
                <span class="method-badge">Cosine Similarity</span>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: #64748b;">
                <strong>Özellikler:</strong> Persistent storage, metadata filtering, incremental updates, batch indexing
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("")  # Empty column for balance

# ═══════════════════════════════════════════════════════════
# TAB 4: PIPELINE FLOWS
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">3 Farklı Pipeline Akışı</div>', unsafe_allow_html=True)

    # Pipeline 1: BA Değerlendirme
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-title">🔵 Pipeline 1: BA Değerlendirme (4-Agent Sequential)</div>
        <div class="pipeline-steps">
            <div class="pipeline-step">
                <div class="pipeline-step-number">1</div>
                <div class="pipeline-step-name">JIRA Tarayıcı</div>
                <div class="pipeline-step-desc">JQL ile BA task'ları tarar, Google Docs URL çıkarır</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">2</div>
                <div class="pipeline-step-name">Doküman Okuyucu</div>
                <div class="pipeline-step-desc">n8n proxy ile BA dokümanını çeker ve parse eder</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">3</div>
                <div class="pipeline-step-name">Kalite Değerlendirici</div>
                <div class="pipeline-step-desc">9 kriter üzerinden AI analizi yapar (Gemini 2.5 Flash)</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">4</div>
                <div class="pipeline-step-name">Raporcu</div>
                <div class="pipeline-step-desc">JIRA'ya comment yazar, label'ları günceller, DB'ye kaydeder</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("**Kullanım:** BA Değerlendirme sayfasından \"⚡ Sıradakini Otomatik Değerlendir\" butonu")
    st.caption("**Ortalama Süre:** 45-60 saniye")
    st.caption("**Çıktı:** 9 kriter puanı, genel puan (0-100), JIRA comment, qa-gecti/qa-gecmedi label")

    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline 2: TC Değerlendirme
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-title">🟢 Pipeline 2: QA Değerlendirme (4-Agent Sequential + BA Link)</div>
        <div class="pipeline-steps">
            <div class="pipeline-step">
                <div class="pipeline-step-number">1</div>
                <div class="pipeline-step-name">JIRA & Sheet Tarayıcı</div>
                <div class="pipeline-step-desc">TC task bulur, linked BA task'ı tespit eder, Sheet URL çıkarır</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">2</div>
                <div class="pipeline-step-name">Doküman Birleştirici</div>
                <div class="pipeline-step-desc">BA dokümanı + TC sheets'i n8n proxy ile çeker ve birleştirir</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">3</div>
                <div class="pipeline-step-name">TC Değerlendirici</div>
                <div class="pipeline-step-desc">8 kriter üzerinden AI analizi yapar, BA coverage kontrolü</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">4</div>
                <div class="pipeline-step-name">TC Raporcu</div>
                <div class="pipeline-step-desc">JIRA comment, tc-qa-gecti/gecmedi label, DB kayıt</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("**Kullanım:** QA Değerlendirme sayfasından \"⚡ Sıradakini Otomatik Değerlendir\" butonu")
    st.caption("**Ortalama Süre:** 60-75 saniye (BA fetch dahil)")
    st.caption("**Çıktı:** 8 kriter puanı, coverage metrikleri, JIRA comment, tc-qa-gecti/gecmedi label")

    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline 3: Design Compliance
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-title">🟣 Pipeline 3: Design Compliance (4-Agent Parallel + Sequential)</div>
        <div class="pipeline-steps">
            <div class="pipeline-step" style="background: rgba(59,130,246,0.05);">
                <div class="pipeline-step-number">1</div>
                <div class="pipeline-step-name">Requirements Extractor</div>
                <div class="pipeline-step-desc">BA'dan REQ-001, REQ-002... formatında gereksinimleri çıkarır</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step" style="background: rgba(139,92,246,0.05);">
                <div class="pipeline-step-number">2</div>
                <div class="pipeline-step-name">Screen Analyzer</div>
                <div class="pipeline-step-desc">Figma ekranlarını Vision AI ile analiz eder (multimodal Gemini)</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step" style="background: rgba(236,72,153,0.05);">
                <div class="pipeline-step-number">3</div>
                <div class="pipeline-step-name">Compliance Checker</div>
                <div class="pipeline-step-desc">REQ ↔ Screen eşleştirmesi yapar, uyumluluk kontrolü</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step" style="background: rgba(16,185,129,0.05);">
                <div class="pipeline-step-number">4</div>
                <div class="pipeline-step-name">Report Generator</div>
                <div class="pipeline-step-desc">Uyumluluk raporu oluşturur (🔴🟡🟢 bulgular)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("**Kullanım:** Design Compliance sayfasından \"🚀 Uyumluluk Kontrolünü Başlat\" butonu")
    st.caption("**Ortalama Süre:** 90-120 saniye (ekran sayısına göre değişir)")
    st.caption("**Çıktı:** Uyumluluk matrisi, kritik/orta/düşük bulgular, eksik gereksinimler, Markdown rapor")

    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline 4: BRD Pipeline
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-title">🟠 Pipeline 4: BRD Pipeline (3-Stage Sequential with QA Referee)</div>
        <div class="pipeline-steps">
            <div class="pipeline-step">
                <div class="pipeline-step-number">1</div>
                <div class="pipeline-step-name">WF1: BA Generator</div>
                <div class="pipeline-step-desc">BRD → BA (Claude AI) → QA (Gemini) → Manual Review</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">2</div>
                <div class="pipeline-step-name">WF2: TA Generator</div>
                <div class="pipeline-step-desc">BA → TA (Claude AI) → QA (Gemini) → Manual Review</div>
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <div class="pipeline-step-number">3</div>
                <div class="pipeline-step-name">WF3: TC Generator</div>
                <div class="pipeline-step-desc">BA + TA → TC (Claude AI) → QA (Gemini) → Export</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("**Kullanım:** BRD Pipeline sayfasından BRD upload → Adım adım manuel onay ile ilerler")
    st.caption("**Ortalama Süre:** 5-8 dakika (3 stage × 2 chunk + QA + revisions)")
    st.caption("**Çıktı:** BA (DOCX), TA (DOCX), TC (CSV + Excel 23 kolon), QA skorları, revision tracking")
    st.caption("**Özellikler:** Checkpoint system, skip QA option, manual edit mode, force pass, database storage")

    st.markdown("---")
    st.markdown("### 🔄 Agent İşbirliği Senaryoları")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 20px; margin-bottom: 14px;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600; color: #f1f5f9; margin-bottom: 12px;">
                📋 Senaryo 1: BA + TC Birlikte Değerlendirme
            </div>
            <div style="font-size: 13px; color: #94a3b8; line-height: 1.7;">
                <strong>Akış:</strong><br>
                1. BA Pipeline çalışır → BA skoru 75/100 (GEÇTİ)<br>
                2. TC Pipeline tetiklenir → BA dokümanını baz alır<br>
                3. TC Agent BA gereksinimlerini kullanarak coverage kontrolü yapar<br>
                4. TC skoru: 82/100 (GEÇTİ, %95 coverage)<br>
                <br>
                <strong>Agent İşbirliği:</strong> TC Agent, BA Agent'ın çıktısını kullanarak traceability analizi yapar.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 20px; margin-bottom: 14px;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600; color: #f1f5f9; margin-bottom: 12px;">
                🎨 Senaryo 2: BA → Design Compliance Chain
            </div>
            <div style="font-size: 13px; color: #94a3b8; line-height: 1.7;">
                <strong>Akış:</strong><br>
                1. BA dokümanı Requirements Extractor'a verilir<br>
                2. Figma ekranları Screen Analyzer'a verilir<br>
                3. Compliance Checker iki agent'ın çıktısını karşılaştırır<br>
                4. Report Generator final raporu oluşturur<br>
                <br>
                <strong>Agent İşbirliği:</strong> 4 agent sequential olarak çalışır, her biri bir öncekinin çıktısını kullanır.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 5: TECH STACK
# ═══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Teknoloji Stack</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">🐍 Backend</div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                • Python 3.14<br>
                • Streamlit 1.40+<br>
                • Agno Framework 2.5+<br>
                • asyncio<br>
                • scikit-learn (TF-IDF)<br>
                • ChromaDB (vector store)
            </div>
        </div>

        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">🧠 AI / LLM</div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                • Gemini 2.5 Flash (Evaluation)<br>
                • Anthropic Claude (Generation)<br>
                • Voyage-3 (Embeddings - 1024d)<br>
                • 200k-1M token context<br>
                • Multimodal (vision)<br>
                • Structured JSON output<br>
                • Prompt caching
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">🔗 Entegrasyonlar</div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                • JIRA REST API v3<br>
                • n8n Webhook Proxy<br>
                • Google Docs/Sheets<br>
                • Figma (design upload)<br>
                • Google Drive API
            </div>
        </div>

        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">💾 Data Storage</div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                • SQLite (metadata)<br>
                • ChromaDB (embeddings)<br>
                • Session State<br>
                • File cache (TTL: 1h)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">📊 Visualization</div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                • Plotly<br>
                • Custom CSS<br>
                • Gradient UI<br>
                • Responsive grid
            </div>
        </div>

        <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">🚀 Deployment</div>
            <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                • Streamlit Cloud<br>
                • GitHub Actions CI<br>
                • Secrets management
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #64748b; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
    BA&QA Intelligence Platform v2.0 — Architecture Document — February 2026<br>
    <span style="font-size: 10px; color: #475569;">Phase 2: Document Intelligence System Active ✨</span>
</div>
""", unsafe_allow_html=True)
