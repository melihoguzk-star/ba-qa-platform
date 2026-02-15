"""Sayfa 9: Ayarlar — API Key Yönetimi"""
import streamlit as st
from components.sidebar import render_custom_sidebar

st.set_page_config(page_title="Ayarlar", page_icon="⚙️", layout="wide")
render_custom_sidebar(active_page="ayarlar")

st.title("⚙️ Platform Ayarları")
st.markdown("Platform API anahtarlarınızı buradan yönetebilirsiniz.")
st.divider()

# ═══════════════════════════════════════════════════════════
# API KEYS MANAGEMENT
# ═══════════════════════════════════════════════════════════

st.markdown("### 🔑 API Key Yönetimi")

with st.form("api_keys_form"):
    st.markdown("#### Anthropic API")
    anthropic_key = st.text_input(
        "Anthropic API Key",
        value=st.session_state.get("anthropic_api_key", ""),
        type="password",
        help="Claude modelleri için gerekli"
    )

    st.markdown("#### Google Gemini API")
    gemini_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.get("gemini_key", ""),
        type="password",
        help="Gemini modelleri için gerekli"
    )

    st.markdown("#### Jira API")
    col1, col2 = st.columns(2)
    with col1:
        jira_email = st.text_input(
            "Jira Email",
            value=st.session_state.get("jira_email", ""),
            help="Jira hesap email adresi"
        )
    with col2:
        jira_token = st.text_input(
            "Jira API Token",
            value=st.session_state.get("jira_token", ""),
            type="password",
            help="Jira API token"
        )

    st.divider()

    submitted = st.form_submit_button("💾 Kaydet", type="primary", use_container_width=True)

    if submitted:
        st.session_state.anthropic_api_key = anthropic_key
        st.session_state.gemini_key = gemini_key
        st.session_state.jira_email = jira_email
        st.session_state.jira_token = jira_token
        st.success("✅ API anahtarları kaydedildi!")
        st.rerun()

# ═══════════════════════════════════════════════════════════
# INFO
# ═══════════════════════════════════════════════════════════

st.divider()
st.markdown("### ℹ️ Bilgi")

st.info("""
**Session State:**
- API anahtarları session state'de saklanır (tarayıcı oturumu boyunca geçerli)
- Güvenli saklama için `.streamlit/secrets.toml` veya environment variables kullanabilirsiniz

**API Anahtarları:**
- `anthropic_api_key` - Claude modelleri için
- `gemini_key` - Gemini modelleri için
- `jira_email` & `jira_token` - Jira entegrasyonu için
""")

# Debug bilgileri
with st.expander("🔍 Debug Bilgileri"):
    st.markdown("**Session State API Keys:**")
    st.json({
        "anthropic_api_key": "✅ Ayarlı" if st.session_state.get("anthropic_api_key") else "❌ Yok",
        "gemini_key": "✅ Ayarlı" if st.session_state.get("gemini_key") else "❌ Yok",
        "jira_email": st.session_state.get("jira_email", "❌ Yok"),
        "jira_token": "✅ Ayarlı" if st.session_state.get("jira_token") else "❌ Yok",
    })
