"""
📥 Import & Merge — Phase 4: Smart Document Integration

End-to-end workflow for importing and merging documents:
1. Import document (JSON, Text, or from Pipeline)
2. Auto-detect similar documents
3. Compare side-by-side
4. Smart merge with conflict resolution
"""
import streamlit as st
import json
from datetime import datetime
from data.database import (
    create_document, get_projects, get_documents_with_content,
    get_document_by_id, get_latest_version, create_document_version
)
from pipeline.document_matching import find_similar
from pipeline.document_adaptation import DocumentAdapter

st.set_page_config(page_title="Import & Merge", page_icon="📥", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .import-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .compare-section {
        border: 2px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .merge-option {
        background: rgba(102, 126, 234, 0.1);
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        cursor: pointer;
        border: 1px solid transparent;
    }
    .merge-option:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.2);
    }
    .diff-added {
        background-color: rgba(16, 185, 129, 0.2);
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
    }
    .diff-removed {
        background-color: rgba(239, 68, 68, 0.2);
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📥 Import & Merge Documents")
st.markdown("**Smart Integration** — Import new documents and merge with existing ones")

# Initialize session state
if 'import_step' not in st.session_state:
    st.session_state['import_step'] = 1

step = st.session_state['import_step']

# Progress indicator
progress_cols = st.columns(4)
with progress_cols[0]:
    st.markdown(f"{'🟢' if step >= 1 else '⚪'} **1. Import**")
with progress_cols[1]:
    st.markdown(f"{'🟢' if step >= 2 else '⚪'} **2. Detect Similar**")
with progress_cols[2]:
    st.markdown(f"{'🟢' if step >= 3 else '⚪'} **3. Compare**")
with progress_cols[3]:
    st.markdown(f"{'🟢' if step >= 4 else '⚪'} **4. Merge**")

st.divider()

# ═══════════════════════════════════════════════════════════════
# STEP 1: IMPORT DOCUMENT
# ═══════════════════════════════════════════════════════════════
if step == 1:
    st.subheader("Step 1: Import Document")

    import_method = st.radio(
        "How would you like to import?",
        ["📋 Paste JSON", "📄 From BRD Pipeline", "📝 Paste Text (AI Parse)"],
        horizontal=True
    )

    if import_method == "📋 Paste JSON":
        st.markdown("### Paste JSON Document")
        st.info("💡 Copy JSON from BRD Pipeline or any other source")

        json_input = st.text_area(
            "Document JSON",
            height=300,
            placeholder='{"ekranlar": [...], "backend_islemler": [...]}',
            help="Paste the complete JSON document"
        )

        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", ["BA", "TA", "TC"])
        with col2:
            title = st.text_input("Document Title*", placeholder="e.g., Face ID Login Analysis")

        if st.button("➡️ Import & Analyze", type="primary"):
            if not json_input or not title:
                st.error("❌ Please provide both JSON and title")
            else:
                try:
                    # Parse JSON
                    content = json.loads(json_input)

                    # Save to session state
                    st.session_state['imported_doc'] = {
                        'title': title,
                        'doc_type': doc_type.lower(),
                        'content_json': content,
                        'import_method': 'json'
                    }

                    st.success("✅ Document parsed successfully!")
                    st.session_state['import_step'] = 2
                    st.rerun()

                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")

    elif import_method == "📄 From BRD Pipeline":
        st.markdown("### Import from BRD Pipeline")
        st.info("💡 Coming soon: Direct import from pipeline results")
        st.markdown("""
        **For now:**
        1. Run BRD Pipeline
        2. Copy the BA/TA/TC JSON output
        3. Use '📋 Paste JSON' option above
        """)

    elif import_method == "📝 Paste Text (AI Parse)":
        st.markdown("### Paste Text Document")
        st.info("💡 AI will parse your text into structured format")

        text_input = st.text_area(
            "Document Text",
            height=300,
            placeholder="Paste your BA/TA/TC document here...",
            help="Paste unstructured text, AI will convert to JSON"
        )

        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", ["BA", "TA", "TC"], key="text_doc_type")
        with col2:
            title = st.text_input("Document Title*", placeholder="e.g., Face ID Login Analysis", key="text_title")

        if st.button("🤖 Parse with AI", type="primary"):
            st.warning("⚠️ AI parsing feature coming soon! Please use JSON import for now.")

# ═══════════════════════════════════════════════════════════════
# STEP 2: DETECT SIMILAR DOCUMENTS
# ═══════════════════════════════════════════════════════════════
elif step == 2:
    if 'imported_doc' not in st.session_state:
        st.session_state['import_step'] = 1
        st.rerun()

    imported = st.session_state['imported_doc']

    st.subheader("Step 2: Detect Similar Documents")
    st.markdown(f"**Imported:** {imported['title']} ({imported['doc_type'].upper()})")

    with st.spinner("🔍 Searching for similar documents..."):
        # Get all documents of same type with content
        candidates = get_documents_with_content(
            doc_type=imported['doc_type'],
            limit=50
        )

        if candidates:
            # Find similar
            similar_docs = find_similar(
                target_doc=imported,
                candidate_docs=candidates,
                top_n=5
            )

            if similar_docs:
                st.success(f"✅ Found {len(similar_docs)} similar documents")

                st.markdown("### Similar Documents")

                for i, (doc, score, breakdown) in enumerate(similar_docs):
                    score_pct = int(score * 100)
                    tfidf_pct = int(breakdown['tfidf_score'] * 100)
                    meta_pct = int(breakdown['metadata_score'] * 100)

                    # Color based on score
                    if score >= 0.7:
                        score_color = "#10b981"
                        emoji = "🟢"
                    elif score >= 0.4:
                        score_color = "#f59e0b"
                        emoji = "🟠"
                    else:
                        score_color = "#6b7280"
                        emoji = "⚪"

                    with st.expander(f"{emoji} {doc['title']} - {score_pct}% match", expanded=(i == 0)):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**Match Score:** {score_pct}%")
                            st.markdown(f"- Content Similarity: {tfidf_pct}%")
                            st.markdown(f"- Metadata Match: {meta_pct}%")
                            st.markdown(f"**Version:** v{doc['current_version']}")
                            st.markdown(f"**Tags:** {', '.join(doc.get('tags', []))}")

                        with col2:
                            if st.button("Compare & Merge", key=f"merge_{doc['id']}", type="primary", use_container_width=True):
                                st.session_state['selected_similar'] = doc
                                st.session_state['similarity_score'] = score
                                st.session_state['import_step'] = 3
                                st.rerun()

                st.divider()

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("⬅️ Back to Import"):
                        st.session_state['import_step'] = 1
                        st.rerun()

                with col_b:
                    if st.button("Skip Merge → Save as New"):
                        # Save directly as new document
                        try:
                            # Get or create default project
                            projects = get_projects()
                            if projects:
                                project_id = projects[0]['id']
                            else:
                                from data.database import create_project
                                project_id = create_project(
                                    name="Imported Documents",
                                    description="Documents imported via Import & Merge",
                                    tags=["imported"]
                                )

                            doc_id = create_document(
                                project_id=project_id,
                                doc_type=imported['doc_type'],
                                title=imported['title'],
                                content_json=imported['content_json'],
                                description="Imported via Import & Merge feature",
                                tags=["imported"],
                                created_by="import"
                            )

                            st.success(f"✅ Document saved! (ID: {doc_id})")
                            st.balloons()

                            # Clear state
                            for key in ['import_step', 'imported_doc']:
                                if key in st.session_state:
                                    del st.session_state[key]

                            if st.button("Import Another Document"):
                                st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error saving: {str(e)}")

            else:
                st.info("📝 No similar documents found. This is a unique document!")

                if st.button("Save as New Document", type="primary"):
                    # Save directly
                    try:
                        projects = get_projects()
                        if projects:
                            project_id = projects[0]['id']
                        else:
                            from data.database import create_project
                            project_id = create_project(
                                name="Imported Documents",
                                description="Documents imported via Import & Merge",
                                tags=["imported"]
                            )

                        doc_id = create_document(
                            project_id=project_id,
                            doc_type=imported['doc_type'],
                            title=imported['title'],
                            content_json=imported['content_json'],
                            description="Imported via Import & Merge feature",
                            tags=["imported"],
                            created_by="import"
                        )

                        st.success(f"✅ Document saved! (ID: {doc_id})")
                        st.balloons()

                        for key in ['import_step', 'imported_doc']:
                            if key in st.session_state:
                                del st.session_state[key]

                        if st.button("Import Another"):
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        else:
            st.info("No documents in library yet. Saving as first document...")

            if st.button("Save Document", type="primary"):
                try:
                    from data.database import create_project
                    project_id = create_project(
                        name="Imported Documents",
                        description="Documents imported via Import & Merge",
                        tags=["imported"]
                    )

                    doc_id = create_document(
                        project_id=project_id,
                        doc_type=imported['doc_type'],
                        title=imported['title'],
                        content_json=imported['content_json'],
                        description="Imported via Import & Merge feature",
                        tags=["imported"],
                        created_by="import"
                    )

                    st.success(f"✅ First document saved! (ID: {doc_id})")
                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# STEP 3: COMPARE DOCUMENTS
# ═══════════════════════════════════════════════════════════════
elif step == 3:
    if 'imported_doc' not in st.session_state or 'selected_similar' not in st.session_state:
        st.session_state['import_step'] = 1
        st.rerun()

    imported = st.session_state['imported_doc']
    similar = st.session_state['selected_similar']
    similarity_score = st.session_state.get('similarity_score', 0)

    st.subheader("Step 3: Compare Documents")

    # Similarity badge
    score_pct = int(similarity_score * 100)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem; border-radius: 8px; margin-bottom: 1rem; color: white;">
        <strong>Similarity:</strong> {score_pct}% match
    </div>
    """, unsafe_allow_html=True)

    # Side-by-side comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 📄 Existing: {similar['title']}")
        st.markdown(f"**Type:** {similar['doc_type'].upper()}")
        st.markdown(f"**Version:** v{similar['current_version']}")
        st.markdown(f"**Tags:** {', '.join(similar.get('tags', []))}")

        st.divider()
        st.markdown("**Content:**")
        st.json(similar.get('content_json', {}))

    with col2:
        st.markdown(f"### 📥 New: {imported['title']}")
        st.markdown(f"**Type:** {imported['doc_type'].upper()}")
        st.markdown(f"**Status:** Imported")

        st.divider()
        st.markdown("**Content:**")
        st.json(imported['content_json'])

    # Action buttons
    st.divider()

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("⬅️ Back to Similar Docs"):
            st.session_state['import_step'] = 2
            del st.session_state['selected_similar']
            st.rerun()

    with col_b:
        if st.button("Save New (No Merge)"):
            # Save as separate document
            try:
                projects = get_projects()
                project_id = projects[0]['id'] if projects else similar.get('project_id', 1)

                doc_id = create_document(
                    project_id=project_id,
                    doc_type=imported['doc_type'],
                    title=imported['title'],
                    content_json=imported['content_json'],
                    description=f"Imported (similar to {similar['title']})",
                    tags=["imported"],
                    created_by="import"
                )

                st.success(f"✅ Saved as separate document! (ID: {doc_id})")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with col_c:
        if st.button("➡️ Merge Documents", type="primary"):
            st.session_state['import_step'] = 4
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# STEP 4: SMART MERGE
# ═══════════════════════════════════════════════════════════════
elif step == 4:
    if 'imported_doc' not in st.session_state or 'selected_similar' not in st.session_state:
        st.session_state['import_step'] = 1
        st.rerun()

    imported = st.session_state['imported_doc']
    similar = st.session_state['selected_similar']

    st.subheader("Step 4: Smart Merge")
    st.markdown(f"**Merging:** {imported['title']} + {similar['title']}")

    st.info("💡 Review and edit the merged content below")

    # Initialize merged content
    if 'merged_content' not in st.session_state:
        # Simple merge: combine both documents
        merged = {}

        # Deep merge strategy
        existing_content = similar.get('content_json', {})
        new_content = imported['content_json']

        # Start with existing
        merged = json.loads(json.dumps(existing_content))

        # Add new content
        for key, value in new_content.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Merge arrays
                merged[key] = merged[key] + value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                # Merge dicts
                merged[key].update(value)
            else:
                # Overwrite
                merged[key] = value

        st.session_state['merged_content'] = merged

    # Editable merged content
    merged_str = json.dumps(st.session_state['merged_content'], indent=2, ensure_ascii=False)

    edited_merged = st.text_area(
        "Merged Content (JSON)",
        value=merged_str,
        height=400,
        help="Edit the merged result as needed"
    )

    # Validate
    if st.button("✓ Validate Merged JSON"):
        try:
            validated = json.loads(edited_merged)
            st.session_state['merged_content'] = validated
            st.success("✅ Merged JSON is valid!")
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")

    st.divider()

    # Save options
    st.markdown("### Save Options")

    save_option = st.radio(
        "How to save?",
        [
            "💾 Update existing document (new version)",
            "📝 Save as new document",
            "🔄 Replace existing document"
        ]
    )

    new_title = st.text_input(
        "Document Title",
        value=f"{similar['title']} (Merged)" if "new" in save_option else similar['title']
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("⬅️ Back to Compare"):
            st.session_state['import_step'] = 3
            st.rerun()

    with col_b:
        if st.button("💾 Save Merged Document", type="primary"):
            try:
                # Parse final content
                final_content = json.loads(edited_merged)

                if "Update existing" in save_option:
                    # Create new version
                    doc_id = similar['id']

                    create_document_version(
                        doc_id=doc_id,
                        content_json=final_content,
                        change_summary=f"Merged with {imported['title']}",
                        created_by="merge"
                    )

                    # Update document metadata
                    from data.database import update_document
                    current_version = similar['current_version'] + 1
                    update_document(
                        doc_id=doc_id,
                        current_version=current_version,
                        updated_at=datetime.now().isoformat()
                    )

                    st.success(f"✅ Updated {similar['title']} with merged content! (v{current_version})")

                elif "new document" in save_option:
                    # Save as new
                    doc_id = create_document(
                        project_id=similar['project_id'],
                        doc_type=similar['doc_type'],
                        title=new_title,
                        content_json=final_content,
                        description=f"Merged from {similar['title']} and {imported['title']}",
                        tags=list(set(similar.get('tags', []) + ["merged"])),
                        created_by="merge",
                        source_document_id=similar['id']
                    )

                    st.success(f"✅ Saved as new document! (ID: {doc_id})")

                st.balloons()

                # Clear state
                for key in ['import_step', 'imported_doc', 'selected_similar', 'merged_content', 'similarity_score']:
                    if key in st.session_state:
                        del st.session_state[key]

                if st.button("Import Another Document"):
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error saving: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>📥 Import & Merge</strong> — Smart Document Integration<br>
    Import → Detect → Compare → Merge
</div>
""", unsafe_allow_html=True)
