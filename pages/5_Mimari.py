"""
BA&QA Intelligence Platform — 🏗️ Mimari
Platform mimari dokümanını gösterir
"""
import streamlit as st
import os

st.set_page_config(page_title="Mimari — BA&QA", page_icon="🏗️", layout="wide")

st.markdown("## 🏗️ Platform Mimarisi")
st.markdown("BA&QA Intelligence Platform katmanlı mimari dokümanı")

# docs_architecture.html dosyasını oku
arch_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs_architecture.html")

if os.path.exists(arch_path):
    with open(arch_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    st.components.v1.html(html_content, height=900, scrolling=True)
else:
    st.error("❌ `docs_architecture.html` dosyası bulunamadı.")
    st.info("Dosyayı proje kök dizinine koy.")
