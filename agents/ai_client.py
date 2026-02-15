"""AI model çağrıları: Claude Sonnet 4 (üretim) + Gemini 2.5 Flash (QA hakem).

Sonnet → chunk üretim (yüksek kalite doküman üretimi)
Flash  → QA değerlendirme (maliyet-etkin kalite kontrol)
"""
import json
import anthropic
from google import genai
from google.genai import types as genai_types

from utils.config import SONNET_MODEL, GEMINI_MODEL, CHUNK_OUTPUT_TOKEN_LIMIT, QA_OUTPUT_TOKEN_LIMIT, is_anthropic_model, is_gemini_model
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
        response = client.models.generate_content(
            model=model or GEMINI_MODEL,
            contents=user_content,
            config=genai_types.GenerateContentConfig(
                system_instruction=clean_prompt,
                max_output_tokens=max_tokens,
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


def call_ai(system_prompt: str, user_content: str, anthropic_key: str, gemini_key: str,
            model: str, max_tokens: int = CHUNK_OUTPUT_TOKEN_LIMIT) -> dict:
    """Unified AI call that routes to Anthropic or Gemini based on model ID."""
    if is_anthropic_model(model):
        return call_sonnet(system_prompt, user_content, anthropic_key, max_tokens, model)
    elif is_gemini_model(model):
        return call_gemini(system_prompt, user_content, gemini_key, max_tokens, model)
    else:
        raise ValueError(f"Unknown model provider for model: {model}")
