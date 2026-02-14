"""
BA&QA Intelligence Platform — Ana Giriş Noktası
Streamlit Multi-Page App
"""
import streamlit as st
import os
import sys

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(__file__))

# Custom sidebar import
from components.sidebar import render_custom_sidebar

st.set_page_config(
    page_title="Anasayfa — BA&QA Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 2rem;
    }
    .platform-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 56px;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        letter-spacing: -1.5px;
        line-height: 1.2;
    }
    .platform-subtitle {
        color: #94a3b8;
        font-size: 18px;
        font-family: 'DM Sans', sans-serif;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 2rem 0;
    }
    .stat-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 12px 12px 0 0;
    }
    .stat-card.blue::before { background: linear-gradient(135deg, #3b82f6, #06b6d4); }
    .stat-card.purple::before { background: linear-gradient(135deg, #8b5cf6, #ec4899); }
    .stat-card.green::before { background: linear-gradient(135deg, #10b981, #06b6d4); }
    .stat-card.orange::before { background: linear-gradient(135deg, #f59e0b, #ef4444); }
    .stat-card:hover {
        border-color: rgba(59,130,246,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .stat-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 36px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 8px;
    }
    .stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .stat-detail {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 8px;
    }

    /* Feature Cards */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 2rem 0;
    }
    .feature-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 32px 24px;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
    }
    .feature-card:hover {
        border-color: rgba(139,92,246,0.4);
        transform: translateY(-6px);
        box-shadow: 0 12px 48px rgba(0,0,0,0.4);
    }
    .feature-icon {
        font-size: 48px;
        margin-bottom: 16px;
        display: block;
    }
    .feature-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 12px;
    }
    .feature-desc {
        font-size: 14px;
        color: #94a3b8;
        line-height: 1.6;
    }

    /* Recent Analyses */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 24px;
        font-weight: 600;
        color: #f1f5f9;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .analysis-row {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.2s;
    }
    .analysis-row:hover {
        border-color: rgba(59,130,246,0.3);
        background: #1e2742;
    }
    .analysis-key {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: #3b82f6;
        font-size: 14px;
    }
    .analysis-info {
        flex: 1;
        font-size: 13px;
        color: #94a3b8;
    }
    .analysis-score {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 18px;
    }

    /* Progress Bar */
    .progress-bar-container {
        background: #0f1624;
        border-radius: 8px;
        height: 6px;
        overflow: hidden;
        margin-top: 6px;
    }
    .progress-bar {
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    .progress-green { background: linear-gradient(90deg, #10b981, #06b6d4); }
    .progress-red { background: linear-gradient(90deg, #ef4444, #dc2626); }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #64748b;
    }
    .empty-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.3;
    }

    /* Footer */
    .footer-cta {
        text-align: center;
        padding: 2rem 0;
        color: #64748b;
        font-size: 14px;
    }

    @media (max-width: 768px) {
        .stats-grid, .features-grid {
            grid-template-columns: 1fr;
        }
        .platform-title {
            font-size: 36px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ── Credentials'ları yükle (secrets.toml'dan okunur) ──
_gemini_key = ""
_jira_email = ""
_jira_token = ""
_anthropic_key = ""

try:
    _gemini_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    _gemini_key = os.environ.get("GEMINI_API_KEY", "")
try:
    _jira_email = st.secrets.get("JIRA_EMAIL", "")
    _jira_token = st.secrets.get("JIRA_API_TOKEN", "")
except Exception:
    _jira_email = os.environ.get("JIRA_EMAIL", "")
    _jira_token = os.environ.get("JIRA_API_TOKEN", "")
try:
    _anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    _anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

# Session state'e yaz
if _gemini_key:
    st.session_state["gemini_key"] = _gemini_key
if _jira_email:
    st.session_state["jira_email"] = _jira_email
if _jira_token:
    st.session_state["jira_token"] = _jira_token
if _anthropic_key:
    st.session_state["anthropic_api_key"] = _anthropic_key

# ── Custom Sidebar ──
render_custom_sidebar(active_page="home")

# ── Hero Section ──
st.markdown("""
<div class="hero-section">
    <div class="platform-title">🧠 BA&QA Intelligence Platform</div>
    <div class="platform-subtitle">
        İş Analizi & QA Kalite Değerlendirme • Design Compliance • JIRA Otomasyon
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick Stats ──
from data.database import get_stats, get_recent_analyses
stats = get_stats()

ba_s = next((s for s in stats["by_type"] if s["analysis_type"] == "ba"), {})
tc_s = next((s for s in stats["by_type"] if s["analysis_type"] == "tc"), {})
design_s = next((s for s in stats["by_type"] if s["analysis_type"] == "design"), {})

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card blue">
        <div class="stat-number">{stats['total']}</div>
        <div class="stat-label">Toplam Analiz</div>
        <div class="stat-detail">Tüm tipler</div>
    </div>
    <div class="stat-card purple">
        <div class="stat-number">{ba_s.get('c', 0)}</div>
        <div class="stat-label">BA Analiz</div>
        <div class="stat-detail">Ort: {ba_s.get('avg_puan', 0) or 0:.0f} | Geçen: {ba_s.get('gecen', 0)}</div>
    </div>
    <div class="stat-card green">
        <div class="stat-number">{tc_s.get('c', 0)}</div>
        <div class="stat-label">TC Analiz</div>
        <div class="stat-detail">Ort: {tc_s.get('avg_puan', 0) or 0:.0f} | Geçen: {tc_s.get('gecen', 0)}</div>
    </div>
    <div class="stat-card orange">
        <div class="stat-number">{design_s.get('c', 0)}</div>
        <div class="stat-label">Design Analiz</div>
        <div class="stat-detail">Uyumluluk kontrolleri</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Feature Cards ──
st.markdown('<div class="section-title">✨ Özellikler</div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">📋</span>
        <div class="feature-title">BA & QA Değerlendirme</div>
        <div class="feature-desc">BA doküman + Test Case kalite analizi<br>JIRA entegrasyonlu 4-agent pipeline</div>
    </div>""", unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🎨</span>
        <div class="feature-title">Design Compliance</div>
        <div class="feature-desc">Figma tasarım ↔ BA uyumluluk kontrolü<br>Gereksinim eşleşme matrisi</div>
    </div>""", unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">📈</span>
        <div class="feature-title">Raporlama & Analitik</div>
        <div class="feature-desc">Trend analizi, sprint bazlı kalite raporu<br>Google Sheets export</div>
    </div>""", unsafe_allow_html=True)

# ── Recent Analyses ──
st.markdown('<div class="section-title">📊 Son Analizler</div>', unsafe_allow_html=True)

recent = get_recent_analyses(limit=10)
if recent:
    for r in recent:
        puan = r.get("genel_puan", 0)
        gecti = r.get("gecti_mi", 0)
        tip = {"ba": "📋 BA", "tc": "🧪 TC", "design": "🎨 Design", "full": "🔄 Full"}.get(r["analysis_type"], "❓")
        status_icon = "✅" if gecti else "❌"
        progress_class = "progress-green" if puan >= 60 else "progress-red"
        score_color = "#10b981" if gecti else "#ef4444"

        st.markdown(f"""
        <div class="analysis-row">
            <div style="flex: 0 0 120px;">
                <span class="analysis-key">{r.get('jira_key', '—')}</span>
            </div>
            <div class="analysis-info">
                {tip} • {r.get('created_at', '')[:16]}
            </div>
            <div style="flex: 0 0 150px;">
                <div class="analysis-score" style="color: {score_color};">{puan:.0f}/100 {status_icon}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar {progress_class}" style="width: {puan}%"></div>
                </div>
            </div>
            <div style="flex: 0 0 80px; text-align: right; font-size: 12px; color: #64748b;">
                {r.get("triggered_by", "manual")}
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📊</div>
        <div>Henüz analiz yapılmadı.</div>
        <div style="margin-top: 8px;">Sol menüden bir modüle giderek başlayabilirsin.</div>
    </div>""", unsafe_allow_html=True)

# ── Footer CTA ──
st.markdown("""
<div class="footer-cta">
    👈 Sol menüden modül seçerek başla
</div>
""", unsafe_allow_html=True)
