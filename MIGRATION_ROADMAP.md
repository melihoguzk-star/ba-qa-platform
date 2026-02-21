# BA&QA Intelligence Platform — Streamlit → React Migration Roadmap

## Genel Kurallar — Her Task İçin Geçerli

1. Her sayfa implementasyonuna başlamadan ÖNCE, o sayfanın mevcut Streamlit dosyasını ve ilgili tüm backend modüllerini oku
2. Okuduğun akışın özetini ver, onay bekle
3. Onay aldıktan sonra implement et
4. Roadmap'teki açıklama ile mevcut Streamlit kodu çelişirse, HER ZAMAN mevcut Streamlit kodunu referans al
5. Mevcut entegrasyonları (JIRA, n8n, Google Docs) atla veya basitleştirme — birebir taşı

## Hedef Stack
- **Framework:** React 18 + Vite
- **UI Library:** Ant Design (antd) v5
- **Routing:** react-router-dom v6
- **Server State:** TanStack Query (React Query) v5
- **Client State:** Zustand
- **HTTP Client:** axios
- **Date:** date-fns v4
- **Icons:** @ant-design/icons + lucide-react
- **Dev Port:** 5173 (Vite default)

## Mevcut Yapı Özeti (Migrasyon Referansı)

### Streamlit Sayfaları → React Route Mapping
| Streamlit Sayfası | Dosya | React Route | Öncelik |
|---|---|---|---|
| Anasayfa | `app.py` | `/` | P1 |
| BA Değerlendirme | `pages/1_BA_Degerlendirme.py` | `/ba-evaluation` | P2 |
| TC Değerlendirme | `pages/2_TC_Degerlendirme.py` | `/tc-evaluation` | P2 |
| Design Compliance | `pages/3_Design_Compliance.py` | `/design-compliance` | P3 |
| Mimari | `pages/5_Mimari.py` | `/architecture` | P4 |
| BRD Pipeline | `pages/6_BRD_Pipeline.py` | `/brd-pipeline` | P2 |
| Raporlar | `pages/7_Raporlar.py` | `/reports` | P3 |
| Settings | `pages/9_Settings.py` | `/settings` | P3 |
| Document Library | `pages/10_Document_Library.py` | `/documents` | P2 |
| Import/Merge | `pages/11_Import_Merge.py` | `/import` | P2 |
| Smart Matching | `pages/12_Smart_Matching.py` | `/smart-matching` | P3 |

### Backend Modüller → API Endpoint Mapping
| Python Modülü | Sorumluluk | API Prefix |
|---|---|---|
| `data/database.py` | SQLite CRUD (projects, documents, versions, pipeline_runs) | `/api/v1/projects`, `/api/v1/documents` |
| `agents/ai_client.py` | Claude Sonnet 4 + Gemini 2.5 Flash unified client | `/api/v1/ai/*` |
| `agents/agent_definitions.py` | BA/TC evaluation agent configs | `/api/v1/evaluate/*` |
| `agents/brd_prompts.py` + `agents/prompts.py` | Prompt templates | Internal (no API) |
| `pipeline/hybrid_search.py` | Semantic + TF-IDF + Metadata fusion search | `/api/v1/search` |
| `pipeline/embedding_pipeline.py` | multilingual-e5-base embedding generation | Internal (triggered by document ops) |
| `pipeline/chunking_strategy.py` | BA/TA/TC-specific document chunking | Internal |
| `pipeline/vector_store.py` | ChromaDB wrapper | Internal |
| `pipeline/document_matching.py` | TF-IDF matching + smart matcher | `/api/v1/match` |
| `pipeline/brd_pipeline.py` | BRD → BA → TA → TC generation pipeline | `/api/v1/pipeline/*` |
| `utils/config.py` | API keys, model config | Internal |
| `utils/text_extractor.py` | PDF/DOCX/text extraction | `/api/v1/upload` |
| `utils/document_reader.py` | DOCX structured parsing | Internal |

---

## PHASE 0 — Backend API Layer (FastAPI)
**Süre:** ~1 hafta
**Amaç:** Streamlit'in yanına bağımsız FastAPI backend kur. Streamlit çalışmaya devam etsin, React paralelde geliştirilsin.

### Task 0.1 — FastAPI Proje Yapısı
```
Proje kökünde `api/` klasörü oluştur:

api/
├── main.py                    # FastAPI app, CORS, lifespan
├── config.py                  # Pydantic Settings (env vars)
├── dependencies.py            # DB session, AI client dependency injection
├── routers/
│   ├── projects.py            # CRUD: /api/v1/projects
│   ├── documents.py           # CRUD: /api/v1/documents, /api/v1/documents/{id}/versions
│   ├── evaluation.py          # POST: /api/v1/evaluate/ba, /api/v1/evaluate/tc
│   ├── pipeline.py            # POST: /api/v1/pipeline/start, GET: /api/v1/pipeline/{id}/status
│   ├── search.py              # POST: /api/v1/search (hybrid search)
│   ├── upload.py              # POST: /api/v1/upload (file upload + parsing)
│   ├── matching.py            # POST: /api/v1/match (smart matching)
│   └── settings.py            # GET/PUT: /api/v1/settings
├── schemas/
│   ├── project.py             # Pydantic models: ProjectCreate, ProjectResponse
│   ├── document.py            # DocumentCreate, DocumentResponse, DocumentVersion
│   ├── evaluation.py          # EvaluationRequest, EvaluationResponse (score, criteria)
│   ├── pipeline.py            # PipelineStartRequest, PipelineStatus
│   ├── search.py              # SearchRequest, SearchResult
│   └── common.py              # PaginatedResponse, ErrorResponse
├── services/
│   ├── database_service.py    # data/database.py fonksiyonlarını wrap et (context manager ile)
│   ├── ai_service.py          # agents/ai_client.py'yi wrap et
│   ├── evaluation_service.py  # BA/TC değerlendirme business logic
│   ├── pipeline_service.py    # BRD pipeline orchestration
│   ├── search_service.py      # hybrid_search.py + vector_store.py
│   ├── document_service.py    # document parsing, embedding, chunking orchestration
│   └── matching_service.py    # smart matching logic
└── tasks/
    └── background.py          # BackgroundTasks: pipeline execution, embedding generation
```

Kurallar:
- FastAPI app port 8000'de çalışsın
- CORS: localhost:5173 (Vite dev) izinli
- Mevcut `data/database.py`'deki fonksiyonları services altında context manager ile wrap et
- Mevcut `agents/`, `pipeline/`, `utils/` modüllerini doğrudan import et, duplicate etme
- SQLite WAL mode aktif olsun (concurrent read desteği için)
- Startup event'te embedding model'i preload et (cold start önleme)
```

### Task 0.2 — Database Service (Connection Safety)
```
data/database.py'deki mevcut fonksiyonları sarmalayan güvenli bir service oluştur.

Mevcut sorun: Her fonksiyonda conn = get_db() / conn.close() pattern'ı var, 
exception durumunda connection leak oluyor.

Çözüm: api/services/database_service.py içinde:
1. contextlib.contextmanager ile get_db_context() oluştur
2. Tüm database fonksiyonlarını bu context manager üzerinden çağır
3. Connection pooling için SQLite URI mode kullan: sqlite:///data/baqa.db?mode=wal

Mevcut fonksiyonlar (hepsi wrap edilecek):
- get_projects(), create_project(), update_project(), delete_project()
- get_documents(), create_document(), update_document(), delete_document()
- get_document_versions(), create_document_version()
- get_pipeline_runs(), create_pipeline_run(), update_pipeline_run()
- get_evaluation_results(), save_evaluation_result()
```

### Task 0.3 — Core API Endpoints
```
İlk etapta şu endpoint'leri implement et:

1. Projects CRUD:
   GET    /api/v1/projects              → list (with pagination)
   POST   /api/v1/projects              → create
   GET    /api/v1/projects/{id}         → detail
   PUT    /api/v1/projects/{id}         → update
   DELETE /api/v1/projects/{id}         → delete

2. Documents CRUD:
   GET    /api/v1/documents             → list (filter by project_id, doc_type)
   POST   /api/v1/documents             → create
   GET    /api/v1/documents/{id}        → detail (with content_json)
   PUT    /api/v1/documents/{id}        → update
   DELETE /api/v1/documents/{id}        → delete
   GET    /api/v1/documents/{id}/versions → version history

3. File Upload:
   POST   /api/v1/upload                → multipart file upload
   - DOCX → utils/text_extractor.py + utils/document_reader.py ile parse et
   - PDF → utils/text_extractor.py ile text çıkar
   - Response: parsed content + metadata + confidence score

4. Search:
   POST   /api/v1/search                → hybrid search
   - Body: { query, doc_type_filter, project_filter, limit }
   - pipeline/hybrid_search.py kullan
   - Response: ranked results with scores and snippets

Her endpoint için:
- Pydantic schema validation
- Proper HTTP status codes (201 created, 404 not found, 422 validation error)
- Error handling middleware
- OpenAPI docs otomatik (/docs)
```

### Task 0.4 — AI & Pipeline Endpoints (Async)
```
Uzun süren AI işlemlerini background task olarak çalıştır.

1. BA Evaluation:
   POST /api/v1/evaluate/ba
   - Body: { document_id } veya { content_json, reference_document_id? }
   - Mevcut agents/agent_definitions.py'deki BA_EVALUATION_CRITERIA kullan
   - agents/ai_client.py üzerinden Claude/Gemini çağır
   - Response: { score, criteria_scores[], passed, feedback }

2. TC Evaluation:
   POST /api/v1/evaluate/tc
   - Aynı pattern, TC_EVALUATION_CRITERIA ile

3. BRD Pipeline (Background Task):
   POST /api/v1/pipeline/start
   - Body: { project_id, brd_content, stages: ["ba", "ta", "tc"] }
   - BackgroundTasks ile async çalıştır
   - Response: { pipeline_run_id, status: "started" }

   GET /api/v1/pipeline/{run_id}/status
   - Response: { status, current_stage, progress_pct, stages_completed[], error? }
   - Polling ile frontend takip edecek (TanStack Query refetchInterval)

4. Smart Matching:
   POST /api/v1/match
   - Body: { document_id, target_doc_type?, limit }
   - pipeline/document_matching.py + smart_matcher kullan
   - Response: matched documents with scores, explanations, suggestions

Önemli:
- Pipeline execution sırasında pipeline_runs tablosunda status güncelle
- Her stage tamamlandığında intermediate result'ı kaydet
- Timeout: max 5 dakika per stage
- Error durumunda partial results dön
```

---

## PHASE 1 — React Proje Kurulumu + Shell
**Süre:** ~3 gün
**Amaç:** Boş React app + layout shell + routing + auth placeholder

### Task 1.1 — Vite + React Projesi
```
Proje kökünde `frontend/` klasörü oluştur:

cd proje-kökü
npm create vite@latest frontend -- --template react
cd frontend
npm install antd @ant-design/icons react-router-dom@6 \
  @tanstack/react-query axios zustand date-fns lucide-react

Vite config (vite.config.js):
- proxy: /api → http://localhost:8000 (FastAPI)
- port: 5173

Klasör yapısı:
frontend/
├── src/
│   ├── main.jsx               # React root + providers
│   ├── App.jsx                # Router + Layout
│   ├── api/
│   │   ├── client.js          # axios instance (baseURL: /api/v1)
│   │   ├── projects.js        # useProjects, useProject, useCreateProject hooks
│   │   ├── documents.js       # useDocuments, useDocument hooks
│   │   ├── evaluation.js      # useEvaluateBA, useEvaluateTC mutations
│   │   ├── pipeline.js        # useStartPipeline, usePipelineStatus hooks
│   │   ├── search.js          # useSearch hook
│   │   └── upload.js          # useUploadFile mutation
│   ├── stores/
│   │   ├── appStore.js        # Zustand: theme, sidebar collapse, global UI state
│   │   └── evaluationStore.js # Zustand: active evaluation session state
│   ├── layouts/
│   │   └── MainLayout.jsx     # Ant Design Layout: Sider + Header + Content
│   ├── components/
│   │   ├── common/            # Reusable: PageHeader, StatusBadge, ScoreCard, LoadingOverlay
│   │   └── ui/                # App-specific shared components
│   ├── pages/
│   │   ├── Dashboard.jsx      # Ana sayfa
│   │   ├── Documents/         # Document Library (list + detail + upload)
│   │   ├── Evaluation/        # BA + TC Evaluation
│   │   ├── Pipeline/          # BRD Pipeline
│   │   ├── Import/            # Import/Merge
│   │   ├── SmartMatch/        # Smart Matching
│   │   ├── Reports/           # Raporlar
│   │   ├── Settings/          # Settings
│   │   └── Architecture/      # Mimari
│   ├── hooks/
│   │   ├── useDebounce.js
│   │   └── usePagination.js
│   ├── utils/
│   │   ├── constants.js       # Route paths, status labels, doc types
│   │   └── formatters.js      # Date format, score format, file size format
│   └── styles/
│       └── theme.js           # Ant Design theme customization (ConfigProvider)
├── index.html
├── vite.config.js
└── package.json
```

### Task 1.2 — Layout Shell + Routing
```
MainLayout.jsx:
- Ant Design Layout component kullan
- Sol sidebar (Sider): Logo + Menu items (Streamlit sayfalarının karşılıkları)
- Sidebar collapse özelliği (Zustand ile persist)
- Header: Breadcrumb + Search input (global hybrid search)
- Content area: Outlet (react-router)
- Dark/Light theme toggle (Ant Design ConfigProvider)

Menu items (sidebar):
- 🏠 Dashboard (/)
- 📋 Dokümanlar (/documents)
- 📎 Import (/import)
- 🔍 BA Değerlendirme (/ba-evaluation)
- 🧪 TC Değerlendirme (/tc-evaluation)
- 🎨 Design Compliance (/design-compliance)
- 🚀 BRD Pipeline (/brd-pipeline)
- 🔎 Smart Matching (/smart-matching)
- 📊 Raporlar (/reports)
- ⚙️ Ayarlar (/settings)
- 🏗️ Mimari (/architecture)

Router yapısı (App.jsx):
<Routes>
  <Route element={<MainLayout />}>
    <Route index element={<Dashboard />} />
    <Route path="documents" element={<Documents />} />
    <Route path="documents/:id" element={<DocumentDetail />} />
    <Route path="import" element={<Import />} />
    <Route path="ba-evaluation" element={<BAEvaluation />} />
    <Route path="tc-evaluation" element={<TCEvaluation />} />
    <Route path="design-compliance" element={<DesignCompliance />} />
    <Route path="brd-pipeline" element={<BRDPipeline />} />
    <Route path="smart-matching" element={<SmartMatching />} />
    <Route path="reports" element={<Reports />} />
    <Route path="settings" element={<Settings />} />
    <Route path="architecture" element={<Architecture />} />
  </Route>
</Routes>

Providers (main.jsx):
<QueryClientProvider client={queryClient}>
  <ConfigProvider theme={antdTheme}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </ConfigProvider>
</QueryClientProvider>
```

### Task 1.3 — API Client + TanStack Query Setup
```
api/client.js:
- axios instance: baseURL = '/api/v1'
- Request interceptor: auth token (ileride)
- Response interceptor: 401 → redirect login, 500 → notification.error()
- Timeout: 30s default, AI endpoints için 120s

TanStack Query defaults (main.jsx):
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 min
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

Örnek hook (api/projects.js):
export const useProjects = (params) =>
  useQuery({
    queryKey: ['projects', params],
    queryFn: () => client.get('/projects', { params }).then(r => r.data),
  });

export const useCreateProject = () =>
  useMutation({
    mutationFn: (data) => client.post('/projects', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  });
```

---

## PHASE 2 — Core Pages (P1-P2)
**Süre:** ~1.5 hafta
**Amaç:** En çok kullanılan sayfaları React'e taşı

### Task 2.1 — Dashboard (Anasayfa)
```
Streamlit'teki app.py karşılığı.

Bileşenler:
- Ant Design Statistic kartları (4'lü grid): Toplam Proje, Toplam Doküman, Pipeline Çalıştırma, Ortalama Skor
- Son aktiviteler listesi (Timeline component)
- Proje bazlı doküman dağılımı (Ant Design Charts veya recharts)
- Quick actions: "Yeni Değerlendirme", "Pipeline Başlat", "Doküman Yükle"

Data:
- GET /api/v1/projects (count)
- GET /api/v1/documents (count, group by doc_type)
- GET /api/v1/pipeline (recent runs)
```

### Task 2.2 — Document Library
```
Streamlit'teki 10_Document_Library.py karşılığı. En karmaşık sayfa.

Ant Design Tabs kullan (Streamlit st.tabs karşılığı):
Tab 1 — Projeler: Table + Create/Edit Modal
Tab 2 — Dokümanlar: Table (filterable by project, doc_type) + Detail drawer
Tab 3 — Doküman Yükle: Upload.Dragger + parse sonucu preview
Tab 4 — Şablondan Oluştur: Form + template selection

Tablo özellikleri:
- Ant Design Table: pagination, sorting, filtering (server-side)
- Row click → DocumentDetail sayfasına navigate
- Bulk actions: delete, export
- Search input (debounced, 300ms)

DocumentDetail sayfası (/documents/:id):
- Doküman metadata (üst kısım)
- Content tabs: JSON viewer, rendered view, version history
- Actions: Edit, Evaluate, Export, Delete
- Version comparison (iki versiyon yan yana diff)
```

### Task 2.3 — BA Değerlendirme
```
Streamlit'teki 1_BA_Degerlendirme.py karşılığı.

Akış:
1. Doküman seçimi: Select (documents listesinden) veya file upload
2. Referans doküman seçimi (opsiyonel): Select
3. "Değerlendir" butonu → POST /api/v1/evaluate/ba
4. Loading state: Skeleton + Progress
5. Sonuç ekranı:
   - Genel skor (Progress circle, renk kodlu: yeşil ≥60, kırmızı <60)
   - 9 kriter bazlı skorlar (Ant Design Descriptions veya custom cards)
   - Her kriter için detaylı feedback (Collapse/Accordion)
   - JSON export butonu

State: Zustand evaluationStore → aktif değerlendirme oturumu
TanStack Query: useEvaluateBA mutation (onSuccess → sonucu cache'e yaz)
```

### Task 2.4 — TC Değerlendirme
```
BA Değerlendirme ile aynı pattern, farklı criteria set.
Ortak component'ler çıkar: EvaluationLayout, CriteriaScoreCard, FeedbackPanel
```

### Task 2.5 — BRD Pipeline
```
Streamlit'teki 6_BRD_Pipeline.py karşılığı. Async + polling gerektirir.

Akış:
1. Proje seçimi + BRD içeriği girişi (textarea veya file upload)
2. Stage seçimi: checkboxes (BA, TA, TC — hepsi varsayılan aktif)
3. "Pipeline Başlat" → POST /api/v1/pipeline/start
4. Pipeline izleme ekranı:
   - Steps component (Ant Design): BRD Analiz → BA Üretim → BA QA → TA Üretim → TA QA → TC Üretim → TC QA
   - Her stage: pending → running (spinner) → completed (check) / failed (error)
   - Canlı log görüntüleme (auto-scroll textarea)
   - TanStack Query: usePipelineStatus(runId, { refetchInterval: 2000 })
5. Tamamlandığında:
   - Üretilen dokümanları tabs'da göster (BA | TA | TC)
   - Her doküman için: View, Edit, Save to Library, Export
   - QA skorları ve feedback

Önemli: Pipeline 2-5 dakika sürebilir. 
- refetchInterval: 2000ms (2 saniye polling)
- Timeout yapma, status "completed" veya "failed" olana kadar poll et
- Browser tab kapatılırsa → sonra geri geldiğinde son status'u göster
```

### Task 2.6 — Import/Merge
```
Streamlit'teki 11_Import_Merge.py karşılığı.

Ant Design Steps + Upload.Dragger:
Step 1: Dosya yükleme (DOCX/PDF/TXT)
Step 2: Parse sonucu önizleme (JSON tree viewer)
Step 3: Proje ve doküman tipi seçimi
Step 4: Kaydet veya mevcut dokümanla merge et

File upload: 
- Ant Design Upload.Dragger (drag & drop)
- POST /api/v1/upload → parse response
- Progress bar during upload
- Sonuç: parsed content + metadata + confidence score + warnings
```

---

## PHASE 3 — Secondary Pages (P3-P4)
**Süre:** ~1 hafta
**Amaç:** Kalan sayfaları tamamla

### Task 3.1 — Smart Matching
```
12_Smart_Matching.py karşılığı.

- Kaynak doküman seçimi
- Match sonuçları: Table veya Card grid (score, explanation, suggested action)
- Detay drawer: match reasoning, action buttons (Update, Create New, Extend)
- Analytics: metric kartları (4'lü grid üstte)
```

### Task 3.2 — Design Compliance
```
3_Design_Compliance.py karşılığı.

- BA doküman seçimi + Figma/screenshot upload
- Compliance sonucu: requirement-by-requirement matching grid
- Score breakdown + detaylı rapor
```

### Task 3.3 — Raporlar
```
7_Raporlar.py karşılığı.

- Tarih aralığı seçimi (Ant Design DatePicker.RangePicker)
- Proje bazlı filtre
- Charts: evaluation trends, pipeline success rate, document growth
- Export: PDF/CSV
```

### Task 3.4 — Settings
```
9_Settings.py karşılığı.

- API key konfigürasyonu (masked input)
- Model seçimi (Claude/Gemini variants)
- ChromaDB durumu ve istatistikleri
- Reindex butonu
- Tema ayarları
```

### Task 3.5 — Architecture
```
5_Mimari.py karşılığı.

Mevcut HTML mimari sayfasını React component olarak embed et.
Ya da Ant Design component'leri ile yeniden oluştur.
```

---

## PHASE 4 — Polish & Cutover
**Süre:** ~3-4 gün
**Amaç:** Test, hata düzeltme, Streamlit'i kapat

### Task 4.1 — Error Handling & Edge Cases
```
- Global error boundary (React ErrorBoundary)
- API error notification system (Ant Design notification)
- Empty states (boş proje, boş doküman listesi)
- Loading skeletons (her sayfa için)
- 404 page
- Offline indicator
```

### Task 4.2 — Responsive Design
```
- Ant Design Grid breakpoints (xs, sm, md, lg, xl)
- Sidebar auto-collapse on mobile
- Table scroll on small screens
- Touch-friendly interactions
```

### Task 4.3 — Testing
```
- React Testing Library: Her sayfa için temel render test
- MSW (Mock Service Worker): API mock'ları
- Cypress veya Playwright: E2E critical flows
  - Login → Dashboard → Create Project → Upload Doc → Evaluate → View Result
  - BRD Pipeline full flow
```

### Task 4.4 — Deployment Config
```
- Vite build: npm run build → dist/
- FastAPI static files: dist/ klasörünü serve et
- Single port deployment: FastAPI 8000'de hem API hem React serve etsin
- Environment variables: .env.production
- Docker: Dockerfile (multi-stage build)
```

### Task 4.5 — Streamlit Deprecation
```
- Tüm Streamlit sayfaları çalışıyor mu kontrol et (regression)
- React'teki feature parity'yi doğrula
- Streamlit'i kaldır veya /legacy altında tut (geçiş dönemi)
- requirements.txt'ten streamlit kaldır (opsiyonel)
```

---

## Claude Code Kullanım Notları

### Her Phase için Claude Code komutu:
```bash
# Phase 0 başlatma
claude "MIGRATION_ROADMAP.md dosyasını oku. Phase 0 - Task 0.1'den başla. 
api/ klasör yapısını oluştur ve FastAPI main.py'yi kur. 
Mevcut data/database.py, agents/, pipeline/, utils/ modüllerini import ederek kullan."

# Phase 1 başlatma  
claude "MIGRATION_ROADMAP.md dosyasını oku. Phase 1 - Task 1.1'den başla.
frontend/ klasöründe Vite + React projesi kur. 
Ant Design, TanStack Query, Zustand, react-router-dom kur."

# Devam etme
claude "MIGRATION_ROADMAP.md dosyasını oku. Phase 2 - Task 2.2'den devam et.
Document Library sayfasını Ant Design Table + Tabs ile oluştur."
```

### Önemli kurallar:
1. Her task'ı ayrı commit olarak at
2. Her phase sonunda çalışır durumda olsun (incremental delivery)
3. Mevcut Python modüllerini DUPLICATE ETME, import et
4. TypeScript kullanma, plain JSX yeterli (karmaşıklık artırma)
5. Her sayfa için en az bir loading state ve error state implement et
6. Ant Design component'lerini customize etme, varsayılan tema ile başla

### Test stratejisi:
- Phase 0 sonunda: FastAPI /docs'tan tüm endpoint'leri test et
- Phase 1 sonunda: Layout + routing çalışsın, tüm sayfalar boş ama erişilebilir
- Phase 2 sonunda: Core sayfalar CRUD yapabilsin, pipeline çalışsın
- Phase 3 sonunda: Tüm sayfalar feature-complete
- Phase 4 sonunda: Production-ready
