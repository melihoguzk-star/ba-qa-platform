"""
AI Service — Wraps agents/ai_client.py for unified AI model access
"""
from typing import Optional, Dict, Any, List
import os


class AIService:
    """
    Unified AI service for Claude and Gemini models.
    Wraps agents/ai_client.py functionality.
    """

    def __init__(self):
        """Initialize AI service with API keys from environment"""
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate text using specified AI model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model ID (claude-* or gemini-*)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum output tokens

        Returns:
            Generated text
        """
        from agents.ai_client import generate_text as _generate_text

        return _generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def generate_with_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate JSON response using AI model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model ID
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            Parsed JSON response
        """
        from agents.ai_client import generate_with_json as _generate_with_json

        return _generate_with_json(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> List[str]:
        """
        Generate multiple responses in parallel.

        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt
            model: Model ID
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            List of generated texts
        """
        # Sequential for now, can be parallelized later
        results = []
        for prompt in prompts:
            result = self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            results.append(result)
        return results


# Singleton instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
