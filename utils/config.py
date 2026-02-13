"""
BA&QA Intelligence Platform — Configuration & Shared Utilities
"""
import streamlit as st
import os

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

JIRA_BASE_URL = "https://loodos.atlassian.net"
N8N_DOCS_PROXY = "https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy"
N8N_SHEETS_PROXY = "https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy"

BA_CRITERIA = [
    ("completeness", "Tamlık"),
    ("wireframes", "Wireframe / Ekran Tasarımları"),
    ("flow_diagrams", "Akış Diyagramları"),
    ("requirement_quality", "Gereksinim Kalitesi"),
    ("acceptance_criteria", "Kabul Kriterleri"),
    ("consistency", "Tutarlılık"),
    ("business_rules", "İş Kuralları Derinliği"),
    ("error_handling", "Hata Yönetimi"),
    ("documentation_quality", "Dokümantasyon Kalitesi"),
]

TC_CRITERIA = [
    ("coverage", "Kapsam"),
    ("test_structure", "Test Case Yapısı"),
    ("edge_cases", "Sınır Değer & Negatif Senaryolar"),
    ("data_quality", "Test Verisi Kalitesi"),
    ("priority_classification", "Öncelik Sınıflandırması"),
    ("regression_scope", "Regresyon Kapsamı"),
    ("traceability", "İzlenebilirlik"),
    ("readability", "Okunabilirlik & Uygulanabilirlik"),
]

# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────

def get_credentials():
    """Returns (gemini_key, jira_email, jira_token) from session state or secrets"""
    gemini_key = st.session_state.get("gemini_key", "")
    jira_email = st.session_state.get("jira_email", "")
    jira_token = st.session_state.get("jira_token", "")

    # Fallback: secrets
    if not gemini_key:
        try:
            gemini_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if not jira_email:
        try:
            jira_email = st.secrets["JIRA_EMAIL"]
        except Exception:
            jira_email = os.environ.get("JIRA_EMAIL", "")

    if not jira_token:
        try:
            jira_token = st.secrets["JIRA_API_TOKEN"]
        except Exception:
            jira_token = os.environ.get("JIRA_API_TOKEN", "")

    return gemini_key, jira_email, jira_token


def all_creds_available():
    g, e, t = get_credentials()
    return all([g, e, t])


def gemini_available():
    g, _, _ = get_credentials()
    return bool(g)


# ─────────────────────────────────────────────
# SHARED UI HELPERS
# ─────────────────────────────────────────────

def emoji_score(p):
    return "🟢" if p >= 8 else "🟡" if p >= 6 else "🔴"


def score_color(p):
    return "#00ff88" if p >= 8 else "#ffd700" if p >= 6 else "#ff4444"
