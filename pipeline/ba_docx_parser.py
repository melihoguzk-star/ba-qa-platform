"""
BA Doküman Parser — Adım 2: Kahve Dünyası Formatı

read_docx_structured() çıktısını alır ve Kahve Dünyası stilinde
BA dokümanını platform JSON şemasına dönüştürür.

Doküman yapısı:
  H1: Üst bölümler (Proje Açıklaması, Kapsam, Gereksinimler)
  H2: Ekran/Modül  (Splash, Login, OTP, ...)
  H3: Alt bölüm   (Açıklama, Tasarım Dosyaları, İş Akışı, ...)
  H4-H6: Daha derin alt akışlar
  Bullet L0-L3: İş kuralları (nested)
"""
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class BADocxParser:
    """Kahve Dünyası stilinde BA dokümanlarını parse eder."""

    # H1 meta bölüm pattern'leri
    META_PATTERNS = {
        'proje_aciklamasi': re.compile(r'proje\s+açıklama', re.IGNORECASE),
        'proje_kapsami':    re.compile(r'proje\s+kapsam',   re.IGNORECASE),
    }

    # "Mobil Uygulama Gereksinimleri" H1 → ekran parse moduna geç
    REQUIREMENTS_PATTERN = re.compile(
        r'(mobil\s+uygulama\s+gereksinim|uygulama\s+gereksinim)', re.IGNORECASE
    )

    # H3 özel alt-bölüm pattern'leri
    ACIKLAMA_PATTERN = re.compile(r'^açıklama$',            re.IGNORECASE)
    TASARIM_PATTERN  = re.compile(r'^tasarım\s+dosyalar',   re.IGNORECASE)

    # ------------------------------------------------------------------
    # Ana metot
    # ------------------------------------------------------------------

    def parse(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        read_docx_structured() çıktısını Kahve Dünyası platform JSON'una dönüştür.

        Returns:
            {
                "meta": {
                    "proje_aciklamasi": "...",
                    "proje_kapsami": "...",
                    "platform": "iOS | Android | Web",
                    "dil_destegi": "Türkçe, İngilizce"
                },
                "ekranlar": [
                    {
                        "ekran_adi": "Splash",
                        "aciklama": "",
                        "tasarim_dosyalari": [],
                        "is_akislari": [
                            {
                                "baslik": "İş Akışı",
                                "kurallar": [
                                    {
                                        "kural": "...",
                                        "level": 0,
                                        "alt_detaylar": [...],
                                        "bold_refs": [],
                                        "links": []
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "linkler": {
                    "lottie": [...],
                    "google_docs": [...],
                    "figma": [],
                    "diger": []
                }
            }
        """
        return {
            "meta":    self._extract_meta(elements),
            "ekranlar": self._extract_screens(elements),
            "linkler": self._collect_all_links(elements),
        }

    # ------------------------------------------------------------------
    # Meta çıkarımı — Proje Açıklaması + Kapsam
    # ------------------------------------------------------------------

    def _extract_meta(self, elements: List[Dict]) -> Dict:
        """H1 Proje Açıklaması ve Proje Kapsamı altındaki paragrafları topla."""
        meta = {
            "proje_aciklamasi": "",
            "proje_kapsami":    "",
            "platform":         "",
            "dil_destegi":      "",
        }
        buffers = {k: [] for k in self.META_PATTERNS}
        current = None  # aktif meta bölümü key'i

        for el in elements:
            if el['type'] == 'heading':
                if el['level'] == 1:
                    matched = None
                    for key, pat in self.META_PATTERNS.items():
                        if pat.search(el['text']):
                            matched = key
                            break
                    current = matched
                continue  # heading'ler içerik değil

            if current is None:
                continue

            text = el.get('text', '')
            if el['type'] in ('paragraph', 'list_item') and text:
                buffers[current].append(text)
                # Platform ve dil desteği satırı tespiti
                if not meta['platform'] and re.search(r'(ios|android|web)', text, re.IGNORECASE):
                    meta['platform'] = text
                if not meta['dil_destegi'] and re.search(r'(türkçe|ingilizce)', text, re.IGNORECASE):
                    meta['dil_destegi'] = text

        meta['proje_aciklamasi'] = ' '.join(buffers['proje_aciklamasi']).strip()
        meta['proje_kapsami']    = ' '.join(buffers['proje_kapsami']).strip()
        return meta

    # ------------------------------------------------------------------
    # Ekran çıkarımı — H2=ekran, H3=alt bölüm
    # ------------------------------------------------------------------

    def _extract_screens(self, elements: List[Dict]) -> List[Dict]:
        """
        'Mobil Uygulama Gereksinimleri' H1'inden itibaren H2 heading'leri
        ekran sınırı olarak kullanarak ekranları ayır.
        """
        screens    = []
        in_req     = False       # requirements bölümünde miyiz?
        screen     = None        # mevcut ekran dict
        subsection = None        # mevcut H3+ başlığı ('aciklama', 'tasarim', veya string)
        buf: List[Dict] = []     # mevcut is_akisi için bullet item buffer

        for el in elements:
            if el['type'] == 'heading':
                level = el['level']
                text  = el['text']

                if level == 1:
                    if self.REQUIREMENTS_PATTERN.search(text):
                        in_req = True
                    else:
                        # Farklı bir H1 → requirements bölümü kapanır
                        if in_req and screen is not None:
                            self._flush_subsection(screen, subsection, buf)
                            screens.append(screen)
                            screen = None
                            subsection = None
                            buf = []
                        in_req = False
                    continue

                if not in_req:
                    continue

                if level == 2:
                    # Önceki ekranı kapat
                    if screen is not None:
                        self._flush_subsection(screen, subsection, buf)
                        screens.append(screen)
                    screen = {
                        "ekran_adi":         text,
                        "aciklama":          "",
                        "tasarim_dosyalari": [],
                        "is_akislari":       [],
                    }
                    subsection = None
                    buf        = []

                elif level >= 3 and screen is not None:
                    # Önceki alt bölümü kapat
                    self._flush_subsection(screen, subsection, buf)
                    buf = []

                    if self.ACIKLAMA_PATTERN.match(text):
                        subsection = 'aciklama'
                    elif self.TASARIM_PATTERN.match(text):
                        subsection = 'tasarim'
                    else:
                        subsection = text  # is_akisi başlığı

                continue  # heading işlendi, içerik satırına geçme

            # İçerik elementleri
            if not in_req or screen is None:
                continue

            if el['type'] == 'list_item':
                self._route_list_item(screen, subsection, buf, el)
            elif el['type'] == 'paragraph':
                self._route_paragraph(screen, subsection, el)

        # Son ekranı flush et
        if screen is not None:
            self._flush_subsection(screen, subsection, buf)
            screens.append(screen)

        return screens

    def _route_list_item(
        self, screen: Dict, subsection: Optional[str], buf: List, el: Dict
    ) -> None:
        """List item'ı doğru hedefe yönlendir."""
        if subsection == 'aciklama':
            screen['aciklama'] = (screen['aciklama'] + ' ' + el['text']).strip()
        elif subsection == 'tasarim':
            links = el.get('links', [])
            if links:
                screen['tasarim_dosyalari'].extend(links)
            else:
                screen['tasarim_dosyalari'].append(el['text'])
        elif subsection is not None:
            buf.append(el)

    def _route_paragraph(
        self, screen: Dict, subsection: Optional[str], el: Dict
    ) -> None:
        """Paragraph'ı doğru hedefe yönlendir."""
        if subsection == 'aciklama':
            screen['aciklama'] = (screen['aciklama'] + ' ' + el['text']).strip()
        elif subsection == 'tasarim':
            links = el.get('links', [])
            screen['tasarim_dosyalari'].extend(links)

    def _flush_subsection(
        self, screen: Dict, subsection: Optional[str], buf: List[Dict]
    ) -> None:
        """Mevcut is_akisi buffer'ını rule tree'ye çevirip ekrana ekle."""
        if subsection is None or subsection in ('aciklama', 'tasarim'):
            return
        kurallar = self._build_rule_tree(buf) if buf else []
        screen['is_akislari'].append({"baslik": subsection, "kurallar": kurallar})

    # ------------------------------------------------------------------
    # Rule tree — stack-based flat → nested dönüşüm
    # ------------------------------------------------------------------

    def _build_rule_tree(self, items: List[Dict]) -> List[Dict]:
        """
        Flat bullet list → nested ağaç yapısı. Stack-based algoritma.

        Input:  [L0, L1, L1, L2, L0, L1]
        Output: [
            {kural: ..., level: 0, alt_detaylar: [
                {kural: ..., level: 1, alt_detaylar: []},
                {kural: ..., level: 1, alt_detaylar: [
                    {kural: ..., level: 2, alt_detaylar: []}
                ]}
            ]},
            {kural: ..., level: 0, alt_detaylar: [
                {kural: ..., level: 1, alt_detaylar: []}
            ]}
        ]
        """
        tree  = []
        stack: List[tuple] = []  # (level, node) çiftleri

        for item in items:
            node = {
                "kural":        item.get("text", ""),
                "level":        item.get("level", 0),
                "alt_detaylar": [],
                "bold_refs":    item.get("bold_segments", []),
                "links":        item.get("links", []),
            }
            level = node["level"]

            # Stack'i mevcut level'dan büyük veya eşit olanları temizle
            while stack and stack[-1][0] >= level:
                stack.pop()

            if stack:
                stack[-1][1]["alt_detaylar"].append(node)
            else:
                tree.append(node)

            stack.append((level, node))

        return tree

    # ------------------------------------------------------------------
    # Link kategorilendirme
    # ------------------------------------------------------------------

    def _collect_all_links(self, elements: List[Dict]) -> Dict[str, List[str]]:
        """Tüm elementlerden link topla ve kategorize et."""
        result: Dict[str, List[str]] = {
            "lottie":      [],
            "google_docs": [],
            "figma":       [],
            "diger":       [],
        }
        seen: set = set()

        for el in elements:
            for url in el.get("links", []):
                if url in seen:
                    continue
                seen.add(url)
                if "lottiefiles.com" in url:
                    result["lottie"].append(url)
                elif "docs.google.com" in url:
                    result["google_docs"].append(url)
                elif "figma.com" in url:
                    result["figma"].append(url)
                else:
                    result["diger"].append(url)

        return result
