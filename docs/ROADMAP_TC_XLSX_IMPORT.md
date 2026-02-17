# Roadmap: Test Case XLSX Import (Tekli + Bulk)

> **Hedef:** Loodos Test Case Excel dokümanlarını (.xlsx) platforma import etmek.
> **Kaynak Doküman Analizi:** `Loodos_-_Kahve_Dünyası_Test_Case_Document_-_MOBİL.xlsx`
> **Dosya İstatistikleri:** 59 sheet, 56 content sheet, ~2291 test case satırı, 5 header varyantı

---

## Doküman Yapı Analizi

### Genel Yapı
- Her `.xlsx` dosyasında birden fazla **sheet** bulunur. Her sheet bir modül/özelliğe ait test case'leri içerir.
- **Skip edilecek sheet'ler:** `Cover`, `Revision Changes`, `DATA` — bunlar meta/referans sheet'leridir, TC satırı içermez.
- **Content sheet'ler:** Geri kalan tüm sheet'ler (örn: `Login&Register`, `Ana Sayfa`, `Sepet`, `Profilim`, vb.)

### Header Varyantları (5 farklı format tespit edildi)

Tüm sheet'lerde ortak olan **çekirdek kolonlar** şunlardır (kolon adı sheet'e göre hafif değişebilir):

| Kavram | Olası Kolon Adları | Zorunlu? |
|--------|-------------------|----------|
| TC ID | `TEST CASE ID` | Hayır (bazı sheet'lerde yok) |
| TC Adı | `TESTCASE` / `TEST CASE` | ✅ Evet |
| Adımlar | `TEST STEPS` | ✅ Evet |
| Beklenen Sonuç | `EXPECTED RESULT` | ✅ Evet |
| Priority | `PRIORTY` / `PRIORITY` | ✅ Evet (typo var!) |
| Channel | `CHANNEL` | ✅ Evet |
| TC Type | `TESTCASE TYPE` | ✅ Evet |
| User Type | `USER TYPE` | ✅ Evet |
| Test Area | `TEST AREA` | ✅ Evet |
| Test Scenario | `TEST SCENARIO` | ✅ Evet |
| Existence | `EXISTANCE` / `c` (typo) | Opsiyonel |
| Date | `DATE` | Opsiyonel |
| App Bundle | `APP BUNDLE` | Opsiyonel |
| BR ID | `BR ID` | Opsiyonel |
| TR ID | `TR ID` | Opsiyonel |
| Precondition | `PRECONDITION` | Opsiyonel |
| Test Data | `TEST DATA` | Opsiyonel |
| Postcondition | `POSTCONDITION` | Opsiyonel |
| Actual Result | `ACTUAL RESULT` | Opsiyonel |
| Status | `STATUS` | Opsiyonel |
| Regression | `REGRESSION CASE` | Opsiyonel |
| Main Business Case | `MAIN BUSINESS CASE` | Opsiyonel |
| Comments | `COMMENTS` | Opsiyonel |
| Created By | `CREATED BY` / `CREATED By` | Opsiyonel |
| Module | `MODULE` | Opsiyonel |
| Otomasyon | `OTOMASYON` | Opsiyonel |

### Header Eşleme Stratejisi (ÇOK ÖNEMLİ)

**Kolon ismi tam eşleşme yerine fuzzy/alias matching kullanılmalı:**

```python
COLUMN_ALIASES = {
    # Her canonical isim için olası header değerleri (case-insensitive)
    "test_case_id": ["TEST CASE ID"],
    "testcase_name": ["TESTCASE", "TEST CASE"],  # İKİ FARKLI AD!
    "test_steps": ["TEST STEPS"],
    "expected_result": ["EXPECTED RESULT"],
    "priority": ["PRIORTY", "PRIORITY"],  # TYPO VAR!
    "channel": ["CHANNEL"],
    "testcase_type": ["TESTCASE TYPE"],
    "user_type": ["USER TYPE"],
    "test_area": ["TEST AREA"],
    "test_scenario": ["TEST SCENARIO"],
    "existence": ["EXISTANCE", "EXISTANCE 2", "EXISTANCE 3", "EXISTANCE 4", "c"],
    "date": ["DATE"],
    "app_bundle": ["APP BUNDLE"],
    "br_id": ["BR ID"],
    "tr_id": ["TR ID"],
    "precondition": ["PRECONDITION"],
    "test_data": ["TEST DATA"],
    "postcondition": ["POSTCONDITION"],
    "actual_result": ["ACTUAL RESULT"],
    "status": ["STATUS"],
    "regression": ["REGRESSION CASE"],
    "main_business_case": ["MAIN BUSINESS CASE"],
    "comments": ["COMMENTS"],
    "created_by": ["CREATED BY", "CREATED By"],
    "module": ["MODULE"],
    "otomasyon": ["OTOMASYON"],
}
```

### Varyant Dağılımı

| Varyant | Sheet Sayısı | Fark |
|---------|-------------|------|
| 1 (Standart 17 kolon) | 47 | `TESTCASE` kullanılır |
| 2 (TEST CASE) | 5 | `TEST CASE` kullanılır (boşluklu) |
| 3 (Extended) | 2 | `PRIORITY` (typo düzeltilmiş) + `POSTCONDITION`, `STATUS`, `REGRESSION CASE`, `COMMENTS` |
| 4 (pinarÜrünDetay) | 1 | `EXISTANCE 2/3/4` ilave kolonlar, `TEST CASE ID` yok |
| 5 (Eksik kolon) | 1 | `EXPECTED RESULT` kolonu yok |

### Özel Durumlar

1. **`Regresyon Seti` sheet'i** ayrı bir yapıya sahip: `OTOMASYON` kolonu ekstra, 261 satır ile en büyük sheet.
2. **`pinarÜrünDetay` sheet'i** `TEST CASE ID` kolonu yok — `EXISTANCE 2/3/4` ile değiştirilmiş.
3. **`Hazır AL - Ürün Sıralama Servis`** sheet'inde `EXPECTED RESULT` kolonu yok, yerine `TEST DATA` son kolon.
4. **`Çekirdek ile ödeme`** sheet'inde ilk kolon header'ı `c` (lowercase, muhtemelen typo).
5. **Boş satırlar:** Bazı sheet'lerde 1000 satıra kadar boyut tanımlı ama sadece birkaç satır dolu. Boş satır filtreleme şart.
6. **Merged cells:** Bazı sheet'lerde mevcut ama nadir. Parse sırasında göz ardı edilebilir.
7. **Multiline cell content:** `TEST STEPS` kolonu genelde `1- Adım\n2- Adım\n3- Adım` formatında multiline text içerir.

---

## Hedef JSON Schema

Her sheet parse edildiğinde aşağıdaki yapıya dönüştürülecek:

```json
{
  "sheet_name": "Login&Register",
  "test_cases": [
    {
      "test_case_id": "TC_LDS_KD_LOGIN_REGISTER_0001",
      "testcase_name": "Splash Ekranı UI Kontrolü",
      "test_scenario": "Splash Ekranı Kontrolü",
      "test_area": "Splash Ekranı",
      "priority": "MEDIUM",
      "channel": "MOBILE",
      "testcase_type": "UI",
      "user_type": "ALL",
      "test_steps": "1- Kahve dünyası appi açılır.\n2- Açılış ekranı kontrol edilir.",
      "expected_result": "Kullanıcının app açılışında tasarımda olan görüntüleme...",
      "precondition": null,
      "test_data": null,
      "existence": "New",
      "date": "20.05.2024",
      "app_bundle": "Kahve Dünyası",
      "br_id": null,
      "tr_id": null,
      "postcondition": null,
      "created_by": null
    }
  ],
  "stats": {
    "total_rows": 38,
    "parsed_rows": 38,
    "skipped_rows": 0,
    "missing_required_fields": 0
  }
}
```

Tüm dosya için:

```json
{
  "file_name": "Loodos_Kahve_Dünyası_TC_MOBIL.xlsx",
  "doc_type": "loodos_test_case",
  "meta": {
    "project_name": "Kahve Dünyası",     // Cover sheet'ten
    "document_code": "LDS-PDQA-MT-KD-1", // Cover sheet'ten
    "created_by": "Salih Diken",          // Cover sheet'ten
    "create_date": "24.04.2024"           // Cover sheet'ten
  },
  "sheets": [ /* yukarıdaki sheet nesneleri */ ],
  "summary": {
    "total_sheets": 56,
    "total_test_cases": 2291,
    "by_priority": {"CRITICAL": 450, "HIGH": 620, "MEDIUM": 980, "LOW": 241},
    "by_channel": {"MOBILE": 1800, "WEB": 300, "API": 191},
    "by_type": {"Functional": 1400, "UI": 850, "Performance": 41}
  }
}
```

---

## Uygulama Adımları

### Adım 1: TC Excel Reader (~2 saat)

**Dosya:** `pipeline/tc_xlsx_reader.py` (YENİ)

Bu modül bir `.xlsx` dosyasını alıp, sheet bazlı raw data döndürür.

```python
"""
Loodos Test Case XLSX okuyucu.
openpyxl kullanarak sheet'leri okur, header'ları eşler, boş satırları filtreler.
"""
import openpyxl
from typing import Optional

# Tüm olası kolon adları → canonical isim eşlemesi
COLUMN_ALIASES: dict[str, list[str]] = {
    "test_case_id": ["TEST CASE ID"],
    "testcase_name": ["TESTCASE", "TEST CASE"],
    "test_steps": ["TEST STEPS"],
    "expected_result": ["EXPECTED RESULT"],
    "priority": ["PRIORTY", "PRIORITY"],
    "channel": ["CHANNEL"],
    "testcase_type": ["TESTCASE TYPE"],
    "user_type": ["USER TYPE"],
    "test_area": ["TEST AREA"],
    "test_scenario": ["TEST SCENARIO"],
    "existence": ["EXISTANCE"],
    "date": ["DATE"],
    "app_bundle": ["APP BUNDLE"],
    "br_id": ["BR ID"],
    "tr_id": ["TR ID"],
    "precondition": ["PRECONDITION"],
    "test_data": ["TEST DATA"],
    "postcondition": ["POSTCONDITION"],
    "actual_result": ["ACTUAL RESULT"],
    "status": ["STATUS"],
    "regression": ["REGRESSION CASE"],
    "main_business_case": ["MAIN BUSINESS CASE"],
    "comments": ["COMMENTS"],
    "created_by": ["CREATED BY", "CREATED By"],
    "module": ["MODULE"],
    "otomasyon": ["OTOMASYON"],
}

SKIP_SHEETS = {"Cover", "Revision Changes", "DATA"}

# Bir satırın geçerli TC olması için en az bu kanonik kolonlardan biri dolu olmalı
REQUIRED_FOR_VALID_ROW = ["testcase_name", "test_steps", "expected_result"]


def read_tc_xlsx(file_content: bytes) -> dict:
    """
    Test Case XLSX dosyasını okur.
    
    Args:
        file_content: XLSX dosyasının byte içeriği
        
    Returns:
        {
            "meta": {...},      # Cover sheet'ten çıkarılan bilgiler
            "sheets": [...],    # Her content sheet'in raw datası
            "skip_sheets": [...] # Atlanan sheet isimleri
        }
    """
    # 1. Workbook aç (data_only=True → formüller yerine değerler)
    # 2. Cover sheet varsa meta bilgileri çıkar (_extract_cover_meta)
    # 3. Her content sheet için:
    #    a. Header satırını bul (_find_header_row) → ilk 5 satır içinde en az 3 dolu hücre
    #    b. Header'ları canonical isimlere eşle (_map_headers)
    #    c. Data satırlarını oku, boş satırları filtrele
    #    d. Her satırı dict'e dönüştür (canonical_name → value)
    # 4. Return
    pass


def _extract_cover_meta(ws) -> dict:
    """
    Cover sheet'ten proje bilgilerini çıkarır.
    Bilinen layout:
      C2: "Document Code"  → D2: değer
      C3: "Project Name"   → D3: değer
      C4: "Created By"     → D4: değer
      C5: "Create Date"    → D5: değer
    """
    pass


def _find_header_row(ws, max_search: int = 5) -> Optional[int]:
    """
    İlk 5 satır içinde en az 3 dolu hücre olan satırı header olarak döndürür.
    """
    pass


def _map_headers(ws, header_row: int) -> dict[int, str]:
    """
    Header satırındaki her hücreyi COLUMN_ALIASES kullanarak canonical isme eşler.
    
    Returns: {col_index: canonical_name} 
    Eşleşmeyen kolonlar: {col_index: "unknown_ORIGINAL_NAME"}
    """
    pass


def _is_valid_row(row_dict: dict) -> bool:
    """
    Satırın geçerli bir TC olup olmadığını kontrol eder.
    REQUIRED_FOR_VALID_ROW'daki alanlardan en az biri dolu olmalı.
    Tamamen boş satırları filtreler.
    """
    pass
```

**Dikkat edilecekler:**
- `openpyxl` ile aç: `load_workbook(BytesIO(file_content), data_only=True)`
- Header eşlemede case-insensitive karşılaştırma: `header.strip().upper()`
- Merged cell'lerde sadece sol üst hücre değer içerir, diğerleri `None`
- Date hücreleri `datetime` objesi olabilir → string'e çevir
- `test_steps` gibi multiline hücrelerde `\n` korunmalı

---

### Adım 2: TC Parser & Normalizer (~2 saat)

**Dosya:** `pipeline/tc_xlsx_parser.py` (YENİ)

Reader'dan gelen raw data'yı normalize eder ve hedef JSON schema'ya dönüştürür.

```python
"""
Test Case Excel verilerini parse ve normalize eder.
Reader'dan gelen raw dict'leri, platform'un beklediği JSON yapısına çevirir.
"""

PRIORITY_NORMALIZE = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH", 
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
    # Olası varyasyonlar
    "MED": "MEDIUM",
    "H": "HIGH",
    "L": "LOW",
    "C": "CRITICAL",
}

CHANNEL_NORMALIZE = {
    "MOBILE": "MOBILE",
    "WEB": "WEB",
    "API": "API",
    "ANDROID": "ANDROID",
    "IOS": "iOS",
}


class TCExcelParser:
    """Test Case Excel dokümanı parser."""
    
    def __init__(self, raw_data: dict):
        """
        Args:
            raw_data: read_tc_xlsx() çıktısı
        """
        self.raw = raw_data
        self.warnings: list[str] = []
    
    def parse(self) -> dict:
        """
        Tüm sheet'leri parse eder.
        
        Returns:
            {
                "file_name": str,
                "doc_type": "loodos_test_case",
                "meta": {...},
                "sheets": [
                    {
                        "sheet_name": str,
                        "test_cases": [...],
                        "stats": {...}
                    }
                ],
                "summary": {...},
                "warnings": [...]
            }
        """
        # 1. Her sheet'i _parse_sheet ile işle
        # 2. Summary hesapla (_calc_summary)
        # 3. Return
        pass
    
    def _parse_sheet(self, sheet_data: dict) -> dict:
        """
        Tek bir sheet'in raw satırlarını parse eder.
        
        Her satır için:
        - Priority normalize et (PRIORTY typo → PRIORITY)
        - Channel normalize et
        - test_steps'i temizle (baştaki/sondaki whitespace, empty line'lar)
        - Boş string'leri None'a çevir
        - TC ID yoksa sheet adı + satır numarasından üret
        """
        pass
    
    def _normalize_priority(self, val: str) -> str:
        """PRIORTY/PRIORITY → normalized value. Bilinmeyen değer → 'UNKNOWN' + warning."""
        pass
    
    def _normalize_channel(self, val: str) -> str:
        """CHANNEL normalize. Bilinmeyen → 'OTHER' + warning."""
        pass
    
    def _clean_test_steps(self, val: str) -> str:
        """
        Test adımlarını temizle:
        - Strip whitespace
        - Birden fazla boş satırı teke indir
        - Numaralandırma formatını koru (1- Adım, 2- Adım)
        """
        pass
    
    def _generate_tc_id(self, sheet_name: str, row_idx: int) -> str:
        """TC ID yoksa üret: TC_AUTO_{SHEET_NAME}_{ROW:04d}"""
        pass
    
    def _calc_summary(self, parsed_sheets: list) -> dict:
        """
        Tüm sheet'lerdeki TC'leri toplayarak summary hesapla:
        - total_sheets, total_test_cases
        - by_priority: {CRITICAL: n, HIGH: n, ...}
        - by_channel: {MOBILE: n, WEB: n, ...}
        - by_type: {Functional: n, UI: n, ...}
        - by_test_area: {Login Ekranı: n, ...} (top 20)
        """
        pass
```

---

### Adım 3: Import Orchestrator Güncelleme (~1.5 saat)

**Dosya:** `pipeline/docx_import_orchestrator.py` → GÜNCELLE (veya yeni `pipeline/import_orchestrator.py`)

Mevcut DOCX import orchestrator'a TC XLSX desteği ekle.

```python
def detect_document_type(file_content: bytes, file_name: str) -> dict:
    """
    Dosya tipini tespit et:
    
    1. Uzantı kontrolü:
       - .xlsx → TC XLSX candidate
       - .docx → BA DOCX candidate (mevcut logic)
    
    2. XLSX için template detection:
       - Sheet isimlerinde "Cover", "Revision Changes" var mı?
       - Header'larda "TEST CASE ID", "TESTCASE", "TEST STEPS" var mı?
       - Evetse → "loodos_test_case" template
       - Hayırsa → "generic_xlsx" (gelecekte desteklenecek)
    
    Returns:
        {
            "file_type": "xlsx" | "docx",
            "template": "loodos_test_case" | "loodos_ba_bullet" | "generic",
            "confidence": 0.0-1.0,
            "details": {...}
        }
    """
    pass
```

**Confidence hesaplama (XLSX):**
- Cover sheet var → +0.2
- "TEST CASE ID" veya "TESTCASE" header var → +0.3
- "PRIORTY" veya "PRIORITY" header var → +0.2
- "TEST STEPS" + "EXPECTED RESULT" var → +0.3
- Toplam ≥ 0.7 → `loodos_test_case`

---

### Adım 4: UI - Import & Merge Sayfası Güncelleme (~2.5 saat)

**Dosya:** `pages/11_Import_Merge.py`

Mevcut "📎 Upload Word Document" bölümünü (satır 489-621) genişlet:

```python
# ===== YENİ: DOSYA UPLOAD BÖLÜMÜ =====

st.subheader("📎 Doküman Yükle")

uploaded_files = st.file_uploader(
    "BA (.docx) veya Test Case (.xlsx) dokümanları yükleyin",
    type=["docx", "xlsx"],
    accept_multiple_files=True,  # BULK IMPORT DESTEĞİ
    help="Birden fazla dosya seçerek toplu import yapabilirsiniz."
)

if uploaded_files:
    # Her dosya için process
    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name}", expanded=len(uploaded_files) == 1):
            file_bytes = uploaded_file.read()
            
            # 1. Tip tespiti
            doc_info = detect_document_type(file_bytes, uploaded_file.name)
            
            # 2. Tip'e göre parse
            if doc_info["template"] == "loodos_test_case":
                _render_tc_import(file_bytes, uploaded_file.name, doc_info)
            elif doc_info["template"] in ("loodos_ba_bullet", "loodos_ba_table"):
                _render_ba_import(file_bytes, uploaded_file.name, doc_info)
            else:
                st.warning(f"Bilinmeyen doküman formatı: {doc_info}")


def _render_tc_import(file_bytes: bytes, file_name: str, doc_info: dict):
    """Test Case XLSX import UI."""
    
    # Parse
    raw = read_tc_xlsx(file_bytes)
    parser = TCExcelParser(raw)
    parsed = parser.parse()
    
    # === Metrics Bar ===
    cols = st.columns(4)
    cols[0].metric("📋 Sheet", parsed["summary"]["total_sheets"])
    cols[1].metric("🧪 Test Case", parsed["summary"]["total_test_cases"])
    cols[2].metric("✅ Confidence", f"{doc_info['confidence']:.0%}")
    cols[3].metric("⚠️ Warning", len(parsed.get("warnings", [])))
    
    # === Warnings ===
    if parsed.get("warnings"):
        with st.expander("⚠️ Uyarılar"):
            for w in parsed["warnings"]:
                st.warning(w)
    
    # === Preview Tabs ===
    tabs = st.tabs(["📋 Sheet Bazlı", "📊 Özet", "🔍 Detaylı TC", "{} JSON"])
    
    with tabs[0]:  # Sheet Bazlı
        for sheet in parsed["sheets"]:
            with st.expander(f"{sheet['sheet_name']} ({sheet['stats']['total_rows']} TC)"):
                # DataFrame göster
                import pandas as pd
                df = pd.DataFrame(sheet["test_cases"])
                # Sadece önemli kolonları göster
                display_cols = ["test_case_id", "testcase_name", "priority", 
                               "channel", "testcase_type", "test_area"]
                existing = [c for c in display_cols if c in df.columns]
                st.dataframe(df[existing], use_container_width=True)
    
    with tabs[1]:  # Özet
        summary = parsed["summary"]
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Priority Dağılımı:**")
            for k, v in summary.get("by_priority", {}).items():
                st.write(f"- {k}: {v}")
        with col2:
            st.write("**Channel Dağılımı:**")
            for k, v in summary.get("by_channel", {}).items():
                st.write(f"- {k}: {v}")
    
    with tabs[2]:  # Detaylı TC
        # Arama + filtreleme
        search = st.text_input("🔍 TC Ara (ID veya isim)")
        # Filtrelenmiş TC listesi
        pass
    
    with tabs[3]:  # JSON
        st.json(parsed)
    
    # === Import Button ===
    if st.button(f"➡️ Import: {file_name}", type="primary"):
        # parsed datayı veritabanına kaydet
        # Her TC'yi ayrı döküman olarak veya sheet bazlı kayıt
        pass
```

**Bulk Import Flow:**
1. Kullanıcı birden fazla `.xlsx` dosyası yükler
2. Her dosya ayrı bir `st.expander` içinde gösterilir
3. Her dosya bağımsız olarak parse edilir ve preview gösterilir
4. "Tümünü Import Et" butonu ile tüm dosyalar tek seferde import edilir
5. Tek dosya yüklendiğinde otomatik olarak expander açık gelir

```python
# Bulk import bottom bar
if len(uploaded_files) > 1:
    st.divider()
    cols = st.columns([3, 1])
    cols[0].info(f"📦 {len(uploaded_files)} dosya yüklendi. Toplamda X test case.")
    if cols[1].button("🚀 Tümünü Import Et", type="primary"):
        progress = st.progress(0)
        for i, uf in enumerate(uploaded_files):
            # import logic per file
            progress.progress((i + 1) / len(uploaded_files))
        st.success("✅ Tüm dosyalar import edildi!")
```

---

### Adım 5: Veritabanı Entegrasyonu (~1.5 saat)

**Dosya:** `database/` altındaki ilgili modüller

TC import'un platform veritabanına nasıl kaydedileceği:

```python
def save_tc_import(parsed_data: dict, source_file: str) -> dict:
    """
    Parse edilmiş TC verisini veritabanına kaydet.
    
    Kayıt stratejisi:
    1. Dosya bazlı üst kayıt oluştur (file_name, import_date, meta bilgiler)
    2. Her sheet için sheet kaydı oluştur
    3. Her TC satırı ayrı doküman olarak kaydet
    4. ChromaDB'ye semantik arama için embedding oluştur:
       - TC adı + test scenario + test steps → embedding text
    
    Duplicate detection:
    - test_case_id aynı olan kayıtlar varsa → güncelle (upsert)
    - test_case_id yoksa → yeni kayıt
    
    Returns: {"imported": n, "updated": n, "skipped": n, "errors": [...]}
    """
    pass
```

---

### Adım 6: Test Suite (~1.5 saat)

**Dosyalar:**
- `tests/test_tc_xlsx_reader.py` (YENİ)
- `tests/test_tc_xlsx_parser.py` (YENİ)

```python
# tests/conftest.py - Test fixture ekle
@pytest.fixture
def sample_tc_xlsx():
    """Minimal TC XLSX fixture oluştur."""
    from openpyxl import Workbook
    
    wb = Workbook()
    
    # Cover sheet
    ws_cover = wb.active
    ws_cover.title = "Cover"
    ws_cover["C2"] = "Document Code"
    ws_cover["D2"] = "LDS-TEST-001"
    ws_cover["C3"] = "Project Name"
    ws_cover["D3"] = "Test Project"
    
    # Content sheet - Varyant 1 (TESTCASE)
    ws1 = wb.create_sheet("Login")
    headers = ["EXISTANCE", "DATE", "APP BUNDLE", "TEST CASE ID", "BR ID", "TR ID",
               "PRIORTY", "CHANNEL", "TESTCASE TYPE", "USER TYPE", 
               "TEST AREA", "TEST SCENARIO", "TESTCASE", "TEST STEPS",
               "PRECONDITION", "TEST DATA", "EXPECTED RESULT"]
    for i, h in enumerate(headers, 1):
        ws1.cell(row=1, column=i, value=h)
    
    # Örnek satır
    row_data = ["New", "20.05.2024", "Test App", "TC_001", None, None,
                "HIGH", "MOBILE", "Functional", "ALL",
                "Login Ekranı", "Login Kontrolü", "Login Test",
                "1- App açılır\n2- Login yapılır", None, None,
                "Başarılı login beklenir"]
    for i, v in enumerate(row_data, 1):
        ws1.cell(row=2, column=i, value=v)
    
    # Content sheet - Varyant 2 (TEST CASE - boşluklu)
    ws2 = wb.create_sheet("Sepet")
    headers2 = ["EXISTANCE", "DATE", "APP BUNDLE", "TEST CASE ID", "BR ID", "TR ID",
                "PRIORTY", "CHANNEL", "TESTCASE TYPE", "USER TYPE",
                "TEST AREA", "TEST SCENARIO", "TEST CASE", "TEST STEPS",
                "PRECONDITION", "TEST DATA", "EXPECTED RESULT"]
    for i, h in enumerate(headers2, 1):
        ws2.cell(row=1, column=i, value=h)
    
    # DATA sheet (skip edilmeli)
    wb.create_sheet("DATA")
    
    # Revision Changes (skip edilmeli)
    wb.create_sheet("Revision Changes")
    
    # BytesIO'ya kaydet
    from io import BytesIO
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


# tests/test_tc_xlsx_reader.py
class TestTCXlsxReader:
    def test_skip_sheets(self, sample_tc_xlsx):
        """Cover, Revision Changes, DATA sheet'leri atlanmalı."""
        result = read_tc_xlsx(sample_tc_xlsx)
        sheet_names = [s["sheet_name"] for s in result["sheets"]]
        assert "Cover" not in sheet_names
        assert "DATA" not in sheet_names
    
    def test_header_mapping_variant1(self, sample_tc_xlsx):
        """TESTCASE kolonu doğru eşlenmeli."""
        result = read_tc_xlsx(sample_tc_xlsx)
        login_sheet = next(s for s in result["sheets"] if s["sheet_name"] == "Login")
        assert login_sheet["rows"][0].get("testcase_name") == "Login Test"
    
    def test_header_mapping_variant2(self, sample_tc_xlsx):
        """TEST CASE (boşluklu) kolonu da doğru eşlenmeli."""
        result = read_tc_xlsx(sample_tc_xlsx)
        sepet_sheet = next(s for s in result["sheets"] if s["sheet_name"] == "Sepet")
        # Header eşleme testcase_name'e map etmeli
        pass
    
    def test_priority_typo(self, sample_tc_xlsx):
        """PRIORTY (typo) → priority olarak eşlenmeli."""
        result = read_tc_xlsx(sample_tc_xlsx)
        login_sheet = next(s for s in result["sheets"] if s["sheet_name"] == "Login")
        assert login_sheet["rows"][0].get("priority") == "HIGH"
    
    def test_empty_rows_filtered(self, sample_tc_xlsx):
        """Tamamen boş satırlar filtrelenmeli."""
        result = read_tc_xlsx(sample_tc_xlsx)
        login_sheet = next(s for s in result["sheets"] if s["sheet_name"] == "Login")
        assert len(login_sheet["rows"]) == 1  # Sadece 1 data satırı
    
    def test_cover_meta_extraction(self, sample_tc_xlsx):
        """Cover sheet'ten meta bilgiler çıkarılmalı."""
        result = read_tc_xlsx(sample_tc_xlsx)
        assert result["meta"]["project_name"] == "Test Project"
        assert result["meta"]["document_code"] == "LDS-TEST-001"
    
    def test_multiline_test_steps(self, sample_tc_xlsx):
        """Multiline test steps korunmalı."""
        result = read_tc_xlsx(sample_tc_xlsx)
        login_sheet = next(s for s in result["sheets"] if s["sheet_name"] == "Login")
        steps = login_sheet["rows"][0].get("test_steps", "")
        assert "\n" in steps


# tests/test_tc_xlsx_parser.py
class TestTCExcelParser:
    def test_priority_normalization(self):
        """Priority değerleri normalize edilmeli."""
        parser = TCExcelParser({"meta": {}, "sheets": []})
        assert parser._normalize_priority("CRITICAL") == "CRITICAL"
        assert parser._normalize_priority("critical") == "CRITICAL"
        assert parser._normalize_priority("MED") == "MEDIUM"
    
    def test_tc_id_generation(self):
        """TC ID yoksa otomatik üretilmeli."""
        parser = TCExcelParser({"meta": {}, "sheets": []})
        assert parser._generate_tc_id("Login", 5) == "TC_AUTO_LOGIN_0005"
    
    def test_summary_calculation(self, sample_tc_xlsx):
        """Summary doğru hesaplanmalı."""
        raw = read_tc_xlsx(sample_tc_xlsx)
        parser = TCExcelParser(raw)
        parsed = parser.parse()
        assert parsed["summary"]["total_test_cases"] >= 1
        assert "MOBILE" in parsed["summary"].get("by_channel", {})
    
    def test_full_parse_pipeline(self, sample_tc_xlsx):
        """Uçtan uca parse pipeline çalışmalı."""
        raw = read_tc_xlsx(sample_tc_xlsx)
        parser = TCExcelParser(raw)
        result = parser.parse()
        assert result["doc_type"] == "loodos_test_case"
        assert len(result["sheets"]) >= 1
```

---

## Dosya Değişiklikleri Özeti

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `pipeline/tc_xlsx_reader.py` | YENİ | XLSX okuma + header eşleme |
| `pipeline/tc_xlsx_parser.py` | YENİ | Normalize + JSON dönüşüm |
| `pipeline/import_orchestrator.py` | GÜNCELLE | XLSX tip tespiti ekle |
| `pages/11_Import_Merge.py` | GÜNCELLE | Multi-file upload, TC preview UI |
| `tests/test_tc_xlsx_reader.py` | YENİ | Reader testleri |
| `tests/test_tc_xlsx_parser.py` | YENİ | Parser testleri |
| `tests/conftest.py` | GÜNCELLE | TC XLSX fixture ekle |

## Bağımlılıklar

- `openpyxl>=3.1.0` ✅ (requirements.txt'te zaten var olmalı, yoksa ekle)
- Yeni dependency yok.

## Uygulama Sırası

```
Adım 1 (Reader) → Adım 2 (Parser) → Adım 3 (Orchestrator) → Adım 4 (UI) → Adım 5 (DB) → Adım 6 (Tests)
```

Her adım bağımsız olarak commit edilebilir. Adım 2, Adım 1'e bağımlıdır. Adım 4, Adım 3'e bağımlıdır.

---

## Claude Code'a Verilecek Prompt

```
docs/ROADMAP_TC_XLSX_IMPORT.md dosyasını oku. Bu roadmap'teki 6 adımı sırasıyla implement et.

Adım 1'den başla. Her adımı bitirdiğinde bana söyle, ben onayladıktan sonra sonraki adıma geç.

Önemli notlar:
- Mevcut dosyaları bozmadan yeni fonksiyonları ekle
- Header eşlemede COLUMN_ALIASES dict'ini kullan (typo'lar var: PRIORTY, EXISTANCE)
- TESTCASE ve TEST CASE (boşluklu) iki farklı kolon adı, ikisi de testcase_name'e map edilmeli
- Cover, Revision Changes, DATA sheet'lerini atla
- Boş satırları filtrele (bazı sheet'ler 1000 satır ama sadece birkaçı dolu)
- accept_multiple_files=True ile bulk import destekle
- openpyxl kullan (python-docx değil)
```
