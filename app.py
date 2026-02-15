"""
BA&QA Intelligence Platform — Ana Giriş Noktası
Streamlit Multi-Page App
"""
import streamlit as st
import os
import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    /* Stat Cards */
    .stat-card {
        width: 100%;
        margin-bottom: 0;
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

    /* Quick Actions */
    .stButton > button {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        border-radius: 10px;
        border: 1px solid #2a3654;
        transition: all 0.3s;
        background: linear-gradient(135deg, #1a2236 0%, #1e2742 100%);
    }
    .stButton > button:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59,130,246,0.2);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-color: #3b82f6;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 8px 24px rgba(59,130,246,0.4);
    }

    /* Time Range Selector */
    .stSelectbox {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
    }

    /* Alert Styling */
    .element-container .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
        font-family: 'DM Sans', sans-serif;
    }
    .element-container .stAlert[data-baseweb="notification"] {
        background: #1a2236;
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

# ── Time Range Selector ──
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="section-title">📊 Dashboard Genel Bakış</div>', unsafe_allow_html=True)
with col2:
    time_range_display = st.selectbox(
        "Zaman Aralığı",
        ["Son 7 Gün", "Son 30 Gün", "Son 90 Gün", "Tüm Zamanlar"],
        index=1,  # Default: Son 30 Gün
        key="time_range_selector",
        label_visibility="collapsed"
    )

# Map display to internal values
time_range_map = {
    "Son 7 Gün": "7days",
    "Son 30 Gün": "30days",
    "Son 90 Gün": "90days",
    "Tüm Zamanlar": "all"
}
time_range = time_range_map[time_range_display]

# ── Quick Stats ──
from data.database import (
    get_stats, get_recent_analyses, get_dashboard_alerts,
    get_quality_trend_data, get_score_distribution, get_sparkline_data
)
stats = get_stats(time_range)

ba_s = next((s for s in stats["by_type"] if s["analysis_type"] == "ba"), {})
tc_s = next((s for s in stats["by_type"] if s["analysis_type"] == "tc"), {})
design_s = next((s for s in stats["by_type"] if s["analysis_type"] == "design"), {})

# Calculate pass rates
ba_pass_rate = (ba_s.get('gecen', 0) / max(ba_s.get('c', 1), 1) * 100) if ba_s.get('c', 0) > 0 else 0
tc_pass_rate = (tc_s.get('gecen', 0) / max(tc_s.get('c', 1), 1) * 100) if tc_s.get('c', 0) > 0 else 0

# Create stat cards in columns for better control
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card blue">
        <div class="stat-number">{stats['total']}</div>
        <div class="stat-label">Toplam Analiz</div>
        <div class="stat-detail">{time_range_display}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card purple">
        <div class="stat-number">{ba_s.get('c', 0)}</div>
        <div class="stat-label">BA Değerlendirme</div>
        <div class="stat-detail">
            Ort: {ba_s.get('avg_puan', 0) or 0:.0f}/100 |
            Geçme: %{ba_pass_rate:.0f} ({ba_s.get('gecen', 0)}/{ba_s.get('c', 0)})
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card green">
        <div class="stat-number">{tc_s.get('c', 0)}</div>
        <div class="stat-label">TC Değerlendirme</div>
        <div class="stat-detail">
            Ort: {tc_s.get('avg_puan', 0) or 0:.0f}/100 |
            Geçme: %{tc_pass_rate:.0f} ({tc_s.get('gecen', 0)}/{tc_s.get('c', 0)})
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card orange">
        <div class="stat-number">{design_s.get('c', 0)}</div>
        <div class="stat-label">Design Compliance</div>
        <div class="stat-detail">
            Ort: {design_s.get('avg_puan', 0) or 0:.0f}/100
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Alerts Section ──
alerts = get_dashboard_alerts()
if alerts:
    st.markdown('<div class="section-title">🚨 Uyarılar ve Öneriler</div>', unsafe_allow_html=True)

    error_alerts = [a for a in alerts if a["level"] == "error"]
    warning_alerts = [a for a in alerts if a["level"] == "warning"]
    info_alerts = [a for a in alerts if a["level"] == "info"]

    for alert in error_alerts:
        st.error(f"**{alert['message']}**\n\n💡 Öneri: {alert['action']}")

    for alert in warning_alerts:
        st.warning(f"**{alert['message']}**\n\n💡 Öneri: {alert['action']}")

    # Info alerts in expandable section
    if info_alerts:
        with st.expander(f"ℹ️ Bilgilendirme ({len(info_alerts)})", expanded=False):
            for alert in info_alerts:
                st.info(f"**{alert['message']}**\n\n💡 Öneri: {alert['action']}")

# ── Quick Actions Panel ──
st.markdown('<div class="section-title">⚡ Hızlı İşlemler</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 BA Değerlendir", use_container_width=True, type="primary", help="İş Analizi dokümanı değerlendirmesi yap"):
        st.switch_page("pages/1_BA_Degerlendirme.py")

with col2:
    if st.button("🧪 TC Değerlendir", use_container_width=True, help="Test Case kalite değerlendirmesi yap"):
        st.switch_page("pages/2_TC_Degerlendirme.py")

with col3:
    if st.button("🎨 Design Check", use_container_width=True, help="Figma tasarım uyumluluk kontrolü"):
        st.switch_page("pages/3_Design_Compliance.py")

with col4:
    if st.button("📋 BRD Pipeline", use_container_width=True, help="BRD'den BA/TA/TC üret"):
        st.switch_page("pages/6_BRD_Pipeline.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Quality Trend Chart ──
st.markdown(f'<div class="section-title">📈 Kalite Trend Analizi ({time_range_display})</div>', unsafe_allow_html=True)

trend_data = get_quality_trend_data(time_range)

if trend_data["dates"]:
    # Create trend chart
    fig = go.Figure()

    # BA Trend
    fig.add_trace(go.Scatter(
        x=trend_data['dates'],
        y=trend_data['ba_scores'],
        name='BA Quality',
        line=dict(color='#8b5cf6', width=3),
        mode='lines+markers',
        marker=dict(size=8),
        hovertemplate='<b>BA</b><br>Date: %{x}<br>Score: %{y:.1f}<extra></extra>'
    ))

    # TC Trend
    fig.add_trace(go.Scatter(
        x=trend_data['dates'],
        y=trend_data['tc_scores'],
        name='TC Quality',
        line=dict(color='#10b981', width=3),
        mode='lines+markers',
        marker=dict(size=8),
        hovertemplate='<b>TC</b><br>Date: %{x}<br>Score: %{y:.1f}<extra></extra>'
    ))

    # Design Trend
    fig.add_trace(go.Scatter(
        x=trend_data['dates'],
        y=trend_data['design_scores'],
        name='Design Quality',
        line=dict(color='#f59e0b', width=3),
        mode='lines+markers',
        marker=dict(size=8),
        hovertemplate='<b>Design</b><br>Date: %{x}<br>Score: %{y:.1f}<extra></extra>'
    ))

    # Threshold line
    fig.add_hline(
        y=60,
        line_dash="dash",
        line_color="rgba(239, 68, 68, 0.5)",
        annotation_text="Pass Threshold (60)",
        annotation_position="right",
        annotation_font_color="#ef4444"
    )

    # Target line
    fig.add_hline(
        y=80,
        line_dash="dot",
        line_color="rgba(16, 185, 129, 0.3)",
        annotation_text="Target (80)",
        annotation_position="right",
        annotation_font_color="#10b981"
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Quality Score",
        hovermode='x unified',
        plot_bgcolor='#0a0e17',
        paper_bgcolor='#1a2236',
        font=dict(color='#f1f5f9', family='DM Sans'),
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(26, 34, 54, 0.8)',
            bordercolor='#2a3654',
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        yaxis=dict(
            gridcolor='#1e2742',
            range=[0, 105]
        ),
        xaxis=dict(
            gridcolor='#1e2742'
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Seçilen zaman aralığında trend verisi bulunamadı.")

# ── Score Distribution Chart ──
st.markdown('<div class="section-title">📊 Puan Dağılımı</div>', unsafe_allow_html=True)

score_dist = get_score_distribution(time_range)

if any([score_dist["ba_scores"], score_dist["tc_scores"], score_dist["design_scores"]]):
    # Create subplots for distributions
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('BA Scores', 'TC Scores', 'Design Scores'),
        horizontal_spacing=0.12
    )

    # BA Distribution
    if score_dist["ba_scores"]:
        fig.add_trace(
            go.Histogram(
                x=score_dist['ba_scores'],
                name='BA',
                marker_color='#8b5cf6',
                opacity=0.7,
                nbinsx=10,
                hovertemplate='Score: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=1
        )

    # TC Distribution
    if score_dist["tc_scores"]:
        fig.add_trace(
            go.Histogram(
                x=score_dist['tc_scores'],
                name='TC',
                marker_color='#10b981',
                opacity=0.7,
                nbinsx=10,
                hovertemplate='Score: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=2
        )

    # Design Distribution
    if score_dist["design_scores"]:
        fig.add_trace(
            go.Histogram(
                x=score_dist['design_scores'],
                name='Design',
                marker_color='#f59e0b',
                opacity=0.7,
                nbinsx=10,
                hovertemplate='Score: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=3
        )

    # Add threshold line to each subplot
    for col in [1, 2, 3]:
        fig.add_vline(
            x=60,
            line_dash="dash",
            line_color="rgba(239, 68, 68, 0.5)",
            row=1, col=col
        )

    fig.update_layout(
        plot_bgcolor='#0a0e17',
        paper_bgcolor='#1a2236',
        font=dict(color='#f1f5f9', family='DM Sans'),
        height=300,
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig.update_xaxes(title_text="Score", gridcolor='#1e2742', range=[0, 105])
    fig.update_yaxes(title_text="Count", gridcolor='#1e2742')

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Seçilen zaman aralığında dağılım verisi bulunamadı.")

st.markdown("<br>", unsafe_allow_html=True)

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
st.markdown(f'<div class="section-title">📊 Son Analizler ({time_range_display})</div>', unsafe_allow_html=True)

recent = get_recent_analyses(limit=10, time_range=time_range)
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
