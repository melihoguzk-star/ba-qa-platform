"""
API Key Manager - Multi-key rotation system for handling quota limits.
"""
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import json


class APIKeyManager:
    """Manages multiple API keys with automatic rotation on quota errors."""
    
    def __init__(self, keys: List[str], provider: str = "gemini"):
        """
        Initialize key manager with a pool of API keys.
        
        Args:
            keys: List of API keys to manage
            provider: Provider name ('gemini' or 'anthropic')
        """
        self.keys = keys if keys else []
        self.provider = provider
        self.current_index = 0
        self.failed_keys = set()  # Set of key hashes that failed
        self.usage_stats = {}  # key_hash -> {requests: int, errors: int, last_used: datetime}
        
        # Initialize stats for all keys
        for key in self.keys:
            key_hash = self._hash_key(key)
            if key_hash not in self.usage_stats:
                self.usage_stats[key_hash] = {
                    "requests": 0,
                    "errors": 0,
                    "last_used": None,
                    "last_error": None,
                    "status": "active"
                }
    
    def _hash_key(self, key: str) -> str:
        """Create SHA256 hash of key for privacy."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def get_next_key(self) -> Optional[str]:
        """
        Get next available key, skip failed ones.
        Uses least-used strategy by default.
        
        Returns:
            Next available API key or None if all exhausted
        """
        if not self.keys:
            return None
        
        # Find least used active key
        available_keys = []
        for key in self.keys:
            key_hash = self._hash_key(key)
            if key_hash not in self.failed_keys:
                stats = self.usage_stats.get(key_hash, {})
                available_keys.append((key, stats.get("requests", 0)))
        
        if not available_keys:
            return None  # All keys exhausted
        
        # Sort by usage count (least used first)
        available_keys.sort(key=lambda x: x[1])
        return available_keys[0][0]
    
    def mark_key_failed(self, key: str, error: str):
        """
        Mark key as failed (quota exceeded, invalid, etc.).
        
        Args:
            key: API key that failed
            error: Error message
        """
        key_hash = self._hash_key(key)
        self.failed_keys.add(key_hash)
        
        if key_hash in self.usage_stats:
            self.usage_stats[key_hash]["status"] = "quota_exceeded"
            self.usage_stats[key_hash]["last_error"] = error
            self.usage_stats[key_hash]["errors"] += 1
    
    def mark_key_invalid(self, key: str, error: str):
        """
        Mark key as permanently invalid (authentication error).
        
        Args:
            key: API key that is invalid
            error: Error message
        """
        key_hash = self._hash_key(key)
        self.failed_keys.add(key_hash)
        
        if key_hash in self.usage_stats:
            self.usage_stats[key_hash]["status"] = "invalid"
            self.usage_stats[key_hash]["last_error"] = error
    
    def record_success(self, key: str):
        """
        Record successful API call.
        
        Args:
            key: API key that succeeded
        """
        key_hash = self._hash_key(key)
        
        if key_hash in self.usage_stats:
            self.usage_stats[key_hash]["requests"] += 1
            self.usage_stats[key_hash]["last_used"] = datetime.now()
    
    def reset_key(self, key: str):
        """
        Reset key status (for daily quota reset).
        
        Args:
            key: API key to reset
        """
        key_hash = self._hash_key(key)
        
        if key_hash in self.failed_keys:
            self.failed_keys.remove(key_hash)
        
        if key_hash in self.usage_stats:
            self.usage_stats[key_hash]["status"] = "active"
            self.usage_stats[key_hash]["last_error"] = None
    
    def reset_all_keys(self):
        """Reset all keys (daily quota reset)."""
        self.failed_keys.clear()
        for key_hash in self.usage_stats:
            self.usage_stats[key_hash]["status"] = "active"
            self.usage_stats[key_hash]["last_error"] = None
    
    def get_stats(self) -> Dict:
        """
        Get usage statistics for all keys.
        
        Returns:
            Dictionary with stats for each key
        """
        stats = {
            "total_keys": len(self.keys),
            "active_keys": len(self.keys) - len(self.failed_keys),
            "failed_keys": len(self.failed_keys),
            "total_requests": sum(s.get("requests", 0) for s in self.usage_stats.values()),
            "total_errors": sum(s.get("errors", 0) for s in self.usage_stats.values()),
            "keys": []
        }
        
        for key in self.keys:
            key_hash = self._hash_key(key)
            key_stats = self.usage_stats.get(key_hash, {})
            
            stats["keys"].append({
                "key_preview": f"{key[:8]}***{key[-4:]}",
                "key_hash": key_hash,
                "status": key_stats.get("status", "unknown"),
                "requests": key_stats.get("requests", 0),
                "errors": key_stats.get("errors", 0),
                "last_used": key_stats.get("last_used"),
                "last_error": key_stats.get("last_error")
            })
        
        return stats
    
    def has_available_keys(self) -> bool:
        """Check if there are any available keys."""
        return len(self.keys) > len(self.failed_keys)
    
    def get_active_key_count(self) -> int:
        """Get count of active (non-failed) keys."""
        return len(self.keys) - len(self.failed_keys)


def is_quota_error(error: Exception) -> bool:
    """
    Detect if error is quota/rate limit related.
    
    Args:
        error: Exception to check
        
    Returns:
        True if error is quota-related
    """
    error_str = str(error).lower()
    quota_indicators = [
        "resource_exhausted",
        "429",
        "quota",
        "rate limit",
        "too many requests",
        "quota exceeded"
    ]
    
    return any(indicator in error_str for indicator in quota_indicators)


def is_auth_error(error: Exception) -> bool:
    """
    Detect if error is authentication related.
    
    Args:
        error: Exception to check
        
    Returns:
        True if error is auth-related
    """
    error_str = str(error).lower()
    auth_indicators = [
        "invalid api key",
        "authentication",
        "unauthorized",
        "401",
        "403",
        "api key not valid"
    ]
    
    return any(indicator in error_str for indicator in auth_indicators)
