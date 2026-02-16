"""
Smart Matching Page

AI-powered task-to-document matching to help users find relevant existing documents.
"""

import streamlit as st
from pipeline.smart_matcher import SmartMatcher
from pipeline.match_explainer import MatchExplainer
from data.database import record_task_match, get_task_match_analytics
import time


def main():
    st.set_page_config(page_title="Smart Matching", page_icon="🔍", layout="wide")

    st.title("🔍 Smart Document Matching")
    st.markdown("""
    **AI-powered task-to-document matching** - Describe your task and find relevant existing documents.
    Saves time by avoiding duplicate work and helping you reuse existing documentation.
    """)

    # Sidebar with analytics
    with st.sidebar:
        st.subheader("📊 Matching Analytics")

        time_range = st.selectbox(
            "Time Range",
            ["7days", "30days", "90days", "all"],
            format_func=lambda x: {
                "7days": "Last 7 Days",
                "30days": "Last 30 Days",
                "90days": "Last 90 Days",
                "all": "All Time"
            }[x],
            index=3  # Default to "all"
        )

        analytics = get_task_match_analytics(time_range)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Matches", analytics["total_matches"])
            st.metric("Accepted", analytics["total_accepted"])
        with col2:
            st.metric("Acceptance Rate", f"{analytics['acceptance_rate']:.1f}%")
            st.metric("Avg Confidence", f"{analytics['avg_confidence']:.2f}")

        if analytics["suggestion_breakdown"]:
            st.markdown("**Suggestions**")
            for item in analytics["suggestion_breakdown"]:
                suggestion = item["suggestion"] or "N/A"
                count = item["count"]
                accepted = item["accepted"] or 0
                rate = (accepted / count * 100) if count > 0 else 0
                st.caption(f"{suggestion}: {count} ({rate:.0f}% accepted)")

    # Main content area
    st.markdown("---")

    # Task Input Section
    st.subheader("1️⃣ Describe Your Task")

    col1, col2 = st.columns([3, 1])
    with col1:
        jira_key = st.text_input(
            "JIRA Key (Optional)",
            placeholder="e.g., PROJ-123",
            help="Optional JIRA key for tracking"
        )
    with col2:
        doc_type_filter = st.selectbox(
            "Document Type",
            ["all", "ba", "ta", "tc"],
            format_func=lambda x: {
                "all": "All Types",
                "ba": "BA Documents",
                "ta": "TA Documents",
                "tc": "Test Cases"
            }[x]
        )

    task_description = st.text_area(
        "Task Description",
        placeholder="Describe what you need to do...\n\nExample: Add biometric authentication (Face ID and Touch ID) to the login screen for mobile app",
        height=150,
        help="Provide a clear description of your task. Include features, components, and technical details."
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_button = st.button("🔍 Find Matches", type="primary", use_container_width=True)
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            # Clear all match-related session state
            for key in ["current_matches", "current_task_description", "current_jira_key", "match_response_time"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Analysis and Results Section
    if search_button:
        if not task_description.strip():
            st.error("Please enter a task description.")
            return

        # Show analysis progress
        with st.spinner("Analyzing task..."):
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

            with st.expander("📋 Task Analysis", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Intent:** {task_features.get('intent', 'Unknown')}")
                    st.markdown(f"**Complexity:** {task_features.get('complexity', 'Unknown')}")
                with col2:
                    st.markdown(f"**Scope:** {task_features.get('scope', 'Unknown')}")
                    keywords = task_features.get('keywords', [])
                    st.markdown(f"**Keywords:** {', '.join(keywords[:5])}")
                with col3:
                    relevance = task_features.get('doc_type_relevance', {})
                    st.markdown("**Doc Type Relevance:**")
                    for dt, score in relevance.items():
                        st.caption(f"{dt.upper()}: {score:.2f}")

        # Show matches
        st.subheader(f"2️⃣ Match Results ({len(matches)} found in {response_time:.2f}s)")

        if not matches:
            st.info("🔍 No relevant documents found. Consider creating a new document.")
            st.markdown("**Suggestion:** Use the Document Library to create a new document for this task.")

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
            st.caption(f"💡 **Tip:** Higher confidence scores (green) indicate stronger matches. You can view or use any document from the results.")

    elif search_button:
        # This happens if search_button was clicked but no matches in session state
        # (shouldn't normally happen, but good to handle)
        st.info("No results to display. Please try searching again.")


def display_match_card(match: dict, rank: int, task_description: str, explainer: MatchExplainer, jira_key: str):
    """Display a match result card."""

    confidence = match["confidence"]
    doc_id = match["document_id"]
    title = match["title"]
    doc_type = match["doc_type"].upper()
    version = match.get("version", "")

    # Determine confidence color
    if confidence >= 0.75:
        confidence_color = "green"
        confidence_label = "High"
    elif confidence >= 0.5:
        confidence_color = "orange"
        confidence_label = "Medium"
    else:
        confidence_color = "red"
        confidence_label = "Low"

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
        st.markdown(f"""
        <div style="border: 2px solid {confidence_color}; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"### {rank}. {title}")
            st.caption(f"**Type:** {doc_type} | **Version:** {version}")

        with col2:
            st.metric("Confidence", f"{confidence:.0%}", help=f"{confidence_label} confidence")

        with col3:
            # Suggestion badge
            suggestion_colors = {
                "UPDATE_EXISTING": "🟢",
                "CREATE_NEW": "🔴",
                "EXTEND_DOCUMENT": "🟡",
                "EVALUATE": "⚪"
            }
            badge = suggestion_colors.get(suggestion, "⚪")
            st.markdown(f"**Suggestion**")
            st.markdown(f"{badge} {suggestion.replace('_', ' ')}")

        # Match preview
        section_matched = match.get("section_matched", "")
        if section_matched:
            st.markdown("**Matched Section Preview:**")
            st.text(section_matched[:200] + "..." if len(section_matched) > 200 else section_matched)

        # Explanation (expandable)
        with st.expander("💡 Why this match?"):
            st.markdown(explanation)
            st.markdown(f"**Suggestion:** {suggestion_reasoning}")

            # Score breakdown
            st.markdown("**Score Breakdown:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"Semantic: {breakdown.get('semantic_score', 0):.2f}")
            with col2:
                st.caption(f"Keyword: {breakdown.get('keyword_score', 0):.2f}")
            with col3:
                st.caption(f"Metadata: {breakdown.get('metadata_score', 0):.2f}")

        # Actions
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        with col1:
            if st.button(f"👁️ View", key=f"view_{doc_id}_{rank}"):
                # Navigate to Document Library with this document
                st.session_state["selected_document_id"] = doc_id
                st.switch_page("pages/10_Document_Library.py")

        with col2:
            if st.button(f"✅ Use This", key=f"use_{doc_id}_{rank}"):
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
                st.success(f"✅ Using document: {title}")
                time.sleep(1)
                st.switch_page("pages/10_Document_Library.py")

        with col3:
            if st.button(f"❌ Not Relevant", key=f"reject_{doc_id}_{rank}"):
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
                st.info("Feedback recorded. Thanks!")


if __name__ == "__main__":
    main()
