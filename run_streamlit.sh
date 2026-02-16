#!/bin/bash
# BA-QA Platform Streamlit Launcher
# Uses Python 3.12 for ChromaDB compatibility

echo "🚀 Starting BA-QA Platform..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /Users/melihoguz/ba-qa-platform

# Activate Python 3.12 environment
echo "📦 Activating Python 3.12 environment..."
source venv_py312/bin/activate

# Check ChromaDB availability
echo "🔍 Checking ChromaDB status..."
python -c "import chromadb; print('✅ ChromaDB ready')" 2>/dev/null || echo "⚠️  ChromaDB import issue"

# Start Streamlit
echo ""
echo "🌐 Starting Streamlit on http://localhost:8501"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
streamlit run app.py
