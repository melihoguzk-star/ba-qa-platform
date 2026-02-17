# 📄 DOCX Import Feature — Claude Code Roadmap (v2 — Gerçek Doküman Analizi)

## Amaç
Import & Merge sayfasındaki (pages/11_Import_Merge.py) "📎 Upload Word Document" özelliğini geliştirmek.
Kahve Dünyası BA doküman formatına uygun **yapısal DOCX import** — heading hierarchy, nested bullet list'ler, bold vurgular, hyperlink'ler korunarak parse edilmeli.

---

## 🔬 Gerçek Doküman Analizi Sonuçları

Kahve Dünyası Mobil Uygulama İş Analizi Dokümanı incelendi. Kritik bulgular:

### Doküman İstatistikleri
- **3414 paragraf**, **0 tablo** (tüm yapı bullet list'lerle oluşturulmuş)
- **150 heading** (H1-H6), **2906 list item** (Level 0-3)
- **6 hyperlink** (Lottie dosyaları + Google Docs referansları)
- **1 gömülü imge**, **18 ekran/modül** (H2 seviyesinde)

### Doküman Yapısı (Gerçek Şablon)
```
H1: İçindekiler
H1: Proje Açıklaması          → Düz paragraflar (proje tanımı, platform, dil)
H1: Proje Kapsamı              → Düz paragraflar (kapsam maddeleri)
H1: Mobil Uygulama Gereksinimleri
  H2: [Ekran/Modül Adı]       → 18 adet ekran (Splash, Login, OTP, Register, ...)
    H3: Açıklama               → (genellikle boş veya kısa)
    H3: Tasarım Dosyaları      → (genellikle boş)
    H3: İş Akışı               → İŞ KURALLARI BURADA (nested bullet list'ler)
    H3: [Özel Alt Akış]        → Ek iş akışları (Sözleşme Popup, Force Update, vb.)
      H4: [Alt-alt bölüm]      → Daha detaylı akışlar
        H5: [Detay]            → En derin seviye
```

### İçerik Pattern'i (Kritik!)
Dokümanda **TABLO YOK**. Tüm iş kuralları **nested bullet list** olarak yazılmış:
```
[L0] Ana iş kuralı (Kullanıcı telefon numarası ile giriş yapacaktır.)
  [L1] Alt detay (Telefon numarası girişi, yalnızca geçerli bir formatta yapılmalıdır.)
    [L2] Alt-alt detay (Başlık: "Güncelleme Gerekli")
```

### Bold Pattern
- Bold text = UI element veya önemli terim vurgusu (ör: **+90 5XX XXX XX XX**, **Giriş Yap**)
- Bold text düz metin içinde inline olarak geçiyor

### Hyperlink Pattern
- Lottie animasyon dosyaları: `https://app.lottiefiles.com/share/...`
- Google Docs referansları: `https://docs.google.com/document/d/...`
- Link'ler genellikle L2 seviyesinde bullet item olarak yer alıyor

---

## Mevcut Durum — Neyin Eksik

### `pipeline/document_reader.py` → `read_docx()` Sorunları:
1. ❌ **List level bilgisi kayboluyor** — `numPr/ilvl` okunmuyor, tüm bullet'lar düz paragraf oluyor
2. ❌ **Heading hiyerarşisi sadece H1-H3** — H4, H5, H6 tanınmıyor
3. ❌ **Hyperlink'ler kayboluyor** — Paragraph text'i alıyor ama URL'leri almıyor
4. ❌ **Bold vurgular kayboluyor** — Tüm run'lar birleştiriliyor, bold bilgisi yok
5. ❌ **Body element sırası korunmuyor** — Sadece `doc.paragraphs` iterasyonu yapıyor

### `pipeline/document_parser_v2.py` → `HeadingBasedParser` Sorunları:
1. ❌ **Markdown heading (#) bekliyor** — Ama DOCX'ten gelen text markdown değil
2. ❌ **List item nesting** — Bullet level bilgisi gelmediği için flat parse yapıyor
3. ❌ **Ekran/Modül konsepti yok** — H2 = Ekran, H3 = Alt bölüm mantığı yok

---

## Roadmap (5 Adım)

### Adım 1: Enhanced DOCX Reader — Bullet Level + Hyperlink + Bold
**Dosya:** `pipeline/document_reader.py`
**Tahmini Süre:** ~2 saat

#### Görevler:
1. Yeni `read_docx_structured(file_content: bytes) -> list` fonksiyonu yaz
2. `doc.element.body` üzerinden iterate et (paragraf + tablo sırası korunsun)
3. Her paragraf için:
   - **Heading level**: H1-H6 style detection
   - **List level**: `numPr/ilvl` XML attribute'ünden (0, 1, 2, 3)
   - **Bold segments**: Run-level bold detection
   - **Hyperlinks**: Relationship ID'lerden URL extraction
4. `sdt` (structured document tag = İçindekiler bloğu) skip et
5. Boş paragrafları filtrele (36 tane boş paragraf cover page'de var)

#### Çıktı Formatı:
```python
[
    {"type": "heading", "level": 1, "text": "Proje Açıklaması"},
    {"type": "heading", "level": 2, "text": "Splash"},
    {"type": "heading", "level": 3, "text": "İş Akışı"},
    {"type": "list_item", "level": 0, "text": "Kullanıcı uygulamaya giriş yapmasının ardından...",
     "bold_segments": [], "links": []},
    {"type": "list_item", "level": 1, "text": "Kahve Dünyası logosu,",
     "bold_segments": [], "links": []},
    {"type": "list_item", "level": 2, "text": "https://app.lottiefiles.com/share/...",
     "bold_segments": [], "links": ["https://app.lottiefiles.com/share/..."]},
    {"type": "paragraph", "text": "Platform Bilgisi: iOS | Android | Web",
     "bold_segments": ["iOS", "Android", "Web"], "links": []},
]
```

#### Implementasyon:
```python
def read_docx_structured(file_content: bytes) -> list:
    from docx import Document
    from docx.oxml.ns import qn
    import io

    doc = Document(io.BytesIO(file_content))
    elements = []
    rels = doc.part.rels

    for child in doc.element.body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'sdt':
            continue  # Skip TOC block

        if tag == 'p':
            para = next((p for p in doc.paragraphs if p._element is child), None)
            if not para or not para.text.strip():
                continue
            element = _parse_paragraph_element(para, rels)
            if element:
                elements.append(element)

        elif tag == 'tbl':
            table = next((t for t in doc.tables if t._element is child), None)
            if table:
                elements.append(_parse_table_element(table))

    return elements

def _parse_paragraph_element(para, rels) -> dict:
    style = para.style.name.lower()
    text = para.text.strip()

    # 1. Heading detection (H1-H6)
    for i in range(1, 7):
        if f'heading {i}' in style:
            return {"type": "heading", "level": i, "text": text}

    # 2. List level detection
    pPr = para._element.find(qn('w:pPr'))
    list_level = None
    if pPr is not None:
        numPr = pPr.find(qn('w:numPr'))
        if numPr is not None:
            ilvl = numPr.find(qn('w:ilvl'))
            if ilvl is not None:
                list_level = int(ilvl.get(qn('w:val')))

    # 3. Bold segments
    bold_segments = [r.text for r in para.runs if r.bold and r.text.strip()]

    # 4. Hyperlinks
    links = _extract_hyperlinks_from_para(para._element, rels)

    elem_type = "list_item" if list_level is not None else "paragraph"
    result = {"type": elem_type, "text": text, "bold_segments": bold_segments, "links": links}
    if list_level is not None:
        result["level"] = list_level
    return result

def _extract_hyperlinks_from_para(p_element, rels) -> list:
    from docx.oxml.ns import qn
    links = []
    for hyperlink in p_element.findall(qn('w:hyperlink')):
        r_id = hyperlink.get(qn('r:id'))
        if r_id and r_id in rels:
            url = rels[r_id].target_ref
            links.append(url)
    return links

def _parse_table_element(table) -> dict:
    rows_data = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows_data.append(cells)
    headers = rows_data[0] if rows_data else []
    data_rows = rows_data[1:] if len(rows_data) > 1 else []
    return {"type": "table", "headers": headers, "rows": data_rows}
```

---

### Adım 2: Kahve Dünyası BA Doküman Parser
**Dosya:** Yeni `pipeline/ba_docx_parser.py`
**Tahmini Süre:** ~3 saat

Bu adım dokümanın gerçek yapısına göre tasarlandı. Tablo aramak yerine **heading + nested bullet list** yapısını parse edecek.

#### Görevler:
1. Structured element listesini (Adım 1 çıktısı) alıp ekran bazlı JSON'a dönüştür
2. H2 heading = Ekran/Modül sınırı olarak kullan
3. H3 heading'leri alt-bölüm olarak grupla (Açıklama, Tasarım Dosyaları, İş Akışı, ...)
4. Nested bullet list'leri (L0 → L1 → L2 → L3) ağaç yapısına dönüştür
5. Bold segment'leri iş kurallarında **UI element referansı** olarak işaretle
6. Link'leri ayrı bir collection'da topla (Lottie, Google Docs, Figma)
7. Proje meta bilgilerini (H1: Proje Açıklaması, Proje Kapsamı) ayrıştır

#### Hedef JSON Çıktısı:
```json
{
  "meta": {
    "proje_aciklamasi": "Bu projede amaç; mevcut Kahve Dünyası...",
    "proje_kapsami": "Mobil ve Web tarafında yapılan geliştirmeler ile...",
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
              "kural": "Kullanıcı uygulamaya giriş yapmasının ardından; splash ekranı görüntülenir.",
              "level": 0,
              "alt_detaylar": [
                {"kural": "Kahve Dünyası logosu,", "level": 1, "alt_detaylar": []},
                {"kural": "Al götür logosu,", "level": 1, "alt_detaylar": []}
              ],
              "bold_refs": [],
              "links": []
            }
          ]
        },
        {
          "baslik": "Sözleşme Güncelleme Popup Akışı",
          "kurallar": [...]
        }
      ]
    },
    {
      "ekran_adi": "Login",
      "is_akislari": [...]
    }
  ],
  "linkler": {
    "lottie": ["https://app.lottiefiles.com/share/..."],
    "google_docs": ["https://docs.google.com/document/d/..."],
    "figma": [],
    "diger": []
  }
}
```

#### En Kritik Fonksiyon — `_build_rule_tree`:
```python
def _build_rule_tree(self, items: list) -> list:
    """Flat bullet list → nested tree. Stack-based algorithm.
    
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
    tree = []
    stack = []  # (level, node) pairs
    
    for item in items:
        node = {
            "kural": item["text"],
            "level": item.get("level", 0),
            "alt_detaylar": [],
            "bold_refs": item.get("bold_segments", []),
            "links": item.get("links", [])
        }
        level = node["level"]
        
        # Pop stack until we find parent
        while stack and stack[-1][0] >= level:
            stack.pop()
        
        if stack:
            stack[-1][1]["alt_detaylar"].append(node)
        else:
            tree.append(node)
        
        stack.append((level, node))
    
    return tree
```

#### Sınıf Taslağı:
```python
# pipeline/ba_docx_parser.py

class BADocxParser:
    """Kahve Dünyası stilinde BA dokümanlarını parse eder.
    
    Doküman yapısı:
    - H1: Üst bölümler (Proje Açıklaması, Kapsam, Gereksinimler)
    - H2: Ekran/Modül (Splash, Login, OTP, ...)
    - H3: Alt bölüm (Açıklama, Tasarım Dosyaları, İş Akışı, ...)
    - H4-H6: Daha derin alt bölümler
    - Bullet L0-L3: İş kuralları (nested)
    """
    
    def parse(self, elements: list) -> dict:
        result = {
            "meta": self._extract_meta(elements),
            "ekranlar": self._extract_screens(elements),
            "linkler": self._collect_all_links(elements)
        }
        return result
    
    def _extract_meta(self, elements: list) -> dict:
        """H1 Proje Açıklaması ve Proje Kapsamı altındaki paragrafları topla"""
        pass
    
    def _extract_screens(self, elements: list) -> list:
        """H2 heading'leri ekran sınırı olarak kullanarak ekranları ayır"""
        # 1. "Mobil Uygulama Gereksinimleri" H1'ini bul (veya ilk H2'den itibaren başla)
        # 2. Her H2'yi yeni ekran olarak başlat
        # 3. H3'leri alt-bölüm olarak grupla
        # 4. H3 "İş Akışı" veya özel isimli H3'ler → is_akislari listesine ekle
        # 5. Her iş akışı altındaki bullet list'leri _build_rule_tree ile ağaçlaştır
        pass
    
    def _build_rule_tree(self, items: list) -> list:
        """Flat list item'ları nested ağaç yapısına dönüştür (yukarıdaki implementasyon)"""
        pass
    
    def _collect_all_links(self, elements: list) -> dict:
        links = {"lottie": [], "google_docs": [], "figma": [], "diger": []}
        for elem in elements:
            for url in elem.get("links", []):
                if "lottiefiles.com" in url:
                    links["lottie"].append(url)
                elif "docs.google.com" in url:
                    links["google_docs"].append(url)
                elif "figma.com" in url:
                    links["figma"].append(url)
                else:
                    links["diger"].append(url)
        return links
```

---

### Adım 3: Import Orchestrator + Şablon Auto-Detect
**Dosya:** `pipeline/docx_import_orchestrator.py`
**Tahmini Süre:** ~1.5 saat

#### Görevler:
1. Upload edilen DOCX'in şablon tipini otomatik algıla
2. Algılama kriterleri:
   - H2 heading'ler altında H3 "Açıklama" / "İş Akışı" / "Tasarım Dosyaları" varsa → `loodos_ba_bullet`
   - İçerik çoğunlukla nested bullet list ise (list_item > paragraph) → `loodos_ba_bullet`
   - Tablo ağırlıklıysa ve numaralı bölümler (1.1, 2.1) varsa → `loodos_ba_table`
   - Hiçbirine uymuyorsa → `generic`
3. Uygun parser'ı seç ve çalıştır
4. Fallback: Rule-based → AI-powered (Gemini)
5. Confidence score hesapla + uyarı listesi oluştur

#### Implementasyon:
```python
# pipeline/docx_import_orchestrator.py

class DocxImportOrchestrator:
    
    def import_docx(self, file_content: bytes, doc_type: str = "auto",
                     use_ai_fallback: bool = True, gemini_key: str = "") -> dict:
        """
        Returns:
            {
                "success": True,
                "doc_type": "ba",
                "template": "loodos_ba_bullet",
                "content_json": {...},
                "confidence": 0.92,
                "stats": {"headings": 150, "screens": 18, "list_items": 2906, "links": 6, "tables": 0},
                "warnings": []
            }
        """
        from pipeline.document_reader import read_docx_structured
        
        elements = read_docx_structured(file_content)
        stats = self._calculate_stats(elements)
        template = self._detect_template(elements, stats)
        
        if template == "loodos_ba_bullet":
            from pipeline.ba_docx_parser import BADocxParser
            content_json = BADocxParser().parse(elements)
            confidence = self._calculate_confidence(content_json, stats)
        elif template == "loodos_ba_table":
            from pipeline.ba_docx_parser import BADocxParser
            content_json = BADocxParser().parse(elements)
            confidence = self._calculate_confidence(content_json, stats)
        else:
            from pipeline.document_reader import read_docx
            from pipeline.document_parser_v2 import parse_text_to_json
            text = read_docx(file_content)
            content_json = parse_text_to_json(text, doc_type if doc_type != "auto" else "ba")
            confidence = 0.4
        
        if confidence < 0.5 and use_ai_fallback and gemini_key:
            pass  # AI fallback logic
        
        return {
            "success": confidence > 0.3,
            "doc_type": doc_type if doc_type != "auto" else "ba",
            "template": template,
            "content_json": content_json,
            "confidence": confidence,
            "stats": stats,
            "warnings": self._generate_warnings(content_json, stats)
        }
    
    def _detect_template(self, elements: list, stats: dict) -> str:
        h3_texts = {e["text"] for e in elements if e["type"] == "heading" and e.get("level") == 3}
        loodos_markers = {"Açıklama", "İş Akışı", "Tasarım Dosyaları"}
        if len(loodos_markers & h3_texts) >= 2 and stats["list_items"] > stats.get("tables", 0):
            return "loodos_ba_bullet"
        if stats.get("tables", 0) > 3:
            return "loodos_ba_table"
        return "generic"
    
    def _calculate_stats(self, elements: list) -> dict:
        headings = [e for e in elements if e["type"] == "heading"]
        return {
            "headings": len(headings),
            "screens": len([e for e in headings if e.get("level") == 2]),
            "list_items": len([e for e in elements if e["type"] == "list_item"]),
            "paragraphs": len([e for e in elements if e["type"] == "paragraph"]),
            "tables": len([e for e in elements if e["type"] == "table"]),
            "links": sum(len(e.get("links", [])) for e in elements),
        }
    
    def _calculate_confidence(self, content_json: dict, stats: dict) -> float:
        score = 0.0
        ekranlar = content_json.get("ekranlar", [])
        if ekranlar:
            score += 0.3
            if len(ekranlar) >= 5: score += 0.2
            screens_with_rules = sum(1 for e in ekranlar
                                      if any(ia.get("kurallar") for ia in e.get("is_akislari", [])))
            if screens_with_rules > 0: score += 0.3
            ratio = screens_with_rules / len(ekranlar) if ekranlar else 0
            score += ratio * 0.2
        return min(score, 1.0)
    
    def _generate_warnings(self, content_json: dict, stats: dict) -> list:
        warnings = []
        for ekran in content_json.get("ekranlar", []):
            if not any(ia.get("kurallar") for ia in ekran.get("is_akislari", [])):
                warnings.append(f"'{ekran['ekran_adi']}' ekranında iş akışı bulunamadı")
        if stats["links"] == 0:
            warnings.append("Doküman içinde hiç link bulunamadı")
        return warnings
```

---

### Adım 4: UI Güncelleme — Enhanced Upload Experience
**Dosya:** `pages/11_Import_Merge.py` (satır 489-621 arası değişecek)
**Tahmini Süre:** ~2 saat

#### Görevler:
1. "📎 Upload Word Document" bölümünü yeniden yaz
2. Orchestrator ile otomatik parse et
3. Sonuç dashboard'ı göster (şablon tipi, güven skoru, ekran sayısı)
4. Tab'lı preview: Ekranlar → İş Kuralları → Linkler → Raw JSON
5. Ekran bazlı ağaç görünümü (nested iş kuralları)
6. Uyarılar göster

#### UI Akışı:
```
1. .docx dosya yükle
2. Otomatik analiz sonucu:
   ┌─────────────────────────────────────────────┐
   │ Şablon: Loodos BA (Bullet)  │ Güven: 92%   │
   │ Ekranlar: 18                │ İş Kuralları: 2906 │
   │ Linkler: 6                  │ Uyarılar: 0  │
   └─────────────────────────────────────────────┘
3. Preview Tabs:
   [📱 Ekranlar] [📋 İş Kuralları] [🔗 Linkler] [{} JSON]
4. [➡️ Import & Analyze] → Step 2
```

#### Kod Taslağı:
```python
elif import_method == "📎 Upload Word Document":
    st.markdown("### Upload Word Document")
    st.info("💡 Loodos BA doküman formatı otomatik algılanır")

    uploaded_file = st.file_uploader("Choose a Word document", type=['docx'])

    if uploaded_file is not None:
        st.success(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

        from pipeline.docx_import_orchestrator import DocxImportOrchestrator

        with st.spinner("📄 Doküman analiz ediliyor..."):
            orchestrator = DocxImportOrchestrator()
            result = orchestrator.import_docx(uploaded_file.read())
            uploaded_file.seek(0)

        if result["success"]:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📐 Şablon", result["template"].replace("_", " ").title())
            col2.metric("🎯 Güven", f"{result['confidence']:.0%}")
            col3.metric("📱 Ekranlar", result["stats"]["screens"])
            col4.metric("📋 İş Kuralları", result["stats"]["list_items"])

            for w in result["warnings"]:
                st.warning(f"⚠️ {w}")

            tab1, tab2, tab3, tab4 = st.tabs(["📱 Ekranlar", "📋 Kurallar", "🔗 Linkler", "{} JSON"])
            with tab1:
                for ekran in result["content_json"]["ekranlar"]:
                    rule_count = sum(len(ia.get("kurallar", [])) for ia in ekran.get("is_akislari", []))
                    with st.expander(f"📱 {ekran['ekran_adi']} ({rule_count} kural)"):
                        for ia in ekran.get("is_akislari", []):
                            st.markdown(f"**{ia['baslik']}**")
                            for k in ia.get("kurallar", [])[:5]:
                                st.markdown(f"- {k['kural'][:120]}")
            with tab4:
                st.json(result["content_json"])

            title = st.text_input("Doküman Başlığı*", value=uploaded_file.name.replace('.docx', ''))
            if st.button("➡️ Import & Analyze", type="primary"):
                st.session_state['imported_doc'] = {
                    'title': title, 'doc_type': 'ba',
                    'content_json': result["content_json"],
                    'import_method': 'docx_structured'
                }
                st.session_state['import_step'] = 2
                st.rerun()
```

---

### Adım 5: Test Suite
**Dosya:** `tests/test_docx_import.py` + `tests/test_ba_docx_parser.py`
**Tahmini Süre:** ~1.5 saat

#### Test Senaryoları:
```python
class TestReadDocxStructured:
    def test_heading_levels(self, sample_loodos_ba_docx):
        """H1-H6 heading'ler doğru seviyeyle çıkarılmalı"""
    def test_list_items_have_level(self, sample_loodos_ba_docx):
        """List item'lar level bilgisi taşımalı"""
    def test_empty_paragraphs_filtered(self, sample_loodos_ba_docx):
        """Boş paragraflar filtrelenmeli"""
    def test_hyperlinks_extracted(self):
        """Hyperlink URL'leri çıkarılmalı"""
    def test_bold_segments_extracted(self):
        """Bold run'lar ayrı olarak çıkarılmalı"""

class TestBADocxParser:
    def test_screens_extracted(self):
        """H2 heading'ler ekran olarak çıkarılmalı"""
    def test_rule_tree_nesting(self):
        """Flat L0→L1→L2 → nested tree dönüşümü doğru olmalı"""
    def test_meta_extraction(self):
        """Proje Açıklaması/Kapsamı meta olarak çıkarılmalı"""
    def test_links_categorized(self):
        """Lottie, Google Docs, Figma linkleri ayrı kategorizlenmeli"""
    def test_empty_screen_handled(self):
        """İş akışı olmayan ekranlar hata vermemeli"""

class TestDocxImportOrchestrator:
    def test_loodos_ba_detection(self):
        """H3 Açıklama/İş Akışı → loodos_ba_bullet algılanmalı"""
    def test_confidence_with_rules(self):
        """İş kuralı olan ekranlar confidence'ı yükseltmeli"""
    def test_warnings_generated(self):
        """İş akışı olmayan ekranlar için uyarı üretilmeli"""
```

---

## Dosya Değişiklik Özeti

| Dosya | İşlem | Açıklama |
|-------|-------|----------|
| `pipeline/document_reader.py` | **Güncelle** | `read_docx_structured()` + helper'lar ekle |
| `pipeline/ba_docx_parser.py` | **Yeni** | Bullet-list bazlı BA parser (ekran/iş akışı/kural ağacı) |
| `pipeline/docx_import_orchestrator.py` | **Yeni** | Şablon auto-detect + parser seçimi + confidence |
| `pages/11_Import_Merge.py` | **Güncelle** | Enhanced upload UI (satır 489-621) |
| `tests/test_docx_import.py` | **Yeni** | Reader + Orchestrator testleri |
| `tests/test_ba_docx_parser.py` | **Yeni** | BA parser + rule tree testleri |
| `tests/conftest.py` | **Güncelle** | `sample_loodos_ba_docx` fixture ekle |

## Bağımlılıklar
- `python-docx>=1.1.0` ✅ (zaten requirements.txt'te var)
- Yeni bağımlılık gerekmiyor

## Uygulama Sırası
```
Adım 1 → Adım 2 → Adım 3 → Adım 4 → Adım 5
(Reader)  (Parser) (Orchestrator) (UI)  (Tests)
```
Her adım bağımsız commit edilebilir. Adım 2, Adım 1'e bağımlı. Adım 4, Adım 3'e bağımlı.
