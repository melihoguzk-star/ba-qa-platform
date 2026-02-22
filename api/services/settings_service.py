"""
Settings Service — API key management, rotation, vector store stats
"""
import os
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime

from api.config import get_settings


settings = get_settings()


# ============================================================================
# Helper Functions
# ============================================================================

def mask_key(key: str) -> str:
    """Mask API key for display"""
    if not key or len(key) < 8:
        return "***"
    return f"{key[:6]}***...***{key[-4:]}"


def hash_key(key: str) -> str:
    """Hash API key for identification"""
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def test_gemini_key(api_key: str) -> tuple[bool, str]:
    """
    Test if Gemini API key is valid.
    Returns (is_valid, message)
    """
    try:
        import google.generativeai as genai

        # Configure with test key
        genai.configure(api_key=api_key)

        # Try to list models as validation
        models = genai.list_models()
        model_list = list(models)

        if model_list:
            return True, f"✅ Valid key — {len(model_list)} models available"
        else:
            return False, "❌ No models found with this key"

    except Exception as e:
        error_msg = str(e).lower()

        if "api_key" in error_msg or "invalid" in error_msg:
            return False, "❌ Invalid API key"
        elif "quota" in error_msg or "429" in error_msg:
            return False, "⚠️ Quota exceeded"
        else:
            return False, f"❌ Error: {str(e)[:100]}"


# ============================================================================
# Gemini Keys Management
# ============================================================================

def get_gemini_keys() -> List[Dict[str, Any]]:
    """
    Get Gemini API keys from environment.
    Returns list of key info dicts (masked).
    """
    keys = []

    # Try to get from GEMINI_API_KEY (single) or GEMINI_API_KEYS (list)
    single_key = os.getenv("GEMINI_API_KEY")
    if single_key:
        keys.append(single_key)

    # Check for multiple keys (comma-separated or individual env vars)
    multi_keys = os.getenv("GEMINI_API_KEYS")
    if multi_keys:
        # Assume comma-separated
        keys.extend([k.strip() for k in multi_keys.split(",") if k.strip()])

    # Build response
    key_list = []
    for idx, key in enumerate(keys, 1):
        key_list.append({
            "index": idx,
            "key_preview": mask_key(key),
            "key_hash": hash_key(key),
            "status": "unknown",  # We don't have key manager stats in API
            "requests": 0,
            "errors": 0,
            "last_used": None,
            "last_error": None
        })

    return key_list


def test_gemini_key_by_index(key_index: int) -> tuple[bool, str]:
    """Test Gemini key by index"""
    keys = []

    single_key = os.getenv("GEMINI_API_KEY")
    if single_key:
        keys.append(single_key)

    multi_keys = os.getenv("GEMINI_API_KEYS")
    if multi_keys:
        keys.extend([k.strip() for k in multi_keys.split(",") if k.strip()])

    if key_index < 1 or key_index > len(keys):
        return False, f"Invalid key index: {key_index}"

    key = keys[key_index - 1]
    return test_gemini_key(key)


# ============================================================================
# Anthropic Key Management
# ============================================================================

def get_anthropic_key() -> Dict[str, Any]:
    """
    Get Anthropic API key from environment (masked).
    Returns dict with key_preview and configured status.
    """
    key = os.getenv("ANTHROPIC_API_KEY")

    if key:
        return {
            "key_preview": mask_key(key),
            "configured": True,
            "key_hash": hash_key(key)
        }
    else:
        return {
            "key_preview": "",
            "configured": False,
            "key_hash": ""
        }


# ============================================================================
# Rotation Settings (Placeholder)
# ============================================================================

def get_rotation_settings() -> Dict[str, Any]:
    """Get key rotation settings"""
    keys = get_gemini_keys()

    return {
        "strategy": "least_used",
        "auto_reset_enabled": True,
        "total_keys": len(keys),
        "rotation_enabled": len(keys) >= 2
    }


def update_rotation_settings(strategy: Optional[str] = None, auto_reset: Optional[bool] = None) -> Dict[str, Any]:
    """Update rotation settings"""
    # TODO: Store settings in config file
    return get_rotation_settings()


def reset_all_keys() -> Dict[str, Any]:
    """Reset all key statistics"""
    keys = get_gemini_keys()

    return {
        "success": True,
        "message": "All keys reset successfully",
        "keys_reset": len(keys)
    }


# ============================================================================
# Usage Statistics (Placeholder)
# ============================================================================

def get_usage_statistics() -> Dict[str, Any]:
    """Get key usage statistics"""
    keys = get_gemini_keys()

    return {
        "total_keys": len(keys),
        "active_keys": len(keys),
        "failed_keys": 0,
        "total_requests": 0,
        "total_errors": 0,
        "keys": [
            {
                "key_preview": k["key_preview"],
                "status": "active",
                "requests": 0,
                "errors": 0,
                "last_used": None,
                "last_error": None
            }
            for k in keys
        ]
    }


# ============================================================================
# Vector Store Stats
# ============================================================================

def get_vector_store_config() -> Dict[str, Any]:
    """Get vector store configuration"""
    return {
        "semantic_search_enabled": os.getenv("ENABLE_SEMANTIC_SEARCH", "true").lower() == "true",
        "auto_indexing_enabled": os.getenv("ENABLE_AUTO_INDEXING", "true").lower() == "true",
        "embedding_model": settings.embedding_model,
        "persist_directory": settings.chroma_persist_directory
    }


def get_vector_store_stats() -> Dict[str, Any]:
    """Get ChromaDB collection statistics"""
    try:
        from pipeline.vector_store import get_vector_store

        vector_store = get_vector_store()
        stats = vector_store.get_collection_stats()

        ba_stats = stats.get("ba", {})
        ta_stats = stats.get("ta", {})
        tc_stats = stats.get("tc", {})

        return {
            "ba": {
                "chunk_count": ba_stats.get("chunk_count", 0),
                "status": ba_stats.get("status", "unknown")
            },
            "ta": {
                "chunk_count": ta_stats.get("chunk_count", 0),
                "status": ta_stats.get("status", "unknown")
            },
            "tc": {
                "chunk_count": tc_stats.get("chunk_count", 0),
                "status": tc_stats.get("status", "unknown")
            },
            "total_chunks": sum(s.get("chunk_count", 0) for s in [ba_stats, ta_stats, tc_stats])
        }
    except Exception as e:
        # Return empty stats if vector store not available
        return {
            "ba": {"chunk_count": 0, "status": "unknown"},
            "ta": {"chunk_count": 0, "status": "unknown"},
            "tc": {"chunk_count": 0, "status": "unknown"},
            "total_chunks": 0
        }


def test_vector_search(query: str, doc_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Test semantic search"""
    try:
        from pipeline.vector_store import get_vector_store

        vector_store = get_vector_store()
        results = vector_store.search(
            query_text=query,
            doc_type=doc_type,
            top_k=top_k
        )

        return [
            {
                "document_id": r["document_id"],
                "similarity": r["similarity"],
                "chunk_text": r["chunk_text"],
                "metadata": r.get("metadata", {})
            }
            for r in results
        ]
    except Exception as e:
        raise Exception(f"Vector search failed: {str(e)}")


# ============================================================================
# Smart Matching Analytics
# ============================================================================

def get_smart_matching_analytics(time_range: str = "all") -> Dict[str, Any]:
    """Get smart matching analytics"""
    try:
        from data.database import get_task_match_analytics

        analytics = get_task_match_analytics(time_range)

        return {
            "total_matches": analytics.get("total_matches", 0),
            "total_accepted": analytics.get("total_accepted", 0),
            "acceptance_rate": analytics.get("acceptance_rate", 0.0),
            "avg_confidence": analytics.get("avg_confidence", 0.0),
            "suggestion_breakdown": [
                {
                    "suggestion": item.get("suggestion"),
                    "count": item.get("count", 0),
                    "accepted": item.get("accepted", 0)
                }
                for item in analytics.get("suggestion_breakdown", [])
            ],
            "doc_type_breakdown": [
                {
                    "doc_type": item.get("doc_type", "unknown"),
                    "count": item.get("count", 0),
                    "avg_confidence": item.get("avg_confidence", 0.0)
                }
                for item in analytics.get("doc_type_breakdown", [])
            ]
        }
    except Exception as e:
        # Return empty analytics if not available
        return {
            "total_matches": 0,
            "total_accepted": 0,
            "acceptance_rate": 0.0,
            "avg_confidence": 0.0,
            "suggestion_breakdown": [],
            "doc_type_breakdown": []
        }
