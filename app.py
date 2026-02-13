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

# ── Ortak CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;700&display=swap');
    .stApp {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(160deg, #0f1117 0%, #1a1d2e 40%, #0f1117 100%);
    }

    .platform-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .platform-subtitle {
        color: #94a3b8; font-size: 1rem; margin-bottom: 2rem;
    }
    .hero-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid #2a2a4a; border-radius: 16px;
        padding: 24px; text-align: center;
        transition: all 0.3s ease;
    }
    .hero-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
    .hero-icon { font-size: 2.5rem; margin-bottom: 8px; }
    .hero-label { font-weight: 600; font-size: 1.1rem; color: #e0e0e0; }
    .hero-desc { font-size: 0.85rem; color: #888; margin-top: 6px; }
    .stat-box {
        background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2);
        border-radius: 12px; padding: 16px; text-align: center;
    }
    .stat-num { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: #3b82f6; }
    .stat-label { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

    /* Score bars */
    .score-bar-bg { background: #1a1a2e; border-radius: 6px; height: 8px; overflow: hidden; margin: 4px 0; }
    .score-bar-fill { height: 100%; border-radius: 6px; transition: width 0.5s; }
    .score-green { background: linear-gradient(90deg, #00ff88, #00cc6a); }
    .score-yellow { background: linear-gradient(90deg, #ffd700, #ffaa00); }
    .score-red { background: linear-gradient(90deg, #ff4444, #cc0000); }
</style>
""", unsafe_allow_html=True)

# ── Credentials'ları yükle (secrets.toml'dan okunur) ──
_gemini_key = ""
_jira_email = ""
_jira_token = ""
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

# Session state'e yaz
if _gemini_key:
    st.session_state["gemini_key"] = _gemini_key
if _jira_email:
    st.session_state["jira_email"] = _jira_email
if _jira_token:
    st.session_state["jira_token"] = _jira_token

# ── Custom Sidebar ──
render_custom_sidebar(active_page="home")


# ── Ana Sayfa ──
st.markdown('<div class="platform-title">🧠 BA&QA Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="platform-subtitle">İş Analizi & QA Kalite Değerlendirme • Design Compliance • JIRA Otomasyon</div>', unsafe_allow_html=True)

# Quick stats
from data.database import get_stats, get_recent_analyses
stats = get_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="stat-box">
        <div class="stat-num">{stats['total']}</div>
        <div class="stat-label">Toplam Analiz</div>
    </div>""", unsafe_allow_html=True)

ba_stats = next((s for s in stats["by_type"] if s["analysis_type"] == "ba"), {})
tc_stats = next((s for s in stats["by_type"] if s["analysis_type"] == "tc"), {})
design_stats = next((s for s in stats["by_type"] if s["analysis_type"] == "design"), {})

with col2:
    avg = ba_stats.get("avg_puan", 0) or 0
    st.markdown(f"""<div class="stat-box">
        <div class="stat-num">{avg:.0f}</div>
        <div class="stat-label">BA Ort. Puan</div>
    </div>""", unsafe_allow_html=True)
with col3:
    avg = tc_stats.get("avg_puan", 0) or 0
    st.markdown(f"""<div class="stat-box">
        <div class="stat-num">{avg:.0f}</div>
        <div class="stat-label">TC Ort. Puan</div>
    </div>""", unsafe_allow_html=True)
with col4:
    avg = design_stats.get("avg_puan", 0) or 0
    st.markdown(f"""<div class="stat-box">
        <div class="stat-num">{avg:.0f}</div>
        <div class="stat-label">Design Ort. Puan</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# Feature Cards
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("""<div class="hero-card">
        <div class="hero-icon">📋</div>
        <div class="hero-label">QA Değerlendirme</div>
        <div class="hero-desc">BA doküman + Test Case kalite analizi<br>JIRA entegrasyonlu 4-agent pipeline</div>
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown("""<div class="hero-card">
        <div class="hero-icon">🎨</div>
        <div class="hero-label">Design Compliance</div>
        <div class="hero-desc">Figma tasarım ↔ BA uyumluluk kontrolü<br>Gereksinim eşleşme matrisi</div>
    </div>""", unsafe_allow_html=True)
with col_c:
    st.markdown("""<div class="hero-card">
        <div class="hero-icon">📈</div>
        <div class="hero-label">Raporlama</div>
        <div class="hero-desc">Trend analizi, sprint bazlı kalite raporu<br>Google Sheets export</div>
    </div>""", unsafe_allow_html=True)

# Son analizler
st.markdown("---")
st.markdown("### 📊 Son Analizler")
recent = get_recent_analyses(limit=10)
if recent:
    for r in recent:
        puan = r.get("genel_puan", 0)
        gecti = r.get("gecti_mi", 0)
        tip = {"ba": "📋 BA", "tc": "🧪 TC", "design": "🎨 Design", "full": "🔄 Full"}.get(r["analysis_type"], "❓")
        color = "#00ff88" if gecti else "#ff4444"
        status_icon = "✅" if gecti else "❌"

        c1, c2, c3, c4 = st.columns([1, 3, 1, 1])
        with c1:
            st.markdown(f"**{r.get('jira_key', '—')}**")
        with c2:
            st.caption(f"{tip} • {r.get('created_at', '')[:16]}")
        with c3:
            bar_cls = "score-green" if puan >= 60 else "score-red"
            st.markdown(f"""<div style="font-weight:700; color:{color};">{puan:.0f}/100 {status_icon}</div>
            <div class="score-bar-bg"><div class="score-bar-fill {bar_cls}" style="width:{puan}%"></div></div>
            """, unsafe_allow_html=True)
        with c4:
            st.caption(r.get("triggered_by", "manual"))
else:
    st.info("Henüz analiz yapılmadı. Soldaki menüden bir modüle giderek başlayabilirsin.")

st.markdown("---")
st.markdown("##### 👈 Sol menüden modül seçerek başla")
