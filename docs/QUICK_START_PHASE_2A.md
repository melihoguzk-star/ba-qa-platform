# Phase 2A Quick Start Guide 🚀

## Installation (One-Time Setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (optional)
cp .env.example .env
# Edit .env if you want to customize settings

# 3. Reindex existing documents
python scripts/reindex_all.py --all --batch-size 50
```

**Expected output:**
```
INFO: Reindexing 123 ba documents...
INFO: Reindexing 78 ta documents...
INFO: Reindexing 95 tc documents...

OVERALL STATISTICS
==================
Total Documents:     296
Successfully Indexed: 296
Failed:              0
```

## Usage

### Semantic Search

```python
from pipeline.vector_store import get_vector_store

# Search for similar documents
vector_store = get_vector_store()
results = vector_store.search(
    query_text="kullanıcı giriş ekranı",
    doc_type='ba',
    top_k=5
)

for match in results:
    print(f"Doc {match['document_id']}: {match['similarity']:.2f}")
```

### Manual Indexing

```python
from pipeline.vector_store import get_vector_store

vector_store = get_vector_store()
vector_store.index_document(
    doc_id=1,
    doc_type='ba',
    content_json={"ekranlar": [...], "backend_islemler": [...]},
    metadata={'project_id': 1, 'tags': ['mobile']}
)
```

### Check Statistics

```python
from pipeline.vector_store import get_vector_store

vector_store = get_vector_store()
stats = vector_store.get_collection_stats()
print(stats)

# Output:
# {'ba': {'chunk_count': 500, 'status': 'active'},
#  'ta': {'chunk_count': 300, 'status': 'active'},
#  'tc': {'chunk_count': 450, 'status': 'active'}}
```

## Testing

```bash
# Run all Phase 2A tests
pytest tests/unit/test_chunking.py tests/unit/test_embedding_pipeline.py tests/unit/test_vector_store.py -v

# Quick test
pytest tests/unit/ -m unit -k "chunking or embedding or vector" -v
```

## Common Commands

```bash
# Reindex specific document type
python scripts/reindex_all.py --doc-type ba

# Dry run (count documents only)
python scripts/reindex_all.py --all --dry-run

# Resume from checkpoint
python scripts/reindex_all.py --doc-type ta --resume

# Clear checkpoint and restart
python scripts/reindex_all.py --doc-type ba --clear-checkpoint
```

## Configuration

Edit `.env` to customize:

```bash
# Change embedding model
EMBEDDING_MODEL=intfloat/multilingual-e5-large  # Larger, more accurate

# Change batch size for memory optimization
CHROMA_MAX_BATCH_SIZE=16  # Reduce if low memory

# Disable auto-indexing (manual only)
ENABLE_AUTO_INDEXING=false

# Adjust similarity threshold
SIMILARITY_THRESHOLD=0.8  # More strict matching
```

## Troubleshooting

### Model Download Failed
```bash
# Pre-download model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"
```

### Out of Memory
```bash
# Reduce batch size
export CHROMA_MAX_BATCH_SIZE=16
python scripts/reindex_all.py --doc-type ba --batch-size 25
```

### ChromaDB Permission Error
```bash
# Fix permissions
chmod -R 755 data/chroma_db/
```

## What's Next?

Phase 2A is complete! Next steps (Phase 2B):

1. **UI Integration** - Add semantic search to Document Library page
2. **Hybrid Search** - Combine semantic + TF-IDF for best results
3. **Settings Dashboard** - Monitor vector store status
4. **BRD Pipeline Integration** - Suggest related documents during analysis

---

**Need Help?** See full documentation: `docs/PHASE_2A_IMPLEMENTATION.md`
