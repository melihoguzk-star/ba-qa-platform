"""
BA&QA Intelligence Platform — 📈 Raporlar & Geçmiş
"""
import streamlit as st
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.sidebar import render_custom_sidebar
from data.database import get_stats, get_recent_analyses
from utils.config import emoji_score

st.set_page_config(page_title="Raporlar — BA&QA", page_icon="📈", layout="wide")

# Custom sidebar
render_custom_sidebar(active_page="reports")

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
        background: linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%);
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

    /* Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }
    .stat-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    .stat-card:hover {
        border-color: rgba(59,130,246,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
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

    /* Analysis Cards */
    .analysis-card {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .analysis-card:hover {
        border-color: rgba(59,130,246,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .analysis-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 4px;
    }
    .analysis-card.passed::before { background: linear-gradient(180deg, #10b981, #06b6d4); }
    .analysis-card.failed::before { background: linear-gradient(180deg, #ef4444, #f59e0b); }

    .analysis-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .analysis-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: #f1f5f9;
    }
    .analysis-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-success {
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.2);
        color: #10b981;
    }
    .badge-error {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.2);
        color: #ef4444;
    }
    .badge-ba { background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); color: #3b82f6; }
    .badge-tc { background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.2); color: #8b5cf6; }
    .badge-design { background: rgba(236,72,153,0.1); border: 1px solid rgba(236,72,153,0.2); color: #ec4899; }

    .analysis-meta {
        display: flex;
        gap: 16px;
        font-size: 12px;
        color: #64748b;
        margin-bottom: 16px;
    }
    .analysis-meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .score-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 16px;
        margin-top: 16px;
        margin-bottom: 16px;
    }
    .score-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        transition: all 0.2s;
    }
    .score-item:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.12);
        transform: translateY(-2px);
    }
    .score-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .score-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 500;
        color: #f1f5f9;
        text-transform: capitalize;
    }
    .score-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 18px;
        font-weight: 700;
        color: #f1f5f9;
    }

    /* Progress Bar */
    .progress-container {
        width: 100%;
        height: 8px;
        background: #1a1d2e;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }
    .progress-bar {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
        position: relative;
        overflow: hidden;
    }
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 2s infinite;
    }
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* Progress colors */
    .progress-excellent { background: linear-gradient(90deg, #10b981, #06b6d4); }
    .progress-good { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
    .progress-fair { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .progress-poor { background: linear-gradient(90deg, #ef4444, #f97316); }

    /* Collapsible Report */
    .report-toggle {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 16px;
        cursor: pointer;
        transition: all 0.2s;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: #94a3b8;
    }
    .report-toggle:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(59,130,246,0.3);
        color: #3b82f6;
    }
    .report-toggle-icon {
        transition: transform 0.3s;
    }
    .report-toggle.active .report-toggle-icon {
        transform: rotate(180deg);
    }

    /* Filter Section */
    .filter-section {
        background: #1a2236;
        border: 1px solid #2a3654;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
    }

    /* Export Button */
    .export-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: white;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 600;
    }
    .export-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59,130,246,0.3);
    }

    /* Scroll to Top */
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

    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
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
    <span class="current">📈 Raporlar</span>
</div>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="page-header">
    <div class="page-title">📈 Raporlar & Analiz Geçmişi</div>
    <div class="page-subtitle">Platform üzerinde yapılan tüm analizlerin detaylı özeti ve istatistikleri</div>
</div>
""", unsafe_allow_html=True)

# ── Scroll to Top Button ──
st.markdown("""
<button id="scrollTopBtn" class="scroll-top-btn" onclick="scrollToTop()">
    ↑
</button>
""", unsafe_allow_html=True)

# ── Get Data ──
stats = get_stats()
ba_s = next((s for s in stats["by_type"] if s["analysis_type"] == "ba"), {})
tc_s = next((s for s in stats["by_type"] if s["analysis_type"] == "tc"), {})
design_s = next((s for s in stats["by_type"] if s["analysis_type"] == "design"), {})

# ── Stats Cards ──
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

st.markdown("<br>", unsafe_allow_html=True)

# ── Filter Section ──
st.markdown("### 🔍 Analiz Geçmişi")

col_f1, col_f2, col_f3 = st.columns([2, 2, 6])
with col_f1:
    filter_type = st.selectbox("Tip Filtre", ["Tümü", "BA", "TC", "Design"], label_visibility="collapsed")
with col_f2:
    limit = st.selectbox("Göster", [10, 25, 50, 100], index=1, label_visibility="collapsed")

type_map = {"Tümü": None, "BA": "ba", "TC": "tc", "Design": "design"}
analyses = get_recent_analyses(limit=limit, analysis_type=type_map[filter_type])

st.markdown("<br>", unsafe_allow_html=True)

# ── Analysis Cards ──
if analyses:
    for r in analyses:
        puan = r.get("genel_puan", 0)
        gecti = r.get("gecti_mi", 0)
        tip_map = {"ba": ("📋 BA", "badge-ba"), "tc": ("🧪 TC", "badge-tc"), "design": ("🎨 Design", "badge-design")}
        tip_icon, tip_badge = tip_map.get(r["analysis_type"], ("❓", "badge-ba"))

        status_class = "passed" if gecti else "failed"
        status_badge = "badge-success" if gecti else "badge-error"
        status_text = "✓ Geçti" if gecti else "✗ Kaldı"

        # Expander label with badges
        expander_label = f"{tip_icon} **{r.get('jira_key', '—')}** • {status_text} • **{puan:.0f}/100** • {r.get('created_at', '')[:16]}"

        # Accordion for each analysis
        with st.expander(expander_label, expanded=False):
            # Meta information
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.markdown(f"**📅 Tarih:** {r.get('created_at', '')[:16]}")
            with col_meta2:
                st.markdown(f"**👤 Tetikleyen:** {r.get('triggered_by', 'manual')}")
            with col_meta3:
                st.markdown(f"**🏷️ Tip:** {r['analysis_type'].upper()}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Scores with Progress Bars
            result = json.loads(r.get("result_json", "{}"))
            if result.get("skorlar"):
                st.markdown("**📊 Skor Detayları:**")
                st.markdown('<div class="score-grid">', unsafe_allow_html=True)
                for s in result["skorlar"]:
                    p = s.get("puan", 0)
                    progress_width = (p / 10) * 100

                    # Color based on score
                    if p >= 8:
                        progress_class = "progress-excellent"
                    elif p >= 6:
                        progress_class = "progress-good"
                    elif p >= 4:
                        progress_class = "progress-fair"
                    else:
                        progress_class = "progress-poor"

                    # Clean label (replace underscores with spaces)
                    label = s['kriter'].replace('_', ' ')

                    st.markdown(f"""
                    <div class="score-item">
                        <div class="score-header">
                            <div class="score-label">{label}</div>
                            <div class="score-value">{emoji_score(p)} {p}/10</div>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar {progress_class}" style="width: {progress_width}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Detailed Report
            if r.get("report_text"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**📄 Detaylı Rapor:**")
                st.markdown(f"""
                <div style="background: #1a1d2e; border-radius: 8px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.8; color: #94a3b8; white-space: pre-wrap;">
{r["report_text"]}
                </div>
                """, unsafe_allow_html=True)

    # ── Export Section ──
    st.markdown("---")
    st.markdown("### 📥 Export")

    import csv, io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "jira_key", "analysis_type", "genel_puan", "gecti_mi", "created_at"])
    writer.writeheader()
    for r in analyses:
        writer.writerow({k: r.get(k, "") for k in ["id", "jira_key", "analysis_type", "genel_puan", "gecti_mi", "created_at"]})

    st.download_button(
        "📥 CSV İndir",
        data=output.getvalue(),
        file_name=f"baqa_analyses_{filter_type.lower()}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("Henüz analiz kaydı yok. Analiz yapmak için ilgili modülleri kullanın.")

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #64748b; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
    BA&QA Intelligence Platform v1.0 — Reports & Analytics — February 2026
</div>
""", unsafe_allow_html=True)
