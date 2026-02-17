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
import requests
from datetime import datetime
from data.database import (
    create_document, get_projects, get_documents_with_content,
    get_document_by_id, get_latest_version, create_document_version,
    get_recent_pipeline_runs, get_pipeline_run_outputs
)
from pipeline.document_matching import find_similar
from pipeline.document_adaptation import DocumentAdapter
from pipeline.document_parser_v2 import parse_text_to_json
from pipeline.document_reader import read_docx, read_document_from_drive, export_google_doc_as_text, extract_google_drive_file_id
from pipeline.google_drive_client import GoogleDriveClient
from agents.ai_client import call_gemini
from components.sidebar import render_custom_sidebar

st.set_page_config(page_title="Import & Merge", page_icon="📥", layout="wide")

# Render custom sidebar
render_custom_sidebar(active_page="import_merge")

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
        ["📋 Paste JSON", "📄 From BRD Pipeline", "📝 Paste Text (AI Parse)",
         "📎 Upload Word Document", "☁️ Google Drive (Public)", "🔗 Google Drive (n8n)"],
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
                                         "1. Using clear headings that end with ':' (e.g., 'Screens:', 'API:')\n"
                                         "2. Organizing content with bullet points under headings\n"
                                         "3. Switching to AI-powered parsing for unstructured text")
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

    elif import_method == "📎 Upload Word Document":
        st.markdown("### Doküman Yükle")
        st.info("BA (.docx) veya Test Case (.xlsx) dosyaları otomatik algılanır. Tek veya birden fazla dosya seçebilirsiniz.")

        uploaded_files = st.file_uploader(
            "BA (.docx) veya Test Case (.xlsx) dosyası seç",
            type=['docx', 'xlsx'],
            accept_multiple_files=True,
            help="Birden fazla dosya seçerek toplu import yapabilirsiniz.",
            key="word_uploader"
        )

        if uploaded_files:
            from pipeline.docx_import_orchestrator import DocxImportOrchestrator, detect_document_type

            # ----------------------------------------------------------------
            # Tek dosya
            # ----------------------------------------------------------------
            if len(uploaded_files) == 1:
                uploaded_file = uploaded_files[0]
                file_bytes = uploaded_file.read()

                doc_info = detect_document_type(file_bytes, uploaded_file.name)

                st.success(f"{uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB) — "
                           f"Tip: **{doc_info['template']}** / Güven: **{doc_info['confidence']:.0%}**")

                # ---- TC XLSX yolu ----
                if doc_info["template"] == "loodos_test_case":
                    cache_key = f"tc_result_{uploaded_file.name}_{uploaded_file.size}"
                    if cache_key not in st.session_state:
                        with st.spinner("Test Case Excel analiz ediliyor..."):
                            from pipeline.tc_xlsx_reader import read_tc_xlsx
                            from pipeline.tc_xlsx_parser import TCExcelParser
                            raw = read_tc_xlsx(file_bytes)
                            parsed = TCExcelParser(raw).parse()
                            st.session_state[cache_key] = parsed
                    else:
                        parsed = st.session_state[cache_key]

                    summary = parsed["summary"]
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Sheet", summary["total_sheets"])
                    col2.metric("Test Case", summary["total_test_cases"])
                    col3.metric("Güven", f"{doc_info['confidence']:.0%}")
                    col4.metric("Uyarı", len(parsed.get("warnings", [])))

                    if parsed.get("warnings"):
                        with st.expander("Uyarılar"):
                            for w in parsed["warnings"]:
                                st.warning(w)

                    tab_sheets, tab_summary, tab_detail, tab_json = st.tabs([
                        "Sheet Bazlı", "Özet", "Detaylı TC", "JSON"
                    ])

                    with tab_sheets:
                        import pandas as pd
                        for sheet in parsed["sheets"]:
                            tc_count = sheet["stats"]["total_rows"]
                            with st.expander(f"{sheet['sheet_name']} ({tc_count} TC)", expanded=False):
                                if sheet["test_cases"]:
                                    df = pd.DataFrame(sheet["test_cases"])
                                    display_cols = ["test_case_id", "testcase_name", "priority",
                                                    "channel", "testcase_type", "test_area"]
                                    existing = [c for c in display_cols if c in df.columns]
                                    st.dataframe(df[existing], use_container_width=True)
                                else:
                                    st.info("Bu sheet'te test case bulunamadı.")

                    with tab_summary:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("**Priority Dağılımı:**")
                            for k, v in summary.get("by_priority", {}).items():
                                st.write(f"- {k}: {v}")
                        with c2:
                            st.write("**Channel Dağılımı:**")
                            for k, v in summary.get("by_channel", {}).items():
                                st.write(f"- {k}: {v}")
                        if summary.get("by_type"):
                            st.write("**Tip Dağılımı:**")
                            for k, v in summary["by_type"].items():
                                st.write(f"- {k}: {v}")

                    with tab_detail:
                        search_q = st.text_input("TC Ara (isim veya ID)", key="tc_search_single")
                        all_tcs = [tc for s in parsed["sheets"] for tc in s["test_cases"]]
                        if search_q:
                            sq = search_q.lower()
                            all_tcs = [tc for tc in all_tcs
                                       if sq in (tc.get("testcase_name") or "").lower()
                                       or sq in (tc.get("test_case_id") or "").lower()]
                        st.caption(f"{len(all_tcs)} TC gösteriliyor")
                        for tc in all_tcs[:50]:
                            with st.expander(f"{tc.get('test_case_id','')} — {tc.get('testcase_name','')}", expanded=False):
                                c1, c2, c3 = st.columns(3)
                                c1.write(f"**Priority:** {tc.get('priority','—')}")
                                c2.write(f"**Channel:** {tc.get('channel','—')}")
                                c3.write(f"**Tip:** {tc.get('testcase_type','—')}")
                                if tc.get("test_steps"):
                                    st.write("**Adımlar:**")
                                    st.text(tc["test_steps"])
                                if tc.get("expected_result"):
                                    st.write("**Beklenen:** " + tc["expected_result"][:200])
                        if len(all_tcs) > 50:
                            st.caption(f"... {len(all_tcs) - 50} TC daha (arama yaparak filtreleyin)")

                    with tab_json:
                        st.json(parsed)

                    st.markdown("---")
                    tc_title = st.text_input(
                        "Doküman Başlığı *",
                        value=uploaded_file.name.replace('.xlsx', ''),
                        key="tc_title_single"
                    )
                    if st.button("Import Test Case", type="primary", key="tc_import_single_btn"):
                        if not tc_title.strip():
                            st.error("Lütfen bir başlık girin.")
                        else:
                            projects = get_projects()
                            project_id = projects[0]['id'] if projects else None
                            with st.spinner("Kaydediliyor ve ChromaDB'ye index ediliyor..."):
                                from pipeline.tc_xlsx_db import save_tc_import
                                result = save_tc_import(
                                    parsed_data=parsed,
                                    source_file=uploaded_file.name,
                                    project_id=project_id,
                                    title=tc_title.strip(),
                                )
                            if result["errors"]:
                                for e in result["errors"]:
                                    st.warning(e)
                            if result["imported"]:
                                st.success(f"'{tc_title}' import edildi! (doc_id={result['doc_id']}, {result['chunks']} chunk index'lendi)")
                            elif result["updated"]:
                                st.info(f"'{tc_title}' mevcut kayıt güncellendi! (doc_id={result['doc_id']}, {result['chunks']} chunk)")
                            elif not result["errors"]:
                                st.warning("İşlem tamamlanamadı.")

                # ---- BA DOCX yolu (mevcut adım bazlı akış) ----
                else:
                    cache_key = f"docx_result_{uploaded_file.name}_{uploaded_file.size}"
                    if cache_key not in st.session_state:
                        with st.spinner("Doküman analiz ediliyor..."):
                            result = DocxImportOrchestrator().import_docx(file_bytes)
                            st.session_state[cache_key] = result
                    else:
                        result = st.session_state[cache_key]

                    if result["success"]:
                        st.markdown("#### Analiz Sonucu")
                        col1, col2, col3, col4 = st.columns(4)
                        template_label = {
                            "loodos_ba_bullet": "Loodos BA (Bullet)",
                            "loodos_ba_table":  "Loodos BA (Tablo)",
                            "generic":          "Genel Doküman",
                        }.get(result["template"], result["template"])
                        col1.metric("Sablon", template_label)
                        col2.metric("Guven", f"{result['confidence']:.0%}")
                        col3.metric("Ekranlar", result["stats"]["screens"])
                        col4.metric("Is Kurallari", result["stats"]["list_items"])

                        for w in result["warnings"]:
                            st.warning(w)

                        tab_screens, tab_rules, tab_links, tab_json = st.tabs([
                            "Ekranlar", "Is Kurallari", "Linkler", "JSON"
                        ])
                        ekranlar = result["content_json"].get("ekranlar", [])

                        with tab_screens:
                            if ekranlar:
                                for ekran in ekranlar:
                                    rule_count = sum(
                                        len(ia.get("kurallar", []))
                                        for ia in ekran.get("is_akislari", [])
                                    )
                                    with st.expander(
                                        f"{ekran['ekran_adi']}  —  {rule_count} kural",
                                        expanded=False
                                    ):
                                        if ekran.get("aciklama"):
                                            st.caption(ekran["aciklama"])
                                        for ia in ekran.get("is_akislari", []):
                                            st.markdown(f"**{ia['baslik']}**")
                                            for k in ia.get("kurallar", [])[:5]:
                                                indent = "&nbsp;" * (k.get("level", 0) * 4)
                                                st.markdown(
                                                    f"{indent}- {k['kural'][:140]}",
                                                    unsafe_allow_html=True
                                                )
                                            if len(ia.get("kurallar", [])) > 5:
                                                st.caption(f"... +{len(ia['kurallar']) - 5} kural daha")
                            else:
                                st.info("Ekran bulunamadı. Dokümanın 'Mobil Uygulama Gereksinimleri' bölümü var mı?")

                        with tab_rules:
                            total_rules = sum(
                                len(ia.get("kurallar", []))
                                for e in ekranlar
                                for ia in e.get("is_akislari", [])
                            )
                            st.metric("Toplam Kural", total_rules)
                            for ekran in ekranlar:
                                for ia in ekran.get("is_akislari", []):
                                    if ia.get("kurallar"):
                                        st.markdown(f"**{ekran['ekran_adi']} — {ia['baslik']}**")
                                        for k in ia["kurallar"][:3]:
                                            st.markdown(f"- {k['kural'][:120]}")
                                        if len(ia["kurallar"]) > 3:
                                            st.caption(f"  ... +{len(ia['kurallar']) - 3} kural")

                        with tab_links:
                            linkler = result["content_json"].get("linkler", {})
                            for kategori, urls in linkler.items():
                                if urls:
                                    st.markdown(f"**{kategori.upper()} ({len(urls)})**")
                                    for url in urls:
                                        st.markdown(f"- [{url[:80]}]({url})")

                        with tab_json:
                            st.json(result["content_json"])

                        st.markdown("---")
                        col_title, col_type = st.columns([3, 1])
                        with col_title:
                            title = st.text_input(
                                "Dokuman Basligi *",
                                value=uploaded_file.name.replace('.docx', ''),
                                key="word_title"
                            )
                        with col_type:
                            st.selectbox("Tip", ["BA"], key="word_doc_type", disabled=True)

                        if st.button("Import & Devam Et", type="primary", key="word_import_btn"):
                            if not title.strip():
                                st.error("Lütfen bir başlık girin.")
                            else:
                                st.session_state['imported_doc'] = {
                                    'title':         title.strip(),
                                    'doc_type':      'ba',
                                    'content_json':  result["content_json"],
                                    'import_method': 'docx_structured',
                                }
                                st.session_state['import_step'] = 2
                                st.rerun()

                    else:
                        st.error("Doküman parse edilemedi. Düşük confidence veya desteklenmeyen format.")
                        st.metric("Güven Skoru", f"{result['confidence']:.0%}")
                        with st.expander("Hata Detayları"):
                            st.json(result)

            # ----------------------------------------------------------------
            # Çoklu dosya → her biri ayrı parse edilir, toplu import
            # ----------------------------------------------------------------
            else:
                st.info(f"{len(uploaded_files)} dosya seçildi. Her biri ayrı doküman olarak import edilecek.")

                from pipeline.tc_xlsx_reader import read_tc_xlsx
                from pipeline.tc_xlsx_parser import TCExcelParser

                file_results = []
                total_tc_count = 0

                for uf in uploaded_files:
                    file_bytes = uf.read()
                    doc_info = detect_document_type(file_bytes, uf.name)
                    cache_key = f"file_result_{uf.name}_{uf.size}"

                    if cache_key not in st.session_state:
                        with st.spinner(f"{uf.name} analiz ediliyor..."):
                            if doc_info["template"] == "loodos_test_case":
                                raw = read_tc_xlsx(file_bytes)
                                parsed = TCExcelParser(raw).parse()
                                st.session_state[cache_key] = {"type": "tc", "data": parsed, "success": True}
                            else:
                                result = DocxImportOrchestrator().import_docx(file_bytes)
                                st.session_state[cache_key] = {"type": "ba", "data": result, "success": result["success"]}
                    entry = st.session_state[cache_key]
                    file_results.append((uf, doc_info, entry))

                    if entry["type"] == "tc":
                        total_tc_count += entry["data"]["summary"]["total_test_cases"]

                # ---- Her dosya için özet kart ----
                st.markdown("---")
                titles = {}
                for i, (uf, doc_info, entry) in enumerate(file_results):
                    icon = "✅" if entry["success"] else "❌"
                    with st.expander(
                        f"{icon} {uf.name} ({uf.size / 1024:.1f} KB)",
                        expanded=True
                    ):
                        if entry["success"]:
                            if entry["type"] == "tc":
                                parsed = entry["data"]
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Tip", "Test Case XLSX")
                                col2.metric("Sheet", parsed["summary"]["total_sheets"])
                                col3.metric("TC", parsed["summary"]["total_test_cases"])
                            else:
                                result = entry["data"]
                                col1, col2, col3, col4 = st.columns(4)
                                template_label = {
                                    "loodos_ba_bullet": "Loodos BA (Bullet)",
                                    "loodos_ba_table":  "Loodos BA (Tablo)",
                                    "generic":          "Genel Doküman",
                                }.get(result["template"], result["template"])
                                col1.metric("Tip", template_label)
                                col2.metric("Güven", f"{result['confidence']:.0%}")
                                col3.metric("Ekranlar", result["stats"]["screens"])
                                col4.metric("Kurallar", result["stats"]["list_items"])
                        else:
                            st.error(f"Parse başarısız — güven: {doc_info['confidence']:.0%}")

                        ext = uf.name.rsplit('.', 1)[-1].lower()
                        titles[i] = st.text_input(
                            "Başlık",
                            value=uf.name.replace(f'.{ext}', ''),
                            key=f"bulk_title_{i}"
                        )

                # ---- Bulk import alt bar ----
                st.divider()
                info_parts = [f"{len(uploaded_files)} dosya"]
                if total_tc_count:
                    info_parts.append(f"toplam {total_tc_count} test case")
                st.info(" • ".join(info_parts))

                if st.button("Tumunu Import Et", type="primary", key="bulk_import_all_btn"):
                    projects = get_projects()
                    project_id = projects[0]['id'] if projects else None
                    progress = st.progress(0)
                    imported_count = 0
                    updated_count = 0
                    total_chunks = 0
                    error_msgs = []

                    from pipeline.tc_xlsx_db import save_tc_import

                    for i, (uf, doc_info, entry) in enumerate(file_results):
                        if not entry["success"]:
                            error_msgs.append(f"{uf.name}: parse başarısız, atlandı")
                            progress.progress((i + 1) / len(file_results))
                            continue

                        title = (titles.get(i) or uf.name).strip()
                        try:
                            if entry["type"] == "tc":
                                r = save_tc_import(
                                    parsed_data=entry["data"],
                                    source_file=uf.name,
                                    project_id=project_id,
                                    title=title,
                                )
                                imported_count += r["imported"]
                                updated_count  += r["updated"]
                                total_chunks   += r["chunks"]
                                for e in r["errors"]:
                                    error_msgs.append(f"{uf.name}: {e}")
                            else:
                                create_document(
                                    project_id=project_id,
                                    doc_type='ba',
                                    title=title,
                                    content_json=entry["data"]["content_json"],
                                    description=f"DOCX import: {uf.name}",
                                    tags=['docx_import'],
                                    created_by='docx_upload',
                                )
                                imported_count += 1
                        except Exception as e:
                            error_msgs.append(f"{uf.name}: {e}")
                        progress.progress((i + 1) / len(file_results))

                    if imported_count:
                        st.success(f"{imported_count} yeni doküman import edildi! ({total_chunks} chunk ChromaDB'ye eklendi)")
                    if updated_count:
                        st.info(f"{updated_count} mevcut doküman güncellendi.")
                    for msg in error_msgs:
                        st.error(msg)

    elif import_method == "☁️ Google Drive (Public)":
        st.markdown("### Import from Google Drive (Public)")
        st.info("💡 For public/shared documents - Paste a Google Drive share link")

        st.markdown("""
        **How to get a shareable link:**
        1. Open your document in Google Drive
        2. Click "Share" button
        3. Change access to "Anyone with the link can view"
        4. Copy the link and paste below
        """)

        drive_url = st.text_input(
            "Google Drive Link",
            placeholder="https://drive.google.com/file/d/.../view or https://docs.google.com/document/d/.../edit",
            help="Paste a Google Drive or Google Docs share link"
        )

        if drive_url:
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox("Document Type", ["BA", "TA", "TC"], key="drive_doc_type")
            with col2:
                title = st.text_input("Document Title*", placeholder="e.g., Face ID Login Analysis", key="drive_title")

            # Choose parsing method
            parse_method = st.radio(
                "Choose parsing method:",
                ["⚡ Rule-based (Fast, Free)", "🤖 AI-powered (Flexible, Requires API Key)"],
                help="Rule-based parser works best with structured documents",
                key="drive_parse_method"
            )

            if st.button("☁️ Download & Parse", type="primary"):
                if not title:
                    st.error("❌ Please provide a title")
                else:
                    try:
                        # Download from Google Drive
                        with st.spinner("☁️ Downloading from Google Drive..."):
                            # Try Google Docs export first if it's a Google Doc
                            if 'docs.google.com/document' in drive_url:
                                extracted_text = export_google_doc_as_text(drive_url)
                            else:
                                extracted_text = read_document_from_drive(drive_url)

                        st.success(f"✅ Downloaded and extracted {len(extracted_text)} characters")

                        # Show preview
                        with st.expander("📝 Downloaded Text Preview", expanded=False):
                            st.text_area("Text", extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text, height=200, disabled=True)

                        # Parse the extracted text
                        if parse_method.startswith("⚡"):
                            # Rule-based parsing
                            with st.spinner("⚡ Parsing with rule-based parser..."):
                                parsed_json = parse_text_to_json(extracted_text, doc_type.lower())

                                # Check if parsing produced meaningful results
                                has_content = any(isinstance(v, list) and len(v) > 0 for v in parsed_json.values())

                                if not has_content:
                                    st.warning("⚠️ Rule-based parser couldn't find structured content. Try AI-powered parsing.")
                                else:
                                    st.success("✅ Document parsed successfully!")

                                    with st.expander("📋 Parsed JSON Preview", expanded=True):
                                        st.json(parsed_json)

                                    st.session_state['imported_doc'] = {
                                        'title': title,
                                        'doc_type': doc_type.lower(),
                                        'content_json': parsed_json,
                                        'import_method': 'google_drive',
                                        'source_url': drive_url
                                    }

                                    st.session_state['import_step'] = 2
                                    st.rerun()

                        else:
                            # AI parsing
                            gemini_key = st.session_state.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
                            if not gemini_key:
                                st.error("❌ Gemini API key not found. Please set it in Settings.")
                            else:
                                with st.spinner("🤖 AI is parsing your document..."):
                                    # Use the same prompts as text parsing
                                    if doc_type == "BA":
                                        system_prompt = """You are a Business Analyst documentation expert.
Parse the given text and convert it into a structured BA (Business Analysis) JSON format.

The JSON structure should follow this schema:
{
  "ekranlar": [...],
  "backend_islemler": [...],
  "guvenlik_gereksinimleri": [...],
  "test_senaryolari": [...]
}

Return ONLY valid JSON, no markdown formatting or explanations."""
                                    elif doc_type == "TA":
                                        system_prompt = """You are a Technical Architect documentation expert.
Parse the given text into structured TA (Technical Analysis) JSON format.
Return ONLY valid JSON."""
                                    else:  # TC
                                        system_prompt = """You are a Test Engineer documentation expert.
Parse the given text into structured TC (Test Cases) JSON format.
Return ONLY valid JSON."""

                                    result = call_gemini(
                                        system_prompt=system_prompt,
                                        user_content=f"Parse this {doc_type} document:\n\n{extracted_text}",
                                        api_key=gemini_key,
                                        max_tokens=8000
                                    )

                                    if result.get('error'):
                                        st.error(f"❌ AI parsing error: {result['error']}")
                                    elif result.get('content'):
                                        parsed_json = result['content']
                                        st.success("✅ Document parsed successfully with AI!")

                                        with st.expander("📋 Parsed JSON Preview", expanded=True):
                                            st.json(parsed_json)

                                        st.session_state['imported_doc'] = {
                                            'title': title,
                                            'doc_type': doc_type.lower(),
                                            'content_json': parsed_json,
                                            'import_method': 'google_drive_ai',
                                            'source_url': drive_url
                                        }

                                        st.session_state['import_step'] = 2
                                        st.rerun()
                                    else:
                                        st.error("❌ AI returned empty response")

                    except ValueError as e:
                        st.error(f"❌ {str(e)}")
                        st.info("💡 Make sure the Google Drive link is set to 'Anyone with the link can view'")
                    except Exception as e:
                        st.error(f"❌ Error downloading from Google Drive: {str(e)}")
                        st.exception(e)

    elif import_method == "🔗 Google Drive (n8n)":
        st.markdown("### Import from Google Drive (via n8n Webhook)")
        st.info("💡 For private/company documents - Uses n8n webhook for OAuth token (same pattern as BA/TC evaluation)")

        st.markdown("""
        **Benefits:**
        - ✅ No public sharing required
        - ✅ Works with company/private documents
        - ✅ OAuth authentication via n8n
        - ✅ Same pattern as BA/TC evaluation stages
        - ✅ Token-based, direct API access

        **Your n8n Webhooks:**
        - Google Docs: https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy
        - Google Sheets: https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy
        """)

        # Get webhook URLs from settings or environment
        docs_webhook = st.session_state.get("n8n_docs_webhook") or os.environ.get("N8N_GOOGLE_DOCS_WEBHOOK", "https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy")
        sheets_webhook = st.session_state.get("n8n_sheets_webhook") or os.environ.get("N8N_GOOGLE_SHEETS_WEBHOOK", "https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy")

        # Show configured webhooks
        with st.expander("⚙️ Webhook Configuration", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Google Docs Webhook", value=docs_webhook, disabled=True, key="show_docs_webhook")
            with col2:
                st.text_input("Google Sheets Webhook", value=sheets_webhook, disabled=True, key="show_sheets_webhook")
            st.caption("💡 These URLs are configured in your n8n instance and return OAuth tokens")

        drive_url = st.text_input(
            "Google Docs/Drive URL",
            placeholder="https://docs.google.com/document/d/.../edit",
            help="Paste any Google Docs or Drive link (no public sharing needed)",
            key="n8n_drive_url"
        )

        if drive_url and docs_webhook and sheets_webhook:
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox("Document Type", ["BA", "TA", "TC"], key="n8n_doc_type")
            with col2:
                title = st.text_input("Document Title*", placeholder="e.g., Face ID Login Analysis", key="n8n_title")

            # Choose parsing method
            parse_method = st.radio(
                "Choose parsing method:",
                ["⚡ Rule-based (Fast, Free)", "🤖 AI-powered (Flexible, Requires API Key)"],
                help="Rule-based parser works best with structured documents",
                key="n8n_parse_method"
            )

            if st.button("🔗 Fetch via n8n Webhook", type="primary"):
                if not title:
                    st.error("❌ Please provide a title")
                else:
                    try:
                        # Extract document ID from URL
                        with st.spinner("📤 Analyzing URL..."):
                            doc_id = extract_google_drive_file_id(drive_url)
                            if not doc_id:
                                st.error("❌ Could not extract document ID from URL")
                                st.stop()

                        st.info(f"📄 Document ID: {doc_id}")

                        # Create Google Drive client with n8n webhooks
                        with st.spinner("🔗 Getting OAuth token from n8n..."):
                            client = GoogleDriveClient(
                                n8n_docs_webhook=docs_webhook,
                                n8n_sheets_webhook=sheets_webhook
                            )

                        # Download document using OAuth token
                        with st.spinner("☁️ Downloading document with OAuth..."):
                            extracted_text, doc_type_detected = client.read_document_from_url(drive_url)
                            char_count = len(extracted_text)

                        st.success(f"✅ Downloaded via n8n webhook: {char_count} characters")

                        # Show preview
                        with st.expander("📝 Downloaded Text Preview", expanded=False):
                            preview_text = extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text
                            st.text_area("Text", preview_text, height=200, disabled=True)

                        # Parse the extracted text
                        if parse_method.startswith("⚡"):
                            # Rule-based parsing
                            with st.spinner("⚡ Parsing with rule-based parser..."):
                                parsed_json = parse_text_to_json(extracted_text, doc_type.lower())

                                # Check if parsing produced meaningful results
                                has_content = any(isinstance(v, list) and len(v) > 0 for v in parsed_json.values())

                                if not has_content:
                                    st.warning("⚠️ Rule-based parser couldn't find structured content. Try AI-powered parsing.")
                                else:
                                    st.success("✅ Document parsed successfully!")

                                    with st.expander("📋 Parsed JSON Preview", expanded=True):
                                        st.json(parsed_json)

                                    st.session_state['imported_doc'] = {
                                        'title': title,
                                        'doc_type': doc_type.lower(),
                                        'content_json': parsed_json,
                                        'import_method': 'n8n_webhook',
                                        'source_url': drive_url,
                                        'document_id': doc_id
                                    }

                                    st.session_state['import_step'] = 2
                                    st.rerun()

                        else:
                            # AI parsing
                            gemini_key = st.session_state.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
                            if not gemini_key:
                                st.error("❌ Gemini API key not found. Please set it in Settings.")
                            else:
                                with st.spinner("🤖 AI is parsing your document..."):
                                    # Use the same prompts as text parsing
                                    if doc_type == "BA":
                                        system_prompt = """You are a Business Analyst documentation expert.
Parse the given text and convert it into a structured BA (Business Analysis) JSON format.

The JSON structure should follow this schema:
{
  "ekranlar": [...],
  "backend_islemler": [...],
  "guvenlik_gereksinimleri": [...],
  "test_senaryolari": [...]
}

Return ONLY valid JSON, no markdown formatting or explanations."""
                                    elif doc_type == "TA":
                                        system_prompt = """You are a Technical Architect documentation expert.
Parse the given text into structured TA (Technical Analysis) JSON format.
Return ONLY valid JSON."""
                                    else:  # TC
                                        system_prompt = """You are a Test Engineer documentation expert.
Parse the given text into structured TC (Test Cases) JSON format.
Return ONLY valid JSON."""

                                    result = call_gemini(
                                        system_prompt=system_prompt,
                                        user_content=f"Parse this {doc_type} document:\n\n{extracted_text}",
                                        api_key=gemini_key,
                                        max_tokens=8000
                                    )

                                    if result.get('error'):
                                        st.error(f"❌ AI parsing error: {result['error']}")
                                    elif result.get('content'):
                                        parsed_json = result['content']
                                        st.success("✅ Document parsed successfully with AI!")

                                        with st.expander("📋 Parsed JSON Preview", expanded=True):
                                            st.json(parsed_json)

                                        st.session_state['imported_doc'] = {
                                            'title': title,
                                            'doc_type': doc_type.lower(),
                                            'content_json': parsed_json,
                                            'import_method': 'n8n_webhook_ai',
                                            'source_url': drive_url,
                                            'document_id': doc_id
                                        }

                                        st.session_state['import_step'] = 2
                                        st.rerun()
                                    else:
                                        st.error("❌ AI returned empty response")

                    except requests.Timeout:
                        st.error("❌ Webhook timeout - document may be too large or n8n is slow")
                        st.info("💡 Try with a smaller document or check n8n workflow status")
                    except requests.RequestException as e:
                        st.error(f"❌ Webhook request failed: {str(e)}")
                        st.info("💡 Check that n8n webhook URL is correct and accessible")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)

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
