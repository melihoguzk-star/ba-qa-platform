"""Sayfa 9: Ayarlar — API Keys, Model Yönetimi, Platform Ayarları"""
import json
import os
import streamlit as st
from pathlib import Path
from components.sidebar import render_custom_sidebar

st.set_page_config(page_title="Ayarlar", page_icon="⚙️", layout="wide")
render_custom_sidebar(active_page="ayarlar")

st.title("⚙️ Platform Ayarları")

# Custom models dosya yolu
CUSTOM_MODELS_FILE = Path("data/custom_models.json")

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def load_custom_models():
    """Load custom models from JSON file."""
    if CUSTOM_MODELS_FILE.exists():
        try:
            with open(CUSTOM_MODELS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"models": {}, "api_keys": {}}
    return {"models": {}, "api_keys": {}}


def save_custom_models(data):
    """Save custom models to JSON file."""
    CUSTOM_MODELS_FILE.parent.mkdir(exist_ok=True)
    with open(CUSTOM_MODELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_all_models():
    """Get all models (default + custom)."""
    from utils.config import ANTHROPIC_MODELS, GEMINI_MODELS

    all_models = {}
    # Default models
    all_models.update(ANTHROPIC_MODELS)
    all_models.update(GEMINI_MODELS)

    # Custom models
    custom = load_custom_models()
    all_models.update(custom.get("models", {}))

    return all_models


def get_provider_from_model_id(model_id):
    """Determine provider from model ID."""
    if model_id.startswith("claude-"):
        return "Anthropic"
    elif model_id.startswith("gemini-"):
        return "Google Gemini"
    elif model_id.startswith("gpt-"):
        return "OpenAI"
    else:
        return "Other"


# ═══════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "🤖 Model Yönetimi", "ℹ️ Bilgi"])

# ─────────────────────────────────────────────────────────
# TAB 1: API KEYS
# ─────────────────────────────────────────────────────────

with tab1:
    st.markdown("### 🔑 API Key Yönetimi")
    st.markdown("Platform API anahtarlarınızı buradan yönetebilirsiniz.")

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

        st.markdown("#### Özel Model API Keys")
        st.info("Eklediğiniz özel modeller için API anahtarları 'Model Yönetimi' sekmesinden eklenir.")

        submitted = st.form_submit_button("💾 Kaydet", type="primary", use_container_width=True)

        if submitted:
            st.session_state.anthropic_api_key = anthropic_key
            st.session_state.gemini_key = gemini_key
            st.session_state.jira_email = jira_email
            st.session_state.jira_token = jira_token
            st.success("✅ API anahtarları kaydedildi!")
            st.rerun()

# ─────────────────────────────────────────────────────────
# TAB 2: MODEL MANAGEMENT
# ─────────────────────────────────────────────────────────

with tab2:
    st.markdown("### 🤖 Model Yönetimi")

    # Mevcut modelleri göster
    st.markdown("#### 📋 Mevcut Modeller")

    all_models = get_all_models()
    custom_data = load_custom_models()
    custom_models = custom_data.get("models", {})

    # Tablo oluştur
    if all_models:
        model_list = []
        for name, model_id in all_models.items():
            provider = get_provider_from_model_id(model_id)
            is_custom = name in custom_models
            model_list.append({
                "Model Adı": name,
                "Model ID": model_id,
                "Provider": provider,
                "Tip": "🔧 Özel" if is_custom else "📦 Varsayılan"
            })

        st.dataframe(model_list, use_container_width=True, hide_index=True)
        st.caption(f"Toplam {len(all_models)} model ({len(custom_models)} özel)")
    else:
        st.info("Henüz model eklenmemiş.")

    st.divider()

    # Yeni model ekleme formu
    st.markdown("#### ➕ Yeni Model Ekle")

    with st.form("add_model_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_model_name = st.text_input(
                "Model Adı *",
                placeholder="örn: GPT-4 Turbo",
                help="Kullanıcı dostu model adı (unique olmalı)"
            )

            new_model_id = st.text_input(
                "Model ID *",
                placeholder="örn: gpt-4-turbo-preview",
                help="API'de kullanılacak model ID"
            )

        with col2:
            provider = st.selectbox(
                "Provider",
                options=["Anthropic", "Google Gemini", "OpenAI", "Other"],
                help="Model sağlayıcısı"
            )

            new_api_key = st.text_input(
                "API Key (Opsiyonel)",
                type="password",
                help="Bu model için özel API anahtarı (yoksa varsayılan kullanılır)"
            )

        add_submitted = st.form_submit_button("➕ Model Ekle", type="primary", use_container_width=True)

        if add_submitted:
            # Validasyon
            errors = []

            if not new_model_name or not new_model_id:
                errors.append("Model adı ve Model ID zorunludur.")

            # Unique kontrolü - model adı
            if new_model_name in all_models:
                errors.append(f"❌ '{new_model_name}' adında bir model zaten mevcut.")

            # Unique kontrolü - model ID
            if new_model_id in all_models.values():
                existing_name = [k for k, v in all_models.items() if v == new_model_id][0]
                errors.append(f"❌ '{new_model_id}' ID'si zaten '{existing_name}' modeli tarafından kullanılıyor.")

            # API key unique kontrolü (eğer girilmişse)
            if new_api_key:
                existing_keys = custom_data.get("api_keys", {}).values()
                if new_api_key in existing_keys:
                    errors.append(f"❌ Bu API anahtarı zaten başka bir model tarafından kullanılıyor.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Model ekle
                custom_data["models"][new_model_name] = new_model_id

                # API key ekle (eğer girilmişse)
                if new_api_key:
                    if "api_keys" not in custom_data:
                        custom_data["api_keys"] = {}
                    custom_data["api_keys"][new_model_id] = new_api_key

                # Kaydet
                save_custom_models(custom_data)
                st.success(f"✅ '{new_model_name}' modeli başarıyla eklendi!")
                st.rerun()

    st.divider()

    # Özel modelleri silme
    if custom_models:
        st.markdown("#### 🗑️ Özel Model Sil")

        col1, col2 = st.columns([3, 1])
        with col1:
            model_to_delete = st.selectbox(
                "Silinecek Model",
                options=list(custom_models.keys()),
                help="Sadece özel modeller silinebilir"
            )
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("🗑️ Sil", type="secondary", use_container_width=True):
                if model_to_delete:
                    model_id = custom_data["models"][model_to_delete]

                    # Modeli sil
                    del custom_data["models"][model_to_delete]

                    # İlişkili API key'i sil
                    if model_id in custom_data.get("api_keys", {}):
                        del custom_data["api_keys"][model_id]

                    # Kaydet
                    save_custom_models(custom_data)
                    st.success(f"✅ '{model_to_delete}' modeli silindi!")
                    st.rerun()

# ─────────────────────────────────────────────────────────
# TAB 3: INFO
# ─────────────────────────────────────────────────────────

with tab3:
    st.markdown("### ℹ️ Ayarlar Hakkında")

    st.markdown("""
    #### 🔑 API Keys
    - Platform genelinde kullanılacak API anahtarlarını buradan yönetebilirsiniz
    - Anahtarlar session state'de saklanır (tarayıcı oturumu boyunca geçerli)
    - Güvenlik için secrets.toml veya environment variables kullanmanız önerilir

    #### 🤖 Model Yönetimi

    **Varsayılan Modeller:**
    - Platform ile gelen hazır modeller (silinmez)
    - `config.py` dosyasında tanımlıdır

    **Özel Modeller:**
    - Kullanıcı tarafından eklenen modeller
    - `data/custom_models.json` dosyasında saklanır
    - Silinebilir ve düzenlenebilir
    - API anahtarları ile birlikte saklanabilir

    **Unique Kontroller:**
    - ✅ Model adı benzersiz olmalı
    - ✅ Model ID benzersiz olmalı
    - ✅ API anahtarı benzersiz olmalı (önerilir)

    #### 📁 Veri Saklama
    ```
    data/
    ├── custom_models.json    # Özel modeller ve API keys
    └── pipeline.db           # Pipeline sonuçları
    ```

    #### 🔄 Session State
    API anahtarları session state'de saklanır:
    - `anthropic_api_key`
    - `gemini_key`
    - `jira_email`
    - `jira_token`
    """)

    st.divider()

    # Debug bilgileri (opsiyonel)
    with st.expander("🔍 Debug Bilgileri"):
        st.markdown("**Session State API Keys:**")
        st.json({
            "anthropic_api_key": "***" if st.session_state.get("anthropic_api_key") else "Yok",
            "gemini_key": "***" if st.session_state.get("gemini_key") else "Yok",
            "jira_email": st.session_state.get("jira_email", "Yok"),
            "jira_token": "***" if st.session_state.get("jira_token") else "Yok",
        })

        st.markdown("**Custom Models File:**")
        if CUSTOM_MODELS_FILE.exists():
            st.code(f"✅ {CUSTOM_MODELS_FILE}")
            custom_data = load_custom_models()
            st.json({
                "models_count": len(custom_data.get("models", {})),
                "api_keys_count": len(custom_data.get("api_keys", {}))
            })
        else:
            st.code(f"❌ {CUSTOM_MODELS_FILE} (henüz oluşturulmadı)")
