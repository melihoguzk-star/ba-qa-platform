"""
Smart Matching Page

AI-powered task-to-document matching to help users find relevant existing documents.
"""

import streamlit as st
from pipeline.smart_matcher import SmartMatcher
from pipeline.match_explainer import MatchExplainer
from data.database import record_task_match, get_task_match_analytics
from components.sidebar import render_custom_sidebar
import time


def main():
    st.set_page_config(page_title="Smart Matching", page_icon="🔍", layout="wide")

    # Render custom sidebar
    render_custom_sidebar(active_page="smart_matching")

    st.title("🔍 Akıllı Doküman Eşleştirme")
    st.markdown("""
    **AI destekli görev-doküman eşleştirme** - Görevinizi tanımlayın ve ilgili mevcut dokümanları bulun.
    Tekrar eden iş yapmaktan kaçınarak zamandan tasarruf edin ve mevcut dokümanları yeniden kullanın.
    """)

    # Analytics Section (moved from sidebar)
    st.markdown("---")

    # Time range filter (compact, inline)
    col_filter, col_spacer = st.columns([1, 3])
    with col_filter:
        time_range = st.selectbox(
            "📊 Analitik Periyodu",
            ["7days", "30days", "90days", "all"],
            format_func=lambda x: {
                "7days": "Son 7 Gün",
                "30days": "Son 30 Gün",
                "90days": "Son 90 Gün",
                "all": "Tüm Zamanlar"
            }[x],
            index=3  # Default to "all"
        )

    analytics = get_task_match_analytics(time_range)

    # 4 metric cards in a row
    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("📊 Toplam Eşleşme", analytics["total_matches"])

    with metric2:
        st.metric("✅ Kabul Edilen", analytics["total_accepted"])

    with metric3:
        st.metric("📈 Kabul Oranı", f"{analytics['acceptance_rate']:.1f}%")

    with metric4:
        st.metric("🎯 Ort. Güven Skoru", f"{analytics['avg_confidence']:.2f}")

    # Main content area
    st.markdown("---")

    # Task Input Section
    st.subheader("1️⃣ Görevinizi Tanımlayın")

    col1, col2 = st.columns([3, 1])
    with col1:
        jira_key = st.text_input(
            "JIRA Anahtarı (Opsiyonel)",
            placeholder="örn: PROJ-123",
            help="Takip için opsiyonel JIRA anahtarı"
        )
    with col2:
        doc_type_filter = st.selectbox(
            "Doküman Tipi",
            ["all", "ba", "ta", "tc"],
            format_func=lambda x: {
                "all": "Tüm Tipler",
                "ba": "BA Dokümanları",
                "ta": "TA Dokümanları",
                "tc": "Test Senaryoları"
            }[x]
        )

    task_description = st.text_area(
        "Görev Açıklaması",
        placeholder="Ne yapmanız gerektiğini açıklayın...\n\nÖrnek: Mobil uygulama için login ekranına biyometrik kimlik doğrulama (Face ID ve Touch ID) ekle",
        height=150,
        help="Görevinizi açık bir şekilde tanımlayın. Özellikler, bileşenler ve teknik detayları dahil edin."
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_button = st.button("🔍 Eşleşme Bul", type="primary", use_container_width=True)
    with col2:
        if st.button("🔄 Temizle", use_container_width=True):
            # Clear all match-related session state
            for key in ["current_matches", "current_task_description", "current_jira_key", "match_response_time"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Analysis and Results Section
    if search_button:
        if not task_description.strip():
            st.error("Lütfen bir görev açıklaması girin.")
            return

        # Show analysis progress
        with st.spinner("Görev analiz ediliyor..."):
            matcher = SmartMatcher()
            explainer = MatchExplainer()

            # Get doc_type filter (None if "all")
            doc_type = None if doc_type_filter == "all" else doc_type_filter

            # Find matches
            start_time = time.time()
            matches = matcher.find_matches_for_task(
                task_description=task_description,
                jira_key=jira_key if jira_key.strip() else None,
                doc_type=doc_type,
                top_k=5
            )
            response_time = time.time() - start_time

            # Store matches in session state so they persist across reruns
            st.session_state["current_matches"] = matches
            st.session_state["current_task_description"] = task_description
            st.session_state["current_jira_key"] = jira_key
            st.session_state["match_response_time"] = response_time

        st.markdown("---")

    # Display results from session state (persists across button clicks)
    if "current_matches" in st.session_state:
        matches = st.session_state["current_matches"]
        task_description = st.session_state.get("current_task_description", task_description)
        jira_key = st.session_state.get("current_jira_key", jira_key)
        response_time = st.session_state.get("match_response_time", 0)
        explainer = MatchExplainer()

        st.markdown("---")

        # Show task analysis results
        if matches:
            task_features = matches[0].get("task_features", {})

            with st.expander("📋 Görev Analizi", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Niyet:** {task_features.get('intent', 'Bilinmiyor')}")
                    st.markdown(f"**Karmaşıklık:** {task_features.get('complexity', 'Bilinmiyor')}")
                with col2:
                    st.markdown(f"**Kapsam:** {task_features.get('scope', 'Bilinmiyor')}")
                    keywords = task_features.get('keywords', [])
                    st.markdown(f"**Anahtar Kelimeler:** {', '.join(keywords[:5])}")
                with col3:
                    relevance = task_features.get('doc_type_relevance', {})
                    st.markdown("**Doküman Tipi İlgisi:**")
                    for dt, score in relevance.items():
                        st.caption(f"{dt.upper()}: {score:.2f}")

        # Show matches
        st.subheader(f"2️⃣ Eşleşme Sonuçları ({len(matches)} bulundu, {response_time:.2f}s)")

        if not matches:
            st.info("🔍 İlgili doküman bulunamadı. Yeni bir doküman oluşturmayı düşünün.")
            st.markdown("**Öneri:** Bu görev için yeni bir doküman oluşturmak üzere Doküman Kütüphanesi'ni kullanın.")

            # Record no-match event (only once when search button was clicked)
            if search_button:
                task_features = {}
                record_task_match(
                    task_description=task_description,
                    task_features=task_features,
                    matched_document_id=None,
                    confidence_score=0.0,
                    match_reasoning="No matches found",
                    suggestion="CREATE_NEW",
                    jira_key=jira_key if jira_key.strip() else None,
                    user_accepted=False
                )
        else:
            # Display matches
            for idx, match in enumerate(matches):
                display_match_card(match, idx + 1, task_description, explainer, jira_key)

            st.markdown("---")
            st.caption(f"💡 **İpucu:** Daha yüksek güven skorları (yeşil) daha güçlü eşleşmeleri gösterir. Sonuçlardan herhangi bir dokümanı görüntüleyebilir veya kullanabilirsiniz.")

    elif search_button:
        # This happens if search_button was clicked but no matches in session state
        # (shouldn't normally happen, but good to handle)
        st.info("Görüntülenecek sonuç yok. Lütfen tekrar arama yapmayı deneyin.")


def display_match_card(match: dict, rank: int, task_description: str, explainer: MatchExplainer, jira_key: str):
    """Display a match result card."""

    confidence = match["confidence"]
    doc_id = match["document_id"]
    title = match["title"]
    doc_type = match["doc_type"].upper()
    version = match.get("version", "")

    # Determine confidence color and emoji
    if confidence >= 0.75:
        confidence_color = "green"
        confidence_label = "Yüksek"
        confidence_emoji = "🟢"
    elif confidence >= 0.5:
        confidence_color = "orange"
        confidence_label = "Orta"
        confidence_emoji = "🟡"
    else:
        confidence_color = "red"
        confidence_label = "Düşük"
        confidence_emoji = "🔴"

    # Generate explanation and suggestion
    task_features = match.get("task_features", {})
    breakdown = match.get("match_breakdown", {})

    # Generate explanation (use template for high confidence, AI for low)
    explanation = explainer.explain_match(
        task_description=task_description,
        matched_doc=match,
        scores=breakdown,
        use_ai=None  # Auto-decide
    )

    # Generate action suggestion
    suggestion_result = explainer.suggest_action(
        task_features=task_features,
        matched_doc=match,
        confidence=confidence
    )

    suggestion = suggestion_result.get("suggestion", "EVALUATE")
    suggestion_reasoning = suggestion_result.get("reasoning", "")

    # Display card
    with st.container():
        # Card with colored left border using markdown
        st.markdown(f"""
        <div style="border-left: 4px solid {confidence_color}; padding-left: 15px; margin-bottom: 15px;">
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"### {confidence_emoji} {rank}. {title}")
            st.caption(f"**Tip:** {doc_type} | **Versiyon:** {version}")

        with col2:
            st.metric("Güven Skoru", f"{confidence:.0%}", help=f"{confidence_label} güven skoru")

        with col3:
            # Suggestion badge
            suggestion_colors = {
                "UPDATE_EXISTING": "🟢",
                "CREATE_NEW": "🔴",
                "EXTEND_DOCUMENT": "🟡",
                "EVALUATE": "⚪"
            }
            badge = suggestion_colors.get(suggestion, "⚪")
            st.markdown(f"**Öneri**")
            st.markdown(f"{badge} {suggestion.replace('_', ' ')}")

        # Match preview
        section_matched = match.get("section_matched", "")
        if section_matched:
            st.markdown("**Eşleşen Bölüm Önizlemesi:**")
            st.text(section_matched[:200] + "..." if len(section_matched) > 200 else section_matched)

        # Explanation (expandable)
        with st.expander("💡 Neden bu eşleşme?"):
            st.markdown(explanation)
            st.markdown(f"**Öneri:** {suggestion_reasoning}")

            # Score breakdown
            st.markdown("**Skor Dağılımı:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"Anlamsal: {breakdown.get('semantic_score', 0):.2f}")
            with col2:
                st.caption(f"Anahtar Kelime: {breakdown.get('keyword_score', 0):.2f}")
            with col3:
                st.caption(f"Metadata: {breakdown.get('metadata_score', 0):.2f}")

        # Actions
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        with col1:
            if st.button(f"👁️ Görüntüle", key=f"view_{doc_id}_{rank}"):
                # Navigate to Document Library with this document
                st.session_state["selected_document_id"] = doc_id
                st.switch_page("pages/10_Document_Library.py")

        with col2:
            if st.button(f"✅ Bunu Kullan", key=f"use_{doc_id}_{rank}"):
                # Record acceptance and navigate
                record_task_match(
                    task_description=task_description,
                    task_features=task_features,
                    matched_document_id=doc_id,
                    confidence_score=confidence,
                    match_reasoning=explanation,
                    suggestion=suggestion,
                    jira_key=jira_key if jira_key.strip() else None,
                    user_accepted=True
                )
                st.session_state["selected_document_id"] = doc_id
                st.success(f"✅ Doküman kullanılıyor: {title}")
                time.sleep(1)
                st.switch_page("pages/10_Document_Library.py")

        with col3:
            if st.button(f"❌ İlgili Değil", key=f"reject_{doc_id}_{rank}"):
                # Record rejection
                record_task_match(
                    task_description=task_description,
                    task_features=task_features,
                    matched_document_id=doc_id,
                    confidence_score=confidence,
                    match_reasoning=explanation,
                    suggestion=suggestion,
                    jira_key=jira_key if jira_key.strip() else None,
                    user_accepted=False
                )
                st.info("Geri bildirim kaydedildi. Teşekkürler!")


if __name__ == "__main__":
    main()
