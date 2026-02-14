"""AI model çağrıları: Claude Sonnet 4 (üretim) + Gemini 2.5 Flash (QA hakem).

Sonnet → chunk üretim (yüksek kalite doküman üretimi)
Flash  → QA değerlendirme (maliyet-etkin kalite kontrol)
"""
import json
import anthropic
from google import genai
from google.genai import types as genai_types

from utils.config import SONNET_MODEL, GEMINI_MODEL, CHUNK_OUTPUT_TOKEN_LIMIT, QA_OUTPUT_TOKEN_LIMIT
from pipeline.json_repair import parse_ai_json


def call_sonnet(system_prompt: str, user_content: str, api_key: str, max_tokens: int = CHUNK_OUTPUT_TOKEN_LIMIT) -> dict:
    """Claude Sonnet 4 ile içerik üretimi. JSON döner."""
    # Python {{ }} escape'lerini düz { } yap (prompt'lar .format() kullanmıyorsa)
    clean_prompt = system_prompt.replace("{{", "{").replace("}}", "}")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=max_tokens,
        system=clean_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    content_text = response.content[0].text
    stop_reason = response.stop_reason or ""
    return parse_ai_json(content_text, stop_reason)


def call_gemini(system_prompt: str, user_content: str, api_key: str, max_tokens: int = QA_OUTPUT_TOKEN_LIMIT) -> dict:
    """Gemini 2.5 Flash ile QA değerlendirme. JSON döner."""
    clean_prompt = system_prompt.replace("{{", "{").replace("}}", "}")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
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
