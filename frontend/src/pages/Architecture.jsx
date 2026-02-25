/**
 * Architecture Page — Platform architecture documentation
 */
import { Card, Row, Col, Statistic, Tabs, Descriptions, Tag, Typography, Space, Divider, theme } from 'antd';
import {
  RocketOutlined,
  ApiOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  FormatPainterOutlined,
  SearchOutlined,
  DatabaseOutlined,
  CloudOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

export default function Architecture() {
  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Tag
          color="cyan"
          style={{
            fontSize: 12,
            padding: '4px 16px',
            marginBottom: 12,
            textTransform: 'uppercase',
            letterSpacing: 1,
          }}
        >
          <CheckCircleOutlined style={{ marginRight: 4 }} />
          Architecture Document
        </Tag>
        <Title level={1} style={{ marginBottom: 12 }}>
          🏗️ Platform Mimarisi
        </Title>
        <Paragraph type="secondary" style={{ fontSize: 16, maxWidth: 700, margin: '0 auto' }}>
          Birleşik BA değerlendirme, QA test analizi, design compliance ve JIRA otomasyon platformu
        </Paragraph>
      </div>

      {/* Quick Stats */}
      <Row gutter={16} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="AI Agents"
              value={15}
              valueStyle={{ color: '#3b82f6', fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Entegrasyonlar"
              value={8}
              valueStyle={{ color: '#8b5cf6', fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Sayfalar"
              value={13}
              valueStyle={{ color: '#10b981', fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Pipeline"
              value={4}
              valueStyle={{ color: '#f59e0b', fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="Doc Chunks"
              value={571}
              valueStyle={{ color: '#06b6d4', fontWeight: 700 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Main Tabs */}
      <Tabs defaultActiveKey="1" size="large">
        <Tabs.TabPane tab={<span><RocketOutlined /> AI Agents</span>} key="1">
          <AIAgentsTab />
        </Tabs.TabPane>
        <Tabs.TabPane tab={<span><DatabaseOutlined /> Document Intelligence</span>} key="2">
          <DocumentIntelligenceTab />
        </Tabs.TabPane>
        <Tabs.TabPane tab={<span><ApiOutlined /> Entegrasyonlar</span>} key="3">
          <IntegrationsTab />
        </Tabs.TabPane>
        <Tabs.TabPane tab={<span><RocketOutlined /> Pipeline Akışları</span>} key="4">
          <PipelineFlowsTab />
        </Tabs.TabPane>
        <Tabs.TabPane tab={<span><CloudOutlined /> Tech Stack</span>} key="5">
          <TechStackTab />
        </Tabs.TabPane>
      </Tabs>

      {/* Footer */}
      <Divider />
      <div style={{ textAlign: 'center', padding: '20px 0' }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          BA&QA Intelligence Platform v2.0 — Architecture Document — February 2026
        </Text>
        <br />
        <Text type="secondary" style={{ fontSize: 10 }}>
          Phase 2: Document Intelligence System Active ✨
        </Text>
      </div>
    </div>
  );
}

// ============================================================================
// Tab 1: AI Agents
// ============================================================================

function AIAgentsTab() {
  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Title level={4}>
        <FileTextOutlined /> BA (İş Analizi) Agents
      </Title>
      <Paragraph type="secondary">
        4 adet specialized agent ile İş Analizi doküman kalite değerlendirmesi yapar
      </Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="🔍 Agent 1: JIRA Tarayıcı"
            role="JIRA Task Discovery & Link Extraction"
            description="JIRA'dan iş analizi task'larını tarar, Google Docs linklerini tespit eder ve task bilgilerini analiz eder."
            tasks={[
              'JIRA task\'larını tarar ve filtreler',
              'Google Docs URL\'lerini description\'dan çıkarır',
              'Task bilgilerini özetler ve yapılandırır',
              'qa-devam-ediyor label\'ını ekler',
            ]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="📄 Agent 2: Doküman Okuyucu"
            role="Document Parser & Structure Analyzer"
            description="Google Docs'tan çekilen BA dokümanını okur, yapısını analiz eder ve içeriği parçalara ayırır."
            tasks={[
              'Doküman yapısını analiz eder (başlıklar, bölümler)',
              'İçeriği parçalara ayırır',
              'Eksik bölümleri tespit eder',
              'Metrik bilgiler çıkarır (karakter sayısı, bölüm sayısı)',
            ]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="🧠 Agent 3: Kalite Değerlendirici"
            role="Quality Assessment & Scoring Engine"
            description="İş analizi dokümanını 9 kriter üzerinden detaylı değerlendirir. Platform'un en kritik AI agent'ıdır."
            tasks={[
              'Tamlık (Completeness)',
              'Wireframe / Ekran Tasarımları',
              'Akış Diyagramları (Flow Diagrams)',
              'Gereksinim Kalitesi',
              'Kabul Kriterleri (Acceptance Criteria)',
              'Tutarlılık (Consistency)',
              'İş Kuralları Derinliği',
              'Hata Yönetimi (Error Handling)',
              'Dokümantasyon Kalitesi',
            ]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                <strong>Puanlama:</strong> Her kriter 1-10, Geçme: 60/100
              </Text>
            }
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="📝 Agent 4: Raporcu"
            role="Report Formatter & JIRA Commenter"
            description="Değerlendirme sonuçlarını JIRA comment formatına dönüştürür ve okunabilir rapor oluşturur."
            tasks={[
              'JSON sonuçlarını Markdown formatına çevirir',
              'Emoji ve görsel elementler ekler',
              "JIRA comment'i oluşturur",
              'qa-gecti/qa-gecmedi label\'larını yönetir',
            ]}
          />
        </Col>
      </Row>

      <Divider />

      <Title level={4}>
        <ExperimentOutlined /> TC (Test Case) Agents
      </Title>
      <Paragraph type="secondary">
        4 adet specialized agent ile Test Case doküman kalite değerlendirmesi yapar
      </Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <AgentCard
            color="green"
            name="🔍 Agent 1: JIRA & Sheet Tarayıcı"
            role="Test Task Discovery & BA Linking"
            description="JIRA'dan TC task'larını tarar, linked BA task'ı bulur ve Google Sheets URL'lerini tespit eder."
            tasks={[
              'JIRA component = Test filtresiyle TC task\'larını bulur',
              'Linked BA task key\'ini tespit eder',
              'Google Sheets URL\'sini çıkarır',
              'tc-qa-devam-ediyor label\'ını ekler',
            ]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="green"
            name="📑 Agent 2: Doküman Birleştirici"
            role="Document Merger & Metrics Extractor"
            description="BA dokümanı ve TC sheet'lerini birleştirip analiz için hazırlar. BA ile TC karşılaştırması yapar."
            tasks={[
              "BA dokümanı ile TC sheet'i birleştirir",
              'Test case sayısını ve coverage metriklerini çıkarır',
              "BA gereksinimlerini TC'lerle eşleştirir",
              'Eksik coverage alanlarını tespit eder',
            ]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="green"
            name="🧠 Agent 3: TC Kalite Değerlendirici"
            role="Test Case Quality Assessor"
            description="Test case dokümanını 8 kriter üzerinden değerlendirir. Loodos standart şablonunu (23 sütun) bekler."
            tasks={[
              'Kapsam (Coverage)',
              'Test Case Yapısı (Structure)',
              'Sınır Değer & Negatif Senaryolar',
              'Test Verisi Kalitesi',
              'Öncelik Sınıflandırması',
              'Regresyon Kapsamı',
              'İzlenebilirlik (Traceability)',
              'Okunabilirlik & Uygulanabilirlik',
            ]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                <strong>Geçme:</strong> 60/100, Loodos şablonu (23 sütun)
              </Text>
            }
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="green"
            name="📝 Agent 4: TC Raporcu"
            role="Test Report Generator"
            description="TC değerlendirme sonuçlarını rapor formatına dönüştürür ve JIRA'ya yazar."
            tasks={[
              'TC sonuçlarını Markdown formatına çevirir',
              'Coverage metrikleri ekler',
              "JIRA comment'i oluşturur",
              'tc-qa-gecti/tc-qa-gecmedi label\'larını yönetir',
            ]}
          />
        </Col>
      </Row>

      <Divider />

      <Title level={4}>
        <FormatPainterOutlined /> Design Compliance Agents
      </Title>
      <Paragraph type="secondary">
        4 adet specialized agent ile Tasarım ↔ BA uyumluluk kontrolü yapar
      </Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <AgentCard
            color="purple"
            name="📋 Agent 1: Requirements Extractor"
            role="Requirement ID Generator & Parser"
            description="BA dokümanından gereksinimleri yapılandırılmış biçimde çıkarır ve her birine benzersiz ID verir (REQ-001, REQ-002...)."
            tasks={[
              'Her fonksiyonel gereksinimi tanımlar ve ID verir',
              'Kabul kriterlerini çıkarır',
              'UI bileşeni beklentilerini belirler',
              'UI metinleri/label\'ları aynen korur',
              'İş kurallarını ve doğrulama koşullarını listeler',
            ]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="purple"
            name="👁️ Agent 2: Screen Analyzer"
            role="UI/UX Vision Analyzer"
            description="Figma ekran görüntüsünü detaylı biçimde analiz eder. Multimodal Gemini ile görsel analiz yapar."
            tasks={[
              'TÜM UI bileşenlerini tespit eder ve listeler',
              'Her bileşenin üzerindeki metni/label\'ı AYNEN yazar',
              'Sayfa yapısını ve navigasyon öğelerini tanımlar',
              'Form alanlarının tipini belirtir',
              'Görünür iş kurallarını tespit eder',
              'Kullanıcı akışı ve etkileşim kalıplarını değerlendirir',
            ]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="purple"
            name="⚖️ Agent 3: Compliance Checker"
            role="Requirement ↔ Design Validator"
            description="İş analizi gereksinimlerini tasarım ekranı analiziyle karşılaştırarak uyumluluk kontrolü yapar."
            tasks={[
              'Gereksinim ↔ Tasarım Eşleştirme (✅ UYUMLU / ⚠️ KISMİ / ❌ EKSİK)',
              'Eksik/Fazla Özellik Tespiti',
              'Acceptance Criteria Karşılaştırma',
              'UI Text/Label Doğrulama',
            ]}
            extra={
              <Space direction="vertical" size={0}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  🔴 KRİTİK - İş akışı etkileniyor
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  🟡 ORTA - UX sorunu var
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  🟢 DÜŞÜK - Minör iyileştirme
                </Text>
              </Space>
            }
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="purple"
            name="📊 Agent 4: Report Generator"
            role="Compliance Report Formatter"
            description="Uyumluluk kontrol sonuçlarını yapılandırılmış rapora dönüştürür. JIRA ticket oluşturulabilecek netlikte yazar."
            tasks={[
              '📊 Uyumluluk Özet Tablosu',
              '🔴 Kritik Bulgular',
              '🟡 Orta Bulgular',
              '🟢 Düşük Bulgular',
              '✅ Uyumlu Gereksinimler',
              '📝 Genel Değerlendirme',
            ]}
          />
        </Col>
      </Row>

      <Divider />

      <Title level={4}>
        <RocketOutlined /> BRD Pipeline Agents (Dual AI System)
      </Title>
      <Paragraph type="secondary">
        3 adet generation agent (Anthropic Claude) + QA referee agents (Gemini 2.5 Flash)
      </Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="📋 WF1: İş Analizi Generator"
            role="Business Requirements → BA Document"
            description="BRD dokümanından ekran bazlı İş Analizi üretir. 2-chunk strategy ile büyük dokümanları işler, sonra merge eder."
            tasks={[
              'Her ekran için: Açıklama, Gerekli Dokümanlar',
              'İş Akışı Diyagramı (adım adım)',
              'Fonksiyonel Gereksinimler (FR-001, FR-002...)',
              'İş Kuralları (BR-001, BR-002...)',
              'Kabul Kriterleri',
              'Validasyonlar (alan, kısıt, hata mesajı)',
            ]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                <strong>QA Referee:</strong> 6 kriter, Geçme: 60/100, Max 3 revizyon
              </Text>
            }
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="⚙️ WF2: Teknik Analiz Generator"
            role="BA → Technical Analysis"
            description="İş analizinden teknik analiz üretir. API endpoint, DTO, validasyon kuralları, cURL örnekleri ile developer-ready çıktı verir."
            tasks={[
              'Genel Tanım (modül, stack, mimari)',
              'API Endpoint Detayları (method, path, request/response)',
              'DTO Veri Yapıları (field, tip, zorunlu, validasyon)',
              'Validasyon Kuralları (VR-001, VR-002...)',
              'Response Error Scenarios (HTTP code, error code, mesaj)',
              'Mock cURL Örnekleri',
            ]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                <strong>QA Referee:</strong> 6 kriter, Geçme: 60/100, Max 3 revizyon
              </Text>
            }
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="blue"
            name="🧪 WF3: Test Case Generator"
            role="BA + TA → Test Cases"
            description="BA ve TA dokümanlarından 23-kolonlu Loodos şablonunda detaylı test case'ler üretir. Happy path + edge cases."
            tasks={[
              'test_case_id, br_id, tr_id, priority, channel',
              'testcase_type, user_type, test_area, test_scenario',
              'testcase, test_steps, precondition, test_data',
              'expected_result, postcondition, regression_case',
            ]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                <strong>QA Referee:</strong> 6 kriter, Hedef: 56+ test case
              </Text>
            }
          />
        </Col>
        <Col xs={24} lg={12}>
          <AgentCard
            color="purple"
            name="🔍 Checkpoint & Revision System"
            role="State Management & Quality Control"
            description="Her aşamada checkpoint kaydeder, kullanıcı onayı bekler. QA geçmezse max 3 kez revizyon yapar veya kullanıcı manuel düzeltme yapabilir."
            tasks={[
              'Session state + database checkpoint',
              'Manuel edit mode (kullanıcı JSON düzeltir)',
              'Skip QA option (force pass, API tasarrufu)',
              'Revizyon tracking (ba_revisions, ta_revisions, tc_revisions)',
              'Export ready: BA/TA (DOCX), TC (CSV/Excel)',
            ]}
          />
        </Col>
      </Row>
    </Space>
  );
}

// ============================================================================
// Tab 2: Document Intelligence
// ============================================================================

function DocumentIntelligenceTab() {
  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card>
        <Paragraph>
          <strong>🚀 Phase 2 Özellikleri:</strong> Doküman depolama, akıllı arama, AI-destekli
          eşleştirme ve doküman yönetimi özellikleri içeren kapsamlı bir doküman repository
          sistemi.
        </Paragraph>
      </Card>

      <Title level={4}>📁 Document Repository</Title>
      <Paragraph type="secondary">Merkezi doküman depolama ve yönetim sistemi</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="📚 Document Library" bordered>
            <Paragraph>
              Tüm BA, TA ve TC dokümanlarını merkezi bir yerde depolar, versiyonlar ve kategorize
              eder.
            </Paragraph>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Özellikler">
                Multi-tab arayüz, Doküman tipi filtreleme, Proje entegrasyonu, Versiyon yönetimi,
                Google Docs/Sheets import
              </Descriptions.Item>
              <Descriptions.Item label="Veri Modeli">
                documents table (metadata), document_content table (full text + enriched chunks)
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="🔀 Import & Merge" bordered>
            <Paragraph>
              Google Drive klasörlerinden toplu doküman import eder, duplicate detection yapar ve
              mevcut dokümanları günceller.
            </Paragraph>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Görevler">
                Folder ID ile batch import, Akıllı duplicate detection, Merge stratejileri, Import
                sonuç raporları
              </Descriptions.Item>
              <Descriptions.Item label="n8n Entegrasyonu">
                Google Drive folder listing webhook, Automated content fetch
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Divider />

      <Title level={4}>🔍 Hybrid Search System</Title>
      <Paragraph type="secondary">Semantic + Keyword dual search engine</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="🧠 ChromaDB Vector Store" bordered>
            <Paragraph>
              Embedding kullanarak dokümanları vektör uzayında depolar ve semantic similarity
              araması yapar.
            </Paragraph>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Embedding Model">
                intfloat/multilingual-e5-base (384 dimensions)
              </Descriptions.Item>
              <Descriptions.Item label="Collection">ba_qa_documents (571 chunks)</Descriptions.Item>
              <Descriptions.Item label="Metadata">
                doc_id, type, project, JIRA key
              </Descriptions.Item>
              <Descriptions.Item label="Enriched Chunks">
                BA: fonksiyonel_gereksinimler, is_kurallari | TA: request_body, response_body | TC:
                precondition, test_data
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="📝 TF-IDF Keyword Search" bordered>
            <Paragraph>
              scikit-learn TF-IDF vectorizer ile keyword-based arama yapar. Exact match ve
              technical term detection için optimize edilmiş.
            </Paragraph>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Features">
                TF-IDF vectorization (max_features=5000), Cosine similarity, N-gram support (1-2),
                Stop words filtering
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <Title level={5}>⚡ Hybrid Fusion Algorithm</Title>
        <Paragraph>
          <strong>Formül:</strong> <code>hybrid_score = 0.4 × keyword_score + 0.6 × semantic_score</code>
        </Paragraph>
        <Paragraph type="secondary">
          <strong>Alpha Weighting:</strong> %40 keyword (exact match) + %60 semantic (intent match)
          <br />
          <strong>Result Deduplication:</strong> Chunk-level → Document-level aggregation
          <br />
          <strong>Ortalama Performans:</strong> &lt;2s response time, 85%+ relevance
        </Paragraph>
      </Card>

      <Divider />

      <Title level={4}>🎯 Smart Matching System</Title>
      <Paragraph type="secondary">AI-powered task-to-document matching</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="🧪 Rule-Based Analyzer (Tier 1)" bordered>
            <Paragraph>
              NLP heuristikleri ile görev açıklamalarını analiz eder. Basit sorgular için AI
              maliyeti olmadan çalışır (%70 maliyet tasarrufu).
            </Paragraph>
            <Tag color="blue">Confidence &gt;0.7 → Free</Tag>
            <Tag color="orange">Confidence &lt;0.7 → AI ($0.002)</Tag>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="🤖 AI Task Analyzer (Tier 2)" bordered>
            <Paragraph>
              Karmaşık görevler için Claude Sonnet ile detaylı analiz yapar. Keywords, intent,
              scope, entities ve doc_type_relevance çıkarır.
            </Paragraph>
            <Paragraph type="secondary">
              Output Schema: keywords, intent, scope, entities, doc_type_relevance, complexity
            </Paragraph>
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <Title level={5}>📈 Smart Matching Metrics</Title>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="Match Accuracy" value="85%" valueStyle={{ color: '#3b82f6' }} />
          </Col>
          <Col span={6}>
            <Statistic title="Acceptance Rate" value="73%" valueStyle={{ color: '#10b981' }} />
          </Col>
          <Col span={6}>
            <Statistic title="Response Time" value="<2s" valueStyle={{ color: '#f59e0b' }} />
          </Col>
          <Col span={6}>
            <Statistic title="Cost/Query" value="$0.007" valueStyle={{ color: '#8b5cf6' }} />
          </Col>
        </Row>
      </Card>
    </Space>
  );
}

// ============================================================================
// Tab 3: Integrations
// ============================================================================

function IntegrationsTab() {
  const integrations = [
    {
      icon: '🔗',
      name: 'n8n Webhook Proxy (Google Docs)',
      endpoint: 'https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy',
      description:
        'Google Docs API authentication bypass için n8n workflow kullanır. BA dokümanlarını proxy üzerinden çeker.',
      methods: ['GET', '?doc_id={id}', 'timeout: 120s'],
      usage: 'BA Değerlendirme ve QA Değerlendirme pipeline\'larında',
    },
    {
      icon: '📊',
      name: 'n8n Webhook Proxy (Google Sheets)',
      endpoint: 'https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy',
      description:
        'Google Sheets API authentication bypass için n8n workflow kullanır. TC dokümanlarını (23 sütun) proxy üzerinden çeker.',
      methods: ['GET', '?spreadsheet_id={id}', 'timeout: 120s'],
      usage: "QA Değerlendirme pipeline'ında",
    },
    {
      icon: '🔑',
      name: 'JIRA REST API v3',
      endpoint: 'https://loodos.atlassian.net/rest/api/3/',
      description: 'JIRA Cloud REST API ile task yönetimi. Basic Auth (email + API token) kullanır.',
      methods: [
        'jira_search()',
        'jira_get_issue()',
        'jira_add_label()',
        'jira_add_comment()',
      ],
      usage: 'JQL ile task arama, Label yönetimi, Comment ekleme',
    },
    {
      icon: '📄',
      name: 'Google Docs Direct Export',
      endpoint: 'https://docs.google.com/document/d/{id}/export?format=txt',
      description:
        "Public paylaşılan Google Docs'u doğrudan export endpoint ile çeker. n8n proxy'ye alternatif.",
      methods: ['GET', 'Public Sharing Required', 'timeout: 30s'],
      usage: 'Design Compliance page\'de manuel BA upload için',
    },
    {
      icon: '🧠',
      name: 'Gemini 2.5 Flash API',
      endpoint: 'Google Generative AI API',
      description:
        "Tüm AI agent'ların backend'i. Agno Framework üzerinden Gemini 2.5 Flash modeli kullanır. 1M token context window.",
      methods: ['Model: gemini-2.5-flash', 'Context: 1M tokens', 'Multimodal'],
      usage: 'Text generation, Vision, Structured output',
    },
    {
      icon: '🤖',
      name: 'Anthropic Claude API',
      endpoint: 'Anthropic Messages API',
      description:
        "BRD Pipeline'da doküman generation için kullanılır. Anthropic Claude modeli ile BA, TA, TC üretimi yapar.",
      methods: ['Provider: Anthropic', 'Context: 200k tokens', 'Max Output: 16k tokens'],
      usage: 'BRD → BA, BA → TA, BA + TA → TC generation',
    },
    {
      icon: '💾',
      name: 'SQLite Database',
      endpoint: 'Local File: data/baqa.db',
      description:
        "Platform'un ana veri deposu. Analiz sonuçları, skorlar, raporlar, pipeline runs ve geçmiş veriler saklanır.",
      methods: ['analyses', 'pipeline_runs', 'documents', 'task_matches'],
      usage: '9 ana tablo (analyses, ba_results, tc_results, design_results, etc.)',
    },
    {
      icon: '🧠',
      name: 'ChromaDB Vector Database',
      endpoint: 'Local Persist: data/chroma_db/',
      description:
        'Doküman embedding\'lerini depolar ve semantic similarity araması yapar. 384-dimensional embeddings kullanır.',
      methods: ['Collection: ba_qa_documents', '571 chunks', 'Cosine Similarity'],
      usage: 'Persistent storage, metadata filtering, incremental updates',
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      {integrations.map((integration, idx) => (
        <Col xs={24} lg={12} key={idx}>
          <Card
            title={
              <Space>
                <span style={{ fontSize: 24 }}>{integration.icon}</span>
                <div>
                  <div>{integration.name}</div>
                  <Text type="secondary" style={{ fontSize: 11 }} code>
                    {integration.endpoint}
                  </Text>
                </div>
              </Space>
            }
            bordered
          >
            <Paragraph>{integration.description}</Paragraph>
            <Space wrap style={{ marginBottom: 12 }}>
              {integration.methods.map((method, i) => (
                <Tag color="blue" key={i}>
                  {method}
                </Tag>
              ))}
            </Space>
            <Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 0 }}>
              <strong>Kullanım:</strong> {integration.usage}
            </Paragraph>
          </Card>
        </Col>
      ))}
    </Row>
  );
}

// ============================================================================
// Tab 4: Pipeline Flows
// ============================================================================

function PipelineFlowsTab() {
  const pipelines = [
    {
      title: '🔵 Pipeline 1: BA Değerlendirme (4-Agent Sequential)',
      steps: [
        { num: 1, name: 'JIRA Tarayıcı', desc: 'JQL ile BA task\'ları tarar, Google Docs URL çıkarır' },
        { num: 2, name: 'Doküman Okuyucu', desc: 'n8n proxy ile BA dokümanını çeker ve parse eder' },
        {
          num: 3,
          name: 'Kalite Değerlendirici',
          desc: '9 kriter üzerinden AI analizi yapar (Gemini 2.5 Flash)',
        },
        {
          num: 4,
          name: 'Raporcu',
          desc: 'JIRA\'ya comment yazar, label\'ları günceller, DB\'ye kaydeder',
        },
      ],
      usage: 'BA Değerlendirme sayfasından "⚡ Sıradakini Otomatik Değerlendir" butonu',
      duration: '45-60 saniye',
      output: '9 kriter puanı, genel puan (0-100), JIRA comment, qa-gecti/qa-gecmedi label',
    },
    {
      title: '🟢 Pipeline 2: QA Değerlendirme (4-Agent Sequential + BA Link)',
      steps: [
        {
          num: 1,
          name: 'JIRA & Sheet Tarayıcı',
          desc: 'TC task bulur, linked BA task\'ı tespit eder, Sheet URL çıkarır',
        },
        {
          num: 2,
          name: 'Doküman Birleştirici',
          desc: 'BA dokümanı + TC sheets\'i n8n proxy ile çeker ve birleştirir',
        },
        { num: 3, name: 'TC Değerlendirici', desc: '8 kriter üzerinden AI analizi yapar, BA coverage kontrolü' },
        { num: 4, name: 'TC Raporcu', desc: 'JIRA comment, tc-qa-gecti/gecmedi label, DB kayıt' },
      ],
      usage: 'QA Değerlendirme sayfasından "⚡ Sıradakini Otomatik Değerlendir" butonu',
      duration: '60-75 saniye (BA fetch dahil)',
      output: '8 kriter puanı, coverage metrikleri, JIRA comment, tc-qa-gecti/gecmedi label',
    },
    {
      title: '🟣 Pipeline 3: Design Compliance (4-Agent Parallel + Sequential)',
      steps: [
        {
          num: 1,
          name: 'Requirements Extractor',
          desc: "BA'dan REQ-001, REQ-002... formatında gereksinimleri çıkarır",
        },
        { num: 2, name: 'Screen Analyzer', desc: 'Figma ekranlarını Vision AI ile analiz eder (multimodal Gemini)' },
        { num: 3, name: 'Compliance Checker', desc: 'REQ ↔ Screen eşleştirmesi yapar, uyumluluk kontrolü' },
        { num: 4, name: 'Report Generator', desc: 'Uyumluluk raporu oluşturur (🔴🟡🟢 bulgular)' },
      ],
      usage: 'Design Compliance sayfasından "🚀 Uyumluluk Kontrolünü Başlat" butonu',
      duration: '90-120 saniye (ekran sayısına göre değişir)',
      output: 'Uyumluluk matrisi, kritik/orta/düşük bulgular, eksik gereksinimler, Markdown rapor',
    },
    {
      title: '🟠 Pipeline 4: BRD Pipeline (3-Stage Sequential with QA Referee)',
      steps: [
        { num: 1, name: 'WF1: BA Generator', desc: 'BRD → BA (Claude AI) → QA (Gemini) → Manual Review' },
        { num: 2, name: 'WF2: TA Generator', desc: 'BA → TA (Claude AI) → QA (Gemini) → Manual Review' },
        { num: 3, name: 'WF3: TC Generator', desc: 'BA + TA → TC (Claude AI) → QA (Gemini) → Export' },
      ],
      usage: 'BRD Pipeline sayfasından BRD upload → Adım adım manuel onay ile ilerler',
      duration: '5-8 dakika (3 stage × 2 chunk + QA + revisions)',
      output: 'BA (DOCX), TA (DOCX), TC (CSV + Excel 23 kolon), QA skorları, revision tracking',
    },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {pipelines.map((pipeline, idx) => (
        <Card key={idx} title={<Title level={5}>{pipeline.title}</Title>} bordered>
          <Row gutter={8} style={{ marginBottom: 16 }}>
            {pipeline.steps.map((step, i) => (
              <>
                <Col flex="1" key={`step-${i}`}>
                  <Card size="small" style={{ textAlign: 'center', height: '100%' }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #3b82f6, #06b6d4)',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 8px',
                        fontWeight: 700,
                      }}
                    >
                      {step.num}
                    </div>
                    <Text strong style={{ fontSize: 13 }}>
                      {step.name}
                    </Text>
                    <Paragraph type="secondary" style={{ fontSize: 11, marginTop: 8 }}>
                      {step.desc}
                    </Paragraph>
                  </Card>
                </Col>
                {i < pipeline.steps.length - 1 && (
                  <Col key={`arrow-${i}`} style={{ display: 'flex', alignItems: 'center' }}>
                    <Text style={{ fontSize: 24, color: '#3b82f6' }}>→</Text>
                  </Col>
                )}
              </>
            ))}
          </Row>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="Kullanım">{pipeline.usage}</Descriptions.Item>
            <Descriptions.Item label="Ortalama Süre">{pipeline.duration}</Descriptions.Item>
            <Descriptions.Item label="Çıktı">{pipeline.output}</Descriptions.Item>
          </Descriptions>
        </Card>
      ))}
    </Space>
  );
}

// ============================================================================
// Tab 5: Tech Stack
// ============================================================================

function TechStackTab() {
  const stacks = [
    {
      title: '🐍 Backend',
      items: [
        'Python 3.11+',
        'FastAPI',
        'SQLite',
        'ChromaDB',
        'scikit-learn (TF-IDF)',
        'sentence-transformers',
      ],
    },
    {
      title: '🧠 AI / LLM',
      items: [
        'Gemini 2.5 Flash (Evaluation)',
        'Anthropic Claude (Generation)',
        'intfloat/multilingual-e5-base (Embeddings - 384d)',
        '200k-1M token context',
        'Multimodal (vision)',
        'Structured JSON output',
      ],
    },
    {
      title: '🔗 Entegrasyonlar',
      items: ['JIRA REST API v3', 'n8n Webhook Proxy', 'Google Docs/Sheets', 'Google Drive API'],
    },
    {
      title: '💾 Data Storage',
      items: ['SQLite (metadata)', 'ChromaDB (embeddings)', 'File cache (TTL: 1h)'],
    },
    {
      title: '⚛️ Frontend',
      items: ['React 18', 'Vite', 'Ant Design v5', 'TanStack Query v5', 'React Router v6'],
    },
    {
      title: '🚀 Deployment',
      items: ['FastAPI (port 8000)', 'Vite Dev Server (port 5173)', 'Environment variables (.env)'],
    },
  ];

  return (
    <Row gutter={[16, 16]}>
      {stacks.map((stack, idx) => (
        <Col xs={24} sm={12} lg={8} key={idx}>
          <Card title={stack.title} bordered>
            <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
              {stack.items.map((item, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  <Text>{item}</Text>
                </li>
              ))}
            </ul>
          </Card>
        </Col>
      ))}
    </Row>
  );
}

// ============================================================================
// Reusable Agent Card Component
// ============================================================================

function AgentCard({ color, name, role, description, tasks, extra }) {
  const { token } = theme.useToken();
  const borderColors = {
    blue: '#3b82f6',
    green: '#10b981',
    purple: '#8b5cf6',
  };

  return (
    <Card
      style={{
        borderLeft: `4px solid ${borderColors[color]}`,
        height: '100%',
      }}
      bordered
    >
      <Title level={5} style={{ marginBottom: 4 }}>
        {name}
      </Title>
      <Text type="secondary" italic style={{ fontSize: 13, display: 'block', marginBottom: 12 }}>
        {role}
      </Text>
      <Paragraph style={{ fontSize: 14 }}>{description}</Paragraph>

      <Card size="small" type="inner" style={{ marginTop: 12 }}>
        <Text strong style={{ fontSize: 11, color: '#06b6d4', textTransform: 'uppercase' }}>
          {tasks.length > 5 ? 'Değerlendirme Kriterleri' : 'Görevler'}
        </Text>
        <ul style={{ paddingLeft: 20, marginTop: 8, marginBottom: 0 }}>
          {tasks.map((task, idx) => (
            <li key={idx} style={{ fontSize: 12, color: token.colorTextTertiary, marginBottom: 4 }}>
              {task}
            </li>
          ))}
        </ul>
      </Card>

      {extra && (
        <div style={{ marginTop: 12, padding: 8, background: token.colorPrimaryBg, borderRadius: 6 }}>
          {extra}
        </div>
      )}
    </Card>
  );
}
