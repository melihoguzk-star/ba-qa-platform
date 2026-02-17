"""
DOCX Import Orchestrator — Adım 3

Upload edilen DOCX dosyasının şablon tipini otomatik algılar,
uygun parser'ı seçer ve confidence score hesaplar.

Desteklenen şablon tipleri:
  loodos_ba_bullet — Kahve Dünyası formatı (nested bullet list, H2=ekran, H3=alt bölüm)
  loodos_ba_table  — Loodos BA tablo formatı (Tarih|Yazar|... tablosu, 1.1 Amaç, vb.)
  generic          — Genel doküman (rule-based heading parser fallback)
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Loodos BA bullet formatı için H3 işaret başlıkları
_LOODOS_BULLET_MARKERS = {"Açıklama", "İş Akışı", "Tasarım Dosyaları"}


def _tr_lower(s: str) -> str:
    """Turkish-aware lowercase: İ→i, I→ı, diğerleri standart lower()."""
    return s.replace('İ', 'i').replace('I', 'ı').lower()


class DocxImportOrchestrator:
    """
    DOCX dosyasını okur, şablon tipini algılar, uygun parser ile parse eder.

    Kullanım:
        orchestrator = DocxImportOrchestrator()
        result = orchestrator.import_docx(file_bytes)
    """

    def import_docx(
        self,
        file_content: bytes,
        doc_type: str = "auto",
        use_ai_fallback: bool = True,
        gemini_key: str = "",
    ) -> Dict[str, Any]:
        """
        DOCX bytes'ını parse edip sonuç dict'i döndür.

        Args:
            file_content:    .docx dosyasının binary içeriği
            doc_type:        "auto" | "ba" | "qa" — "auto" ise şablona göre seçilir
            use_ai_fallback: Düşük confidence'ta AI fallback kullanılsın mı?
            gemini_key:      AI fallback için Gemini API key (opsiyonel)

        Returns:
            {
                "success":      bool,
                "doc_type":     "ba" | "qa",
                "template":     "loodos_ba_bullet" | "loodos_ba_table" | "generic",
                "content_json": {...},
                "confidence":   0.0–1.0,
                "stats":        {"headings": int, "screens": int, "list_items": int,
                                 "paragraphs": int, "tables": int, "links": int},
                "warnings":     [str, ...]
            }
        """
        from pipeline.document_reader import read_docx_structured

        elements = read_docx_structured(file_content)
        stats    = self._calculate_stats(elements)
        template = self._detect_template(elements, stats)

        effective_doc_type = doc_type if doc_type != "auto" else "ba"

        if template in ("loodos_ba_bullet", "loodos_ba_table"):
            from pipeline.ba_docx_parser import BADocxParser
            content_json = BADocxParser().parse(elements)
            confidence   = self._calculate_confidence(content_json, stats)
        else:
            # Generic fallback — heading-based text parser
            try:
                from pipeline.document_reader import read_docx
                from pipeline.document_parser_v2 import parse_text_to_json
                text         = read_docx(file_content)
                content_json = parse_text_to_json(text, effective_doc_type)
                confidence   = 0.4
            except Exception as exc:
                logger.warning("Generic parser failed: %s", exc)
                content_json = {"ekranlar": [], "meta": {}, "linkler": {}}
                confidence   = 0.1

        # AI fallback — düşük confidence için (ileride implement edilecek)
        if confidence < 0.5 and use_ai_fallback and gemini_key:
            logger.info("AI fallback triggered (confidence=%.2f)", confidence)

        warnings = self._generate_warnings(content_json, stats)

        return {
            "success":      confidence > 0.3,
            "doc_type":     effective_doc_type,
            "template":     template,
            "content_json": content_json,
            "confidence":   confidence,
            "stats":        stats,
            "warnings":     warnings,
        }

    # ------------------------------------------------------------------
    # Şablon tespiti
    # ------------------------------------------------------------------

    def _detect_template(self, elements: List[Dict], stats: Dict) -> str:
        """
        Element listesinden şablon tipini algıla.

        Kural 1 — loodos_ba_bullet:
            H3 başlıkları arasında ≥2 Loodos işaret başlığı varsa
            (Açıklama, İş Akışı, Tasarım Dosyaları) VE list_items > tables

        Kural 2 — loodos_ba_table:
            Tablolar > 3 (tablo ağırlıklı doküman)

        Kural 3 — generic:
            Hiçbirine uymadı
        """
        h3_texts = {
            e["text"]
            for e in elements
            if e["type"] == "heading" and e.get("level") == 3
        }

        # Turkish-aware case-insensitive karşılaştırma
        h3_lower      = {_tr_lower(t.strip()) for t in h3_texts}
        markers_lower = {_tr_lower(m) for m in _LOODOS_BULLET_MARKERS}
        matched_count = sum(1 for m in markers_lower if m in h3_lower)

        if matched_count >= 2 and stats["list_items"] > stats.get("tables", 0):
            return "loodos_ba_bullet"

        if stats.get("tables", 0) > 3:
            return "loodos_ba_table"

        return "generic"

    # ------------------------------------------------------------------
    # İstatistik hesabı
    # ------------------------------------------------------------------

    def _calculate_stats(self, elements: List[Dict]) -> Dict:
        """Element listesinden doküman istatistiklerini hesapla."""
        headings = [e for e in elements if e["type"] == "heading"]
        return {
            "headings":   len(headings),
            "screens":    len([e for e in headings if e.get("level") == 2]),
            "list_items": len([e for e in elements if e["type"] == "list_item"]),
            "paragraphs": len([e for e in elements if e["type"] == "paragraph"]),
            "tables":     len([e for e in elements if e["type"] == "table"]),
            "links":      sum(len(e.get("links", [])) for e in elements),
        }

    # ------------------------------------------------------------------
    # Confidence skoru
    # ------------------------------------------------------------------

    def _calculate_confidence(self, content_json: Dict, stats: Dict) -> float:
        """
        Parse kalitesine göre 0.0–1.0 arası confidence skoru hesapla.

        Puan tablosu:
          +0.30  En az 1 ekran çıkarıldı
          +0.20  5+ ekran çıkarıldı
          +0.30  En az 1 ekranda iş kuralı var
          +0.20  İş kuralı olan ekran oranıyla ağırlıklı
        """
        score    = 0.0
        ekranlar = content_json.get("ekranlar", [])

        if not ekranlar:
            return score

        score += 0.3
        if len(ekranlar) >= 5:
            score += 0.2

        screens_with_rules = sum(
            1 for e in ekranlar
            if any(ia.get("kurallar") for ia in e.get("is_akislari", []))
        )
        if screens_with_rules > 0:
            score += 0.3

        ratio  = screens_with_rules / len(ekranlar)
        score += ratio * 0.2

        return min(score, 1.0)

    # ------------------------------------------------------------------
    # Uyarı üretimi
    # ------------------------------------------------------------------

    def _generate_warnings(self, content_json: Dict, stats: Dict) -> List[str]:
        """Parse sonucuna göre kullanıcı uyarıları oluştur."""
        warnings = []

        for ekran in content_json.get("ekranlar", []):
            has_rules = any(
                ia.get("kurallar") for ia in ekran.get("is_akislari", [])
            )
            if not has_rules:
                warnings.append(
                    f"'{ekran['ekran_adi']}' ekranında iş akışı bulunamadı"
                )

        if stats.get("links", 0) == 0:
            warnings.append("Doküman içinde hiç link bulunamadı")

        return warnings
