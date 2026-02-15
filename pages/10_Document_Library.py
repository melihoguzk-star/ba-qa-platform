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
    get_document_stats
)

st.set_page_config(page_title="Document Library", page_icon="📚", layout="wide")

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

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["📊 Dashboard", "📁 Projects", "📄 Documents", "⬆️ Upload Document"],
        label_visibility="collapsed"
    )

    st.divider()

    # Quick stats
    stats = get_document_stats()
    st.metric("Total Projects", stats['total_projects'])
    st.metric("Total Documents", stats['total_documents'])

    for type_stat in stats['by_type']:
        type_label = {"ba": "BA", "ta": "TA", "tc": "TC"}.get(type_stat['doc_type'], type_stat['doc_type'])
        st.metric(f"{type_label} Documents", type_stat['c'])


# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────
if page == "📊 Dashboard":
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
elif page == "📁 Projects":
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
    search = st.text_input("🔍 Search Projects", placeholder="Search by name or description")

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
elif page == "📄 Documents":
    st.header("📄 Documents")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        projects = get_projects()
        project_options = ["All Projects"] + [p['name'] for p in projects]
        selected_project_name = st.selectbox("Project", project_options)

        selected_project_id = None
        if selected_project_name != "All Projects":
            selected_project_id = next((p['id'] for p in projects if p['name'] == selected_project_name), None)

    with col2:
        doc_type_filter = st.selectbox("Document Type", ["All Types", "BA", "TA", "TC"])
        doc_type = None
        if doc_type_filter != "All Types":
            doc_type = doc_type_filter.lower()

    with col3:
        search = st.text_input("🔍 Search", placeholder="Search documents...")

    # Get documents
    documents = get_documents(
        project_id=selected_project_id,
        doc_type=doc_type,
        search=search
    )

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

            with st.expander(f"📄 {doc['title']}", expanded=False):
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

                with col_b:
                    if st.button("View Content", key=f"view_{doc['id']}", use_container_width=True):
                        st.session_state['view_doc_id'] = doc['id']

                    if st.button("Version History", key=f"history_{doc['id']}", use_container_width=True):
                        st.session_state['history_doc_id'] = doc['id']

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
    else:
        st.info("No documents found. Upload your first document to get started!")

# ─────────────────────────────────────────────
# UPLOAD DOCUMENT PAGE
# ─────────────────────────────────────────────
elif page == "⬆️ Upload Document":
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
            selected_project_name = st.selectbox("Project*", list(project_options.keys()))
            selected_project_id = project_options[selected_project_name]

            # Document type
            doc_type = st.selectbox("Document Type*", ["BA", "TA", "TC"])

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

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>Phase 1: Document Repository</strong> — Storage, organization, and retrieval<br>
    Coming in Phase 2: Smart Matching & Recommendations<br>
    Coming in Phase 3: Incremental Updates & Evolution
</div>
""", unsafe_allow_html=True)
