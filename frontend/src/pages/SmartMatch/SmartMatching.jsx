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
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  CheckOutlined,
  CloseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useSearchMatches, useMatchAnalytics, useRecordMatch } from '../../api/matching';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Panel } = Collapse;

export default function SmartMatching() {
  const navigate = useNavigate();

  // State
  const [timeRange, setTimeRange] = useState('all');
  const [jiraKey, setJiraKey] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [taskDescription, setTaskDescription] = useState('');
  const [searchResults, setSearchResults] = useState(null);

  // API hooks
  const { data: analytics } = useMatchAnalytics(timeRange);
  const searchMutation = useSearchMatches();
  const recordMutation = useRecordMatch();

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
          <Col xs={24} md={18}>
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
          {searchResults.matches.length > 0 && searchResults.task_features && (
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

          {/* Match Results */}
          <Card
            title={
              <div>
                2️⃣ Eşleşme Sonuçları ({searchResults.total_found} bulundu, {searchResults.response_time.toFixed(2)}s)
              </div>
            }
          >
            {searchResults.matches.length === 0 ? (
              <Empty
                description={
                  <div>
                    <Paragraph>🔍 İlgili doküman bulunamadı. Yeni bir doküman oluşturmayı düşünün.</Paragraph>
                    <Paragraph type="secondary">
                      <strong>Öneri:</strong> Bu görev için yeni bir doküman oluşturmak üzere Doküman Kütüphanesi'ni kullanın.
                    </Paragraph>
                  </div>
                }
              />
            ) : (
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

                <Paragraph type="secondary" style={{ textAlign: 'center', marginTop: 16 }}>
                  💡 <strong>İpucu:</strong> Daha yüksek güven skorları (yeşil) daha güçlü eşleşmeleri gösterir.
                  Sonuçlardan herhangi bir dokümanı görüntüleyebilir veya kullanabilirsiniz.
                </Paragraph>
              </Space>
            )}
          </Card>
        </>
      )}
    </div>
  );
}

/**
 * Match Card Component
 */
function MatchCard({ match, rank, onView, onUse, onReject, getConfidenceStyle, getSuggestionBadge }) {
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
              backgroundColor: '#f5f5f5',
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
