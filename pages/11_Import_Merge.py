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
import os
from datetime import datetime
from data.database import (
    create_document, get_projects, get_documents_with_content,
    get_document_by_id, get_latest_version, create_document_version,
    get_recent_pipeline_runs, get_pipeline_run_outputs
)
from pipeline.document_matching import find_similar
from pipeline.document_adaptation import DocumentAdapter
from pipeline.document_parser_v2 import parse_text_to_json
from agents.ai_client import call_gemini

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
        st.info("💡 Select a completed pipeline run to import BA/TA/TC outputs")

        # Get recent pipeline runs
        with st.spinner("Loading pipeline runs..."):
            pipeline_runs = get_recent_pipeline_runs(limit=50)

        if not pipeline_runs:
            st.warning("No pipeline runs found. Run BRD Pipeline first!")
        else:
            # Filter to completed runs only
            completed_runs = [r for r in pipeline_runs if r.get('status') == 'completed']

            if not completed_runs:
                st.warning("No completed pipeline runs found. Complete a BRD Pipeline run first!")
            else:
                # Show pipeline runs in selectbox
                run_options = {}
                for run in completed_runs:
                    run_id = run['id']
                    project = run.get('project_name', 'Unknown')
                    jira = run.get('jira_key', 'N/A')
                    created = run.get('created_at', '')[:16]  # YYYY-MM-DD HH:MM
                    label = f"Run #{run_id}: {project} ({jira}) - {created}"
                    run_options[label] = run

                selected_label = st.selectbox(
                    "Select Pipeline Run",
                    options=list(run_options.keys()),
                    help="Choose a completed pipeline run"
                )

                if selected_label:
                    selected_run = run_options[selected_label]
                    run_id = selected_run['id']

                    # Show run details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("BA Score", f"{selected_run.get('ba_score', 0):.0%}")
                    with col2:
                        st.metric("TA Score", f"{selected_run.get('ta_score', 0):.0%}")
                    with col3:
                        st.metric("TC Score", f"{selected_run.get('tc_score', 0):.0%}")

                    st.divider()

                    # Get outputs for this run
                    with st.spinner("Loading outputs..."):
                        outputs = get_pipeline_run_outputs(run_id)

                    if not outputs:
                        st.warning("No outputs found for this pipeline run")
                    else:
                        # Group outputs by stage, get latest revision
                        stage_outputs = {}
                        for output in outputs:
                            stage = output.get('stage')
                            revision = output.get('revision_number', 0)

                            if stage not in stage_outputs or revision > stage_outputs[stage].get('revision_number', 0):
                                stage_outputs[stage] = output

                        # Show available stages
                        st.markdown("### Available Outputs")

                        available_stages = list(stage_outputs.keys())
                        selected_stage = st.radio(
                            "Select output to import",
                            options=available_stages,
                            format_func=lambda x: f"{x.upper()} (rev {stage_outputs[x].get('revision_number', 0)})",
                            horizontal=True
                        )

                        if selected_stage:
                            output = stage_outputs[selected_stage]

                            # Show preview
                            st.markdown(f"**{selected_stage.upper()} Output** (Revision {output.get('revision_number', 0)})")

                            try:
                                content_json = json.loads(output.get('content_json', '{}'))
                                st.json(content_json)
                            except:
                                st.error("Invalid JSON in pipeline output")
                                content_json = None

                            # Title input
                            default_title = f"{selected_run.get('project_name', 'Document')} - {selected_stage.upper()}"
                            title = st.text_input("Document Title*", value=default_title)

                            if st.button("➡️ Import from Pipeline", type="primary"):
                                if not title or not content_json:
                                    st.error("❌ Cannot import: missing title or invalid content")
                                else:
                                    # Save to session state
                                    st.session_state['imported_doc'] = {
                                        'title': title,
                                        'doc_type': selected_stage.lower(),
                                        'content_json': content_json,
                                        'import_method': 'pipeline',
                                        'pipeline_run_id': run_id
                                    }

                                    st.success(f"✅ {selected_stage.upper()} imported from pipeline run #{run_id}!")
                                    st.session_state['import_step'] = 2
                                    st.rerun()

    elif import_method == "📝 Paste Text (AI Parse)":
        st.markdown("### Paste Text Document")

        # Let user choose parsing method
        parse_method = st.radio(
            "Choose parsing method:",
            ["⚡ Rule-based (Fast, Free)", "🤖 AI-powered (Flexible, Requires API Key)"],
            help="Rule-based parser works best with structured documents with clear headings"
        )

        if parse_method.startswith("⚡"):
            st.info("💡 Rule-based parser analyzes headings and structure - works best with organized documents")
        else:
            st.info("💡 AI parser understands context and handles unstructured text better")

        text_input = st.text_area(
            "Document Text",
            height=300,
            placeholder="Paste your BA/TA/TC document here...\n\nFor best results with rule-based parsing, use clear headings:\n- Ekranlar / Screens\n- Backend / API\n- Güvenlik / Security\n- Test Senaryoları / Test Scenarios",
            help="Paste text content from Word, Confluence, or any source"
        )

        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", ["BA", "TA", "TC"], key="text_doc_type")
        with col2:
            title = st.text_input("Document Title*", placeholder="e.g., Face ID Login Analysis", key="text_title")

        # Choose button based on parse method
        if parse_method.startswith("⚡"):
            parse_button_label = "⚡ Parse with Rules"
        else:
            parse_button_label = "🤖 Parse with AI"

        if st.button(parse_button_label, type="primary"):
            if not text_input or not title:
                st.error("❌ Please provide both text and title")
            else:
                # RULE-BASED PARSING
                if parse_method.startswith("⚡"):
                    with st.spinner("⚡ Analyzing document structure..."):
                        try:
                            # Use rule-based parser
                            parsed_json = parse_text_to_json(text_input, doc_type.lower())

                            # Check if parsing produced meaningful results
                            has_content = False
                            for key, value in parsed_json.items():
                                if isinstance(value, list) and len(value) > 0:
                                    has_content = True
                                    break

                            if not has_content:
                                st.warning("⚠️ Rule-based parser couldn't find structured content. Try:\n"
                                         "1. Using clear section headings (Ekranlar, Backend, etc.)\n"
                                         "2. Switching to AI-powered parsing")
                            else:
                                st.success("✅ Document parsed successfully with rule-based parser!")

                                # Show preview
                                with st.expander("📋 Parsed JSON Preview", expanded=True):
                                    st.json(parsed_json)

                                # Show parsing stats
                                stats = []
                                for key, value in parsed_json.items():
                                    if isinstance(value, list):
                                        stats.append(f"{key}: {len(value)} items")

                                if stats:
                                    st.caption("📊 " + " | ".join(stats))

                                # Save to session state
                                st.session_state['imported_doc'] = {
                                    'title': title,
                                    'doc_type': doc_type.lower(),
                                    'content_json': parsed_json,
                                    'import_method': 'rule_parse'
                                }

                                st.session_state['import_step'] = 2
                                st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error parsing document: {str(e)}")
                            st.info("💡 Try AI-powered parsing for better flexibility")

                # AI PARSING
                else:
                    # Check API key
                    gemini_key = st.session_state.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
                    if not gemini_key:
                        st.error("❌ Gemini API key not found. Please set it in Settings.")
                        st.info("💡 Or try rule-based parsing (free, no API key needed)")
                    else:
                        with st.spinner("🤖 AI is parsing your document..."):
                            try:
                                # Build parsing prompt based on document type
                                if doc_type == "BA":
                                    system_prompt = """You are a Business Analyst documentation expert.
Parse the given text and convert it into a structured BA (Business Analysis) JSON format.

The JSON structure should follow this schema:
{
  "ekranlar": [
    {
      "ekran_adi": "Screen name",
      "aciklama": "Screen description",
      "fields": [
        {"name": "field_name", "type": "field_type", "required": true/false, "description": "..."}
      ],
      "actions": [
        {"button": "Button text", "action": "action_name"}
      ]
    }
  ],
  "backend_islemler": [
    {
      "islem": "Operation name",
      "aciklama": "Operation description",
      "endpoint": "/api/path",
      "method": "GET/POST/PUT/DELETE",
      "request": {...},
      "response": {...}
    }
  ],
  "guvenlik_gereksinimleri": [
    {"gereksinim": "Requirement", "aciklama": "Description"}
  ],
  "test_senaryolari": [
    {"senaryo": "Scenario name", "adimlar": ["Step 1", "Step 2", ...]}
  ]
}

Return ONLY valid JSON, no markdown formatting or explanations."""

                                elif doc_type == "TA":
                                    system_prompt = """You are a Technical Architect documentation expert.
Parse the given text and convert it into a structured TA (Technical Analysis) JSON format.

The JSON structure should follow this schema:
{
  "servisler": [
    {
      "servis_adi": "Service name",
      "aciklama": "Service description",
      "teknolojiler": ["tech1", "tech2"],
      "endpoints": [
        {"path": "/api/path", "method": "GET/POST/PUT/DELETE", "aciklama": "..."}
      ]
    }
  ],
  "veri_modeli": [
    {
      "entity": "Entity name",
      "fields": [
        {"name": "field_name", "type": "data_type", "required": true/false}
      ]
    }
  ],
  "teknolojik_gereksinimler": [
    {"kategori": "Category", "gereksinim": "Requirement", "aciklama": "Description"}
  ]
}

Return ONLY valid JSON, no markdown formatting or explanations."""

                                else:  # TC
                                    system_prompt = """You are a QA Test Case documentation expert.
Parse the given text and convert it into a structured TC (Test Cases) JSON format.

The JSON structure should follow this schema:
{
  "test_cases": [
    {
      "test_id": "TC-001",
      "test_name": "Test name",
      "description": "Test description",
      "priority": "High/Medium/Low",
      "steps": [
        {"step": 1, "action": "Action to perform", "expected": "Expected result"}
      ],
      "test_data": {...},
      "prerequisites": ["prerequisite 1", ...]
    }
  ],
  "test_senaryolari": [
    {"senaryo": "Scenario name", "test_cases": ["TC-001", "TC-002"]}
  ]
}

Return ONLY valid JSON, no markdown formatting or explanations."""

                                # Call AI
                                result = call_gemini(
                                    system_prompt=system_prompt,
                                    user_content=f"Parse this {doc_type} document:\n\n{text_input}",
                                    api_key=gemini_key,
                                    max_tokens=8000
                                )

                                # Check if we got valid JSON
                                if result.get('error'):
                                    st.error(f"❌ AI parsing error: {result['error']}")
                                elif result.get('content'):
                                    parsed_json = result['content']

                                    st.success("✅ Document parsed successfully with AI!")

                                    # Show preview
                                    with st.expander("📋 Parsed JSON Preview", expanded=True):
                                        st.json(parsed_json)

                                    # Save to session state
                                    st.session_state['imported_doc'] = {
                                        'title': title,
                                        'doc_type': doc_type.lower(),
                                        'content_json': parsed_json,
                                        'import_method': 'ai_parse'
                                    }

                                    st.session_state['import_step'] = 2
                                    st.rerun()
                                else:
                                    st.error("❌ AI returned empty response")

                            except Exception as e:
                                st.error(f"❌ Error parsing document: {str(e)}")
                                st.exception(e)
                                st.info("💡 Try rule-based parsing as alternative")

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
