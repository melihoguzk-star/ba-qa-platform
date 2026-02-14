# 🧠 BA&QA Intelligence Platform

Birleşik BA değerlendirme, QA test analizi, design compliance ve JIRA otomasyon platformu.
BA ve QA ekibinin tüm kalite süreçlerini tek çatı altında toplayan Streamlit dashboard.

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Mimari ve Çalışma Yapısı](#-mimari-ve-çalışma-yapısı)
- [Klasör Yapısı](#-klasör-yapısı)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Teknoloji Stack](#-teknoloji-stack)
- [Agent Sistemi](#-agent-sistemi)
- [Database Şeması](#-database-şeması)
- [Entegrasyonlar](#-entegrasyonlar)
- [Konfigürasyon](#-konfigürasyon)

---

## ✨ Özellikler

### 1. 📋 BA Değerlendirme
İş Analizi dokümanlarını otomatik olarak değerlendirir:
- **9 Kriter Üzerinden Puanlama**: Hedef Okuyucu, Kapsam, Fonksiyonel Gereksinimler, Kullanıcı Hikayeleri, vb.
- **JIRA Entegrasyonu**: Task'lardan otomatik Google Docs çekimi
- **4-Agent Pipeline**: Tarama → Okuma → Değerlendirme → Raporlama
- **Otomatik Label Yönetimi**: Geçen/kalan BA taskları için `✅ BA-PASSED` / `❌ BA-FAILED`
- **JIRA Comment**: Detaylı değerlendirme raporu otomatik olarak task'a eklenir

### 2. 🧪 TC Değerlendirme
Test Case dokümanlarını otomatik olarak değerlendirir:
- **8 Kriter Üzerinden Puanlama**: Case Coverage, Acceptance Criteria, Edge Cases, Preconditions, vb.
- **BA ↔ TC Uyumluluk Kontrolü**: Linked BA taskı otomatik bulunur
- **Google Sheets Entegrasyonu**: Test case sheet'lerini otomatik okur
- **4-Agent Pipeline**: Tarama → Birleştirme → Değerlendirme → Raporlama
- **Metrik Analizi**: Toplam case sayısı, kabul kriterleri karşılama oranı

### 3. 🎨 Design Compliance
Figma tasarımlarını BA gereksinimleriyle karşılaştırır:
- **Gereksinim ↔ Tasarım Eşleşme Matrisi**
- **Eksik/Fazla Özellik Tespiti**
- **UI Text/Label Doğrulama**
- **Ciddiyet Bazlı Bulgular** (🔴 Kritik / 🟡 Orta / 🟢 Düşük)
- **4-Agent Pipeline**: Requirements Extraction → Screen Analysis → Compliance Check → Report
- **JIRA Comment**: Uyumluluk raporu otomatik olarak task'a eklenir

### 4. 📈 Raporlar ve Analitik
- **Trend Analizi**: Son 7/30/90 günlük puan trendleri (Plotly grafikleri)
- **Detaylı Analiz Geçmişi**: Tüm analizlerin filtrelenebilir listesi
- **CSV Export**: Analiz sonuçlarını CSV olarak indir
- **Tip Bazlı Filtreleme**: BA, TC, Design analizlerini ayrı ayrı görüntüle
- **İstatistikler**: Toplam analiz, ortalama puan, geçme oranları

### 5. 🚀 BRD Pipeline (Yeni!)
BRD dokümanından otomatik olarak İş Analizi, Teknik Analiz ve Test Case üretimi:
- **3-Stage Pipeline**: WF1 (BA) → WF2 (TA) → WF3 (TC)
- **Chunk-based Generation**: 2 chunk + merge stratejisi ile büyük dokümanlar
- **QA Hakem Sistemi**: Claude Sonnet 4 üretim + Gemini 2.5 Flash değerlendirme
- **Checkpoint System**: Her aşamada ara kayıt, revizyon desteği (max 3)
- **DOCX/Excel Export**: BA, TA ve TC dokümanlarını Word/Excel formatında indir
- **Kullanıcı Onaylı Akış**: Her aşama sonrası manuel onay ve düzenleme imkanı

---

## 🏗 Mimari ve Çalışma Yapısı

### Sistem Akışı

```
┌─────────────────┐
│  Streamlit UI   │
│   (Multi-Page)  │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         v                                      v
┌─────────────────┐                  ┌──────────────────┐
│  BA Evaluation  │                  │ TC Evaluation    │
│   Pipeline      │                  │   Pipeline       │
└────────┬────────┘                  └────────┬─────────┘
         │                                    │
         │   ┌──────────────────┐             │
         ├──>│  JIRA Client     │<────────────┤
         │   └──────────────────┘             │
         │                                    │
         │   ┌──────────────────┐             │
         ├──>│  Google Docs API │             │
         │   └──────────────────┘             │
         │                                    │
         │   ┌──────────────────┐             │
         │   │  Google Sheets   │<────────────┤
         │   └──────────────────┘             │
         │                                    │
         │   ┌──────────────────┐             │
         └──>│  Gemini AI       │<────────────┤
             │  4-Agent System  │             │
             └────────┬─────────┘             │
                      │                       │
                      v                       v
              ┌───────────────────────────────┐
              │      SQLite Database          │
              │   (Analysis History & Stats)  │
              └───────────────────────────────┘
```

### Agent Pipeline Detayları

#### BA Değerlendirme Pipeline (4 Agent)

```
Agent 1: JIRA Tarayıcı
├─ JIRA task bilgilerini çeker
├─ Google Docs linklerini tespit eder
└─ Task meta verilerini toplar

Agent 2: Doküman Okuyucu
├─ Google Docs API ile BA dokümanını okur
├─ Doküman yapısını analiz eder
└─ İçeriği agent 3'e aktarır

Agent 3: Kalite Değerlendirici
├─ 9 kriter üzerinden puanlama yapar
│  1. Hedef Okuyucu ve Ön Bilgi (10 puan)
│  2. Kapsam Tanımı (10 puan)
│  3. Kullanıcı Rolleri ve İzinler (10 puan)
│  4. Fonksiyonel Gereksinimler (10 puan)
│  5. Kullanıcı Hikayeleri (10 puan)
│  6. İş Akışları (10 puan)
│  7. Acceptance Criteria (10 puan)
│  8. UI/UX Beklentisi (10 puan)
│  9. Non-Functional Requirements (10 puan)
├─ Geçme kriteri: 60/100
└─ JSON formatında sonuç döner

Agent 4: Raporcu
├─ Değerlendirme sonuçlarını okunabilir rapora dönüştürür
├─ JIRA comment formatında hazırlar
└─ Emoji ve Markdown desteği
```

#### TC Değerlendirme Pipeline (4 Agent)

```
Agent 1: JIRA & Sheet Tarayıcı
├─ TC task bilgilerini çeker
├─ Linked BA taskını bulur
├─ Google Sheets linklerini tespit eder
└─ BA dokümanını da getirir (uyumluluk için)

Agent 2: Doküman Birleştirici
├─ BA ve TC dokümanlarını birleştirir
├─ Test case metriklerini çıkarır
└─ Kabul kriteri eşleştirmesi yapar

Agent 3: TC Kalite Değerlendirici
├─ 8 kriter üzerinden puanlama yapar
│  1. Case Coverage (10 puan)
│  2. BA Alignment (10 puan)
│  3. Acceptance Criteria (10 puan)
│  4. Preconditions (10 puan)
│  5. Expected Result (10 puan)
│  6. Edge Cases (10 puan)
│  7. Negative Scenarios (10 puan)
│  8. Table Structure (10 puan)
├─ Geçme kriteri: 60/100
└─ JSON formatında sonuç döner

Agent 4: TC Raporcu
├─ TC sonuçlarını okunabilir rapora dönüştürür
├─ JIRA comment formatında hazırlar
└─ Emoji ve Markdown desteği
```

#### Design Compliance Pipeline (4 Agent)

```
Agent 1: Requirements Extractor
├─ BA dokümanından gereksinimleri çıkarır
├─ Her gereksinime ID atar (REQ-001, REQ-002, ...)
├─ Kabul kriterleri, UI beklentisi, iş kuralları
└─ Yapılandırılmış gereksinim listesi oluşturur

Agent 2: Screen Analyzer
├─ Figma ekran görüntüsünü analiz eder
├─ Tüm UI bileşenlerini tespit eder
├─ Label/text'leri aynen kaydeder
├─ Form alanları, validasyonlar, navigasyon
└─ Kullanıcı akışı değerlendirmesi

Agent 3: Compliance Checker
├─ Gereksinim ↔ Tasarım eşleştirmesi
├─ Eksik/fazla özellik tespiti
├─ Acceptance criteria karşılaştırma
├─ UI text/label doğrulama
└─ Ciddiyet seviyesi (🔴 Kritik / 🟡 Orta / 🟢 Düşük)

Agent 4: Report Generator
├─ Gereksinim Eşleşme Matrisi
├─ Eksik Kapsam Listesi
├─ Ciddiyet Bazlı Bulgular
└─ JIRA ticket oluşturabilir netlikte rapor
```

---

## 📁 Klasör Yapısı

```
ba-qa-platform/
├── app.py                      # Ana giriş noktası (Streamlit entry point)
├── requirements.txt            # Python bağımlılıkları
├── README.md                   # Bu dosya
├── docs_architecture.html      # Detaylı mimari dokümanı
│
├── .streamlit/
│   ├── config.toml             # Streamlit tema ayarları
│   └── secrets.toml            # API keys (GIT'e COMMIT EDİLMEZ)
│
├── agents/                     # AI Agent tanımları
│   ├── __init__.py
│   ├── agent_definitions.py    # BA, TC, Design agent'larının tanımları
│   └── prompts.py              # Agent prompt'ları
│
├── components/                 # UI bileşenleri
│   ├── __init__.py
│   └── sidebar.py              # Custom sidebar (tüm sayfalarda ortak)
│
├── data/                       # Database ve veri yönetimi
│   ├── __init__.py
│   ├── database.py             # SQLite CRUD fonksiyonları
│   └── baqa.db                 # SQLite database (otomatik oluşturulur)
│
├── integrations/               # Dış servis entegrasyonları
│   ├── __init__.py
│   ├── jira_client.py          # JIRA REST API client
│   └── google_docs.py          # Google Docs/Sheets API client
│
├── pages/                      # Streamlit multi-page sayfa dosyaları
│   ├── 1_BA_Degerlendirme.py   # BA değerlendirme sayfası
│   ├── 2_TC_Degerlendirme.py   # TC değerlendirme sayfası
│   ├── 3_Design_Compliance.py  # Design compliance sayfası
│   ├── 4_Raporlar.py            # Raporlama ve analitik sayfası
│   ├── 5_Mimari.py              # Mimari dokümantasyon sayfası
│   ├── 6_BRD_Pipeline.py        # BRD Pipeline ana sayfa (YENI!)
│   ├── 7_Pipeline_Sonuc.py      # Pipeline sonuç görüntüleme (YENI!)
│   └── 8_Pipeline_Gecmis.py     # Pipeline çalıştırma geçmişi (YENI!)
│
├── pipeline/                   # BRD Pipeline modülleri (YENI!)
│   └── brd/                    # BRD doküman işleme pipeline
│       ├── __init__.py
│       ├── orchestrator.py     # Pipeline orchestrator (BA→TA→TC)
│       ├── checkpoint.py       # Ara kayıt sistemi
│       └── json_repair.py      # AI JSON çıktı onarıcı
│
└── utils/                      # Yardımcı fonksiyonlar
    ├── __init__.py
    ├── config.py               # Genel konfigürasyon ayarları
    ├── text_extractor.py       # PDF/DOCX text extraction (YENI!)
    └── export.py               # DOCX/Excel export (YENI!)
```

---

## 🚀 Kurulum

### 1. Gereksinimler

- **Python**: 3.11+
- **pip**: En güncel sürüm
- **API Anahtarları**:
  - Google Gemini API Key
  - JIRA Email & API Token
  - Google Cloud Service Account (Docs/Sheets erişimi için)

### 2. Projeyi Klonlama

```bash
git clone <repo-url>
cd ba-qa-platform
```

### 3. Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

### 4. Secrets Dosyası Oluşturma

`.streamlit/secrets.toml` dosyasını oluştur:

```toml
# .streamlit/secrets.toml

# Gemini AI
GEMINI_API_KEY = "your-gemini-api-key-here"

# Anthropic Claude (for BRD Pipeline)
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

# JIRA
JIRA_EMAIL = "your-email@loodos.com"
JIRA_API_TOKEN = "your-jira-api-token"

# Google Cloud (Docs/Sheets için)
# Service account JSON'ını buraya yapıştır
[google_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

**ÖNEMLİ**: `.gitignore` dosyasında `secrets.toml` olduğundan emin ol!

### 5. Uygulamayı Çalıştırma

```bash
streamlit run app.py
```

Tarayıcıda otomatik olarak `http://localhost:8501` açılacaktır.

---

## 🎯 Kullanım

### BA Değerlendirme Yapmak

1. Sol menüden **📋 BA Değerlendirme** seçeneğine tıkla
2. JIRA task key'ini gir (örn: `PROJ-123`)
3. **"Değerlendirmeyi Başlat"** butonuna tıkla
4. 4-agent pipeline çalışır:
   - JIRA'dan task bilgileri çekilir
   - Google Docs dokümanı okunur
   - 9 kriter üzerinden puanlama yapılır
   - Rapor JIRA'ya yüklenir
5. Sonuçlar ekranda görüntülenir ve database'e kaydedilir

### TC Değerlendirme Yapmak

1. Sol menüden **🧪 TC Değerlendirme** seçeneğine tıkla
2. JIRA task key'ini gir (örn: `PROJ-456`)
3. **"Değerlendirmeyi Başlat"** butonuna tıkla
4. 4-agent pipeline çalışır:
   - JIRA'dan TC task ve linked BA bulunur
   - Google Sheets test case dokümanı okunur
   - 8 kriter üzerinden puanlama yapılır
   - BA ↔ TC uyumluluk kontrol edilir
5. Sonuçlar ekranda görüntülenir ve JIRA'ya yüklenir

### Design Compliance Kontrolü

1. Sol menüden **🎨 Design Compliance** seçeneğine tıkla
2. JIRA task key'ini gir (BA task)
3. Figma ekran görüntüsü yükle (PNG/JPG)
4. **"Kontrolü Başlat"** butonuna tıkla
5. 4-agent pipeline çalışır:
   - BA dokümanından gereksinimler çıkarılır
   - Figma tasarımı analiz edilir
   - Uyumluluk kontrolü yapılır
   - Detaylı rapor oluşturulur
6. Rapor JIRA'ya comment olarak eklenir

### Raporlar ve Analitik

1. Sol menüden **📈 Raporlar** seçeneğine tıkla
2. **Trend Analizi**: Son 7/30/90 günlük puan grafikleri
3. **Detaylı Geçmiş**: Tüm analizleri filtrele ve ara
4. **CSV Export**: Sonuçları CSV olarak indir
5. **İstatistikler**: Toplam analiz, ortalama puan, geçme oranları

---

## 🛠 Teknoloji Stack

### Backend
- **Python**: 3.11+
- **Streamlit**: 1.40+ (Multi-page web framework)
- **Agno Framework**: 2.5+ (AI agent orchestration)
- **SQLite**: Database (Python built-in)

### AI
- **Google Gemini 2.5 Flash**: 1M context, ultra hızlı analiz & QA değerlendirme
- **Model ID**: `gemini-2.5-flash`
- **Claude Sonnet 4**: Doküman üretimi (BRD Pipeline) (YENI!)
- **Model ID**: `claude-sonnet-4-20250514`

### Entegrasyonlar
- **JIRA REST API**: Task yönetimi, comment, label
- **Google Docs API**: BA doküman okuma
- **Google Sheets API**: TC doküman okuma
- **Figma**: Design compliance (manuel upload)

### Frontend
- **Streamlit Components**: UI rendering
- **Plotly**: İnteraktif grafikler
- **Custom CSS**: Modern dark theme

### Utilities
- **requests**: HTTP client
- **Pillow**: Image processing
- **python-dateutil**: Date parsing

---

## 🤖 Agent Sistemi

### Agent Framework: Agno

Agno, multi-agent orchestration framework'üdür. Her agent:
- **name**: Agent ismi
- **model**: Gemini 2.5 Flash
- **description**: Agent'ın görevi
- **instructions**: Detaylı yönergeler (prompt engineering)
- **markdown**: Markdown output desteği

### Agent Özellikleri

#### BA Agent'ları
- **Agent 1 (JIRA Tarayıcı)**: Task meta verilerini toplar
- **Agent 2 (Doküman Okuyucu)**: Google Docs dokümanını parse eder
- **Agent 3 (Kalite Değerlendirici)**: 9 kriter, JSON output, 60+ geçme
- **Agent 4 (Raporcu)**: Emoji'li, Türkçe, JIRA comment formatı

#### TC Agent'ları
- **Agent 1 (JIRA & Sheet Tarayıcı)**: TC + BA bilgilerini toplar
- **Agent 2 (Doküman Birleştirici)**: BA ↔ TC alignment
- **Agent 3 (TC Kalite Değerlendirici)**: 8 kriter, JSON output
- **Agent 4 (TC Raporcu)**: Metrik analizi + rapor

#### Design Agent'ları
- **Requirements Extractor**: BA → REQ-XXX listesi
- **Screen Analyzer**: Figma → UI bileşen analizi
- **Compliance Checker**: REQ ↔ UI eşleştirme
- **Report Generator**: Markdown tablo + ciddiyet bazlı bulgular

---

## 💾 Database Şeması

### analyses tablosu

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jira_key TEXT,                    -- JIRA task key (örn: PROJ-123)
    project TEXT DEFAULT '',          -- Proje adı
    analysis_type TEXT,               -- 'ba' | 'tc' | 'design' | 'full'
    status TEXT DEFAULT 'done',       -- 'done' | 'failed'
    genel_puan REAL DEFAULT 0,        -- 0-100 arası puan
    gecti_mi INTEGER DEFAULT 0,       -- 1: geçti, 0: kaldı
    result_json TEXT DEFAULT '{}',    -- Agent sonuçları (JSON)
    report_text TEXT DEFAULT '',      -- JIRA comment metni
    triggered_by TEXT DEFAULT 'manual', -- 'manual' | 'webhook'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### jira_sync_log tablosu

```sql
CREATE TABLE jira_sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER,              -- analyses.id foreign key
    action TEXT,                      -- 'comment' | 'label'
    jira_key TEXT,                    -- JIRA task key
    success INTEGER DEFAULT 1,        -- 1: başarılı, 0: hata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);
```

### pipeline_runs tablosu (BRD Pipeline)

```sql
CREATE TABLE pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,       -- Proje adı
    jira_key TEXT,                    -- JIRA task key (opsiyonel)
    priority TEXT,                    -- Öncelik (HIGH, MEDIUM, LOW)
    brd_filename TEXT,                -- BRD dosya adı
    status TEXT DEFAULT 'running',    -- 'running' | 'completed' | 'failed'
    current_stage TEXT DEFAULT 'ba',  -- 'ba' | 'ta' | 'tc'
    ba_score REAL DEFAULT 0,          -- BA QA skoru
    ta_score REAL DEFAULT 0,          -- TA QA skoru
    tc_score REAL DEFAULT 0,          -- TC QA skoru
    ba_revisions INTEGER DEFAULT 0,   -- BA revizyon sayısı
    ta_revisions INTEGER DEFAULT 0,   -- TA revizyon sayısı
    tc_revisions INTEGER DEFAULT 0,   -- TC revizyon sayısı
    total_time_sec INTEGER DEFAULT 0, -- Toplam süre (saniye)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### stage_outputs tablosu (BRD Pipeline)

```sql
CREATE TABLE stage_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_run_id INTEGER NOT NULL, -- pipeline_runs.id foreign key
    stage TEXT NOT NULL,              -- 'ba' | 'ta' | 'tc'
    content_json TEXT,                -- Üretilen içerik (JSON)
    qa_result_json TEXT,              -- QA değerlendirme sonucu (JSON)
    revision_number INTEGER DEFAULT 0,-- Revizyon numarası (0, 1, 2, 3)
    forced_pass INTEGER DEFAULT 0,    -- Zorla geçirildi mi (1: evet, 0: hayır)
    generation_time_sec INTEGER DEFAULT 0, -- Üretim süresi (saniye)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(id)
);
```

### Önemli Fonksiyonlar

**Analiz Fonksiyonları:**
- `init_db()`: Database'i oluşturur (otomatik)
- `save_analysis()`: Yeni analiz kaydı ekler
- `get_recent_analyses(limit, analysis_type)`: Son analizleri getirir
- `get_stats()`: İstatistikleri döner (toplam, tip bazlı, 7 günlük)

**BRD Pipeline Fonksiyonları:**
- `create_pipeline_run()`: Yeni pipeline çalıştırması oluşturur
- `update_pipeline_run()`: Pipeline durumunu günceller
- `save_pipeline_stage_output()`: Aşama çıktısını kaydeder
- `get_recent_pipeline_runs(limit)`: Son pipeline çalıştırmalarını getirir
- `get_pipeline_run_outputs(run_id)`: Belirli bir pipeline'ın tüm çıktılarını getirir

---

## 🔗 Entegrasyonlar

### JIRA REST API

**Base URL**: `https://loodos.atlassian.net`

#### Kullanılan Endpoint'ler

```python
# Task arama (JQL)
GET /rest/api/3/search/jql?jql=key=PROJ-123

# Task detayı
GET /rest/api/3/issue/PROJ-123?fields=description

# Label ekleme/güncelleme
PUT /rest/api/3/issue/PROJ-123
Body: {"update": {"labels": [{"add": "✅ BA-PASSED"}]}}

# Comment ekleme
POST /rest/api/3/issue/PROJ-123/comment
Body: {"body": {"type": "doc", "content": [...]}}
```

#### Fonksiyonlar

- `jira_search(email, token, jql)`: JQL ile task arama
- `jira_get_issue(email, token, key)`: Tek task getir
- `jira_add_label(email, token, key, label)`: Label ekle
- `jira_update_labels(email, token, key, remove_labels, add_labels)`: Label güncelle
- `jira_add_comment(email, token, key, text)`: Comment ekle

### Google Docs/Sheets API

**Service Account Authentication** kullanılır.

#### Kullanılan Scopes

```python
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",  # Docs okuma
    "https://www.googleapis.com/auth/spreadsheets.readonly"  # Sheets okuma
]
```

#### Fonksiyonlar (Örnek)

```python
def get_google_docs_content(doc_id: str) -> str:
    """Google Docs dokümanını plain text olarak getirir"""
    # Service account credentials ile authenticate
    # Documents API ile doküman okuma
    # Paragraf ve liste öğelerini parse etme
    return full_text

def get_google_sheets_content(sheet_id: str) -> list:
    """Google Sheets test case'lerini getirir"""
    # Sheets API ile range okuma
    # Header satırı + data satırları
    return rows
```

---

## ⚙️ Konfigürasyon

### Environment Variables

```bash
# .env dosyasında (opsiyonel, secrets.toml tercih edilir)
GEMINI_API_KEY=your-key
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-token
```

### Streamlit Config

`.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#0a0e17"
secondaryBackgroundColor = "#1a2236"
textColor = "#f1f5f9"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### Agent Parametreleri

`agents/agent_definitions.py` dosyasında:

```python
# Model konfigürasyonu
model = Gemini(id="gemini-2.5-flash", api_key=api_key)

# Agent instruction'ları
instructions = [
    "Sen son derece deneyimli bir iş analizi kalite kontrol uzmanısın.",
    "PUANLAMA: Varsayılan 5/10. 8+ = MÜKEMMEL.",
    "Geçme: 60+.",
]
```

---

## 📊 Önemli Metrikler

### BA Değerlendirme

- **9 Kriter**: Her biri 10 puan üzerinden
- **Genel Puan**: (9 kriter ortalaması) × 100/90
- **Geçme Kriteri**: 60/100

### TC Değerlendirme

- **8 Kriter**: Her biri 10 puan üzerinden
- **Genel Puan**: (8 kriter ortalaması) × 100/80
- **Geçme Kriteri**: 60/100

### Design Compliance

- Skorlama yok, sadece uyumluluk durumu
- **Durum**: ✅ UYUMLU / ⚠️ KISMİ / ❌ EKSİK
- **Ciddiyet**: 🔴 Kritik / 🟡 Orta / 🟢 Düşük

---

## 🔐 Güvenlik

- `.streamlit/secrets.toml` dosyası **GIT'e commit edilmez**
- JIRA API Token kullanılır (password değil)
- Google Service Account (OAuth2 değil)
- Database lokal (SQLite), dışarıya açılmaz

---

## 🐛 Troubleshooting

### JIRA API 401 Unauthorized

- JIRA_EMAIL ve JIRA_API_TOKEN kontrolü
- API token'ın geçerli olduğunu doğrula
- Base64 encoding kontrolü

### Google Docs/Sheets 403 Forbidden

- Service account'a doküman erişimi verilmiş mi?
- Share → Add people → service account email ekle
- Scope'lar doğru mu? (`documents.readonly`, `spreadsheets.readonly`)

### Gemini API 429 Rate Limit

- Gemini API quota kontrolü
- Gemini Flash: 15 RPM (free tier)
- Gerekirse model değişikliği: `gemini-2.5-pro`

### Database Locked Error

- Eşzamanlı yazma hatası
- `PRAGMA journal_mode=WAL` kullanılıyor (düzeltilmiş)

---

## 📝 Güncellemeler (Changelog)

### v1.1.1 - BRD Pipeline İyileştirmeleri (2025-02-15)

#### Hata Düzeltmeleri
- 🐛 **QA Result Display**: TA/BA/TC QA sonuçlarında `TypeError: expected str instance, dict found` hatası düzeltildi
  - QA hakem sonuçlarında `aciklama` field'ı dict/list olduğunda otomatik string'e dönüştürülüyor
- 🐛 **Import Path Fixes**: Tüm BRD Pipeline import hataları düzeltildi
  - `pipeline.json_repair` → `pipeline.brd.json_repair`
  - Database fonksiyon alias'ları düzeltildi (`update_pipeline_run`, `save_pipeline_stage_output`, `get_pipeline_run_outputs`)
- 🐛 **Config Constants**: BRD Pipeline sabitleri `utils/config.py`'ye eklendi
  - `BA_PASS_THRESHOLD`, `TA_PASS_THRESHOLD`, `TC_PASS_THRESHOLD`, `MAX_REVISIONS`
  - `CHUNK_OUTPUT_TOKEN_LIMIT`, `QA_OUTPUT_TOKEN_LIMIT`, `SONNET_MODEL`, `GEMINI_MODEL`

#### Yeni Özellikler
- ⚡ **Hakeme Gönderme Seçeneği**: Her review aşamasında QA'yı atlama imkanı
  - BA Review, TA Review, TC Review aşamalarında checkbox
  - "⚡ Hakeme göndermeden devam et (QA'yı atla)" seçeneği
  - İşaretlenirse: Gemini QA'ya gönderilmez, otomatik 100 puan (force pass)
  - İşaretlenmezse: Normal akış, QA hakem değerlendirmesi yapılır
  - **Avantajlar**: API maliyet tasarrufu, hızlı iterasyon, kullanıcı kontrolü

#### Kullanıcı Deneyimi İyileştirmeleri
- ✨ Review aşamalarında buton metinleri güncellendi: "Onayla — Hakeme Gönder" → "Onayla ve İlerle"
- ✨ QA atlandığında bilgilendirme mesajı: "⚡ QA atlandı, [sonraki aşama]'ya geçiliyor..."

---

### v1.1 - BRD Pipeline Entegrasyonu (2025-02-15)

#### Yeni Özellikler
- ✅ **BRD Pipeline Modülü**: BRD dokümanından otomatik BA, TA, TC üretimi
  - WF1: İş Analizi (BA) üretimi - Ekran bazlı, FR/BR numaralandırmalı
  - WF2: Teknik Analiz (TA) üretimi - API endpoint, DTO, validasyon
  - WF3: Test Case (TC) üretimi - 56+ test case, 23 kolonlu Loodos şablonu
- ✅ **Chunk-based Generation**: Büyük dokümanlar için 2 chunk + merge stratejisi
- ✅ **QA Hakem Sistemi**: Claude Sonnet 4 üretim + Gemini 2.5 Flash değerlendirme
- ✅ **Checkpoint System**: Her aşamada ara kayıt ve revizyon desteği (max 3)
- ✅ **DOCX/Excel Export**: BA, TA ve TC dokümanlarını Word/Excel olarak indir
- ✅ **Pipeline Geçmişi**: Tüm pipeline çalıştırmalarının detaylı geçmişi
- ✅ **Anthropic Claude API**: BRD Pipeline için Claude Sonnet 4 entegrasyonu
- ✅ **PDF/DOCX Parser**: BRD doküman okuma (PyPDF2, python-docx)
- ✅ 3 Yeni Sayfa: BRD Pipeline, Pipeline Sonuç, Pipeline Geçmiş

#### Database Güncellemeleri
- ✅ `pipeline_runs` tablosu: Pipeline çalıştırma geçmişi
- ✅ `stage_outputs` tablosu: Her aşamanın çıktı ve QA sonuçları

#### Teknik İyileştirmeler
- ✅ Modüler pipeline yapısı: `pipeline/brd/` klasörü
- ✅ BRD-specific agent prompts: `agents/brd_prompts.py`
- ✅ Text extraction utilities: PDF ve DOCX okuma
- ✅ Export utilities: Doküman formatına dönüştürme
- ✅ Sidebar'a "BRD Pipeline" section eklendi

#### Bilinen Sorunlar
- Figma API entegrasyonu yok (manuel upload)
- Webhook desteği henüz aktif değil
- Multi-tenant (çoklu proje) desteği yok
- BRD Pipeline JIRA entegrasyonu henüz yok (sadece manuel BRD upload)

---

### v1.0 - İlk Sürüm (2025-02-14)

#### Yeni Özellikler
- ✅ BA Değerlendirme modülü (4-agent pipeline)
- ✅ TC Değerlendirme modülü (4-agent pipeline)
- ✅ Design Compliance modülü (4-agent pipeline)
- ✅ Raporlama ve analitik sayfası
- ✅ JIRA entegrasyonu (search, comment, label)
- ✅ Google Docs/Sheets entegrasyonu
- ✅ SQLite database
- ✅ Modern dark theme UI
- ✅ Plotly trend grafikleri
- ✅ CSV export

#### Bilinen Sorunlar
- Figma API entegrasyonu yok (manuel upload)
- Webhook desteği henüz aktif değil
- Multi-tenant (çoklu proje) desteği yok

---

## 🚧 Roadmap

### v1.1 (Planlanan)

- [ ] Figma API entegrasyonu (otomatik frame çekme)
- [ ] JIRA Webhook desteği (otomatik tetikleme)
- [ ] Multi-tenant proje desteği
- [ ] Kullanıcı yetkilendirme sistemi
- [ ] Email bildirimleri
- [ ] Slack entegrasyonu

### v1.2 (Gelecek)

- [ ] BA + TC + Design combo analizi (full pipeline)
- [ ] Custom kriter tanımlama
- [ ] Agent prompt'ları UI'dan düzenleme
- [ ] PostgreSQL desteği (SQLite yerine)
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

## 👥 Katkıda Bulunanlar

**Loodos BA&QA Ekibi**

- BA Uzmanları: Kriter tanımlama, iş analizi standartları
- QA Uzmanları: Test case şablonu, değerlendirme kriterleri
- AI Engineer: Agent orchestration, prompt engineering

---

## 📄 Lisans

Bu proje Loodos şirketi iç kullanımı içindir.

---

## 📞 Destek

Sorularınız için:
- **JIRA**: BA&QA Platform projesi
- **Slack**: #ba-qa-platform kanalı
- **Email**: ba-qa-platform@loodos.com

---

**BA&QA Intelligence Platform v1.0** — Loodos BA&QA Ekibi
