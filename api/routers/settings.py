"""
Settings Router — API key management, rotation, vector store
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.schemas.settings import (
    GeminiKeysListResponse,
    KeyTestRequest,
    KeyTestResponse,
    AnthropicKeyResponse,
    RotationSettingsResponse,
    RotationSettingsRequest,
    ResetKeysResponse,
    UsageStatisticsResponse,
    VectorStoreConfigResponse,
    VectorStoreStatsResponse,
    VectorSearchRequest,
    VectorSearchResponse,
    SmartMatchingAnalyticsResponse
)
from api.services.settings_service import (
    get_gemini_keys,
    test_gemini_key_by_index,
    get_anthropic_key,
    get_rotation_settings,
    update_rotation_settings,
    reset_all_keys,
    get_usage_statistics,
    get_vector_store_config,
    get_vector_store_stats,
    test_vector_search,
    get_smart_matching_analytics
)

router = APIRouter()


# ============================================================================
# Gemini Keys Management
# ============================================================================

@router.get("/gemini-keys", response_model=GeminiKeysListResponse)
async def list_gemini_keys():
    """List all configured Gemini API keys (masked)"""
    keys = get_gemini_keys()
    return {
        "keys": keys,
        "total": len(keys)
    }


@router.post("/gemini-keys/test", response_model=KeyTestResponse)
async def test_gemini_key_endpoint(request: KeyTestRequest):
    """Test a Gemini API key by index"""
    is_valid, message = test_gemini_key_by_index(request.key_index)
    return {
        "is_valid": is_valid,
        "message": message
    }


# ============================================================================
# Anthropic Key Management
# ============================================================================

@router.get("/anthropic-key", response_model=AnthropicKeyResponse)
async def get_anthropic_key_endpoint():
    """Get Anthropic API key from environment (masked, read-only)"""
    key_info = get_anthropic_key()
    return {
        "key_preview": key_info["key_preview"],
        "configured": key_info["configured"]
    }


# ============================================================================
# Rotation Settings
# ============================================================================

@router.get("/rotation", response_model=RotationSettingsResponse)
async def get_rotation_settings_endpoint():
    """Get key rotation settings"""
    settings = get_rotation_settings()
    return settings


@router.put("/rotation", response_model=RotationSettingsRequest)
async def update_rotation_settings_endpoint(request: RotationSettingsRequest):
    """Update rotation settings"""
    settings = update_rotation_settings(
        strategy=request.strategy,
        auto_reset=request.auto_reset_enabled
    )
    return settings


@router.post("/rotation/reset", response_model=ResetKeysResponse)
async def reset_keys_endpoint():
    """Reset all key statistics"""
    result = reset_all_keys()
    return result


# ============================================================================
# Statistics
# ============================================================================

@router.get("/statistics", response_model=UsageStatisticsResponse)
async def get_statistics_endpoint():
    """Get API key usage statistics"""
    stats = get_usage_statistics()
    return stats


# ============================================================================
# Vector Store
# ============================================================================

@router.get("/vector-store/config", response_model=VectorStoreConfigResponse)
async def get_vector_store_config_endpoint():
    """Get vector store configuration"""
    config = get_vector_store_config()
    return config


@router.get("/vector-store/stats", response_model=VectorStoreStatsResponse)
async def get_vector_store_stats_endpoint():
    """Get ChromaDB collection statistics"""
    stats = get_vector_store_stats()
    return stats


@router.post("/vector-store/search", response_model=VectorSearchResponse)
async def test_vector_search_endpoint(request: VectorSearchRequest):
    """Test semantic search"""
    try:
        results = test_vector_search(
            query=request.query,
            doc_type=request.doc_type,
            top_k=request.top_k
        )
        return {
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Smart Matching Analytics
# ============================================================================

@router.get("/smart-matching/analytics", response_model=SmartMatchingAnalyticsResponse)
async def get_smart_matching_analytics_endpoint(
    time_range: str = Query("all", pattern="^(7days|30days|90days|all)$")
):
    """Get smart matching analytics"""
    analytics = get_smart_matching_analytics(time_range)
    return analytics
