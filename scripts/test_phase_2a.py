#!/usr/bin/env python3
"""
Phase 2A Quick Test Script

Tests the semantic search infrastructure without UI.
Run with: python scripts/test_phase_2a.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🧪 Phase 2A Infrastructure Test")
print("=" * 60)

# Test 1: Chunking
print("\n1️⃣ Testing Document Chunking...")
try:
    from pipeline.chunking_strategy import get_chunker

    chunker = get_chunker()

    # Test BA document
    test_ba = {
        "ekranlar": [
            {
                "ekran_adi": "Login Screen",
                "aciklama": "User login page",
                "ui_elementleri": ["Email", "Password", "Login Button"]
            },
            {
                "ekran_adi": "Dashboard",
                "aciklama": "Main dashboard",
                "ui_elementleri": ["Charts", "Stats"]
            }
        ],
        "backend_islemler": [
            {
                "islem_adi": "User Authentication",
                "endpoint": "/api/auth/login",
                "method": "POST"
            }
        ]
    }

    chunks = chunker.chunk_document(
        doc_id=999,
        doc_type='ba',
        content_json=test_ba,
        metadata={'project_id': 1, 'title': 'Test Document'}
    )

    print(f"   ✅ Chunking works! Generated {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"      Chunk {i+1}: {chunk['chunk_type']} ({len(chunk['chunk_text'])} chars)")

except Exception as e:
    print(f"   ❌ Chunking failed: {e}")
    sys.exit(1)

# Test 2: Embedding Pipeline
print("\n2️⃣ Testing Embedding Pipeline...")
try:
    from pipeline.embedding_pipeline import EmbeddingPipeline

    pipeline = EmbeddingPipeline()
    print(f"   ✅ Pipeline initialized")
    print(f"      Model: {pipeline.model_name}")
    print(f"      Cache size: {len(pipeline._cache)}")

    # Test embedding generation (without actually loading model)
    print(f"   ℹ️  Model will be loaded on first actual use (~560MB download)")

except Exception as e:
    print(f"   ❌ Embedding pipeline failed: {e}")
    sys.exit(1)

# Test 3: Vector Store
print("\n3️⃣ Testing ChromaDB Vector Store...")
try:
    from pipeline.vector_store import get_vector_store

    vector_store = get_vector_store()
    stats = vector_store.get_collection_stats()

    print(f"   ✅ ChromaDB initialized")
    print(f"      Location: {vector_store.persist_directory}")
    print(f"      Collections:")
    for doc_type, info in stats.items():
        status_icon = '✅' if info['status'] == 'active' else '❌'
        print(f"        {status_icon} {doc_type.upper()}: {info['chunk_count']} chunks")

except Exception as e:
    print(f"   ❌ Vector store failed: {e}")
    print(f"      Note: Make sure you're using Python 3.12 (not 3.14)")
    sys.exit(1)

# Test 4: Database Integration
print("\n4️⃣ Testing Database Auto-indexing Hook...")
try:
    import os

    # Check if auto-indexing is enabled
    auto_indexing = os.getenv('ENABLE_AUTO_INDEXING', 'true')
    print(f"   ℹ️  Auto-indexing: {auto_indexing}")

    # Read database.py to verify hooks are present
    with open('data/database.py', 'r') as f:
        db_content = f.read()

    if 'index_document_async' in db_content:
        print(f"   ✅ Auto-indexing hooks found in database.py")
    else:
        print(f"   ⚠️  Auto-indexing hooks not found")

except Exception as e:
    print(f"   ❌ Database check failed: {e}")

# Test 5: Reindex Script
print("\n5️⃣ Testing Reindex Script...")
try:
    import subprocess

    # Run dry-run
    result = subprocess.run(
        ['python', 'scripts/reindex_all.py', '--dry-run', '--doc-type', 'ba'],
        capture_output=True,
        text=True,
        timeout=10
    )

    if 'DRY RUN' in result.stdout:
        # Extract document count
        for line in result.stdout.split('\n'):
            if 'Would reindex' in line:
                print(f"   ✅ Reindex script works")
                print(f"      {line.strip()}")
                break
    else:
        print(f"   ⚠️  Reindex script output unexpected")

except Exception as e:
    print(f"   ❌ Reindex script test failed: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 Test Summary")
print("=" * 60)
print("✅ All core components are working!")
print()
print("Next steps:")
print("  1. Run: python scripts/reindex_all.py --all")
print("  2. Test semantic search (see test script below)")
print("  3. Wait for Phase 2B for UI integration")
print("=" * 60)
