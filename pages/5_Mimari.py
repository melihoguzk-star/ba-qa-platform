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
        max-width: 1400px;
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

    /* Layer Cards */
    .layer-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .layer-card:hover {
        border-color: rgba(59,130,246,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .layer-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }
    .layer-card.blue::before { background: linear-gradient(135deg, #3b82f6, #06b6d4); }
    .layer-card.purple::before { background: linear-gradient(135deg, #8b5cf6, #ec4899); }
    .layer-card.green::before { background: linear-gradient(135deg, #10b981, #06b6d4); }
    .layer-card.orange::before { background: linear-gradient(135deg, #f59e0b, #ef4444); }

    .layer-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
    }
    .layer-icon {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    .layer-icon.blue { background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.2); }
    .layer-icon.purple { background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.2); }
    .layer-icon.green { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.2); }
    .layer-icon.orange { background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.2); }

    .layer-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: #f1f5f9;
    }
    .layer-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-top: 2px;
    }

    /* Component Cards */
    .component-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    .component-card:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.1);
    }
    .component-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 500;
        color: #f1f5f9;
        margin-bottom: 4px;
    }
    .component-desc {
        font-size: 12px;
        color: #64748b;
        line-height: 1.5;
    }
    .component-tag {
        display: inline-block;
        margin-top: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }
    .tag-new { background: rgba(16,185,129,0.15); color: #10b981; }
    .tag-existing { background: rgba(59,130,246,0.15); color: #3b82f6; }
    .tag-enhanced { background: rgba(245,158,11,0.15); color: #f59e0b; }

    /* Flow Nodes */
    .flow-container {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .flow-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #06b6d4;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 16px;
        text-align: center;
        font-weight: 600;
    }
    .flow-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .flow-node {
        background: #111827;
        border: 1px solid #2a3654;
        border-radius: 10px;
        padding: 14px 20px;
        text-align: center;
        min-width: 140px;
        transition: all 0.2s;
    }
    .flow-node:hover {
        transform: scale(1.05);
        border-color: rgba(59,130,246,0.4);
    }
    .flow-node-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        color: #f1f5f9;
    }
    .flow-node-sub {
        font-size: 10px;
        color: #64748b;
        margin-top: 4px;
    }
    .flow-arrow {
        color: #64748b;
        font-size: 20px;
        font-family: 'JetBrains Mono', monospace;
    }
    .node-blue { border-color: rgba(59,130,246,0.3); background: rgba(59,130,246,0.08); }
    .node-purple { border-color: rgba(139,92,246,0.3); background: rgba(139,92,246,0.08); }
    .node-green { border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.08); }
    .node-orange { border-color: rgba(245,158,11,0.3); background: rgba(245,158,11,0.08); }
    .node-cyan { border-color: rgba(6,182,212,0.3); background: rgba(6,182,212,0.08); }
    .node-pink { border-color: rgba(236,72,153,0.3); background: rgba(236,72,153,0.08); }

    /* Page Cards */
    .page-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 14px;
        position: relative;
        transition: all 0.3s;
    }
    .page-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59,130,246,0.3);
    }
    .page-card-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 48px;
        font-weight: 700;
        color: rgba(255,255,255,0.04);
        position: absolute;
        top: 12px; right: 20px;
    }
    .page-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 4px;
        color: #f1f5f9;
    }
    .page-card-route {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #06b6d4;
        margin-bottom: 12px;
    }
    .page-card-features {
        list-style: none;
        padding: 0;
    }
    .page-card-features li {
        font-size: 13px;
        color: #94a3b8;
        padding: 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .page-card-features li::before {
        content: '›';
        color: #3b82f6;
        font-weight: 700;
        font-size: 16px;
    }

    /* Tech Cards */
    .tech-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 18px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin-bottom: 12px;
    }
    .tech-card-icon {
        width: 40px; height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .tech-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 4px;
        color: #f1f5f9;
    }
    .tech-card-items {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.6;
    }

    /* DB Tables */
    .db-table {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .db-table-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 600;
        color: #06b6d4;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .db-table-name::before {
        content: '⊞';
        font-size: 16px;
    }
    .db-field {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #94a3b8;
        padding: 4px 0;
    }
    .db-field .type {
        color: #64748b;
        font-size: 11px;
    }
    .db-field .pk {
        color: #f59e0b;
        font-size: 10px;
        margin-left: 4px;
    }

    /* File Tree */
    .file-tree {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.8;
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 24px;
    }
    .file-tree .folder { color: #06b6d4; }
    .file-tree .file { color: #f59e0b; }
    .file-tree .comment { color: #64748b; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
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

    /* Copy Button */
    .copy-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 6px;
        padding: 6px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #3b82f6;
        cursor: pointer;
        transition: all 0.2s;
        margin-left: 8px;
    }
    .copy-btn:hover {
        background: rgba(59,130,246,0.2);
        border-color: rgba(59,130,246,0.4);
    }
    .copy-btn.copied {
        background: rgba(16,185,129,0.1);
        border-color: rgba(16,185,129,0.2);
        color: #10b981;
    }

    /* Smooth Scroll */
    html {
        scroll-behavior: smooth;
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

    /* Hover effects for layer cards */
    .layer-card {
        cursor: default;
    }

    /* Add animation to stats */
    @keyframes countUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Print Styles */
    @media print {
        .scroll-top-btn,
        .breadcrumb,
        button {
            display: none !important;
        }

        .main {
            background: white;
        }

        .layer-card,
        .component-card,
        .flow-container,
        .page-card,
        .tech-card,
        .db-table {
            border: 1px solid #ccc;
            page-break-inside: avoid;
        }

        * {
            color: #000 !important;
        }
    }

    /* Responsive Grid for Stats */
    @media (max-width: 768px) {
        div[style*="grid-template-columns: repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
</style>

<script>
    // Scroll to Top Button
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

    // Add active state to TOC items based on scroll position
    window.addEventListener('scroll', function() {
        const tocItems = document.querySelectorAll('.toc-item');
        tocItems.forEach(item => {
            // This is a simplified version - you can enhance this
            // to detect which tab is currently visible
        });
    });
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
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px;">
    <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">4</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Katman</div>
    </div>
    <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #8b5cf6; margin-bottom: 4px;">6+</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Agent</div>
    </div>
    <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #10b981; margin-bottom: 4px;">6</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Sayfa</div>
    </div>
    <div style="background: #1a2236; border: 1px solid #2a3654; border-radius: 12px; padding: 18px; text-align: center;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #f59e0b; margin-bottom: 4px;">5+</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">Entegrasyon</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tab Navigation ──
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏗️ Mimari", "🔄 Veri Akışı", "📱 Sayfa Yapısı", "⚙️ Tech Stack", "🗄️ Veri Modeli"])

# ═══════════════════════════════════════════════════════════
# TAB 1: ARCHITECTURE OVERVIEW
# ═══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Katmanlı Mimari</div>', unsafe_allow_html=True)

    # Layer 1: Presentation
    st.markdown("""
    <div class="layer-card blue">
        <div class="layer-header">
            <div class="layer-icon blue">🖥️</div>
            <div>
                <div class="layer-title">Presentation Layer</div>
                <div class="layer-subtitle">Streamlit Multi-Page Dashboard</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Dashboard</div>
            <div class="component-desc">Genel bakış, KPI'lar, son analizler, skor trendleri</div>
            <span class="component-tag tag-new">NEW</span>
        </div>
        <div class="component-card">
            <div class="component-name">QA Analiz</div>
            <div class="component-desc">BA doküman + Test Case kalite değerlendirme</div>
            <span class="component-tag tag-existing">FROM QA-AGENT</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Design Compliance</div>
            <div class="component-desc">Figma tasarım vs BA uyumluluk kontrolü</div>
            <span class="component-tag tag-existing">FROM DESIGN-AGENT</span>
        </div>
        <div class="component-card">
            <div class="component-name">JIRA Entegrasyon</div>
            <div class="component-desc">Task çekme, comment yazma, label yönetimi</div>
            <span class="component-tag tag-enhanced">ENHANCED</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Raporlar</div>
            <div class="component-desc">Google Sheets export, trend grafikleri</div>
            <span class="component-tag tag-enhanced">ENHANCED</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Layer 2: Agent Orchestration
    st.markdown("""
    <div class="layer-card purple">
        <div class="layer-header">
            <div class="layer-icon purple">🤖</div>
            <div>
                <div class="layer-title">Agent Orchestration Layer</div>
                <div class="layer-subtitle">Agno Framework + Multi-Agent Coordinator</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">BA Analyst Agent</div>
            <div class="component-desc">İş Analizi doküman kalite skoru (yapı, kapsam, netlik)</div>
            <span class="component-tag tag-existing">FROM QA-AGENT</span>
        </div>
        <div class="component-card">
            <div class="component-name">TC Evaluator Agent</div>
            <div class="component-desc">Test Case completeness & coverage analizi</div>
            <span class="component-tag tag-existing">FROM QA-AGENT</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">UX Reviewer Agent</div>
            <div class="component-desc">Figma screen vs gereksinim uyumluluk kontrolü</div>
            <span class="component-tag tag-existing">FROM DESIGN-AGENT</span>
        </div>
        <div class="component-card">
            <div class="component-name">Requirements Agent</div>
            <div class="component-desc">BA'dan gereksinim listesi çıkarma (REQ-xxx)</div>
            <span class="component-tag tag-existing">FROM DESIGN-AGENT</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Orchestrator</div>
            <div class="component-desc">Agent seçimi, paralel çalıştırma, sonuç birleştirme</div>
            <span class="component-tag tag-new">NEW</span>
        </div>
        <div class="component-card">
            <div class="component-name">Report Generator Agent</div>
            <div class="component-desc">Tüm sonuçları birleştirip unified rapor üretme</div>
            <span class="component-tag tag-new">NEW</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Layer 3: Integration
    st.markdown("""
    <div class="layer-card green">
        <div class="layer-header">
            <div class="layer-icon green">🔗</div>
            <div>
                <div class="layer-title">Integration Layer</div>
                <div class="layer-subtitle">Dış Servis Bağlantıları</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">JIRA Client</div>
            <div class="component-desc">REST API — task CRUD, comment, label, transition</div>
            <span class="component-tag tag-enhanced">ENHANCED</span>
        </div>
        <div class="component-card">
            <div class="component-name">Google Docs Client</div>
            <div class="component-desc">BA doküman okuma (Drive API v3)</div>
            <span class="component-tag tag-existing">FROM QA-AGENT</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Google Sheets Client</div>
            <div class="component-desc">TC veri okuma + sonuç yazma (Sheets API v4)</div>
            <span class="component-tag tag-enhanced">ENHANCED</span>
        </div>
        <div class="component-card">
            <div class="component-name">Figma Client</div>
            <div class="component-desc">Design frame export, node traverse (Figma REST API)</div>
            <span class="component-tag tag-existing">FROM DESIGN-AGENT</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Gemini API Client</div>
            <div class="component-desc">Gemini 2.5 Flash — tüm agent'ların LLM backend'i</div>
            <span class="component-tag tag-existing">SHARED</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Layer 4: Data & Storage
    st.markdown("""
    <div class="layer-card orange">
        <div class="layer-header">
            <div class="layer-icon orange">💾</div>
            <div>
                <div class="layer-title">Data & Storage Layer</div>
                <div class="layer-subtitle">Sonuç Saklama & Cache</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">SQLite DB</div>
            <div class="component-desc">Analiz sonuçları, skorlar, geçmiş veriler</div>
            <span class="component-tag tag-new">NEW</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Google Sheets</div>
            <div class="component-desc">Mevcut sonuç tabloları (geriye uyumlu)</div>
            <span class="component-tag tag-existing">EXISTING</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="component-card">
            <div class="component-name">Session State</div>
            <div class="component-desc">Streamlit session — anlık analiz sonuçları</div>
            <span class="component-tag tag-existing">EXISTING</span>
        </div>
        <div class="component-card">
            <div class="component-name">Cache Layer</div>
            <div class="component-desc">Doküman cache, API response cache (TTL: 1h)</div>
            <span class="component-tag tag-new">NEW</span>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 2: DATA FLOW
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Veri Akışları</div>', unsafe_allow_html=True)

    # Flow 1
    st.markdown("""
    <div class="flow-container">
        <div class="flow-label">Flow 1 — BA + TC Quality Assessment</div>
        <div class="flow-row">
            <div class="flow-node node-blue">
                <div class="flow-node-label">JIRA Task</div>
                <div class="flow-node-sub">Issue key ile çek</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-cyan">
                <div class="flow-node-label">Parse Links</div>
                <div class="flow-node-sub">Docs + Sheets URL</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-green">
                <div class="flow-node-label">Fetch Docs</div>
                <div class="flow-node-sub">BA doc + TC sheets</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-purple">
                <div class="flow-node-label">BA Agent</div>
                <div class="flow-node-sub">Kalite analizi</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-purple">
                <div class="flow-node-label">TC Agent</div>
                <div class="flow-node-sub">Coverage analizi</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-orange">
                <div class="flow-node-label">Report</div>
                <div class="flow-node-sub">Sheets + JIRA comment</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Flow 2
    st.markdown("""
    <div class="flow-container">
        <div class="flow-label">Flow 2 — Design Compliance Check</div>
        <div class="flow-row">
            <div class="flow-node node-blue">
                <div class="flow-node-label">BA Document</div>
                <div class="flow-node-sub">Upload / JIRA link</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-cyan">
                <div class="flow-node-label">Req Extract</div>
                <div class="flow-node-sub">REQ-001, REQ-002...</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-green">
                <div class="flow-node-label">Figma Screens</div>
                <div class="flow-node-sub">Image upload</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-purple">
                <div class="flow-node-label">UX Review Agent</div>
                <div class="flow-node-sub">Screen ↔ Req eşleşme</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-orange">
                <div class="flow-node-label">Compliance Report</div>
                <div class="flow-node-sub">Score + eksikler</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Flow 3
    st.markdown("""
    <div class="flow-container">
        <div class="flow-label">Flow 3 — Full Pipeline (Combined)</div>
        <div class="flow-row">
            <div class="flow-node node-blue">
                <div class="flow-node-label">JIRA Issue</div>
                <div class="flow-node-sub">Tek tıkla başlat</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-pink">
                <div class="flow-node-label">🎯 Orchestrator</div>
                <div class="flow-node-sub">Paralel agent dispatch</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-purple" style="min-width: 220px;">
                <div class="flow-node-label" style="font-size: 10px;">BA Agent ∥ TC Agent ∥ UX Agent</div>
                <div class="flow-node-sub">Eş zamanlı çalışma</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-green">
                <div class="flow-node-label">Merge Results</div>
                <div class="flow-node-sub">Unified score</div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-node node-orange">
                <div class="flow-node-label">Dashboard</div>
                <div class="flow-node-sub">Sheets + JIRA + UI</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 3: PAGE STRUCTURE
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Sayfa Yapısı</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="page-card">
            <div class="page-card-num">01</div>
            <div class="page-card-title">📊 Dashboard</div>
            <div class="page-card-route">
                /pages/1_Dashboard.py
                <button class="copy-btn" onclick="navigator.clipboard.writeText('/pages/1_Dashboard.py'); this.classList.add('copied'); this.innerHTML='✓'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋'}, 2000)">
                    📋
                </button>
            </div>
            <ul class="page-card-features">
                <li>Toplam analiz sayısı, ortalama skorlar</li>
                <li>Son 7 gün trend grafiği (Plotly)</li>
                <li>Proje bazlı kalite heat-map</li>
                <li>En son 10 analiz sonucu tablosu</li>
                <li>Agent bazlı performans metrikleri</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-card">
            <div class="page-card-num">02</div>
            <div class="page-card-title">📋 QA Değerlendirme</div>
            <div class="page-card-route">
                /pages/2_QA_Analysis.py
                <button class="copy-btn" onclick="navigator.clipboard.writeText('/pages/2_QA_Analysis.py'); this.classList.add('copied'); this.innerHTML='✓'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋'}, 2000)">
                    📋
                </button>
            </div>
            <ul class="page-card-features">
                <li>JIRA issue key ile otomatik veri çekme</li>
                <li>BA doküman kalite analizi (skor + detay)</li>
                <li>TC coverage & completeness değerlendirme</li>
                <li>BA vs BRD çapraz referans kontrolü</li>
                <li>JIRA'ya otomatik comment yazma</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="page-card">
            <div class="page-card-num">03</div>
            <div class="page-card-title">🎨 Design Compliance</div>
            <div class="page-card-route">
                /pages/3_Design_Compliance.py
                <button class="copy-btn" onclick="navigator.clipboard.writeText('/pages/3_Design_Compliance.py'); this.classList.add('copied'); this.innerHTML='✓'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋'}, 2000)">
                    📋
                </button>
            </div>
            <ul class="page-card-features">
                <li>BA doküman yükleme veya JIRA'dan çekme</li>
                <li>Figma ekran görselleri yükleme</li>
                <li>Gereksinim listesi çıkarma (REQ-xxx)</li>
                <li>Screen ↔ Requirement eşleşme matrisi</li>
                <li>Compliance skoru & eksik kapsam raporu</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-card">
            <div class="page-card-num">04</div>
            <div class="page-card-title">🔗 JIRA Manager</div>
            <div class="page-card-route">
                /pages/4_JIRA_Manager.py
                <button class="copy-btn" onclick="navigator.clipboard.writeText('/pages/4_JIRA_Manager.py'); this.classList.add('copied'); this.innerHTML='✓'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋'}, 2000)">
                    📋
                </button>
            </div>
            <ul class="page-card-features">
                <li>Proje bazlı task listeleme & filtreleme</li>
                <li>Toplu analiz başlatma (batch mode)</li>
                <li>Label yönetimi (qa-devam, qa-tamamlandi)</li>
                <li>Comment geçmişi görüntüleme</li>
                <li>Task transition (status değiştirme)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="page-card">
            <div class="page-card-num">05</div>
            <div class="page-card-title">📈 Raporlar</div>
            <div class="page-card-route">
                /pages/5_Reports.py
                <button class="copy-btn" onclick="navigator.clipboard.writeText('/pages/5_Reports.py'); this.classList.add('copied'); this.innerHTML='✓'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋'}, 2000)">
                    📋
                </button>
            </div>
            <ul class="page-card-features">
                <li>Google Sheets'e toplu export</li>
                <li>Sprint bazlı kalite raporu</li>
                <li>Agent performans karşılaştırma</li>
                <li>CSV / Excel indirme</li>
                <li>Zaman serisi trend analizi</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-card">
            <div class="page-card-num">06</div>
            <div class="page-card-title">⚙️ Ayarlar</div>
            <div class="page-card-route">
                /pages/6_Settings.py
                <button class="copy-btn" onclick="navigator.clipboard.writeText('/pages/6_Settings.py'); this.classList.add('copied'); this.innerHTML='✓'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋'}, 2000)">
                    📋
                </button>
            </div>
            <ul class="page-card-features">
                <li>API key yönetimi (Gemini, JIRA, Google)</li>
                <li>JIRA proje konfigürasyonu</li>
                <li>Google Sheets hedef tablo seçimi</li>
                <li>Agent prompt özelleştirme</li>
                <li>Bildirim & webhook ayarları</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 4: TECH STACK
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Teknoloji Stack</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-icon">🐍</div>
            <div>
                <div class="tech-card-title">Backend</div>
                <div class="tech-card-items">Python 3.11+ · Streamlit 1.40+ · Agno Framework · asyncio</div>
            </div>
        </div>
        <div class="tech-card">
            <div class="tech-card-icon">🧠</div>
            <div>
                <div class="tech-card-title">AI / LLM</div>
                <div class="tech-card-items">Gemini 2.5 Flash (1M context) · Agno multi-agent · Structured output</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-icon">🔗</div>
            <div>
                <div class="tech-card-title">Entegrasyonlar</div>
                <div class="tech-card-items">JIRA REST API v3 · Google Drive/Sheets API · Figma REST API</div>
            </div>
        </div>
        <div class="tech-card">
            <div class="tech-card-icon">💾</div>
            <div>
                <div class="tech-card-title">Data Storage</div>
                <div class="tech-card-items">SQLite (lokal) · Google Sheets (paylaşılabilir) · Streamlit Session State</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-icon">📊</div>
            <div>
                <div class="tech-card-title">Visualizasyon</div>
                <div class="tech-card-items">Plotly · Streamlit charts · Custom CSS theming</div>
            </div>
        </div>
        <div class="tech-card">
            <div class="tech-card-icon">🚀</div>
            <div>
                <div class="tech-card-title">Deployment</div>
                <div class="tech-card-items">Streamlit Cloud · GitHub Actions CI · Secrets management</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 5: DATA MODEL
# ═══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 600; color: #f1f5f9; margin-bottom: 20px;">Veri Modeli (SQLite)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="db-table">
            <div class="db-table-name">
                analyses
                <button class="copy-btn" onclick="navigator.clipboard.writeText('analyses'); this.classList.add('copied'); this.innerHTML='✓ Kopyalandı'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋 Kopyala'}, 2000)">
                    📋 Kopyala
                </button>
            </div>
            <div class="db-field">id <span class="type">INTEGER</span><span class="pk">PK</span></div>
            <div class="db-field">jira_key <span class="type">TEXT</span></div>
            <div class="db-field">project <span class="type">TEXT</span></div>
            <div class="db-field">analysis_type <span class="type">ENUM(qa, design, full)</span></div>
            <div class="db-field">status <span class="type">ENUM(pending, running, done, error)</span></div>
            <div class="db-field">created_at <span class="type">DATETIME</span></div>
            <div class="db-field">completed_at <span class="type">DATETIME</span></div>
            <div class="db-field">triggered_by <span class="type">TEXT</span></div>
        </div>

        <div class="db-table">
            <div class="db-table-name">
                qa_results
                <button class="copy-btn" onclick="navigator.clipboard.writeText('qa_results'); this.classList.add('copied'); this.innerHTML='✓ Kopyalandı'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋 Kopyala'}, 2000)">
                    📋 Kopyala
                </button>
            </div>
            <div class="db-field">id <span class="type">INTEGER</span><span class="pk">PK</span></div>
            <div class="db-field">analysis_id <span class="type">INTEGER</span><span class="pk">FK</span></div>
            <div class="db-field">ba_score <span class="type">FLOAT</span></div>
            <div class="db-field">ba_detail <span class="type">JSON</span></div>
            <div class="db-field">tc_score <span class="type">FLOAT</span></div>
            <div class="db-field">tc_detail <span class="type">JSON</span></div>
            <div class="db-field">tc_coverage_pct <span class="type">FLOAT</span></div>
            <div class="db-field">overall_score <span class="type">FLOAT</span></div>
            <div class="db-field">recommendations <span class="type">JSON</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="db-table">
            <div class="db-table-name">
                design_results
                <button class="copy-btn" onclick="navigator.clipboard.writeText('design_results'); this.classList.add('copied'); this.innerHTML='✓ Kopyalandı'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋 Kopyala'}, 2000)">
                    📋 Kopyala
                </button>
            </div>
            <div class="db-field">id <span class="type">INTEGER</span><span class="pk">PK</span></div>
            <div class="db-field">analysis_id <span class="type">INTEGER</span><span class="pk">FK</span></div>
            <div class="db-field">requirements_count <span class="type">INTEGER</span></div>
            <div class="db-field">screens_count <span class="type">INTEGER</span></div>
            <div class="db-field">compliance_score <span class="type">FLOAT</span></div>
            <div class="db-field">coverage_matrix <span class="type">JSON</span></div>
            <div class="db-field">missing_reqs <span class="type">JSON</span></div>
            <div class="db-field">ux_findings <span class="type">JSON</span></div>
        </div>

        <div class="db-table">
            <div class="db-table-name">
                jira_sync_log
                <button class="copy-btn" onclick="navigator.clipboard.writeText('jira_sync_log'); this.classList.add('copied'); this.innerHTML='✓ Kopyalandı'; setTimeout(() => {this.classList.remove('copied'); this.innerHTML='📋 Kopyala'}, 2000)">
                    📋 Kopyala
                </button>
            </div>
            <div class="db-field">id <span class="type">INTEGER</span><span class="pk">PK</span></div>
            <div class="db-field">analysis_id <span class="type">INTEGER</span><span class="pk">FK</span></div>
            <div class="db-field">action <span class="type">ENUM(comment, label, transition)</span></div>
            <div class="db-field">jira_key <span class="type">TEXT</span></div>
            <div class="db-field">payload <span class="type">JSON</span></div>
            <div class="db-field">success <span class="type">BOOLEAN</span></div>
            <div class="db-field">created_at <span class="type">DATETIME</span></div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #64748b; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
    BA&QA Intelligence Platform v1.0 — Architecture Document — February 2026
</div>
""", unsafe_allow_html=True)
