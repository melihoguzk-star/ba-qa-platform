"""
Custom Sidebar Navigation Component
Modern UI tasarımı ile sol menü
"""
import streamlit as st

def render_custom_sidebar(active_page="home"):
    """
    Özel tasarlanmış sidebar menüsü

    Args:
        active_page: Aktif sayfa ('home', 'ba', 'tc', 'design', 'reports', 'architecture')
    """

    # Sidebar CSS
    st.markdown("""
    <style>
        /* Streamlit varsayılan menüyü gizle */
        section[data-testid="stSidebarNav"] {
            display: none;
        }

        /* Custom Navigation */
        .nav-container {
            padding: 0;
            margin: 0;
        }

        .nav-header {
            padding: 24px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 16px;
        }

        .nav-logo {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }

        .nav-subtitle {
            font-size: 11px;
            color: #64748b;
            font-family: 'JetBrains Mono', monospace;
        }

        .nav-item {
            display: flex !important;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            margin: 4px 8px;
            border-radius: 8px;
            color: #94a3b8 !important;
            text-decoration: none !important;
            transition: all 0.2s;
            cursor: pointer;
            border: 1px solid transparent;
            font-size: 14px;
        }

        a.nav-item {
            display: flex !important;
        }

        .nav-item:hover {
            background: rgba(59,130,246,0.05);
            border-color: rgba(59,130,246,0.2);
            color: #3b82f6;
        }

        .nav-item.active {
            background: rgba(59,130,246,0.1);
            border-color: rgba(59,130,246,0.3);
            color: #3b82f6;
            font-weight: 600;
        }

        .nav-icon {
            font-size: 18px;
            width: 24px;
            text-align: center;
        }

        .nav-label {
            flex: 1;
        }

        .nav-section {
            margin-top: 24px;
            padding: 0 16px;
        }

        .nav-section-title {
            font-size: 11px;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-family: 'JetBrains Mono', monospace;
        }

        .nav-footer {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
            background: rgba(10,14,23,0.8);
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 10px;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 4px;
        }

        .status-success {
            background: rgba(16,185,129,0.1);
            border: 1px solid rgba(16,185,129,0.2);
            color: #10b981;
        }

        .status-error {
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.2);
            color: #ef4444;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: currentColor;
        }
    </style>
    """, unsafe_allow_html=True)

    # Navigation menu
    # Streamlit URL formatı: Türkçe karakterler URL encode edilir
    pages = [
        {
            "key": "home",
            "icon": "🏠",
            "label": "Ana Sayfa",
            "url": "/",
            "section": "main"
        },
        {
            "key": "ba",
            "icon": "📋",
            "label": "BA Değerlendirme",
            "url": "/BA_De%C4%9Ferlendirme",  # ğ -> %C4%9F
            "section": "main"
        },
        {
            "key": "tc",
            "icon": "🧪",
            "label": "TC Değerlendirme",
            "url": "/TC_De%C4%9Ferlendirme",  # ğ -> %C4%9F
            "section": "main"
        },
        {
            "key": "design",
            "icon": "🎨",
            "label": "Design Compliance",
            "url": "/Design_Compliance",
            "section": "main"
        },
        {
            "key": "reports",
            "icon": "📈",
            "label": "Raporlar",
            "url": "/Raporlar",
            "section": "tools"
        },
        {
            "key": "architecture",
            "icon": "🏗️",
            "label": "Mimari",
            "url": "/Mimari",
            "section": "tools"
        },
        {
            "key": "document_library",
            "icon": "📚",
            "label": "Document Library",
            "url": "/Document_Library",
            "section": "tools"
        },
        {
            "key": "import_merge",
            "icon": "📥",
            "label": "Import & Merge",
            "url": "/Import_Merge",
            "section": "tools"
        },
        {
            "key": "smart_matching",
            "icon": "🔍",
            "label": "Smart Matching",
            "url": "/Smart_Matching",
            "section": "tools"
        },
        {
            "key": "brd_pipeline",
            "icon": "🚀",
            "label": "BRD Pipeline",
            "url": "/BRD_Pipeline",
            "section": "pipeline"
        },
        {
            "key": "pipeline_sonuc",
            "icon": "📊",
            "label": "Pipeline Sonuç",
            "url": "/Pipeline_Sonuc",
            "section": "pipeline"
        },
        {
            "key": "pipeline_gecmis",
            "icon": "📜",
            "label": "Pipeline Geçmiş",
            "url": "/Pipeline_Gecmis",
            "section": "pipeline"
        },
        {
            "key": "ayarlar",
            "icon": "⚙️",
            "label": "Settings",
            "url": "/Settings",
            "section": "settings"
        }
    ]

    with st.sidebar:
        # Header
        st.markdown("""
        <div class="nav-header">
            <div class="nav-logo">🧠 BA&QA Platform</div>
            <div class="nav-subtitle">Intelligence Platform v2.0</div>
        </div>
        """, unsafe_allow_html=True)

        # Main navigation
        st.markdown('<div class="nav-section-title">Ana Modüller</div>', unsafe_allow_html=True)

        for page in pages:
            if page["section"] == "main":
                # Streamlit button ile sayfa değiştirme
                if page["key"] == "home":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("app.py")
                elif page["key"] == "ba":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/1_BA_Degerlendirme.py")
                elif page["key"] == "tc":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/2_TC_Degerlendirme.py")
                elif page["key"] == "design":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/3_Design_Compliance.py")

        # Tools section
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-section-title">Araçlar</div>', unsafe_allow_html=True)

        for page in pages:
            if page["section"] == "tools":
                if page["key"] == "reports":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/4_Raporlar.py")
                elif page["key"] == "architecture":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/5_Mimari.py")
                elif page["key"] == "document_library":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/10_Document_Library.py")
                elif page["key"] == "import_merge":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/11_Import_Merge.py")
                elif page["key"] == "smart_matching":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/12_Smart_Matching.py")

        st.markdown('</div>', unsafe_allow_html=True)

        # Pipeline section
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-section-title">BRD Pipeline</div>', unsafe_allow_html=True)

        for page in pages:
            if page["section"] == "pipeline":
                if page["key"] == "brd_pipeline":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/6_BRD_Pipeline.py")
                elif page["key"] == "pipeline_sonuc":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/7_Pipeline_Sonuc.py")
                elif page["key"] == "pipeline_gecmis":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/8_Pipeline_Gecmis.py")

        st.markdown('</div>', unsafe_allow_html=True)

        # Settings section
        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-section-title">Sistem</div>', unsafe_allow_html=True)

        for page in pages:
            if page["section"] == "settings":
                if page["key"] == "ayarlar":
                    if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                        st.switch_page("pages/9_Settings.py")

        st.markdown('</div>', unsafe_allow_html=True)

        # Connection status
        st.markdown("---")
        st.markdown("#### 🔌 Bağlantı Durumu")

        # Check credentials
        import os
        gemini_key = st.session_state.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
        anthropic_key = st.session_state.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY", "")
        jira_email = st.session_state.get("jira_email") or os.environ.get("JIRA_EMAIL", "")
        jira_token = st.session_state.get("jira_token") or os.environ.get("JIRA_API_TOKEN", "")

        if gemini_key:
            st.markdown("""
            <div class="status-badge status-success">
                <span class="status-dot"></span>
                Gemini API
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-error">
                <span class="status-dot"></span>
                Gemini API
            </div>
            """, unsafe_allow_html=True)

        if anthropic_key:
            st.markdown("""
            <div class="status-badge status-success">
                <span class="status-dot"></span>
                Anthropic API
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-error">
                <span class="status-dot"></span>
                Anthropic API
            </div>
            """, unsafe_allow_html=True)

        if jira_email and jira_token:
            st.markdown("""
            <div class="status-badge status-success">
                <span class="status-dot"></span>
                JIRA
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-error">
                <span class="status-dot"></span>
                JIRA
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.caption("BA&QA Platform v2.0")
        st.caption("© 2026 Loodos")
