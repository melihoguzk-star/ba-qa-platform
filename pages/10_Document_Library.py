"""
📚 Document Library — Smart Document Repository & Evolution System

Phase 1: Document storage, organization, and retrieval
Stores previous BA/TA/TC documents for reuse and evolution.
"""
import streamlit as st
import json
from datetime import datetime
from data.database import (
    create_project, get_projects, get_project_by_id,
    create_document, get_documents, get_document_by_id, update_document,
    create_document_version, get_document_versions, get_latest_version,
    get_document_stats, get_documents_with_content,
    get_template_candidates, get_document_lineage
)
from pipeline.document_matching import find_similar
from pipeline.document_adaptation import DocumentAdapter
from components.sidebar import render_custom_sidebar

# Phase 2B: Semantic Search
try:
    from pipeline.vector_store import get_vector_store
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False

st.set_page_config(page_title="Document Library", page_icon="📚", layout="wide")

# Render custom sidebar
render_custom_sidebar(active_page="document_library")

# Custom CSS
st.markdown("""
<style>
    .doc-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .doc-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .doc-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .doc-meta {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
    .stat-label {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
    }
    .tag {
        background: rgba(255,255,255,0.2);
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.5rem;
        color: white;
    }
    .version-badge {
        background: #10b981;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Document Library")
st.markdown("**Smart Document Repository** — Store, organize, and evolve your BA/TA/TC documents")

# Check if coming from Smart Matching with a selected document
if "selected_document_id" in st.session_state:
    selected_doc_id = st.session_state["selected_document_id"]
    # Force page to Documents view and set document to view
    st.session_state["view_document_id"] = selected_doc_id
    # Clear the selected_document_id so it doesn't persist
    del st.session_state["selected_document_id"]
    st.success(f"📄 Opening document ID {selected_doc_id}")

# Get stats for dashboard
stats = get_document_stats()

# Default to Documents tab if view_document_id is set
default_tab = 2 if "view_document_id" in st.session_state else 0

# Tabs for navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📁 Projeler",
    "📄 Dokümanlar",
    "📝 Şablondan Oluştur",
    "⬆️ Doküman Yükle"
])

# ─────────────────────────────────────────────
# TAB 1: DASHBOARD
# ─────────────────────────────────────────────
with tab1:
    st.header("📊 Document Repository Dashboard")

    # Stats overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['total_projects']}</div>
            <div class="stat-label">Projects</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['total_documents']}</div>
            <div class="stat-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)

    ba_count = next((s['c'] for s in stats['by_type'] if s['doc_type'] == 'ba'), 0)
    tc_count = next((s['c'] for s in stats['by_type'] if s['doc_type'] == 'tc'), 0)

    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{ba_count}</div>
            <div class="stat-label">BA Docs</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{tc_count}</div>
            <div class="stat-label">TC Docs</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Recent documents
    st.subheader("📄 Recent Documents")

    if stats['recent_documents']:
        for doc in stats['recent_documents']:
            doc_tags = json.loads(doc.get('tags', '[]'))
            doc_type_label = {"ba": "Business Analysis", "ta": "Technical Analysis", "tc": "Test Cases"}.get(doc['doc_type'], doc['doc_type'])

            st.markdown(f"""
            <div class="doc-card">
                <div class="doc-title">{doc['title']}</div>
                <div class="doc-meta">
                    📁 {doc.get('project_name', 'Unknown Project')} •
                    📝 {doc_type_label} •
                    v{doc['current_version']} •
                    Updated: {doc['updated_at'][:10]}
                </div>
                <div style="margin-top: 0.5rem;">
                    {''.join([f'<span class="tag">{tag}</span>' for tag in doc_tags])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No documents yet. Upload your first document to get started!")

# ─────────────────────────────────────────────
# PROJECTS PAGE
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# TAB 2: PROJECTS
# ─────────────────────────────────────────────
with tab2:
    st.header("📁 Projects")

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("➕ New Project", type="primary", use_container_width=True):
            st.session_state['show_new_project'] = True

    # Create new project form
    if st.session_state.get('show_new_project', False):
        with st.form("new_project_form"):
            st.subheader("Create New Project")

            project_name = st.text_input("Project Name*", placeholder="e.g., Mobile Banking App")
            project_desc = st.text_area("Description", placeholder="Brief description of the project")
            jira_key = st.text_input("JIRA Project Key", placeholder="e.g., MBA")
            tags_input = st.text_input("Tags (comma separated)", placeholder="e.g., mobile, banking, ios")

            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Create Project", type="primary", use_container_width=True)
            with col_b:
                cancel = st.form_submit_button("Cancel", use_container_width=True)

            if submit and project_name:
                tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                try:
                    project_id = create_project(
                        name=project_name,
                        description=project_desc,
                        jira_project_key=jira_key,
                        tags=tags
                    )
                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.session_state['show_new_project'] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating project: {str(e)}")

            if cancel:
                st.session_state['show_new_project'] = False
                st.rerun()

    st.divider()

    # Search projects
    search = st.text_input("🔍 Search Projects", placeholder="Search by name or description", key="tab2_search_projects")

    # List projects
    projects = get_projects(search=search)

    if projects:
        for project in projects:
            project_tags = project.get('tags', [])

            with st.expander(f"📁 {project['name']}", expanded=False):
                st.markdown(f"**Description:** {project.get('description', 'No description')}")
                st.markdown(f"**JIRA Key:** {project.get('jira_project_key', 'N/A')}")
                st.markdown(f"**Created:** {project['created_at'][:10]}")

                if project_tags:
                    st.markdown("**Tags:** " + " ".join([f'<span class="tag">{tag}</span>' for tag in project_tags]), unsafe_allow_html=True)

                # Get documents for this project
                project_docs = get_documents(project_id=project['id'])
                st.markdown(f"**Documents:** {len(project_docs)}")

                if st.button(f"View Documents", key=f"view_docs_{project['id']}"):
                    st.session_state['selected_project'] = project['id']
                    st.session_state['page'] = "📄 Documents"
                    st.rerun()
    else:
        st.info("No projects found. Create your first project to get started!")

# ─────────────────────────────────────────────
# DOCUMENTS PAGE
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# TAB 3: DOCUMENTS
# ─────────────────────────────────────────────
with tab3:
    st.header("📄 Documents")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        projects = get_projects()
        project_options = ["All Projects"] + [p['name'] for p in projects]
        selected_project_name = st.selectbox("Project", project_options, key="tab3_project_filter")

        selected_project_id = None
        if selected_project_name != "All Projects":
            selected_project_id = next((p['id'] for p in projects if p['name'] == selected_project_name), None)

    with col2:
        doc_type_filter = st.selectbox("Document Type", ["All Types", "BA", "TA", "TC"], key="tab3_doctype_filter")
        doc_type = None
        if doc_type_filter != "All Types":
            doc_type = doc_type_filter.lower()

    with col3:
        search = st.text_input("🔍 Search", placeholder="Search documents...", key="tab3_search_documents")

    # Phase 2B: Semantic Search & Hybrid Mode
    use_semantic = False
    use_hybrid = False
    if SEMANTIC_SEARCH_AVAILABLE and search:
        import os
        semantic_enabled = os.getenv('ENABLE_SEMANTIC_SEARCH', 'true').lower() == 'true'
        hybrid_enabled = os.getenv('ENABLE_HYBRID_SEARCH', 'true').lower() == 'true'

        if semantic_enabled:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                use_semantic = st.checkbox(
                    "🔍 Use Semantic Search (AI-powered)",
                    value=False,
                    help="Find documents by meaning, not just keywords. Supports Turkish + English.",
                    key="tab3_use_semantic"
                )
            with col_s2:
                if hybrid_enabled and use_semantic:
                    use_hybrid = st.checkbox(
                        "⚡ Hybrid Mode (Best Results)",
                        value=True,
                        help="Combines keyword + semantic search. Exact matches ranked higher.",
                        key="tab3_use_hybrid"
                    )

    # Get documents
    documents = []
    similarity_scores = {}  # Store similarity scores for semantic/hybrid results
    chunk_info = {}  # Store chunk information (text, type) for semantic results
    search_mode = "keyword"  # Track which search mode was used

    if use_semantic and search:
        try:
            if use_hybrid:
                # Hybrid search (TF-IDF + Semantic fusion)
                search_mode = "hybrid"
                with st.spinner("Searching with hybrid AI..."):
                    from pipeline.hybrid_search import hybrid_search

                    # Search across document types
                    doc_types_to_search = [doc_type] if doc_type else ['ba', 'ta', 'tc']
                    all_results = []

                    for dt in doc_types_to_search:
                        results = hybrid_search(
                            query_text=search,
                            doc_type=dt,
                            top_k=20,
                            alpha=float(os.getenv('HYBRID_SEARCH_ALPHA', '0.6'))
                        )
                        all_results.extend(results)

                    # Get unique document IDs with scores and chunk info
                    doc_ids_with_data = {}
                    for result in all_results:
                        doc_id = result['document_id']
                        score = result.get('hybrid_score', result.get('similarity', 0))

                        # Keep the result with highest score for each document
                        if doc_id not in doc_ids_with_data or score > doc_ids_with_data[doc_id]['score']:
                            doc_ids_with_data[doc_id] = {
                                'score': score,
                                'chunk_text': result.get('chunk_text', ''),
                                'chunk_type': result.get('metadata', {}).get('chunk_type', 'unknown'),
                                'result': result  # Store full result for context
                            }

                    # Fetch full documents
                    for doc_id, data in doc_ids_with_data.items():
                        doc = get_document_by_id(doc_id)
                        if doc and doc['status'] == 'active':
                            documents.append(doc)
                            similarity_scores[doc_id] = data['score']
                            chunk_info[doc_id] = {
                                'text': data['chunk_text'],
                                'type': data['chunk_type'],
                                'result': data['result']
                            }

                    # Sort by hybrid score (highest first)
                    documents.sort(key=lambda d: similarity_scores.get(d['id'], 0), reverse=True)

            else:
                # Pure semantic search using vector store
                search_mode = "semantic"
                with st.spinner("Searching with AI..."):
                    vector_store = get_vector_store()

                    # Search across document types
                    doc_types_to_search = [doc_type] if doc_type else ['ba', 'ta', 'tc']
                    all_results = []

                    for dt in doc_types_to_search:
                        results = vector_store.search(
                            query_text=search,
                            doc_type=dt,
                            top_k=20,
                            filter_metadata={'project_id': selected_project_id} if selected_project_id else None
                        )
                        all_results.extend(results)

                    # Get unique document IDs with scores and chunk info
                    doc_ids_with_data = {}
                    for result in all_results:
                        doc_id = result['document_id']
                        similarity = result['similarity']

                        # Keep the result with highest similarity for each document
                        if doc_id not in doc_ids_with_data or similarity > doc_ids_with_data[doc_id]['score']:
                            doc_ids_with_data[doc_id] = {
                                'score': similarity,
                                'chunk_text': result.get('chunk_text', ''),
                                'chunk_type': result.get('metadata', {}).get('chunk_type', 'unknown'),
                                'result': result  # Store full result for context
                            }

                    # Fetch full documents
                    for doc_id, data in doc_ids_with_data.items():
                        doc = get_document_by_id(doc_id)
                        if doc and doc['status'] == 'active':
                            documents.append(doc)
                            similarity_scores[doc_id] = data['score']
                            chunk_info[doc_id] = {
                                'text': data['chunk_text'],
                                'type': data['chunk_type'],
                                'result': data['result']
                            }

                    # Sort by similarity score (highest first)
                    documents.sort(key=lambda d: similarity_scores.get(d['id'], 0), reverse=True)

        except Exception as e:
            st.error(f"❌ {search_mode.capitalize()} search failed: {str(e)}")
            st.info("Falling back to keyword search...")
            search_mode = "keyword"
            # Fall back to regular search
            documents = get_documents(
                project_id=selected_project_id,
                doc_type=doc_type,
                search=search
            )
    else:
        # Regular keyword search
        documents = get_documents(
            project_id=selected_project_id,
            doc_type=doc_type,
            search=search
        )

    # Display document count and search mode
    if search:
        if search_mode == "hybrid":
            st.markdown(f"**Found {len(documents)} documents** ⚡ *Hybrid Search Mode (Keyword + AI)*")
        elif search_mode == "semantic":
            st.markdown(f"**Found {len(documents)} documents** 🔍 *Semantic Search Mode (AI)*")
        else:
            st.markdown(f"**Found {len(documents)} documents** 🔤 *Keyword Search*")
    else:
        st.markdown(f"**Found {len(documents)} documents**")

    # Display documents
    if documents:
        for doc in documents:
            doc_tags = doc.get('tags', [])
            jira_keys = doc.get('jira_keys', [])
            doc_type_label = {"ba": "Business Analysis", "ta": "Technical Analysis", "tc": "Test Cases"}.get(doc['doc_type'], doc['doc_type'])

            # Get project name
            project = get_project_by_id(doc['project_id'])
            project_name = project['name'] if project else "Unknown"

            # Build title with similarity score if available
            doc_title = f"📄 {doc['title']}"
            if doc['id'] in similarity_scores:
                similarity = similarity_scores[doc['id']]
                similarity_pct = f"{similarity:.0%}"
                doc_title = f"📄 {doc['title']} 💡 Similarity: {similarity_pct}"

            # Auto-expand if this is the document selected from Smart Matching
            is_selected = st.session_state.get("view_document_id") == doc['id']
            if is_selected:
                # Clear after using it
                if "view_document_id" in st.session_state:
                    del st.session_state["view_document_id"]

            with st.expander(doc_title, expanded=is_selected):
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    st.markdown(f"**Project:** {project_name}")
                    st.markdown(f"**Type:** {doc_type_label}")
                    st.markdown(f"**Description:** {doc.get('description', 'No description')}")
                    st.markdown(f"**Current Version:** v{doc['current_version']}")
                    st.markdown(f"**Status:** {doc['status'].upper()}")
                    st.markdown(f"**Created:** {doc['created_at'][:10]} by {doc['created_by']}")
                    st.markdown(f"**Updated:** {doc['updated_at'][:10]}")

                    if jira_keys:
                        st.markdown(f"**JIRA Keys:** {', '.join(jira_keys)}")

                    if doc_tags:
                        st.markdown("**Tags:** " + " ".join([f'<span class="tag">{tag}</span>' for tag in doc_tags]), unsafe_allow_html=True)

                    # Phase 2B: Show matched chunk info for semantic/hybrid search
                    if doc['id'] in chunk_info and search_mode in ['semantic', 'hybrid']:
                        chunk = chunk_info[doc['id']]
                        chunk_text = chunk.get('text', '')
                        chunk_type = chunk.get('type', 'unknown')

                        # Only show if we have actual chunk info (from semantic search)
                        if chunk_text and chunk_type != 'unknown':
                            # Chunk type with icon (match chunking_strategy.py types)
                            type_icons = {
                                'ekran': '🖥️',
                                'screen': '🖥️',
                                'backend_operation': '⚙️',
                                'backend_islem': '⚙️',
                                'endpoint': '🔌',
                                'test_case': '🧪',
                                'test_scenario': '🧪',
                                'data_entity': '📊',
                                'unknown': '📄'
                            }
                            icon = type_icons.get(chunk_type.lower(), '📄')

                            st.divider()
                            st.markdown(f"**{icon} Matched Chunk:** *{chunk_type}*")

                            # Show chunk preview (max 200 chars)
                            preview = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
                            st.info(f"💡 \"{preview}\"")

                            # "View Full Context" expander
                            if len(chunk_text) > 200:
                                with st.expander("📖 View Full Matched Text"):
                                    st.text(chunk_text)
                        elif search_mode == 'hybrid' and not chunk_text:
                            # Hybrid mode but no semantic match - show TF-IDF only indicator
                            st.divider()
                            st.caption("🔤 Matched via keyword search (TF-IDF)")

                    # Phase 3: Lineage information
                    if doc.get('source_document_id'):
                        lineage = get_document_lineage(doc['id'])
                        if lineage and lineage['source']:
                            source = lineage['source']
                            st.markdown(f"🌳 **Adapted from:** [{source['title']}](#) (ID: {source['id']})")
                            if doc.get('adaptation_notes'):
                                st.caption(f"_{doc['adaptation_notes']}_")

                with col_b:
                    if st.button("View Content", key=f"view_{doc['id']}", use_container_width=True):
                        st.session_state['view_doc_id'] = doc['id']

                    if st.button("Version History", key=f"history_{doc['id']}", use_container_width=True):
                        st.session_state['history_doc_id'] = doc['id']

                    if st.button("🔍 Find Similar", key=f"similar_{doc['id']}", use_container_width=True):
                        st.session_state['similar_doc_id'] = doc['id']

                    if st.button("🌳 View Lineage", key=f"lineage_{doc['id']}", use_container_width=True):
                        st.session_state['lineage_doc_id'] = doc['id']

                # View content
                if st.session_state.get('view_doc_id') == doc['id']:
                    st.divider()
                    st.subheader("Document Content")

                    latest_version = get_latest_version(doc['id'])
                    if latest_version:
                        content = latest_version['content_json']
                        st.json(content)
                    else:
                        st.warning("No content available")

                # Version history
                if st.session_state.get('history_doc_id') == doc['id']:
                    st.divider()
                    st.subheader("Version History")

                    versions = get_document_versions(doc['id'])
                    for version in versions:
                        st.markdown(f"""
                        **v{version['version_number']}** — {version['created_at'][:16]} by {version['created_by']}
                        {version.get('change_summary', 'No summary')}
                        """)

                # Similar documents
                if st.session_state.get('similar_doc_id') == doc['id']:
                    st.divider()
                    st.subheader("🔍 Similar Documents")

                    with st.spinner("Finding similar documents..."):
                        # Get current document with content
                        current_doc_full = get_document_by_id(doc['id'])
                        latest_version = get_latest_version(doc['id'])

                        if latest_version:
                            current_doc_full['content_json'] = latest_version['content_json']

                            # Get all candidate documents with content (same type)
                            candidates = get_documents_with_content(
                                doc_type=doc['doc_type'],
                                limit=100
                            )

                            # Find similar
                            similar_docs = find_similar(
                                target_doc=current_doc_full,
                                candidate_docs=candidates,
                                top_n=5
                            )

                            if similar_docs:
                                st.markdown(f"**Found {len(similar_docs)} similar documents:**")

                                for sim_doc, score, breakdown in similar_docs:
                                    # Get project name
                                    sim_project = get_project_by_id(sim_doc['project_id'])
                                    sim_project_name = sim_project['name'] if sim_project else "Unknown"

                                    # Score breakdown
                                    score_pct = int(score * 100)
                                    tfidf_pct = int(breakdown['tfidf_score'] * 100)
                                    meta_pct = int(breakdown['metadata_score'] * 100)

                                    # Color based on score
                                    if score >= 0.7:
                                        score_color = "#10b981"  # Green
                                    elif score >= 0.4:
                                        score_color = "#f59e0b"  # Orange
                                    else:
                                        score_color = "#6b7280"  # Gray

                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div style="flex: 1;">
                                                <div style="color: white; font-weight: 600; margin-bottom: 0.3rem;">
                                                    📄 {sim_doc['title']}
                                                </div>
                                                <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">
                                                    📁 {sim_project_name} • v{sim_doc['current_version']} • {sim_doc['updated_at'][:10]}
                                                </div>
                                                <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin-top: 0.3rem;">
                                                    Content: {tfidf_pct}% • Metadata: {meta_pct}%
                                                </div>
                                            </div>
                                            <div style="text-align: center; margin-left: 1rem;">
                                                <div style="background: {score_color}; color: white;
                                                           padding: 0.5rem 1rem; border-radius: 8px;
                                                           font-weight: bold; font-size: 1.1rem;">
                                                    {score_pct}%
                                                </div>
                                                <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem; margin-top: 0.2rem;">
                                                    Match
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # View button
                                    if st.button(f"View Document", key=f"view_similar_{sim_doc['id']}", use_container_width=True):
                                        st.session_state['view_doc_id'] = sim_doc['id']
                                        st.rerun()

                            else:
                                st.info("No similar documents found. This document is unique!")
                        else:
                            st.warning("No content available for similarity matching")

                # Document lineage (Phase 3)
                if st.session_state.get('lineage_doc_id') == doc['id']:
                    st.divider()
                    st.subheader("🌳 Document Lineage")

                    lineage = get_document_lineage(doc['id'])

                    if lineage:
                        # Source document
                        if lineage['source']:
                            source = lineage['source']
                            st.markdown("### 📥 Source Template")
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                <div style="color: white; font-weight: 600; margin-bottom: 0.3rem;">
                                    📄 {source['title']}
                                </div>
                                <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">
                                    Type: {source['doc_type'].upper()} • Version: v{source['current_version']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            if doc.get('adaptation_notes'):
                                st.info(f"**Adaptation Notes:** {doc['adaptation_notes']}")

                        # Derived documents
                        if lineage['derived']:
                            st.markdown("### 📤 Derived Documents")
                            st.markdown(f"**{len(lineage['derived'])} document(s) created from this template:**")

                            for derived in lineage['derived']:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                                            padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                                    <div style="color: white; font-weight: 600; margin-bottom: 0.3rem;">
                                        📄 {derived['title']}
                                    </div>
                                    <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">
                                        Created: {derived['created_at'][:10]} by {derived['created_by']}
                                    </div>
                                    {f'<div style="color: rgba(255,255,255,0.9); font-size: 0.8rem; margin-top: 0.3rem;">{derived.get("adaptation_notes", "")}</div>' if derived.get('adaptation_notes') else ''}
                                </div>
                                """, unsafe_allow_html=True)

                        # Lineage stats
                        if not lineage['source'] and not lineage['derived']:
                            st.info("This document has no lineage. It was created independently.")
                        else:
                            col_x, col_y = st.columns(2)
                            with col_x:
                                st.metric("Lineage Depth", lineage['lineage_depth'])
                            with col_y:
                                st.metric("Derived Documents", len(lineage['derived']))

                    else:
                        st.warning("Unable to load lineage information")
    else:
        st.info("No documents found. Upload your first document to get started!")

# ─────────────────────────────────────────────
# UPLOAD DOCUMENT PAGE
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# TAB 5: UPLOAD DOCUMENT
# ─────────────────────────────────────────────
with tab5:
    st.header("⬆️ Upload New Document")

    # Get projects
    projects = get_projects()

    if not projects:
        st.warning("⚠️ No projects found. Please create a project first.")
        if st.button("Go to Projects"):
            st.session_state['page'] = "📁 Projects"
            st.rerun()
    else:
        with st.form("upload_document_form"):
            st.subheader("Document Information")

            # Project selection
            project_options = {p['name']: p['id'] for p in projects}
            selected_project_name = st.selectbox("Project*", list(project_options.keys()), key="tab5_project_select")
            selected_project_id = project_options[selected_project_name]

            # Document type
            doc_type = st.selectbox("Document Type*", ["BA", "TA", "TC"], key="tab5_doctype_select")

            # Basic info
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Title*", placeholder="e.g., User Login Flow")
            with col2:
                created_by = st.text_input("Created By", value="system", placeholder="Your name")

            description = st.text_area("Description", placeholder="Brief description of the document")

            # Tags and JIRA keys
            col1, col2 = st.columns(2)
            with col1:
                tags_input = st.text_input("Tags (comma separated)", placeholder="e.g., authentication, security")
            with col2:
                jira_keys_input = st.text_input("JIRA Keys (comma separated)", placeholder="e.g., MBA-123, MBA-456")

            # Document content (JSON)
            st.subheader("Document Content")
            st.markdown("Paste your BA/TA/TC JSON content below:")

            content_text = st.text_area(
                "Content (JSON format)*",
                height=300,
                placeholder='{"ekranlar": [...], "backend_islemler": [...]}',
                help="Paste the complete JSON output from the BRD pipeline"
            )

            # Submit
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("📤 Upload Document", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)

            if submit:
                if not title or not content_text:
                    st.error("❌ Please fill in all required fields (Title and Content)")
                else:
                    try:
                        # Parse JSON content
                        content_json = json.loads(content_text)

                        # Parse tags and JIRA keys
                        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                        jira_keys = [key.strip() for key in jira_keys_input.split(",")] if jira_keys_input else []

                        # Create document
                        doc_id = create_document(
                            project_id=selected_project_id,
                            doc_type=doc_type.lower(),
                            title=title,
                            content_json=content_json,
                            description=description,
                            tags=tags,
                            jira_keys=jira_keys,
                            created_by=created_by
                        )

                        st.success(f"✅ Document '{title}' uploaded successfully! (ID: {doc_id})")
                        st.balloons()

                        # Reset form
                        if st.button("Upload Another Document"):
                            st.rerun()

                    except json.JSONDecodeError as e:
                        st.error(f"❌ Invalid JSON format: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error uploading document: {str(e)}")

            if cancel:
                st.rerun()

# ─────────────────────────────────────────────
# CREATE FROM TEMPLATE PAGE (PHASE 3)
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# TAB 4: CREATE FROM TEMPLATE
# ─────────────────────────────────────────────
with tab4:
    st.header("📝 Create from Template")
    st.markdown("**Reuse & Adapt** — Create new documents based on existing templates")

    # Step indicator
    if 'template_step' not in st.session_state:
        st.session_state['template_step'] = 1

    step = st.session_state['template_step']

    # Progress indicator
    progress_cols = st.columns(3)
    with progress_cols[0]:
        st.markdown(f"{'🟢' if step >= 1 else '⚪'} **1. Select Template**")
    with progress_cols[1]:
        st.markdown(f"{'🟢' if step >= 2 else '⚪'} **2. Adapt Content**")
    with progress_cols[2]:
        st.markdown(f"{'🟢' if step >= 3 else '⚪'} **3. Save Document**")

    st.divider()

    # ─── STEP 1: SELECT TEMPLATE ───
    if step == 1:
        st.subheader("Step 1: Select a Template")

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            template_type = st.selectbox("Document Type", ["All Types", "BA", "TA", "TC"], key="tab4_template_type")
            type_filter = None if template_type == "All Types" else template_type.lower()

        with col2:
            projects = get_projects()
            project_options = ["All Projects"] + [p['name'] for p in projects]
            selected_project_name = st.selectbox("Project", project_options, key="tab4_project_filter")
            project_filter = None
            if selected_project_name != "All Projects":
                project_filter = next((p['id'] for p in projects if p['name'] == selected_project_name), None)

        # Get template candidates
        templates = get_template_candidates(
            doc_type=type_filter,
            project_id=project_filter,
            limit=20
        )

        if templates:
            st.markdown(f"**Found {len(templates)} templates:**")

            for template in templates:
                with st.expander(f"📄 {template['title']}", expanded=False):
                    col_a, col_b = st.columns([3, 1])

                    with col_a:
                        st.markdown(f"**Project:** {template.get('project_name', 'Unknown')}")
                        st.markdown(f"**Type:** {template['doc_type'].upper()}")
                        st.markdown(f"**Description:** {template.get('description', 'No description')}")

                        tags = template.get('tags', [])
                        if tags:
                            st.markdown("**Tags:** " + " ".join([f'<span class="tag">{tag}</span>' for tag in tags]), unsafe_allow_html=True)

                        times_used = template.get('times_used_as_template', 0)
                        if times_used > 0:
                            st.markdown(f"✨ **Used as template {times_used} time(s)**")

                    with col_b:
                        if st.button("Use Template", key=f"use_template_{template['id']}", type="primary", use_container_width=True):
                            # Load template with content
                            latest_version = get_latest_version(template['id'])
                            if latest_version:
                                template['content_json'] = latest_version['content_json']
                                st.session_state['selected_template'] = template
                                st.session_state['template_step'] = 2
                                st.rerun()
                            else:
                                st.error("❌ No content available for this template")
        else:
            st.info("No templates found. Upload documents first to use them as templates.")

    # ─── STEP 2: ADAPT CONTENT ───
    elif step == 2:
        if 'selected_template' not in st.session_state:
            st.session_state['template_step'] = 1
            st.rerun()

        template = st.session_state['selected_template']

        st.subheader(f"Step 2: Adapt Template")
        st.markdown(f"**Template:** {template['title']}")

        # Initialize adapter
        if 'adapter' not in st.session_state:
            st.session_state['adapter'] = DocumentAdapter()
            st.session_state['adapted_content'] = template['content_json'].copy()

        # Tabs for different editing modes
        tab1, tab2, tab3 = st.tabs(["📝 Metadata", "✏️ Edit Content (JSON)", "👁️ Preview"])

        # TAB 1: Metadata
        with tab1:
            st.markdown("### Document Metadata")

            # Basic info
            new_title = st.text_input("New Title*", value=f"{template['title']} (Copy)")
            new_description = st.text_area("Description", value=template.get('description', ''))

            col_a, col_b = st.columns(2)
            with col_a:
                # Tags
                template_tags = template.get('tags', [])
                tags_input = st.text_input("Tags (comma separated)", value=", ".join(template_tags))

            with col_b:
                # JIRA keys
                jira_input = st.text_input("JIRA Keys (comma separated)", value="")

            # Adaptation notes
            adaptation_notes = st.text_area(
                "Adaptation Notes",
                value="",
                help="Describe what you changed and why",
                height=100
            )

            st.info("💡 Switch to 'Edit Content' tab to modify the document content")

        # TAB 2: Content Editor
        with tab2:
            st.markdown("### Edit Document Content")

            st.warning("⚠️ Edit the JSON below to adapt the template content. Keep valid JSON format!")

            # JSON editor
            content_str = json.dumps(st.session_state['adapted_content'], indent=2, ensure_ascii=False)

            edited_content = st.text_area(
                "Content JSON",
                value=content_str,
                height=400,
                help="Edit the JSON structure. Changes will be validated when you continue."
            )

            # Validate button
            if st.button("✓ Validate JSON", type="secondary"):
                try:
                    validated = json.loads(edited_content)
                    st.session_state['adapted_content'] = validated
                    st.success("✅ JSON is valid and saved!")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")

            # Quick tips
            with st.expander("💡 Quick Editing Tips"):
                st.markdown("""
                **Common Edits:**
                - Change text values: `"old value"` → `"new value"`
                - Add array items: Add comma and new item in `[...]`
                - Remove items: Delete the line (keep commas valid)
                - Change numbers: Just update the number value

                **JSON Rules:**
                - Strings in double quotes: `"text"`
                - Numbers without quotes: `123`
                - Booleans: `true` or `false`
                - Arrays: `["item1", "item2"]`
                - Objects: `{"key": "value"}`
                - Use commas between items (not after last item)

                **Example:**
                ```json
                {
                  "ekran_adi": "Login Screen",  ← Change this
                  "fields": [
                    {"name": "email"},  ← Modify fields
                    {"name": "password"}
                  ]
                }
                ```
                """)

        # TAB 3: Preview
        with tab3:
            st.markdown("### Preview")

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("**Original Template:**")
                st.json(template['content_json'])

            with col_right:
                st.markdown("**Adapted Content:**")
                st.json(st.session_state['adapted_content'])

            # Show differences
            st.divider()
            st.markdown("### 🔍 Changes Summary")

            original_str = json.dumps(template['content_json'], sort_keys=True)
            adapted_str = json.dumps(st.session_state['adapted_content'], sort_keys=True)

            if original_str == adapted_str:
                st.info("📝 No content changes yet (only metadata will be different)")
            else:
                st.success("✅ Content has been modified")

                # Simple change detection
                original_keys = set(str(template['content_json']).split())
                adapted_keys = set(str(st.session_state['adapted_content']).split())

                added = len(adapted_keys - original_keys)
                removed = len(original_keys - adapted_keys)

                if added > 0:
                    st.markdown(f"- ➕ ~{added} tokens added")
                if removed > 0:
                    st.markdown(f"- ➖ ~{removed} tokens removed")

        # Action buttons
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("⬅️ Back to Templates", use_container_width=True):
                st.session_state['template_step'] = 1
                st.rerun()

        with col_b:
            if st.button("🔄 Reset to Template", use_container_width=True):
                st.session_state['adapted_content'] = template['content_json'].copy()
                st.session_state['adapter'] = DocumentAdapter()
                st.rerun()

        with col_c:
            if st.button("➡️ Continue to Save", type="primary", use_container_width=True):
                if not new_title:
                    st.error("❌ Please provide a title")
                else:
                    # Validate JSON one more time from text area
                    try:
                        if edited_content:
                            validated = json.loads(edited_content)
                            st.session_state['adapted_content'] = validated
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Invalid JSON in content editor: {str(e)}")
                        st.stop()

                    st.session_state['new_title'] = new_title
                    st.session_state['new_description'] = new_description
                    st.session_state['new_tags'] = [t.strip() for t in tags_input.split(",")] if tags_input else []
                    st.session_state['new_jira_keys'] = [k.strip() for k in jira_input.split(",")] if jira_input else []
                    st.session_state['adaptation_notes'] = adaptation_notes
                    st.session_state['template_step'] = 3
                    st.rerun()

    # ─── STEP 3: SAVE DOCUMENT ───
    elif step == 3:
        if 'selected_template' not in st.session_state:
            st.session_state['template_step'] = 1
            st.rerun()

        template = st.session_state['selected_template']

        st.subheader("Step 3: Review & Save")

        # Summary
        st.markdown("### Document Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Source Template:**")
            st.markdown(f"- Title: {template['title']}")
            st.markdown(f"- Type: {template['doc_type'].upper()}")
            st.markdown(f"- Project: {template.get('project_name', 'Unknown')}")

        with col2:
            st.markdown("**New Document:**")
            st.markdown(f"- Title: {st.session_state.get('new_title')}")
            st.markdown(f"- Tags: {', '.join(st.session_state.get('new_tags', []))}")
            st.markdown(f"- JIRA: {', '.join(st.session_state.get('new_jira_keys', []))}")

        if st.session_state.get('adaptation_notes'):
            st.markdown("**Adaptation Notes:**")
            st.info(st.session_state['adaptation_notes'])

        st.divider()

        # Action buttons
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("⬅️ Back to Adapt", use_container_width=True):
                st.session_state['template_step'] = 2
                st.rerun()

        with col_b:
            if st.button("💾 Save Document", type="primary", use_container_width=True):
                try:
                    # Create adapted document
                    doc_id = create_document(
                        project_id=template['project_id'],
                        doc_type=template['doc_type'],
                        title=st.session_state['new_title'],
                        content_json=st.session_state['adapted_content'],
                        description=st.session_state.get('new_description', ''),
                        tags=st.session_state.get('new_tags', []),
                        jira_keys=st.session_state.get('new_jira_keys', []),
                        created_by="user",
                        source_document_id=template['id'],
                        adaptation_notes=st.session_state.get('adaptation_notes', '')
                    )

                    st.success(f"✅ Document created successfully! (ID: {doc_id})")
                    st.balloons()

                    # Clear session state
                    for key in ['template_step', 'selected_template', 'adapter', 'adapted_content',
                               'new_title', 'new_description', 'new_tags', 'new_jira_keys', 'adaptation_notes']:
                        if key in st.session_state:
                            del st.session_state[key]

                    # Show lineage
                    st.markdown("### 🌳 Document Lineage")
                    st.markdown(f"**Derived from:** {template['title']} (ID: {template['id']})")

                    if st.button("View New Document"):
                        st.session_state['view_doc_id'] = doc_id
                        st.session_state['template_step'] = 1
                        st.rerun()

                    if st.button("Create Another from Template"):
                        st.session_state['template_step'] = 1
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating document: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>✅ Phase 1:</strong> Document Repository — Storage, organization, and retrieval<br>
    <strong>✅ Phase 2:</strong> Smart Matching & Recommendations — Hybrid TF-IDF + Metadata matching<br>
    <strong>✅ Phase 3:</strong> Reuse & Adapt Workflow — Template-based document creation with lineage tracking
</div>
""", unsafe_allow_html=True)
