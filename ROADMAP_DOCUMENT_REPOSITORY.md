# 📚 Smart Document Repository & Evolution System - Roadmap

## 🎯 Vision

Daha önce oluşturulan BA/TA/TC dokümanlarını sakla, yeni geliştirmelerde bu dokümanları akıllıca bul, güncelle, ve öneri yap. Dokümanları "living documents" olarak sürekli güncel tut.

---

## 🔒 Understanding Lock (Approved)

### What We're Building
**Smart Document Repository & Evolution System** - AI-assisted document management with intelligent matching and incremental updates.

### Why It Exists
**Problem:**
- Dokümanlar kayboluyur (email, local files)
- Her yeni feature için sıfırdan BA/TC yazılıyor
- Mevcut dokümanlar güncel kalmıyor
- "Bu daha önce yapılmış mı?" sorusu sürekli sorulur

**Solution:**
- Centralized document repository
- AI-powered smart matching (task → related documents)
- Incremental updates (append to existing docs)
- Version control & change tracking

### Who It's For
- **BA'lar**: Mevcut BA'ları bul, güncelle
- **QA'lar**: TC'leri tekrar kullan, genişlet
- **Tech Leads**: TA'ları evrimleştir
- **Product Managers**: Ürün feature history'yi gör

### Success Criteria
- ✅ Document reuse rate > 70%
- ✅ Time to create BA/TC %50 azalır (reuse ile)
- ✅ Document freshness: %90+ dokümanlar son 3 ayda güncellenmiş
- ✅ Search accuracy > 85% (doğru dokümanı bulma)

### Key Decision
**Automation Level:** AI-Assisted (B)
- AI analyzes task and suggests matching documents
- AI proposes update options (append/new/replace)
- User makes final decision
- User can edit AI suggestions

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Document    │  │  Search &    │  │  Update      │  │
│  │  Library     │  │  Matching    │  │  Assistant   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Core Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Document    │  │  AI Matching │  │  Version     │  │
│  │  Manager     │  │  Engine      │  │  Control     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  SQLite      │  │  File        │  │  Vector      │  │
│  │  Database    │  │  Storage     │  │  Store       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📅 Phased Implementation Plan

### ✅ Phase 1: Document Repository (Weeks 1-2) — COMPLETED
**Goal:** Store and organize existing BA/TA/TC documents

**Status:** ✅ Completed on 2026-02-14

#### Features
- [x] Document upload (JSON files)
- [x] Project organization (folder structure)
- [x] Document metadata (type, version, date, author)
- [x] Basic search (by project, type, keyword)
- [x] Document viewer (formatted display)
- [x] Version history tracking
- [x] Document stats dashboard

**Deliverables:**
- ✅ Database schema created (`projects`, `documents`, `document_versions`, `document_sections`)
- ✅ CRUD functions implemented in `data/database.py`
- ✅ UI page created at `pages/10_Document_Library.py`
- ✅ Sample data created for testing
- ✅ Version control system working

#### Database Schema
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    doc_type TEXT CHECK(doc_type IN ('ba', 'ta', 'tc')),
    version INTEGER DEFAULT 1,
    title TEXT NOT NULL,
    content_json TEXT NOT NULL,
    metadata_json TEXT,  -- {author, jira_keys, tags}
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE document_versions (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    content_json TEXT NOT NULL,
    change_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

#### UI Pages
- **📁 Document Library** (`pages/10_Document_Library.py`)
  - Project list (sidebar or dropdown)
  - Document grid/list view
  - Filter by type, date
  - Search box

- **📄 Document Viewer** (modal or new page)
  - Formatted JSON display
  - Metadata panel
  - Version history
  - Download button

#### Implementation Tasks
1. [ ] Create database schema (migration script)
2. [ ] Build document storage service
3. [ ] Create UI: Document Library page
4. [ ] Implement document upload
5. [ ] Implement search/filter
6. [ ] Build document viewer
7. [ ] Test with sample documents

#### Success Metrics
- ✅ Can upload 10+ documents successfully
- ✅ Search returns results in <1s
- ✅ UI responsive and intuitive

---

### 🟢 Phase 2: Smart Matching (Weeks 3-4)
**Goal:** AI-powered task analysis and document matching

#### Features
- [ ] Task analysis (extract scope, keywords, intent)
- [ ] Semantic search (embedding-based)
- [ ] Match scoring (confidence %)
- [ ] Match suggestions UI
- [ ] Match reasoning (why this document?)

#### AI Matching Engine

**Approach: Hybrid Search**
```python
# 1. Extract task features
task_features = extract_task_features(jira_task)
# → {
#     "keywords": ["biometric", "authentication", "login"],
#     "intent": "ADD_FEATURE",
#     "scope": "Login Screen",
#     "entities": ["Face ID", "Touch ID"]
# }

# 2. Semantic search (embeddings)
from openai import OpenAI
task_embedding = get_embedding(task_description)

# Find similar document sections
matches = vector_search(
    query_embedding=task_embedding,
    collection="document_sections",
    top_k=5
)

# 3. Keyword matching (fallback)
keyword_matches = keyword_search(
    keywords=task_features["keywords"],
    documents=all_documents
)

# 4. Combine & rank
final_matches = rank_matches(
    semantic_matches=matches,
    keyword_matches=keyword_matches,
    weights={"semantic": 0.7, "keyword": 0.3}
)

# 5. Return top suggestions
return {
    "matches": final_matches[:3],
    "confidence": calculate_confidence(final_matches),
    "reasoning": explain_matches(final_matches)
}
```

#### Vector Store Options
- **Option A: Local (ChromaDB)**
  - Pros: Free, local, privacy
  - Cons: Setup complexity

- **Option B: Cloud (Pinecone)**
  - Pros: Managed, scalable
  - Cons: Cost ($)

**Recommendation:** ChromaDB (local, free)

#### UI: Smart Matching
- **Task Input Panel**
  - JIRA key input or manual description
  - "Find Related Documents" button

- **Match Results**
  ```
  📊 Found 3 Related Documents

  1. ⭐⭐⭐⭐⭐ 95% Match
     📄 Mobile Banking App - BA v2
     Section: Login Screen
     Reason: "Contains authentication, login flow"
     [View Document] [Use This]

  2. ⭐⭐⭐⭐ 78% Match
     📄 Mobile Banking App - TA v1
     Section: Auth API
     Reason: "API endpoints for authentication"
     [View Document] [Use This]

  3. ⭐⭐⭐ 62% Match
     📄 ERP App - BA v1
     Section: User Login
     Reason: "Similar login functionality"
     [View Document]
  ```

#### Implementation Tasks
1. [ ] Set up ChromaDB (vector store)
2. [ ] Build embedding pipeline (generate embeddings for all docs)
3. [ ] Implement task analysis (LLM-based feature extraction)
4. [ ] Build semantic search function
5. [ ] Implement ranking algorithm
6. [ ] Create match explanation (reasoning)
7. [ ] Build UI: Smart Matching panel
8. [ ] Test with real JIRA tasks

#### Success Metrics
- ✅ Match accuracy > 85% (manual validation)
- ✅ Search response time < 2s
- ✅ Top-3 contains relevant doc in 90% of cases

---

### 🟡 Phase 3: Incremental Updates (Weeks 5-6)
**Goal:** AI-assisted document evolution with diff visualization

#### Features
- [ ] Update strategy suggestions (append/replace/new)
- [ ] AI-generated incremental updates
- [ ] Diff viewer (before/after comparison)
- [ ] Merge conflicts detection
- [ ] Version history timeline
- [ ] Rollback capability

#### Update Workflow

```
User Flow:
1. User selects task (JIRA-1500: Add biometric auth)
2. AI finds match: "Mobile Banking - BA v2 - Login Screen"
3. AI suggests: "Update existing document (append to Login section)"
4. AI generates draft update:

   Draft Changes:
   + FR-25: User can authenticate using Face ID
   + FR-26: User can authenticate using Touch ID
   + FR-27: System falls back to password if biometric fails
   + BR-15: Biometric authentication must comply with iOS/Android guidelines
   ~ Modified: Login flow diagram (added step 2.5: biometric check)

5. User reviews diff
6. User can:
   - Accept (create BA v3)
   - Edit (modify AI suggestion)
   - Reject (start from scratch)
```

#### AI Update Generator

```python
def generate_incremental_update(task, matched_document, section):
    """
    Generate incremental update for existing document.
    """
    system_prompt = """
    You are a BA document update assistant.

    Given:
    - A new task requirement
    - An existing BA document section

    Generate:
    - New functional requirements (FR-XX)
    - New business rules (BR-XX)
    - Updated workflows (if needed)
    - Updated validations (if needed)

    Rules:
    - Only add what's necessary for the new task
    - Reuse existing numbering scheme
    - Don't duplicate existing requirements
    - Mark modifications with "~", additions with "+"
    """

    user_prompt = f"""
    Task: {task.description}

    Existing Document Section:
    {matched_document.sections[section]}

    Generate incremental update in JSON format.
    """

    response = call_ai(
        system_prompt=system_prompt,
        user_content=user_prompt,
        model="claude-sonnet-4.5"
    )

    return parse_update_json(response)
```

#### Diff Viewer

```
┌─────────────────────────────────────────────────────────┐
│  BA v2 → BA v3 (Draft)                     [Accept] [Edit] [Reject]
├─────────────────────────────────────────────────────────┤
│  Login Screen                                            │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Fonksiyonel Gereksinimler:                             │
│    FR-01: User can enter email                           │
│    FR-02: User can enter password                        │
│  + FR-25: User can authenticate using Face ID            │ <- NEW
│  + FR-26: User can authenticate using Touch ID           │ <- NEW
│  + FR-27: System falls back to password if biometric fails│ <- NEW
│                                                          │
│  İş Kuralları:                                          │
│    BR-01: Email must be valid format                     │
│  + BR-15: Biometric must comply with platform guidelines │ <- NEW
│                                                          │
│  İş Akışı:                                              │
│    1. User opens app                                     │
│    2. User sees login screen                             │
│  ~ 2.5. If biometric enabled, prompt for Face/Touch ID   │ <- MODIFIED
│    3. User enters credentials                            │
│    4. System validates                                   │
└─────────────────────────────────────────────────────────┘

Legend: + Added | ~ Modified | - Deleted
```

#### Version History

```
┌─────────────────────────────────────────────────────────┐
│  Version History: Mobile Banking - BA                    │
├─────────────────────────────────────────────────────────┤
│  ● v4 (Current - Draft)                                  │
│    2025-02-15 | Add biometric authentication             │
│    Changes: +3 FR, +1 BR, ~1 workflow                    │
│    [View] [Compare with v3]                              │
│                                                          │
│  ● v3                                                    │
│    2025-01-10 | Add social login (Google, Apple)         │
│    Changes: +5 FR, +2 BR, +1 screen                      │
│    [View] [Restore] [Compare with v2]                    │
│                                                          │
│  ● v2                                                    │
│    2024-12-20 | Add forgot password flow                 │
│    Changes: +2 FR, +1 screen                             │
│    [View] [Restore] [Compare with v1]                    │
│                                                          │
│  ● v1                                                    │
│    2024-11-15 | Initial: Login, Dashboard, Transfer      │
│    Changes: Initial version                              │
│    [View]                                                │
└─────────────────────────────────────────────────────────┘
```

#### Implementation Tasks
1. [ ] Build update suggestion algorithm
2. [ ] Implement AI update generator
3. [ ] Create diff computation (JSON diff)
4. [ ] Build diff viewer UI (side-by-side or unified)
5. [ ] Implement version creation
6. [ ] Build version history timeline
7. [ ] Add rollback functionality
8. [ ] Test incremental update flow end-to-end

#### Success Metrics
- ✅ Update suggestions are accurate (>80% user acceptance)
- ✅ Diff viewer is intuitive (user testing)
- ✅ Version history is complete and navigable

---

## 🗂️ Database Schema (Complete)

```sql
-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Documents
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    doc_type TEXT CHECK(doc_type IN ('ba', 'ta', 'tc')) NOT NULL,
    title TEXT NOT NULL,
    current_version INTEGER DEFAULT 1,
    content_json TEXT NOT NULL,  -- Latest version content
    metadata_json TEXT,  -- {author, jira_keys, tags, created_by}
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Document Versions (History)
CREATE TABLE document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    content_json TEXT NOT NULL,
    change_summary TEXT,  -- "Added biometric auth (JIRA-1500)"
    changes_json TEXT,    -- Structured diff {added: [], modified: [], deleted: []}
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, version)
);

-- Document Sections (for semantic search)
CREATE TABLE document_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    section_type TEXT,  -- 'screen', 'api_endpoint', 'test_case'
    section_name TEXT,  -- 'Login Screen', 'POST /api/auth/login'
    content_text TEXT,  -- Plain text for search
    embedding_vector BLOB,  -- Vector embedding
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Task Matching History (for analytics)
CREATE TABLE task_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jira_key TEXT,
    task_description TEXT,
    matched_document_id INTEGER,
    confidence_score REAL,
    user_accepted BOOLEAN,  -- Did user use this match?
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_document_id) REFERENCES documents(id)
);

-- Indexes
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(doc_type);
CREATE INDEX idx_versions_document ON document_versions(document_id);
CREATE INDEX idx_sections_document ON document_sections(document_id);
CREATE INDEX idx_task_matches_jira ON task_matches(jira_key);
```

---

## 🔧 Technical Stack

### Backend
- **Database:** SQLite (existing)
- **Vector Store:** ChromaDB (local, free)
- **AI Models:**
  - Task Analysis: Claude Sonnet 4.5
  - Update Generation: Claude Sonnet 4.5
  - Embeddings: OpenAI `text-embedding-3-small` (cheap, fast)

### Frontend
- **Framework:** Streamlit (existing)
- **Diff Viewer:** `difflib` (Python standard library) + custom CSS
- **JSON Editor:** `streamlit-ace` or custom component

### New Dependencies
```bash
pip install chromadb          # Vector database
pip install openai           # Embeddings API
pip install python-dotenv    # Environment variables
```

---

## 📊 Cost Estimation

### AI Costs (Monthly, assuming 100 tasks/month)

| Operation | Model | Cost per Request | Monthly Cost |
|-----------|-------|------------------|--------------|
| Task Analysis | Claude Sonnet 4.5 | $0.02 | $2.00 |
| Document Matching (Embeddings) | OpenAI Embedding | $0.0001 | $0.01 |
| Update Generation | Claude Sonnet 4.5 | $0.05 | $5.00 |
| **Total** | | | **~$7/month** |

### Infrastructure
- **ChromaDB:** Free (local)
- **SQLite:** Free
- **Streamlit:** Free (local hosting)

**Total Monthly Cost:** ~$7 (AI APIs only)

---

## ⚠️ Risks & Mitigations

### Risk 1: AI Matching Accuracy
**Risk:** AI matches wrong documents (low precision)

**Mitigation:**
- Start with high confidence threshold (>80%)
- Show top-3 matches (not just top-1)
- User feedback loop (track acceptance rate)
- Manual override always available

### Risk 2: Update Conflicts
**Risk:** AI generates updates that conflict with recent manual changes

**Mitigation:**
- Always show diff before applying
- Merge conflict detection
- User can edit AI suggestions
- Rollback capability

### Risk 3: Embedding Quality
**Risk:** Embeddings don't capture semantic similarity well

**Mitigation:**
- Use proven embedding model (OpenAI text-embedding-3)
- Hybrid search (semantic + keyword)
- Fine-tune threshold based on feedback

### Risk 4: Version History Bloat
**Risk:** Too many versions, database grows large

**Mitigation:**
- Keep only N most recent versions (e.g., 10)
- Archive old versions to separate storage
- Compress version diffs (store deltas, not full docs)

---

## 🎯 Success Metrics & KPIs

### Phase 1: Repository
- **Documents stored:** 20+ documents in first month
- **Search usage:** 50+ searches/week
- **User satisfaction:** >80% find UI intuitive

### Phase 2: Matching
- **Match accuracy:** >85% (top-3 contains relevant doc)
- **Match acceptance rate:** >70% (users actually use suggested docs)
- **Search time:** <2s per query

### Phase 3: Updates
- **Update acceptance rate:** >60% (users accept AI suggestions)
- **Time saved:** 30 min → 10 min (to update a document)
- **Version control usage:** 80% of updates create new version

---

## 📋 Decision Log

### Decision 1: Automation Level
**Options Considered:**
- A) Fully automated (AI decides everything)
- B) AI-assisted (AI suggests, user decides)
- C) Hybrid (mix of both)

**Decision:** **B) AI-Assisted**

**Reasoning:**
- Balances automation with user control
- Reduces risk of wrong decisions
- Builds user trust in AI gradually
- User expertise is valuable (domain knowledge)

---

### Decision 2: Implementation Approach
**Options Considered:**
- A) Minimalist MVP (2-3 weeks, basic features)
- B) Full system (6-8 weeks, all features at once)
- C) Phased approach (incremental delivery)

**Decision:** **C) Phased Approach**

**Reasoning:**
- Early value delivery (Phase 1 in 2 weeks)
- Risk mitigation (learn from each phase)
- User feedback shapes later phases
- Budget control (spread costs)

---

### Decision 3: Vector Store
**Options Considered:**
- A) ChromaDB (local, free)
- B) Pinecone (cloud, managed)
- C) PostgreSQL pgvector (existing DB)

**Decision:** **A) ChromaDB**

**Reasoning:**
- Free (no ongoing cost)
- Local (data privacy)
- Easy setup (Python library)
- Good enough for <10k documents
- Can migrate to Pinecone later if needed

---

### Decision 4: Embedding Model
**Options Considered:**
- A) OpenAI text-embedding-3-small ($0.02/1M tokens)
- B) OpenAI text-embedding-3-large ($0.13/1M tokens)
- C) Open-source (sentence-transformers)

**Decision:** **A) text-embedding-3-small**

**Reasoning:**
- Proven quality
- Very cheap ($0.0001 per document)
- Fast API response
- Good enough for semantic search
- Can upgrade to large if needed

---

## 🚀 Next Steps

### Immediate Actions (This Week)
1. [ ] **Create Phase 1 implementation plan** (detailed tasks)
2. [ ] **Set up development environment**
   - Install ChromaDB
   - Install OpenAI Python SDK
   - Create .env for API keys
3. [ ] **Design database schema** (finalize tables)
4. [ ] **Create mockups for Document Library UI**

### Phase 1 Kickoff (Next Week)
1. [ ] Implement database migrations
2. [ ] Build document storage service
3. [ ] Start UI development

---

## 📖 Appendix

### Example: Document JSON Structure

```json
{
  "document_id": "doc_001",
  "project": "Mobile Banking App",
  "type": "ba",
  "version": 3,
  "title": "Mobile Banking - Business Analysis",
  "created_at": "2024-11-15",
  "updated_at": "2025-01-10",
  "metadata": {
    "author": "BA Team",
    "jira_keys": ["BAQA-1200", "BAQA-1300", "BAQA-1500"],
    "tags": ["mobile", "banking", "authentication"]
  },
  "content": {
    "ekranlar": [
      {
        "ekran_adi": "Login Screen",
        "aciklama": "User authentication screen with email/password and biometric options",
        "fonksiyonel_gereksinimler": [
          {"id": "FR-01", "tanim": "User can enter email"},
          {"id": "FR-02", "tanim": "User can enter password"},
          {"id": "FR-25", "tanim": "User can authenticate using Face ID"},
          {"id": "FR-26", "tanim": "User can authenticate using Touch ID"}
        ],
        "is_kurallari": [
          {"id": "BR-01", "kural": "Email must be valid format"},
          {"id": "BR-15", "kural": "Biometric authentication must comply with platform guidelines"}
        ]
      }
    ]
  },
  "version_history": [
    {
      "version": 1,
      "date": "2024-11-15",
      "summary": "Initial version: Login, Dashboard, Transfer",
      "jira_key": "BAQA-1200"
    },
    {
      "version": 2,
      "date": "2024-12-20",
      "summary": "Added forgot password flow",
      "jira_key": "BAQA-1300"
    },
    {
      "version": 3,
      "date": "2025-01-10",
      "summary": "Added biometric authentication",
      "jira_key": "BAQA-1500"
    }
  ]
}
```

### Example: Task Matching Response

```json
{
  "task": {
    "jira_key": "BAQA-1500",
    "summary": "Add biometric authentication to login",
    "description": "Users should be able to login using Face ID or Touch ID..."
  },
  "matches": [
    {
      "rank": 1,
      "document_id": "doc_001",
      "project": "Mobile Banking App",
      "type": "ba",
      "version": 2,
      "section": "Login Screen",
      "confidence": 0.95,
      "reasoning": "High semantic similarity: login + authentication. Document already contains login flow. Biometric is incremental add.",
      "suggestion": "UPDATE_EXISTING",
      "preview": "Login Screen section has 10 FRs, 5 BRs. Suggest appending biometric FRs."
    },
    {
      "rank": 2,
      "document_id": "doc_002",
      "project": "Mobile Banking App",
      "type": "ta",
      "version": 1,
      "section": "Authentication API",
      "confidence": 0.78,
      "reasoning": "Related to authentication. API endpoints need update for biometric.",
      "suggestion": "UPDATE_EXISTING",
      "preview": "Auth API section describes POST /api/auth/login. May need biometric token endpoint."
    }
  ]
}
```

---

**Document Version:** 1.0
**Last Updated:** 2025-02-15
**Status:** Approved - Ready for Phase 1 Implementation
**Next Review:** After Phase 1 Completion (Week 2)
