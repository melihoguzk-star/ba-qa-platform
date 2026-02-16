# Phase 2B: UI Integration Implementation Plan

## 🎯 Goal
Connect Phase 2A infrastructure to user-facing features in Streamlit UI.

## 📦 Scope

### 1. Document Library Enhancement
**File:** `pages/10_Document_Library.py`

**Changes:**
- Add "Use Semantic Search" checkbox
- Implement semantic search when checkbox enabled
- Show similarity scores in results
- Hybrid search option (TF-IDF + Semantic fusion)

**Estimated:** 2-3 hours

---

### 2. Settings Page - Vector Store Monitoring
**File:** `pages/99_Settings.py`

**Changes:**
- Add "Vector Store Status" section
- Show indexed document counts per type
- Display ChromaDB health status
- Add "Test Semantic Search" button
- Show cache statistics

**Estimated:** 1-2 hours

---

### 3. Hybrid Search Implementation
**New File:** `pipeline/hybrid_search.py`

**Features:**
- Combine TF-IDF + Semantic results
- Reciprocal Rank Fusion algorithm
- Configurable weight (alpha parameter)
- Performance optimization

**Estimated:** 2 hours

---

### 4. Search Results Enhancement
**File:** `pages/10_Document_Library.py`

**Features:**
- Show why documents matched (matched chunk preview)
- Display similarity scores as percentage
- Show chunk type (ekran, endpoint, test_case)
- Add "View Context" expander

**Estimated:** 1-2 hours

---

### 5. Import & Merge Integration (Optional)
**File:** `pages/11_Import_Merge.py`

**Features:**
- Suggest similar documents during import
- Show similarity scores
- Quick preview of similar docs
- "Reuse Similar Document" option

**Estimated:** 2-3 hours

---

## 🏗️ Implementation Order

### Day 1: Core Search UI (4-5 hours)
1. ✅ Settings page monitoring (easy win)
2. ✅ Document Library checkbox
3. ✅ Basic semantic search integration

### Day 2: Enhanced Features (4-5 hours)
4. ✅ Hybrid search implementation
5. ✅ Search results enhancement
6. ✅ Testing and refinement

### Day 3: Polish & Optional (2-3 hours)
7. ⚡ Import & Merge integration (if time)
8. ⚡ Performance optimization
9. ⚡ User documentation

---

## 🧪 Testing Strategy

### Manual Testing Checklist
- [ ] Settings page shows correct stats
- [ ] Semantic search checkbox works
- [ ] Results show similarity scores
- [ ] Hybrid search produces good results
- [ ] Performance is acceptable (<2s)
- [ ] No breaking changes to existing features

### Test Scenarios
1. Search with semantic ON vs OFF
2. Empty search with semantic enabled
3. Turkish query matching English docs
4. English query matching Turkish docs
5. Very long queries (>100 words)
6. Queries with no results

---

## 🎨 UI Mockups

### Settings Page
```
┌─────────────────────────────────────────────────┐
│ ⚙️ Settings                                     │
├─────────────────────────────────────────────────┤
│                                                 │
│ 📊 Vector Store Status                         │
│ ┌─────────────┬─────────────┬─────────────┐    │
│ │ BA Docs     │ TA Docs     │ TC Docs     │    │
│ │ 150 chunks  │ 95 chunks   │ 200 chunks  │    │
│ └─────────────┴─────────────┴─────────────┘    │
│                                                 │
│ Last Updated: 2026-02-16 14:30                 │
│ Status: ✅ Active                              │
│                                                 │
│ [🧪 Test Semantic Search]                      │
└─────────────────────────────────────────────────┘
```

### Document Library
```
┌─────────────────────────────────────────────────┐
│ 📚 Document Library                            │
├─────────────────────────────────────────────────┤
│                                                 │
│ 🔍 Search: [login screen_______________] [🔎]  │
│ ☑️ Use Semantic Search (AI-powered)            │
│ ☐ Hybrid Mode (Best of both)                   │
│                                                 │
│ ─────────────────────────────────────────────  │
│                                                 │
│ 📄 Mobile Banking Login                        │
│    💡 Similarity: 92% | Matched: Login Screen  │
│    📍 Chunk: "Kullanıcı giriş ekranı..."       │
│    [View Document]                              │
│                                                 │
│ 📄 User Authentication Flow                    │
│    💡 Similarity: 87% | Matched: Auth Screen   │
│    [View Document]                              │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Already in .env.example from Phase 2A
ENABLE_SEMANTIC_SEARCH=true
SIMILARITY_THRESHOLD=0.7

# New for Phase 2B
HYBRID_SEARCH_ALPHA=0.5  # 50% semantic + 50% keyword
ENABLE_HYBRID_SEARCH=true
SEARCH_RESULT_LIMIT=20
SHOW_CHUNK_PREVIEW=true
```

### Feature Flags
```python
# In-app feature toggles
FEATURES = {
    'semantic_search': True,      # Enable semantic search
    'hybrid_search': True,         # Enable hybrid mode
    'similarity_scores': True,     # Show scores in UI
    'chunk_preview': True,         # Show matched chunks
    'import_suggestions': False,   # Phase 2B optional
}
```

---

## 📊 Success Metrics

### Technical Metrics
- [ ] Search latency < 2 seconds (p95)
- [ ] No UI freezing during search
- [ ] Hybrid search accuracy > TF-IDF alone
- [ ] Zero breaking changes

### User Experience Metrics
- [ ] Semantic search finds relevant docs that keyword missed
- [ ] Similarity scores make sense (>80% = very similar)
- [ ] UI is intuitive (no training needed)
- [ ] Feature can be disabled (fallback to keyword)

---

## 🚨 Risk Mitigation

### Risk 1: Slow Search
**Mitigation:**
- Cache search results
- Show loading spinner
- Timeout after 5 seconds

### Risk 2: Poor Results
**Mitigation:**
- Fall back to keyword search
- Hybrid mode as default
- User can disable semantic

### Risk 3: Model Not Downloaded
**Mitigation:**
- Check model on app start
- Show warning if missing
- Provide download instructions

### Risk 4: Breaking Changes
**Mitigation:**
- Keep existing search as default
- Semantic is opt-in (checkbox)
- Extensive testing before merge

---

## 📝 Deliverables

### Code
- [ ] Updated `pages/10_Document_Library.py`
- [ ] Updated `pages/99_Settings.py`
- [ ] New `pipeline/hybrid_search.py`
- [ ] Updated `.env.example`

### Documentation
- [ ] Phase 2B completion guide
- [ ] User guide for semantic search
- [ ] Troubleshooting guide

### Testing
- [ ] Manual test checklist completed
- [ ] Test scenarios passed
- [ ] Performance benchmarks run

---

## 🎓 Learning Resources

For team members implementing this:

1. **Streamlit Components:**
   - `st.checkbox()` - For semantic search toggle
   - `st.metric()` - For vector store stats
   - `st.expander()` - For chunk previews

2. **Vector Search:**
   - Review `pipeline/vector_store.py`
   - Understand similarity scores (0-1 range)
   - Know when to use semantic vs keyword

3. **Hybrid Search:**
   - Reciprocal Rank Fusion algorithm
   - Alpha parameter tuning
   - Result merging strategies

---

## 🚀 Getting Started

```bash
# 1. Ensure Phase 2A is working
source venv_py312/bin/activate
python scripts/test_phase_2a.py

# 2. Start Streamlit
streamlit run Home.py

# 3. Navigate to Settings
# Check if Vector Store Status shows up

# 4. Navigate to Document Library
# Try the semantic search checkbox
```

---

**Ready to implement!** Let's start with Settings page (quick win) ⚡
