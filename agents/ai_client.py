"""AI model çağrıları: Claude Sonnet 4 (üretim) + Gemini 2.5 Flash (QA hakem).

Sonnet → chunk üretim (yüksek kalite doküman üretimi)
Flash  → QA değerlendirme (maliyet-etkin kalite kontrol)
"""
import json
import anthropic
from google import genai
from google.genai import types as genai_types

from utils.config import SONNET_MODEL, GEMINI_MODEL, CHUNK_OUTPUT_TOKEN_LIMIT, QA_OUTPUT_TOKEN_LIMIT, is_anthropic_model, is_gemini_model, get_gemini_keys
from utils.key_manager import APIKeyManager, is_quota_error, is_auth_error
from pipeline.brd.json_repair import parse_ai_json


def call_sonnet(system_prompt: str, user_content: str, api_key: str, max_tokens: int = CHUNK_OUTPUT_TOKEN_LIMIT, model: str | None = None) -> dict:
    """Claude ile içerik üretimi. JSON döner."""
    try:
        # Python {{ }} escape'lerini düz { } yap (prompt'lar .format() kullanmıyorsa)
        clean_prompt = system_prompt.replace("{{", "{").replace("}}", "}")
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model or SONNET_MODEL,
            max_tokens=max_tokens,
            system=clean_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        content_text = response.content[0].text
        stop_reason = response.stop_reason or ""
        return parse_ai_json(content_text, stop_reason)
    except anthropic.AuthenticationError as e:
        raise Exception(f"❌ Anthropic API key hatası: API anahtarınız geçersiz.\n\nDetay: {str(e)}")
    except anthropic.RateLimitError as e:
        raise Exception(f"❌ Anthropic rate limit hatası: Çok fazla istek gönderildi. Lütfen biraz bekleyin.\n\nDetay: {str(e)}")
    except anthropic.APIError as e:
        error_msg = str(e)
        if "overloaded" in error_msg.lower():
            raise Exception(f"❌ Anthropic API aşırı yüklü: Sunucular yoğun, lütfen tekrar deneyin.\n\nDetay: {error_msg}")
        else:
            raise Exception(f"❌ Anthropic API hatası: {error_msg}")
    except Exception as e:
        raise Exception(f"❌ Claude API hatası: {str(e)}")


def call_gemini(system_prompt: str, user_content: str, api_key: str, max_tokens: int = QA_OUTPUT_TOKEN_LIMIT, model: str | None = None) -> dict:
    """Gemini ile QA değerlendirme. JSON döner."""
    try:
        clean_prompt = system_prompt.replace("{{", "{").replace("}}", "}")
        client = genai.Client(api_key=api_key)
        
        # Gemini 2.5 Flash max output: 8192 tokens
        # Cap max_tokens to prevent MAX_TOKENS errors
        capped_max_tokens = min(max_tokens, 8192)
        
        response = client.models.generate_content(
            model=model or GEMINI_MODEL,
            contents=user_content,
            config=genai_types.GenerateContentConfig(
                system_instruction=clean_prompt,
                max_output_tokens=capped_max_tokens,
                temperature=0.3,
            ),
        )
        content_text = response.text or ""
        stop_reason = ""
        if response.candidates and response.candidates[0].finish_reason:
            fr = response.candidates[0].finish_reason
            if hasattr(fr, 'name'):
                stop_reason = fr.name
            elif str(fr) == "2" or "MAX_TOKENS" in str(fr):
                stop_reason = "max_tokens"
        return parse_ai_json(content_text, stop_reason)
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error messages
        if "quota" in error_msg.lower() or "limit" in error_msg.lower():
            raise Exception(f"❌ Gemini API kota/limit hatası: API kotanız dolmuş veya rate limit aşılmış olabilir. Lütfen biraz bekleyin veya API ayarlarınızı kontrol edin.\n\nDetay: {error_msg}")
        elif "api" in error_msg.lower() and "key" in error_msg.lower():
            raise Exception(f"❌ Gemini API key hatası: API anahtarınız geçersiz veya yetkilendirilmemiş.\n\nDetay: {error_msg}")
        elif "content" in error_msg.lower() and ("filter" in error_msg.lower() or "safety" in error_msg.lower()):
            raise Exception(f"❌ Gemini içerik filtresi: İçerik güvenlik politikası tarafından engellenmiş olabilir.\n\nDetay: {error_msg}")
        else:
            raise Exception(f"❌ Gemini API hatası: {error_msg}")


def call_gemini_with_rotation(system_prompt: str, user_content: str, max_tokens: int = QA_OUTPUT_TOKEN_LIMIT, model: str | None = None) -> dict:
    """
    Gemini with automatic key rotation on quota errors.
    Uses multiple API keys if available, rotates on quota exceeded.
    """
    keys = get_gemini_keys()
    
    if not keys:
        raise Exception("❌ Gemini API key bulunamadı. Lütfen secrets.toml dosyasına GEMINI_API_KEY veya GEMINI_API_KEYS ekleyin.")
    
    # If only one key, use regular call_gemini
    if len(keys) == 1:
        return call_gemini(system_prompt, user_content, keys[0], max_tokens, model)
    
    # Multiple keys: use rotation
    key_manager = APIKeyManager(keys, provider="gemini")
    max_retries = len(keys)
    
    for attempt in range(max_retries):
        current_key = key_manager.get_next_key()
        
        if not current_key:
            # All keys exhausted
            raise Exception(f"❌ Tüm Gemini API keyleri tükendi ({len(keys)} key denendi). Lütfen quota reset'i bekleyin veya yeni key ekleyin.")
        
        try:
            response = call_gemini(system_prompt, user_content, current_key, max_tokens, model)
            key_manager.record_success(current_key)
            return response
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a quota error
            if is_quota_error(e):
                key_manager.mark_key_failed(current_key, error_msg)
                if attempt < max_retries - 1:
                    # Try next key
                    continue
                else:
                    # All keys exhausted
                    raise Exception(f"❌ Tüm Gemini API keyleri quota limitine ulaştı. Lütfen quota reset'i bekleyin veya yeni key ekleyin.\n\nSon hata: {error_msg}")
            elif is_auth_error(e):
                # Auth error - mark as invalid and try next
                key_manager.mark_key_invalid(current_key, error_msg)
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception(f"❌ Tüm Gemini API keyleri geçersiz. Lütfen key'lerinizi kontrol edin.\n\nSon hata: {error_msg}")
            else:
                # Other errors - don't rotate, just raise
                raise e


def call_ai(system_prompt: str, user_content: str, anthropic_key: str, gemini_key: str,
            model: str, max_tokens: int = CHUNK_OUTPUT_TOKEN_LIMIT) -> dict:
    """Unified AI call that routes to Anthropic or Gemini based on model ID."""
    if is_anthropic_model(model):
        return call_sonnet(system_prompt, user_content, anthropic_key, max_tokens, model)
    elif is_gemini_model(model):
        # Gemini has 8192 token output limit, cap it
        capped_tokens = min(max_tokens, 8192)
        # Use rotation-enabled function
        return call_gemini_with_rotation(system_prompt, user_content, capped_tokens, model)
    else:
        raise ValueError(f"Unknown model provider for model: {model}")
