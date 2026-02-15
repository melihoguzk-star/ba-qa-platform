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


def get_gemini_keys():
    """
    Returns list of Gemini API keys for rotation.
    Supports both single key (GEMINI_API_KEY) and multiple keys (GEMINI_API_KEYS).
    
    Returns:
        List of Gemini API keys
    """
    keys = []
    
    # Try session state first
    if "gemini_keys" in st.session_state:
        keys = st.session_state.gemini_keys
    elif "gemini_key" in st.session_state and st.session_state.gemini_key:
        keys = [st.session_state.gemini_key]
    
    # Fallback to secrets
    if not keys:
        try:
            # Try multiple keys first (new format)
            if "GEMINI_API_KEYS" in st.secrets:
                keys_raw = st.secrets["GEMINI_API_KEYS"]
                if isinstance(keys_raw, list):
                    keys = keys_raw
                elif isinstance(keys_raw, str):
                    # Support comma-separated string
                    keys = [k.strip() for k in keys_raw.split(",") if k.strip()]
            # Fallback to single key (old format - backward compatible)
            elif "GEMINI_API_KEY" in st.secrets:
                single_key = st.secrets["GEMINI_API_KEY"]
                if single_key:
                    keys = [single_key]
        except:
            pass
    
    # Final fallback: environment variable
    if not keys:
        env_key = os.environ.get("GEMINI_API_KEY", "")
        if env_key:
            keys = [env_key]
    
    return keys


# ─────────────────────────────────────────────
# SHARED UI HELPERS
# ─────────────────────────────────────────────

def emoji_score(p):
    return "🟢" if p >= 8 else "🟡" if p >= 6 else "🔴"


def score_color(p):
    return "#00ff88" if p >= 8 else "#ffd700" if p >= 6 else "#ff4444"


# ─────────────────────────────────────────────
# BRD PIPELINE CONSTANTS
# ─────────────────────────────────────────────

MAX_REVISIONS = 3
BA_PASS_THRESHOLD = 60
TA_PASS_THRESHOLD = 60
TC_PASS_THRESHOLD = 60
CHECKPOINT_TTL_HOURS = 24
CHUNK_OUTPUT_TOKEN_LIMIT = 16000
QA_OUTPUT_TOKEN_LIMIT = 8000

# Default Models
SONNET_MODEL = "claude-sonnet-4-20250514"
GEMINI_MODEL = "gemini-2.5-flash"

# Available Models for Selection
ANTHROPIC_MODELS = {
    "Claude Opus 4.6": "claude-opus-4-6",
    "Claude Sonnet 4.5": "claude-sonnet-4-5-20250929",
    "Claude Sonnet 4": "claude-sonnet-4-20250514",
    "Claude Haiku 4.5": "claude-haiku-4-5-20251001",
}

GEMINI_MODELS = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.0 Flash": "gemini-2.0-flash",
}

# Combined models for flexible selection
ALL_MODELS = {
    "Claude Opus 4.6": "claude-opus-4-6",
    "Claude Sonnet 4.5": "claude-sonnet-4-5-20250929",
    "Claude Sonnet 4": "claude-sonnet-4-20250514",
    "Claude Haiku 4.5": "claude-haiku-4-5-20251001",
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.0 Flash": "gemini-2.0-flash",
}


def is_anthropic_model(model_id: str) -> bool:
    """Check if a model ID belongs to Anthropic."""
    return model_id.startswith("claude-")


def is_gemini_model(model_id: str) -> bool:
    """Check if a model ID belongs to Google Gemini."""
    return model_id.startswith("gemini-")


def load_custom_models():
    """Load custom models from JSON file and merge with ALL_MODELS."""
    import json
    from pathlib import Path

    custom_models_file = Path("data/custom_models.json")

    if custom_models_file.exists():
        try:
            with open(custom_models_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                custom_models = data.get("models", {})

                # Merge with ALL_MODELS
                global ALL_MODELS
                ALL_MODELS = {
                    "Claude Opus 4.6": "claude-opus-4-6",
                    "Claude Sonnet 4.5": "claude-sonnet-4-5-20250929",
                    "Claude Sonnet 4": "claude-sonnet-4-20250514",
                    "Claude Haiku 4.5": "claude-haiku-4-5-20251001",
                    "Gemini 2.5 Flash": "gemini-2.5-flash",
                    "Gemini 2.5 Pro": "gemini-2.5-pro",
                    "Gemini 2.0 Flash": "gemini-2.0-flash",
                }
                ALL_MODELS.update(custom_models)

                return custom_models
        except Exception:
            pass

    return {}


def get_all_models():
    """Get all models (default + custom)."""
    load_custom_models()  # Ensure custom models are loaded
    return ALL_MODELS


def get_model_api_key(model_id: str) -> str:
    """Get API key for a specific model (checks custom models first)."""
    import json
    from pathlib import Path

    custom_models_file = Path("data/custom_models.json")

    if custom_models_file.exists():
        try:
            with open(custom_models_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                api_keys = data.get("api_keys", {})

                if model_id in api_keys:
                    return api_keys[model_id]
        except Exception:
            pass

    # Fallback to default API keys
    if is_anthropic_model(model_id):
        return get_anthropic_key()
    elif is_gemini_model(model_id):
        g, _, _ = get_credentials()
        return g

    return ""


def get_anthropic_key() -> str:
    """Returns Anthropic API key from session state or secrets"""
    key = st.session_state.get("anthropic_api_key", "")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            key = os.environ.get("ANTHROPIC_API_KEY", "")
    return key
