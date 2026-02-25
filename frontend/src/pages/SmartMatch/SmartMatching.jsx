/**
 * Smart Matching Page
 *
 * AI-powered task-to-document matching to help users find relevant existing documents.
 */
import React, { useState } from 'react';
import {
  Typography,
  Input,
  Select,
  Button,
  Card,
  Row,
  Col,
  Statistic,
  Space,
  Empty,
  Progress,
  Tag,
  Collapse,
  Descriptions,
  message,
  Spin,
  Segmented,
  Tabs,
  Tooltip,
  Alert,
  theme,
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  CheckOutlined,
  CloseOutlined,
  ThunderboltOutlined,
  LinkOutlined,
  GoogleOutlined,
  FileTextOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileOutlined,
  ClockCircleOutlined,
  UserOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useSearchMatches, useMatchAnalytics, useRecordMatch } from '../../api/matching';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Panel } = Collapse;

// ── MIME filter options ────────────────────────────────────────
const MIME_FILTERS = [
  { label: 'Tümü', value: '' },
  { label: 'Docs', value: 'docs' },
  { label: 'Sheets', value: 'sheets' },
  { label: 'Word', value: 'docx' },
  { label: 'PDF', value: 'pdf' },
];

// ── MIME type → icon/label/color mapping ──────────────────────
const MIME_INFO = {
  'application/vnd.google-apps.document': { icon: <FileTextOutlined style={{ color: '#4285f4' }} />, label: 'Google Docs', color: 'blue' },
  'application/vnd.google-apps.spreadsheet': { icon: <FileExcelOutlined style={{ color: '#0f9d58' }} />, label: 'Google Sheets', color: 'green' },
  'application/vnd.google-apps.presentation': { icon: <FileOutlined style={{ color: '#f4b400' }} />, label: 'Slides', color: 'orange' },
  'application/pdf': { icon: <FilePdfOutlined style={{ color: '#ea4335' }} />, label: 'PDF', color: 'red' },
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { icon: <FileWordOutlined style={{ color: '#2b579a' }} />, label: 'Word', color: 'blue' },
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { icon: <FileExcelOutlined style={{ color: '#217346' }} />, label: 'Excel', color: 'green' },
  'application/msword': { icon: <FileWordOutlined style={{ color: '#2b579a' }} />, label: 'Word', color: 'blue' },
  'text/plain': { icon: <FileTextOutlined />, label: 'Metin', color: 'default' },
};

function getMimeInfo(mimeType = '') {
  if (MIME_INFO[mimeType]) return MIME_INFO[mimeType];
  if (mimeType.includes('document')) return { icon: <FileTextOutlined />, label: 'Doküman', color: 'default' };
  if (mimeType.includes('spreadsheet')) return { icon: <FileExcelOutlined />, label: 'Tablo', color: 'green' };
  if (mimeType.includes('pdf')) return { icon: <FilePdfOutlined />, label: 'PDF', color: 'red' };
  return { icon: <FileOutlined />, label: 'Dosya', color: 'default' };
}

function formatRelativeDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Bugün';
  if (diffDays === 1) return 'Dün';
  if (diffDays < 7) return `${diffDays} gün önce`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} hafta önce`;
  return date.toLocaleDateString('tr-TR');
}

function formatSize(bytes) {
  if (!bytes) return '';
  const num = Number(bytes);
  if (isNaN(num)) return '';
  if (num < 1024) return `${num} B`;
  if (num < 1024 * 1024) return `${(num / 1024).toFixed(1)} KB`;
  return `${(num / (1024 * 1024)).toFixed(1)} MB`;
}

export default function SmartMatching() {
  const navigate = useNavigate();

  // State
  const [timeRange, setTimeRange] = useState('all');
  const [jiraKey, setJiraKey] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [taskDescription, setTaskDescription] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [source, setSource] = useState('Platform');
  const [mimeFilter, setMimeFilter] = useState('');
  const [resultTab, setResultTab] = useState('all');
  const sourceMap = { Platform: 'platform', Drive: 'drive', 'Tümü': 'both' };

  // API hooks
  const { data: analytics } = useMatchAnalytics(timeRange);
  const searchMutation = useSearchMatches();
  const recordMutation = useRecordMatch();
  const { token } = theme.useToken();

  // Handle search
  const handleSearch = async () => {
    if (!taskDescription.trim()) {
      message.error('Lütfen bir görev açıklaması girin.');
      return;
    }

    try {
      const result = await searchMutation.mutateAsync({
        task_description: taskDescription,
        jira_key: jiraKey || undefined,
        doc_type: docTypeFilter === 'all' ? undefined : docTypeFilter,
        top_k: 5,
        source: sourceMap[source],
        mime_type_filter: mimeFilter,
      });

      setSearchResults(result);

      // Record no-match event if no results
      if (result.matches.length === 0) {
        await recordMutation.mutateAsync({
          task_description: taskDescription,
          task_features: result.task_features || {},
          matched_document_id: null,
          confidence_score: 0.0,
          match_reasoning: 'No matches found',
          suggestion: 'CREATE_NEW',
          jira_key: jiraKey || undefined,
          user_accepted: false,
        });
      }
    } catch (error) {
      message.error('Eşleşme araması başarısız oldu.');
      console.error('Search error:', error);
    }
  };

  // Handle clear
  const handleClear = () => {
    setSearchResults(null);
    setTaskDescription('');
    setJiraKey('');
  };

  // Handle view document
  const handleView = (documentId) => {
    navigate(`/documents/${documentId}`);
  };

  // Handle use document
  const handleUse = async (match) => {
    try {
      await recordMutation.mutateAsync({
        task_description: taskDescription,
        task_features: match.task_features,
        matched_document_id: match.document_id,
        confidence_score: match.confidence,
        match_reasoning: match.reasoning,
        suggestion: match.suggestion,
        jira_key: jiraKey || undefined,
        user_accepted: true,
      });

      message.success(`Doküman kullanılıyor: ${match.title}`);
      setTimeout(() => {
        navigate(`/documents/${match.document_id}`);
      }, 1000);
    } catch (error) {
      message.error('Kayıt başarısız oldu.');
      console.error('Record error:', error);
    }
  };

  // Handle reject document
  const handleReject = async (match) => {
    try {
      await recordMutation.mutateAsync({
        task_description: taskDescription,
        task_features: match.task_features,
        matched_document_id: match.document_id,
        confidence_score: match.confidence,
        match_reasoning: match.reasoning,
        suggestion: match.suggestion,
        jira_key: jiraKey || undefined,
        user_accepted: false,
      });

      message.info('Geri bildirim kaydedildi. Teşekkürler!');
    } catch (error) {
      message.error('Kayıt başarısız oldu.');
      console.error('Record error:', error);
    }
  };

  // Helper to get confidence color and label
  const getConfidenceStyle = (confidence) => {
    if (confidence >= 0.75) {
      return { color: 'green', emoji: '🟢', label: 'Yüksek' };
    } else if (confidence >= 0.5) {
      return { color: 'orange', emoji: '🟡', label: 'Orta' };
    } else {
      return { color: 'red', emoji: '🔴', label: 'Düşük' };
    }
  };

  // Helper to get suggestion badge
  const getSuggestionBadge = (suggestion) => {
    const badges = {
      UPDATE_EXISTING: { emoji: '🟢', label: 'UPDATE EXISTING', color: 'success' },
      CREATE_NEW: { emoji: '🔴', label: 'CREATE NEW', color: 'error' },
      EXTEND_DOCUMENT: { emoji: '🟡', label: 'EXTEND DOCUMENT', color: 'warning' },
      EVALUATE: { emoji: '⚪', label: 'EVALUATE', color: 'default' },
    };
    return badges[suggestion] || badges.EVALUATE;
  };

  // Result counts
  const platformCount = searchResults?.matches?.length || 0;
  const driveCount = searchResults?.drive_matches?.length || 0;
  const totalCount = platformCount + driveCount;

  // ── Render helpers for tab contents ────────────────────────

  const renderPlatformResults = () => {
    if (platformCount === 0) {
      return (
        <Empty description={
          <div>
            <Paragraph>Platformda ilgili doküman bulunamadı.</Paragraph>
            <Paragraph type="secondary">Yeni doküman oluşturmayı düşünün.</Paragraph>
          </div>
        } />
      );
    }
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {searchResults.matches.map((match, index) => (
          <MatchCard
            key={match.document_id}
            match={match}
            rank={index + 1}
            onView={handleView}
            onUse={handleUse}
            onReject={handleReject}
            getConfidenceStyle={getConfidenceStyle}
            getSuggestionBadge={getSuggestionBadge}
          />
        ))}
      </Space>
    );
  };

  const renderDriveResults = () => {
    if (driveCount === 0) {
      return (
        <Empty description={
          <div>
            <Paragraph>Drive'da sonuç bulunamadı.</Paragraph>
            <Paragraph type="secondary">Dosya türü filtresini değiştirmeyi deneyin.</Paragraph>
          </div>
        } />
      );
    }
    return (
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {searchResults.drive_matches.map((item) => (
          <DriveMatchCard key={item.file_id} item={item} token={token} />
        ))}
      </Space>
    );
  };

  const renderAllResults = () => {
    if (totalCount === 0) {
      return (
        <Empty description={
          <div>
            <Paragraph>Hiçbir kaynakta sonuç bulunamadı.</Paragraph>
            <Paragraph type="secondary">Farklı anahtar kelimeler deneyin.</Paragraph>
          </div>
        } />
      );
    }
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Platform section */}
        {platformCount > 0 ? (
          <>
            <Text strong style={{ fontSize: 14 }}>
              <DatabaseOutlined /> Platform Sonuçları ({platformCount})
            </Text>
            {searchResults.matches.map((match, index) => (
              <MatchCard
                key={match.document_id}
                match={match}
                rank={index + 1}
                onView={handleView}
                onUse={handleUse}
                onReject={handleReject}
                getConfidenceStyle={getConfidenceStyle}
                getSuggestionBadge={getSuggestionBadge}
              />
            ))}
          </>
        ) : driveCount > 0 && (
          <Alert type="info" showIcon message="Platformda ilgili doküman bulunamadı. Yeni doküman oluşturmayı düşünün." />
        )}

        {/* Drive section */}
        {driveCount > 0 ? (
          <>
            <Text strong style={{ fontSize: 14 }}>
              <GoogleOutlined /> Drive Sonuçları ({driveCount})
            </Text>
            {searchResults.drive_matches.map((item) => (
              <DriveMatchCard key={item.file_id} item={item} token={token} />
            ))}
          </>
        ) : platformCount > 0 && (
          <Alert type="info" showIcon message="Drive'da sonuç bulunamadı. Dosya türü filtresini değiştirmeyi deneyin." />
        )}

        <Paragraph type="secondary" style={{ textAlign: 'center', marginTop: 16 }}>
          💡 <strong>İpucu:</strong> Daha yüksek güven skorları (yeşil) daha güçlü eşleşmeleri gösterir.
          Sonuçlardan herhangi bir dokümanı görüntüleyebilir veya kullanabilirsiniz.
        </Paragraph>
      </Space>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          🔍 Akıllı Doküman Eşleştirme
        </Title>
        <Paragraph>
          <strong>AI destekli görev-doküman eşleştirme</strong> — Görevinizi tanımlayın ve ilgili mevcut dokümanları bulun.
          Tekrar eden iş yapmaktan kaçınarak zamandan tasarruf edin ve mevcut dokümanları yeniden kullanın.
        </Paragraph>
      </div>

      {/* Analytics Section */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Text strong>📊 Analitik Periyodu:</Text>
          </Col>
          <Col>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: 150 }}
              options={[
                { value: '7days', label: 'Son 7 Gün' },
                { value: '30days', label: 'Son 30 Gün' },
                { value: '90days', label: 'Son 90 Gün' },
                { value: 'all', label: 'Tüm Zamanlar' },
              ]}
            />
          </Col>
        </Row>

        {analytics && (
          <Row gutter={16}>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="📊 Toplam Eşleşme"
                value={analytics.total_matches}
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="✅ Kabul Edilen"
                value={analytics.total_accepted}
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="📈 Kabul Oranı"
                value={analytics.acceptance_rate}
                precision={1}
                suffix="%"
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="🎯 Ort. Güven Skoru"
                value={analytics.avg_confidence}
                precision={2}
              />
            </Col>
          </Row>
        )}
      </Card>

      {/* Input Section */}
      <Card title="1️⃣ Görevinizi Tanımlayın" style={{ marginBottom: 24 }}>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={24} md={source !== 'Platform' ? 8 : 12}>
            <Text strong>JIRA Anahtarı (Opsiyonel)</Text>
            <Input
              placeholder="örn: PROJ-123"
              value={jiraKey}
              onChange={(e) => setJiraKey(e.target.value)}
              style={{ marginTop: 8 }}
            />
          </Col>
          <Col xs={24} md={6}>
            <Text strong>Doküman Tipi</Text>
            <Select
              value={docTypeFilter}
              onChange={setDocTypeFilter}
              style={{ width: '100%', marginTop: 8 }}
              options={[
                { value: 'all', label: 'Tüm Tipler' },
                { value: 'ba', label: 'BA Dokümanları' },
                { value: 'ta', label: 'TA Dokümanları' },
                { value: 'tc', label: 'Test Senaryoları' },
              ]}
            />
          </Col>
          <Col xs={24} md={source !== 'Platform' ? 4 : 6}>
            <Text strong>Kaynak</Text>
            <div style={{ marginTop: 8 }}>
              <Segmented
                options={['Platform', 'Drive', 'Tümü']}
                value={source}
                onChange={(val) => { setSource(val); setResultTab('all'); }}
                block
              />
            </div>
          </Col>
          {source !== 'Platform' && (
            <Col xs={24} md={6}>
              <Text strong>Dosya Türü</Text>
              <div style={{ marginTop: 8 }}>
                <Segmented
                  options={MIME_FILTERS}
                  value={mimeFilter}
                  onChange={setMimeFilter}
                  block
                />
              </div>
            </Col>
          )}
        </Row>

        <Text strong>Görev Açıklaması</Text>
        <TextArea
          placeholder={`Ne yapmanız gerektiğini açıklayın...\n\nÖrnek: Mobil uygulama için login ekranına biyometrik kimlik doğrulama (Face ID ve Touch ID) ekle`}
          value={taskDescription}
          onChange={(e) => setTaskDescription(e.target.value)}
          rows={6}
          style={{ marginTop: 8, marginBottom: 16 }}
        />

        <Space>
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={searchMutation.isPending}
            size="large"
          >
            Eşleşme Bul
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleClear}
            size="large"
          >
            Temizle
          </Button>
        </Space>
      </Card>

      {/* Results Section */}
      {searchMutation.isPending && (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <Paragraph style={{ marginTop: 16 }}>Görev analiz ediliyor...</Paragraph>
          </div>
        </Card>
      )}

      {searchResults && !searchMutation.isPending && (
        <>
          {/* Task Analysis */}
          {(platformCount > 0 || driveCount > 0) && searchResults.task_features && (
            <Card style={{ marginBottom: 24 }}>
              <Collapse>
                <Panel header="📋 Görev Analizi" key="1">
                  <Descriptions column={3} size="small">
                    <Descriptions.Item label="Niyet">
                      {searchResults.task_features.intent || 'Bilinmiyor'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Karmaşıklık">
                      {searchResults.task_features.complexity || 'Bilinmiyor'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Kapsam">
                      {searchResults.task_features.scope || 'Bilinmiyor'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Anahtar Kelimeler" span={3}>
                      {searchResults.task_features.keywords?.slice(0, 5).join(', ') || 'Yok'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Doküman Tipi İlgisi" span={3}>
                      {searchResults.task_features.doc_type_relevance && (
                        <Space>
                          <Tag>BA: {searchResults.task_features.doc_type_relevance.ba?.toFixed(2) || '0.00'}</Tag>
                          <Tag>TA: {searchResults.task_features.doc_type_relevance.ta?.toFixed(2) || '0.00'}</Tag>
                          <Tag>TC: {searchResults.task_features.doc_type_relevance.tc?.toFixed(2) || '0.00'}</Tag>
                        </Space>
                      )}
                    </Descriptions.Item>
                  </Descriptions>
                </Panel>
              </Collapse>
            </Card>
          )}

          {/* Tabbed Results */}
          <Card
            title={
              <div>
                2️⃣ Eşleşme Sonuçları ({totalCount} bulundu, {searchResults.response_time.toFixed(2)}s)
              </div>
            }
          >
            <Tabs
              activeKey={resultTab}
              onChange={setResultTab}
              items={[
                {
                  key: 'all',
                  label: `Tümü (${totalCount})`,
                  children: renderAllResults(),
                },
                {
                  key: 'platform',
                  label: `Platform (${platformCount})`,
                  children: renderPlatformResults(),
                },
                {
                  key: 'drive',
                  label: `Drive (${driveCount})`,
                  children: renderDriveResults(),
                },
              ]}
            />
          </Card>
        </>
      )}
    </div>
  );
}

/**
 * Drive Match Card Component — enriched Drive result card
 */
function DriveMatchCard({ item, token }) {
  const mime = getMimeInfo(item.mimeType);
  return (
    <Card size="small" style={{ borderLeft: `4px solid ${token.colorSuccess}` }}>
      <Row gutter={16} align="middle">
        <Col flex="auto">
          <Space wrap>
            {mime.icon}
            <a href={item.webViewLink} target="_blank" rel="noopener noreferrer">
              <Text strong>{item.name}</Text>
            </a>
            <Tag color={mime.color}>{mime.label}</Tag>
            <Tag color="success">Drive</Tag>
            <Tag>{item.relevance_tag}</Tag>
          </Space>
          <div style={{ marginTop: 4 }}>
            <Space size="large" wrap>
              {item.modifiedTime && (
                <Tooltip title={new Date(item.modifiedTime).toLocaleString('tr-TR')}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    <ClockCircleOutlined /> {formatRelativeDate(item.modifiedTime)}
                  </Text>
                </Tooltip>
              )}
              {item.lastModifiedBy && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <UserOutlined /> {item.lastModifiedBy}
                </Text>
              )}
              {item.size && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatSize(item.size)}
                </Text>
              )}
              {item.relevance_score > 0 && (
                <Tag color="blue">%{Math.round(item.relevance_score * 100)}</Tag>
              )}
            </Space>
          </div>
        </Col>
        <Col>
          <Button
            type="primary"
            ghost
            icon={<LinkOutlined />}
            href={item.webViewLink}
            target="_blank"
          >
            Drive'da Aç
          </Button>
        </Col>
      </Row>
    </Card>
  );
}

/**
 * Match Card Component
 */
function MatchCard({ match, rank, onView, onUse, onReject, getConfidenceStyle, getSuggestionBadge }) {
  const { token } = theme.useToken();
  const confidenceStyle = getConfidenceStyle(match.confidence);
  const suggestionBadge = getSuggestionBadge(match.suggestion);

  return (
    <Card
      style={{
        borderLeft: `4px solid ${confidenceStyle.color}`,
      }}
    >
      <Row gutter={16}>
        <Col xs={24} md={14}>
          <Title level={4}>
            {confidenceStyle.emoji} {rank}. {match.title}
          </Title>
          <Text type="secondary">
            <strong>Tip:</strong> {match.doc_type.toUpperCase()} | <strong>Versiyon:</strong> {match.version}
          </Text>
        </Col>
        <Col xs={24} md={5}>
          <Statistic
            title="Güven Skoru"
            value={(match.confidence * 100).toFixed(0)}
            suffix="%"
            valueStyle={{ color: confidenceStyle.color }}
          />
          <Text type="secondary">{confidenceStyle.label} güven skoru</Text>
        </Col>
        <Col xs={24} md={5}>
          <div>
            <Text strong>Öneri</Text>
            <div style={{ marginTop: 8 }}>
              <Tag color={suggestionBadge.color}>
                {suggestionBadge.emoji} {suggestionBadge.label}
              </Tag>
            </div>
          </div>
        </Col>
      </Row>

      {match.section_matched && (
        <div style={{ marginTop: 16 }}>
          <Text strong>Eşleşen Bölüm Önizlemesi:</Text>
          <Paragraph
            ellipsis={{ rows: 3 }}
            style={{
              backgroundColor: token.colorBgLayout,
              padding: '12px',
              borderRadius: '4px',
              marginTop: 8,
            }}
          >
            {match.section_matched}
          </Paragraph>
        </div>
      )}

      <Collapse style={{ marginTop: 16 }}>
        <Panel header="💡 Neden bu eşleşme?" key="1">
          <Paragraph>{match.reasoning}</Paragraph>
          <Paragraph>
            <strong>Öneri:</strong> {match.suggestion_reasoning}
          </Paragraph>

          <Text strong>Skor Dağılımı:</Text>
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={8}>
              <Text type="secondary">
                Anlamsal: {match.match_breakdown.semantic_score.toFixed(2)}
              </Text>
            </Col>
            <Col span={8}>
              <Text type="secondary">
                Anahtar Kelime: {match.match_breakdown.keyword_score.toFixed(2)}
              </Text>
            </Col>
            <Col span={8}>
              <Text type="secondary">
                Metadata: {match.match_breakdown.metadata_score.toFixed(2)}
              </Text>
            </Col>
          </Row>
        </Panel>
      </Collapse>

      <Space style={{ marginTop: 16 }}>
        <Button
          icon={<EyeOutlined />}
          onClick={() => onView(match.document_id)}
        >
          Görüntüle
        </Button>
        <Button
          type="primary"
          icon={<CheckOutlined />}
          onClick={() => onUse(match)}
        >
          Bunu Kullan
        </Button>
        <Button
          danger
          icon={<CloseOutlined />}
          onClick={() => onReject(match)}
        >
          İlgili Değil
        </Button>
      </Space>
    </Card>
  );
}
