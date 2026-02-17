"""
Tests for BADocxParser — Adım 2: Kahve Dünyası BA Doküman Parser
Bullet-list tabanlı, H2=ekran, H3=alt bölüm, nested rule tree
"""
import pytest
from pipeline.ba_docx_parser import BADocxParser


# ---------------------------------------------------------------------------
# Helpers — Sentetik element listeleri
# ---------------------------------------------------------------------------

def h(level: int, text: str) -> dict:
    return {"type": "heading", "level": level, "text": text}

def p(text: str, bold_segments=None, links=None) -> dict:
    return {"type": "paragraph", "text": text,
            "bold_segments": bold_segments or [], "links": links or []}

def li(level: int, text: str, bold_segments=None, links=None) -> dict:
    return {"type": "list_item", "level": level, "text": text,
            "bold_segments": bold_segments or [], "links": links or []}


# ---------------------------------------------------------------------------
# _build_rule_tree — Stack-based flat→nested dönüşüm
# ---------------------------------------------------------------------------

class TestBuildRuleTree:
    def _tree(self, items):
        return BADocxParser()._build_rule_tree(items)

    def test_empty_input_returns_empty(self):
        assert self._tree([]) == []

    def test_single_l0_item(self):
        result = self._tree([li(0, "Tek kural")])
        assert len(result) == 1
        assert result[0]['kural'] == "Tek kural"
        assert result[0]['level'] == 0
        assert result[0]['alt_detaylar'] == []

    def test_multiple_l0_items_flat(self):
        result = self._tree([
            li(0, "Kural 1"),
            li(0, "Kural 2"),
            li(0, "Kural 3"),
        ])
        assert len(result) == 3
        assert result[0]['kural'] == "Kural 1"
        assert result[2]['kural'] == "Kural 3"

    def test_l0_with_l1_children(self):
        result = self._tree([
            li(0, "Ana kural"),
            li(1, "Alt detay 1"),
            li(1, "Alt detay 2"),
        ])
        assert len(result) == 1
        assert result[0]['kural'] == "Ana kural"
        assert len(result[0]['alt_detaylar']) == 2
        assert result[0]['alt_detaylar'][0]['kural'] == "Alt detay 1"
        assert result[0]['alt_detaylar'][1]['kural'] == "Alt detay 2"

    def test_deep_nesting_l0_l1_l2(self):
        result = self._tree([
            li(0, "L0"),
            li(1, "L1"),
            li(2, "L2"),
        ])
        assert len(result) == 1
        l0 = result[0]
        assert l0['kural'] == "L0"
        assert len(l0['alt_detaylar']) == 1
        l1 = l0['alt_detaylar'][0]
        assert l1['kural'] == "L1"
        assert len(l1['alt_detaylar']) == 1
        assert l1['alt_detaylar'][0]['kural'] == "L2"

    def test_deep_nesting_l0_l1_l2_l3(self):
        result = self._tree([
            li(0, "L0"),
            li(1, "L1"),
            li(2, "L2"),
            li(3, "L3"),
        ])
        l3 = result[0]['alt_detaylar'][0]['alt_detaylar'][0]['alt_detaylar'][0]
        assert l3['kural'] == "L3"
        assert l3['level'] == 3

    def test_mixed_levels_separate_trees(self):
        result = self._tree([
            li(0, "Ana 1"),
            li(1, "Alt 1.1"),
            li(0, "Ana 2"),
            li(1, "Alt 2.1"),
        ])
        assert len(result) == 2
        assert result[0]['kural'] == "Ana 1"
        assert len(result[0]['alt_detaylar']) == 1
        assert result[1]['kural'] == "Ana 2"
        assert len(result[1]['alt_detaylar']) == 1

    def test_l1_first_becomes_top_level(self):
        """L1 item ilk gelirse (L0 parent yok) top-level olmalı."""
        result = self._tree([li(1, "Yetim L1")])
        assert len(result) == 1
        assert result[0]['kural'] == "Yetim L1"
        assert result[0]['level'] == 1

    def test_bold_refs_preserved(self):
        result = self._tree([
            li(0, "Giriş Yap butonuna bas", bold_segments=["Giriş Yap"])
        ])
        assert result[0]['bold_refs'] == ["Giriş Yap"]

    def test_links_preserved(self):
        url = "https://app.lottiefiles.com/share/abc"
        result = self._tree([
            li(2, url, links=[url])
        ])
        assert result[0]['links'] == [url]

    def test_sibling_after_deep_nesting(self):
        """L2'den sonra gelen L0 yeni top-level node olmalı."""
        result = self._tree([
            li(0, "Ana 1"),
            li(1, "Alt 1.1"),
            li(2, "Alt 1.1.1"),
            li(0, "Ana 2"),
        ])
        assert len(result) == 2
        assert result[1]['kural'] == "Ana 2"
        assert result[1]['alt_detaylar'] == []

    def test_level_back_up_correct(self):
        """L0 → L1 → L2 → L1 (geri çıkış) doğru çalışmalı."""
        result = self._tree([
            li(0, "Ana"),
            li(1, "Alt 1"),
            li(2, "Alt 1.1"),
            li(1, "Alt 2"),  # L1'e geri dön
        ])
        assert len(result) == 1
        ana = result[0]
        assert len(ana['alt_detaylar']) == 2
        assert ana['alt_detaylar'][0]['kural'] == "Alt 1"
        assert ana['alt_detaylar'][1]['kural'] == "Alt 2"
        assert len(ana['alt_detaylar'][0]['alt_detaylar']) == 1


# ---------------------------------------------------------------------------
# Ekran çıkarımı
# ---------------------------------------------------------------------------

class TestScreenExtraction:
    def _parse(self, elements):
        return BADocxParser().parse(elements)

    def test_no_requirements_h1_no_screens(self):
        """Requirements H1 yoksa ekran çıkarılmamalı."""
        elements = [
            h(1, "Proje Açıklaması"),
            h(2, "Splash"),
            li(0, "Bir kural"),
        ]
        result = self._parse(elements)
        assert result['ekranlar'] == []

    def test_single_screen_extracted(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
        ]
        result = self._parse(elements)
        assert len(result['ekranlar']) == 1
        assert result['ekranlar'][0]['ekran_adi'] == "Splash"

    def test_multiple_screens_extracted(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(2, "Login"),
            h(2, "OTP"),
        ]
        result = self._parse(elements)
        names = [e['ekran_adi'] for e in result['ekranlar']]
        assert names == ["Splash", "Login", "OTP"]

    def test_screen_has_required_keys(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
        ]
        result = self._parse(elements)
        screen = result['ekranlar'][0]
        for key in ('ekran_adi', 'aciklama', 'tasarim_dosyalari', 'is_akislari'):
            assert key in screen

    def test_aciklama_h3_parsed(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "Açıklama"),
            p("Splash ekranı açıklaması."),
        ]
        result = self._parse(elements)
        assert "Splash ekranı açıklaması." in result['ekranlar'][0]['aciklama']

    def test_aciklama_from_list_item(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Login"),
            h(3, "Açıklama"),
            li(0, "Giriş ekranı"),
        ]
        result = self._parse(elements)
        assert "Giriş ekranı" in result['ekranlar'][0]['aciklama']

    def test_is_akisi_h3_with_rules(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "İş Akışı"),
            li(0, "Splash ekranı görüntülenir."),
            li(1, "Logo gösterilir."),
        ]
        result = self._parse(elements)
        screen = result['ekranlar'][0]
        assert len(screen['is_akislari']) == 1
        ia = screen['is_akislari'][0]
        assert ia['baslik'] == "İş Akışı"
        assert len(ia['kurallar']) == 1
        assert ia['kurallar'][0]['kural'] == "Splash ekranı görüntülenir."
        assert len(ia['kurallar'][0]['alt_detaylar']) == 1

    def test_multiple_is_akisi_per_screen(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Login"),
            h(3, "İş Akışı"),
            li(0, "Ana akış kuralı"),
            h(3, "Şifre Sıfırlama Akışı"),
            li(0, "Şifre sıfırlama kuralı"),
        ]
        result = self._parse(elements)
        screen = result['ekranlar'][0]
        assert len(screen['is_akislari']) == 2
        assert screen['is_akislari'][0]['baslik'] == "İş Akışı"
        assert screen['is_akislari'][1]['baslik'] == "Şifre Sıfırlama Akışı"

    def test_empty_is_akisi_added_with_empty_kurallar(self):
        """İş akışı başlığı var ama bullet yok → kurallar=[] ile eklenmeli."""
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Register"),
            h(3, "İş Akışı"),
            # Bullet item yok
        ]
        result = self._parse(elements)
        screen = result['ekranlar'][0]
        assert len(screen['is_akislari']) == 1
        assert screen['is_akislari'][0]['kurallar'] == []

    def test_tasarim_dosyalari_links(self):
        url = "https://figma.com/file/abc/design"
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "Tasarım Dosyaları"),
            li(0, "Figma linki", links=[url]),
        ]
        result = self._parse(elements)
        assert url in result['ekranlar'][0]['tasarim_dosyalari']

    def test_tasarim_dosyalari_plain_text_when_no_link(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "Tasarım Dosyaları"),
            li(0, "splash_design.figma"),
        ]
        result = self._parse(elements)
        assert "splash_design.figma" in result['ekranlar'][0]['tasarim_dosyalari']

    def test_h4_creates_new_is_akisi(self):
        """H4 başlığı yeni bir is_akisi oluşturmalı."""
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "İş Akışı"),
            li(0, "Ana akış"),
            h(4, "Force Update Alt Akışı"),
            li(0, "Force update kuralı"),
        ]
        result = self._parse(elements)
        screen = result['ekranlar'][0]
        assert len(screen['is_akislari']) == 2
        assert screen['is_akislari'][1]['baslik'] == "Force Update Alt Akışı"

    def test_screens_separated_correctly(self):
        """Bir ekranın kuralları diğerine karışmamalı."""
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "İş Akışı"),
            li(0, "Splash kuralı"),
            h(2, "Login"),
            h(3, "İş Akışı"),
            li(0, "Login kuralı"),
        ]
        result = self._parse(elements)
        splash_rules = result['ekranlar'][0]['is_akislari'][0]['kurallar']
        login_rules  = result['ekranlar'][1]['is_akislari'][0]['kurallar']
        assert len(splash_rules) == 1
        assert splash_rules[0]['kural'] == "Splash kuralı"
        assert len(login_rules) == 1
        assert login_rules[0]['kural'] == "Login kuralı"

    def test_requirements_h1_case_insensitive(self):
        elements = [
            h(1, "Uygulama Gereksinimleri"),  # farklı ama eşleşmeli
            h(2, "Test Ekranı"),
        ]
        result = self._parse(elements)
        assert len(result['ekranlar']) == 1


# ---------------------------------------------------------------------------
# Meta çıkarımı
# ---------------------------------------------------------------------------

class TestMetaExtraction:
    def _parse(self, elements):
        return BADocxParser().parse(elements)['meta']

    def test_proje_aciklamasi_extracted(self):
        elements = [
            h(1, "Proje Açıklaması"),
            p("Bu projede amaç; Kahve Dünyası mobil uygulama geliştirmek."),
        ]
        meta = self._parse(elements)
        assert "Kahve Dünyası" in meta['proje_aciklamasi']

    def test_proje_kapsami_extracted(self):
        elements = [
            h(1, "Proje Kapsamı"),
            p("Mobil ve Web tarafında yapılan geliştirmeler."),
        ]
        meta = self._parse(elements)
        assert "Mobil ve Web" in meta['proje_kapsami']

    def test_platform_detected_in_paragraph(self):
        elements = [
            h(1, "Proje Açıklaması"),
            p("Platform Bilgisi: iOS | Android | Web"),
        ]
        meta = self._parse(elements)
        assert meta['platform'] != ""
        assert "iOS" in meta['platform'] or "ios" in meta['platform'].lower()

    def test_dil_destegi_detected(self):
        elements = [
            h(1, "Proje Açıklaması"),
            p("Dil Desteği: Türkçe, İngilizce"),
        ]
        meta = self._parse(elements)
        assert meta['dil_destegi'] != ""

    def test_missing_sections_return_empty_string(self):
        elements = [
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
        ]
        meta = self._parse(elements)
        assert meta['proje_aciklamasi'] == ""
        assert meta['proje_kapsami'] == ""

    def test_multiple_paragraphs_joined(self):
        elements = [
            h(1, "Proje Açıklaması"),
            p("Birinci paragraf."),
            p("İkinci paragraf."),
        ]
        meta = self._parse(elements)
        assert "Birinci paragraf." in meta['proje_aciklamasi']
        assert "İkinci paragraf." in meta['proje_aciklamasi']


# ---------------------------------------------------------------------------
# Link kategorilendirme
# ---------------------------------------------------------------------------

class TestLinkCategorization:
    def _links(self, elements):
        return BADocxParser().parse(elements)['linkler']

    def test_lottie_link_categorized(self):
        url = "https://app.lottiefiles.com/share/abc123"
        elements = [li(2, url, links=[url])]
        links = self._links(elements)
        assert url in links['lottie']

    def test_google_docs_link_categorized(self):
        url = "https://docs.google.com/document/d/xyz/edit"
        elements = [li(0, "Referans", links=[url])]
        links = self._links(elements)
        assert url in links['google_docs']

    def test_figma_link_categorized(self):
        url = "https://figma.com/file/abc/design"
        elements = [p("Tasarım", links=[url])]
        links = self._links(elements)
        assert url in links['figma']

    def test_other_link_in_diger(self):
        url = "https://example.com/some-doc"
        elements = [p("Link", links=[url])]
        links = self._links(elements)
        assert url in links['diger']

    def test_duplicate_links_deduplicated(self):
        url = "https://app.lottiefiles.com/share/abc"
        elements = [
            li(0, url, links=[url]),
            li(1, url, links=[url]),
        ]
        links = self._links(elements)
        assert links['lottie'].count(url) == 1

    def test_empty_elements_return_empty_links(self):
        links = self._links([])
        assert links == {"lottie": [], "google_docs": [], "figma": [], "diger": []}


# ---------------------------------------------------------------------------
# Entegrasyon testi
# ---------------------------------------------------------------------------

class TestFullIntegration:
    def test_full_parse_structure(self):
        """Tam doküman parse → meta + ekranlar + linkler çıktısı."""
        lottie_url = "https://app.lottiefiles.com/share/splash"
        figma_url  = "https://figma.com/file/abc/splash"

        elements = [
            h(1, "Proje Açıklaması"),
            p("Bu proje Kahve Dünyası mobil uygulamasıdır."),
            p("Platform: iOS | Android | Web"),
            h(1, "Proje Kapsamı"),
            p("Kapsam açıklaması buraya gelir."),
            h(1, "Mobil Uygulama Gereksinimleri"),
            h(2, "Splash"),
            h(3, "Açıklama"),
            p("Splash ekranı açıklaması."),
            h(3, "Tasarım Dosyaları"),
            li(0, "Figma linki", links=[figma_url]),
            h(3, "İş Akışı"),
            li(0, "Kullanıcı uygulamaya girer."),
            li(1, "Kahve Dünyası logosu gösterilir."),
            li(2, "Lottie animasyonu oynatılır.", links=[lottie_url]),
            h(2, "Login"),
            h(3, "İş Akışı"),
            li(0, "Kullanıcı telefon ile giriş yapar."),
        ]

        result = BADocxParser().parse(elements)

        # Meta
        assert "Kahve Dünyası" in result['meta']['proje_aciklamasi']
        assert "iOS" in result['meta']['platform'] or "ios" in result['meta']['platform'].lower()
        assert "Kapsam" in result['meta']['proje_kapsami']

        # Ekranlar
        assert len(result['ekranlar']) == 2
        splash = result['ekranlar'][0]
        assert splash['ekran_adi'] == "Splash"
        assert "Splash ekranı açıklaması." in splash['aciklama']
        assert figma_url in splash['tasarim_dosyalari']
        assert len(splash['is_akislari']) == 1
        ia = splash['is_akislari'][0]
        assert ia['baslik'] == "İş Akışı"
        assert ia['kurallar'][0]['kural'] == "Kullanıcı uygulamaya girer."
        assert len(ia['kurallar'][0]['alt_detaylar']) == 1

        login = result['ekranlar'][1]
        assert login['ekran_adi'] == "Login"
        assert len(login['is_akislari']) == 1

        # Linkler
        assert lottie_url in result['linkler']['lottie']
        assert figma_url in result['linkler']['figma']
