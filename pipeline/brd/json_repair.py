"""Güçlendirilmiş JSON repair — truncated ve malformed JSON recovery."""
import json
import re


def parse_ai_json(content: str, stop_reason: str = "") -> dict:
    """AI yanıtından JSON parse eder. Birden fazla strateji dener."""
    text = content.strip()

    # Markdown code block temizle
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    end_block = text.rfind("```")
    if end_block > 0:
        text = text[:end_block]
    text = text.strip()

    first_brace = text.find("{")
    if first_brace == -1:
        raise ValueError(f"JSON bulunamadı - {{ yok. İlk 300 karakter: {content[:300]}")

    # ── STRATEJİ 1: Tam JSON parse (first { → last }) ──
    last_brace = text.rfind("}")
    if last_brace > first_brace:
        json_str = text[first_brace:last_brace + 1]
        result = _try_parse(json_str)
        if result is not None:
            return result

        # Temizleyip tekrar dene
        result = _try_parse(_clean_json(json_str))
        if result is not None:
            return result

    # ── STRATEJİ 2: Satır satır geriye git, } bul ──
    lines = text[first_brace:].split("\n")
    for i in range(len(lines) - 1, 0, -1):
        candidate = "\n".join(lines[:i + 1]).rstrip().rstrip(",")
        if candidate.endswith("}"):
            result = _try_parse(_clean_json(candidate))
            if result is not None:
                result["_repaired"] = "line_backtrack"
                return result

    # ── STRATEJİ 3: Bracket balancing (agresif) ──
    partial = _clean_json(text[first_brace:])
    result = _bracket_balance_repair(partial)
    if result is not None:
        result["_repaired"] = "bracket_balance"
        return result

    # ── STRATEJİ 4: Kademeli comma-cut + bracket balance ──
    for _ in range(30):
        last_comma = partial.rfind(",")
        if last_comma > len(partial) * 0.2:
            partial = partial[:last_comma]
            result = _bracket_balance_repair(partial)
            if result is not None:
                result["_truncated"] = True
                result["_stop_reason"] = stop_reason
                return result
        else:
            break

    # ── STRATEJİ 5: String truncation sonrası balance ──
    # Açık string'i kapat
    partial2 = _clean_json(text[first_brace:])
    if partial2.count('"') % 2 != 0:
        partial2 = partial2 + '"'
    result = _bracket_balance_repair(partial2)
    if result is not None:
        result["_repaired"] = "string_close"
        return result

    raise ValueError(
        f"JSON parse hatası (tüm stratejiler başarısız) | "
        f"stop_reason: {stop_reason} | Son 200: {content[-200:]}"
    )


def _try_parse(text: str) -> dict | None:
    """JSON parse dene, başarısızsa None döner."""
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _bracket_balance_repair(text: str) -> dict | None:
    """Açık bracket'ları kapatarak JSON repair."""
    # Trailing comma temizle
    text = re.sub(r",\s*$", "", text)

    open_brackets = text.count("[") - text.count("]")
    open_braces = text.count("{") - text.count("}")

    # Açık string varsa kapat
    in_string = False
    escape = False
    for ch in text:
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_string = not in_string

    if in_string:
        text = text + '"'

    # Trailing comma sonra bracket kapatma
    text = re.sub(r",\s*$", "", text)

    suffix = "]" * max(0, open_brackets) + "}" * max(0, open_braces)
    return _try_parse(text + suffix)


def _clean_json(text: str) -> str:
    """JSON string'i temizle."""
    # Control chars
    text = re.sub(r"[\x00-\x1f]", " ", text)
    # Trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    # Double commas
    text = re.sub(r",\s*,", ",", text)
    return text
