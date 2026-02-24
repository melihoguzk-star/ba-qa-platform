/**
 * Settings Page — API keys, rotation, vector store, analytics
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Typography,
  Space,
  Divider,
  Button,
  Collapse,
  Tag,
  Descriptions,
  message,
  Form,
  Input,
  Radio,
  Checkbox,
  Row,
  Col,
  Statistic,
  Select,
  Empty,
  Progress,
  Spin,
} from 'antd';
import {
  KeyOutlined,
  SettingOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  ExperimentOutlined,
  ReloadOutlined,
  DeleteOutlined,
  PlusOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import {
  useGeminiKeys,
  useTestGeminiKey,
  useAnthropicKey,
  useRotationSettings,
  useUpdateRotationSettings,
  useResetAllKeys,
  useUsageStatistics,
  useVectorStoreConfig,
  useVectorStoreStats,
  useTestVectorSearch,
  useSmartMatchingAnalytics,
} from '../api/settings';
import {
  useReindexTrigger,
  useReindexStatus,
  useSearchStats,
} from '../api/search';

const { Title, Text, Paragraph } = Typography;

export default function Settings() {
  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <SettingOutlined /> Ayarlar
        </Title>
        <Paragraph type="secondary">
          API key yönetimi, rotation ayarları ve kullanım istatistikleri
        </Paragraph>
      </div>

      <Tabs defaultActiveKey="1">
        <Tabs.TabPane
          tab={
            <span>
              <KeyOutlined /> API Keys
            </span>
          }
          key="1"
        >
          <APIKeysTab />
        </Tabs.TabPane>
        <Tabs.TabPane
          tab={
            <span>
              <SettingOutlined /> Rotation
            </span>
          }
          key="2"
        >
          <RotationTab />
        </Tabs.TabPane>
        <Tabs.TabPane
          tab={
            <span>
              <BarChartOutlined /> İstatistikler
            </span>
          }
          key="3"
        >
          <StatisticsTab />
        </Tabs.TabPane>
        <Tabs.TabPane
          tab={
            <span>
              <DatabaseOutlined /> Vector Store
            </span>
          }
          key="4"
        >
          <VectorStoreTab />
        </Tabs.TabPane>
      </Tabs>
    </div>
  );
}

// ============================================================================
// Tab 1: API Keys Management
// ============================================================================

function APIKeysTab() {
  const { data: geminiKeys, isLoading: geminiLoading, refetch: refetchGemini } = useGeminiKeys();
  const { data: anthropicKey, isLoading: anthropicLoading, refetch: refetchAnthropic } = useAnthropicKey();
  const testGeminiMutation = useTestGeminiKey();

  const handleTestGemini = async (keyIndex) => {
    try {
      const result = await testGeminiMutation.mutateAsync(keyIndex);
      if (result.is_valid) {
        message.success(result.message);
      } else {
        message.error(result.message);
      }
    } catch (error) {
      message.error('Test başarısız');
    }
  };

  const handleRefresh = () => {
    refetchGemini();
    refetchAnthropic();
    message.success('API key yapılandırması yenilendi');
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* Info Card */}
      <Card>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Paragraph>
            <strong>ℹ️ API Key Yönetimi</strong>
          </Paragraph>
          <Paragraph type="secondary">
            API key'ler environment variable'lardan okunur. Key eklemek veya değiştirmek için{' '}
            <code>.env</code> dosyasını düzenleyin ve backend'i yeniden başlatın.
          </Paragraph>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
            Yapılandırmayı Yenile
          </Button>
        </Space>
      </Card>

      {/* Gemini Keys */}
      <Card title="🔑 Gemini API Keys" loading={geminiLoading}>
        <Paragraph type="secondary">
          💡 <strong>Key eklemek için:</strong> <code>.env</code> dosyasına{' '}
          <code>GEMINI_API_KEY</code> veya <code>GEMINI_API_KEYS</code> ekleyin ve backend'i
          yeniden başlatın.
        </Paragraph>

        {geminiKeys && geminiKeys.total > 0 ? (
          <>
            <Tag color="success" style={{ marginBottom: 16 }}>
              ✅ {geminiKeys.total} key yapılandırılmış
            </Tag>

            <Collapse>
              {geminiKeys.keys.map((key) => (
                <Collapse.Panel
                  header={
                    <Space>
                      <Text strong>Key {key.index}:</Text>
                      <Text code>{key.key_preview}</Text>
                      {key.status === 'active' && <Tag color="success">Active</Tag>}
                      {key.status === 'quota_exceeded' && <Tag color="warning">Quota Exceeded</Tag>}
                      {key.status === 'invalid' && <Tag color="error">Invalid</Tag>}
                    </Space>
                  }
                  key={key.index}
                >
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="Key Hash">{key.key_hash}</Descriptions.Item>
                    <Descriptions.Item label="Status">
                      {key.status.replace('_', ' ').toUpperCase()}
                    </Descriptions.Item>
                    <Descriptions.Item label="Requests">{key.requests}</Descriptions.Item>
                    <Descriptions.Item label="Errors">{key.errors}</Descriptions.Item>
                    {key.last_used && (
                      <Descriptions.Item label="Last Used">{key.last_used}</Descriptions.Item>
                    )}
                    {key.last_error && (
                      <Descriptions.Item label="Last Error">
                        <Text type="danger">{key.last_error}</Text>
                      </Descriptions.Item>
                    )}
                  </Descriptions>

                  <Button
                    type="primary"
                    icon={<ExperimentOutlined />}
                    loading={testGeminiMutation.isPending}
                    onClick={() => handleTestGemini(key.index)}
                    style={{ marginTop: 16 }}
                  >
                    Test Key
                  </Button>
                </Collapse.Panel>
              ))}
            </Collapse>
          </>
        ) : (
          <Card size="small" type="inner">
            <Empty
              description="Henüz Gemini key yapılandırılmamış"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
            <Divider />
            <Paragraph>
              <strong>Key eklemek için:</strong>
              <ol>
                <li>
                  Proje kökünde <code>.env</code> dosyasını açın
                </li>
                <li>
                  Tek key için:
                  <pre>GEMINI_API_KEY=your-key-here</pre>
                </li>
                <li>
                  Veya çoklu key için (comma-separated):
                  <pre>GEMINI_API_KEYS=key-1,key-2,key-3</pre>
                </li>
                <li>Backend'i yeniden başlatın (uvicorn restart)</li>
              </ol>
            </Paragraph>
          </Card>
        )}
      </Card>

      {/* Anthropic Key */}
      <Card title="Anthropic API Key (Claude)" loading={anthropicLoading}>
        <Paragraph type="secondary">
          💡 <strong>Key eklemek için:</strong> <code>.env</code> dosyasına{' '}
          <code>ANTHROPIC_API_KEY</code> ekleyin ve backend'i yeniden başlatın.
        </Paragraph>

        {anthropicKey?.configured ? (
          <>
            <Tag color="success" icon={<CheckCircleOutlined />} style={{ marginBottom: 16 }}>
              ✅ Key yapılandırılmış
            </Tag>

            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Key Preview">{anthropicKey.key_preview}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color="success">Configured</Tag>
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Paragraph>
              <strong>Key'i kaldırmak için:</strong>
              <ol>
                <li>
                  <code>.env</code> dosyasından <code>ANTHROPIC_API_KEY</code> satırını silin
                </li>
                <li>Backend'i yeniden başlatın</li>
              </ol>
            </Paragraph>
          </>
        ) : (
          <Card size="small" type="inner">
            <Empty
              description="Henüz Anthropic key yapılandırılmamış"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
            <Divider />
            <Paragraph>
              <strong>Key eklemek için:</strong>
              <ol>
                <li>
                  Proje kökünde <code>.env</code> dosyasını açın
                </li>
                <li>
                  Şu satırı ekleyin:
                  <pre>ANTHROPIC_API_KEY=sk-ant-your-key-here</pre>
                </li>
                <li>Backend'i yeniden başlatın (uvicorn restart)</li>
              </ol>
            </Paragraph>
          </Card>
        )}
      </Card>

      <Divider />

      <Paragraph type="secondary">
        💡 <strong>İpucu:</strong> Günlük kota limitini artırmak ve otomatik rotation'ı
        etkinleştirmek için <code>.env</code> dosyasına birden fazla Gemini key ekleyin.
      </Paragraph>
    </Space>
  );
}

// ============================================================================
// Tab 2: Rotation Settings
// ============================================================================

function RotationTab() {
  const { data: settings, isLoading } = useRotationSettings();
  const updateMutation = useUpdateRotationSettings();
  const resetMutation = useResetAllKeys();

  const [strategy, setStrategy] = useState('least_used');
  const [autoReset, setAutoReset] = useState(true);

  const handleUpdateSettings = async () => {
    try {
      await updateMutation.mutateAsync({
        strategy,
        auto_reset_enabled: autoReset,
      });
      message.success('Ayarlar güncellendi');
    } catch (error) {
      message.error('Ayarlar güncellenirken hata oluştu');
    }
  };

  const handleResetKeys = async () => {
    try {
      const result = await resetMutation.mutateAsync();
      message.success(result.message);
    } catch (error) {
      message.error('Reset başarısız');
    }
  };

  if (isLoading) {
    return <Spin />;
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card>
        {!settings?.rotation_enabled || settings.total_keys < 2 ? (
          <Tag color="warning" icon={<WarningOutlined />}>
            ⚠️ Rotation'ı etkinleştirmek için en az 2 Gemini key ekleyin
          </Tag>
        ) : (
          <Tag color="success" icon={<CheckCircleOutlined />}>
            ✅ Rotation {settings.total_keys} key ile etkin
          </Tag>
        )}
      </Card>

      <Card title="Rotation Stratejisi">
        <Radio.Group
          value={strategy}
          onChange={(e) => setStrategy(e.target.value)}
          style={{ width: '100%' }}
        >
          <Space direction="vertical">
            <Radio value="least_used">
              <strong>Least Used</strong> — En az kullanılan key'i seç (önerilen)
            </Radio>
            <Radio value="round_robin">
              <strong>Round Robin</strong> — Key'leri sırayla kullan
            </Radio>
            <Radio value="random">
              <strong>Random</strong> — Rastgele key seç
            </Radio>
          </Space>
        </Radio.Group>

        <Divider />

        <Paragraph type="secondary">
          ℹ️ Aktif strateji: <strong>{settings?.strategy?.replace('_', ' ').toUpperCase()}</strong>
        </Paragraph>
      </Card>

      <Card title="Otomatik Reset Ayarları">
        <Checkbox checked={autoReset} onChange={(e) => setAutoReset(e.target.checked)}>
          Günlük quota reset'i etkinleştir
        </Checkbox>

        {autoReset && (
          <Paragraph type="success" style={{ marginTop: 16 }}>
            ✅ Key'ler her gün 00:00 UTC'de otomatik reset edilecek
          </Paragraph>
        )}
      </Card>

      <Card title="Manuel İşlemler">
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleResetKeys}
            loading={resetMutation.isPending}
          >
            Tüm Key'leri Şimdi Reset Et
          </Button>

          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>
            İstatistikleri Yenile
          </Button>

          <Button
            type="primary"
            onClick={handleUpdateSettings}
            loading={updateMutation.isPending}
          >
            Ayarları Kaydet
          </Button>
        </Space>
      </Card>
    </Space>
  );
}

// ============================================================================
// Tab 3: Statistics
// ============================================================================

function StatisticsTab() {
  const [timeRange, setTimeRange] = useState('all');
  const { data: stats, isLoading: statsLoading } = useUsageStatistics();
  const { data: analytics, isLoading: analyticsLoading } = useSmartMatchingAnalytics(timeRange);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* Usage Statistics */}
      <Card title="📊 Kullanım İstatistikleri" loading={statsLoading}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="Toplam Key" value={stats?.total_keys || 0} />
          </Col>
          <Col span={6}>
            <Statistic
              title="Aktif Key"
              value={stats?.active_keys || 0}
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic title="Toplam İstek" value={stats?.total_requests || 0} />
          </Col>
          <Col span={6}>
            <Statistic
              title="Toplam Hata"
              value={stats?.total_errors || 0}
              valueStyle={{ color: stats?.total_errors > 0 ? '#cf1322' : undefined }}
            />
          </Col>
        </Row>

        <Divider />

        <Title level={5}>Key Bazlı İstatistikler</Title>

        {stats?.keys && stats.keys.length > 0 ? (
          <Collapse>
            {stats.keys.map((key, idx) => (
              <Collapse.Panel
                header={
                  <Space>
                    <Text strong>{key.key_preview}</Text>
                    {key.status === 'active' && <Tag color="success">Active</Tag>}
                    {key.status === 'quota_exceeded' && <Tag color="warning">Quota Exceeded</Tag>}
                    {key.status === 'invalid' && <Tag color="error">Invalid</Tag>}
                  </Space>
                }
                key={idx}
              >
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic title="Requests" value={key.requests} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Errors" value={key.errors} />
                  </Col>
                </Row>

                {key.last_used && (
                  <Paragraph type="secondary" style={{ marginTop: 16 }}>
                    Son kullanım: {key.last_used}
                  </Paragraph>
                )}

                {key.last_error && <Paragraph type="danger">Son hata: {key.last_error}</Paragraph>}
              </Collapse.Panel>
            ))}
          </Collapse>
        ) : (
          <Empty description="Henüz kullanım verisi yok" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>

      {/* Smart Matching Analytics */}
      <Card
        title="🔍 Smart Matching Analytics"
        loading={analyticsLoading}
        extra={
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 150 }}
            options={[
              { label: 'Son 7 Gün', value: '7days' },
              { label: 'Son 30 Gün', value: '30days' },
              { label: 'Son 90 Gün', value: '90days' },
              { label: 'Tümü', value: 'all' },
            ]}
          />
        }
      >
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="Toplam Eşleşme" value={analytics?.total_matches || 0} />
          </Col>
          <Col span={6}>
            <Statistic
              title="Kabul Edilen"
              value={analytics?.total_accepted || 0}
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Kabul Oranı"
              value={analytics?.acceptance_rate || 0}
              suffix="%"
              precision={1}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Ort. Güven"
              value={analytics?.avg_confidence || 0}
              precision={2}
            />
          </Col>
        </Row>

        {analytics?.suggestion_breakdown && analytics.suggestion_breakdown.length > 0 && (
          <>
            <Divider />
            <Title level={5}>Öneri Dağılımı</Title>
            <Row gutter={[16, 16]}>
              {analytics.suggestion_breakdown.map((item, idx) => (
                <Col span={12} key={idx}>
                  <Card size="small">
                    <Text strong>{item.suggestion || 'N/A'}</Text>
                    <br />
                    <Text type="secondary">
                      {item.count} eşleşme ({item.accepted} kabul —{' '}
                      {item.count > 0 ? ((item.accepted / item.count) * 100).toFixed(0) : 0}%)
                    </Text>
                  </Card>
                </Col>
              ))}
            </Row>
          </>
        )}

        {analytics?.doc_type_breakdown && analytics.doc_type_breakdown.length > 0 && (
          <>
            <Divider />
            <Title level={5}>Doküman Tipi Dağılımı</Title>
            <Row gutter={[16, 16]}>
              {analytics.doc_type_breakdown.map((item, idx) => (
                <Col span={8} key={idx}>
                  <Card size="small">
                    <Text strong>{item.doc_type.toUpperCase()}</Text>
                    <br />
                    <Text type="secondary">
                      {item.count} eşleşme (ort: {item.avg_confidence.toFixed(2)})
                    </Text>
                  </Card>
                </Col>
              ))}
            </Row>
          </>
        )}

        {(!analytics?.total_matches || analytics.total_matches === 0) && (
          <Empty
            description="Henüz smart matching verisi yok"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>
    </Space>
  );
}

// ============================================================================
// Tab 4: Vector Store
// ============================================================================

function VectorStoreTab() {
  const { data: config, isLoading: configLoading } = useVectorStoreConfig();
  const { data: stats, isLoading: statsLoading } = useVectorStoreStats();
  const searchMutation = useTestVectorSearch();
  const reindexMutation = useReindexTrigger();
  const { data: searchStats } = useSearchStats();
  const [reindexPolling, setReindexPolling] = useState(false);
  const { data: reindexStatus } = useReindexStatus(reindexPolling);

  const [searchForm] = Form.useForm();
  const [searchResults, setSearchResults] = useState(null);
  const [driveFolderId, setDriveFolderId] = useState('');

  // Handle reindex
  const handleReindex = async () => {
    try {
      await reindexMutation.mutateAsync();
      setReindexPolling(true);
      message.info('Platform reindex başlatıldı...');
    } catch (err) {
      if (err?.response?.status === 409) {
        message.warning('Reindex zaten çalışıyor');
        setReindexPolling(true);
      } else {
        message.error('Reindex başlatılamadı');
      }
    }
  };

  // Stop polling when reindex completes
  useEffect(() => {
    if (reindexStatus && reindexStatus.status !== 'running' && reindexPolling) {
      setReindexPolling(false);
      if (reindexStatus.status === 'completed') {
        message.success(`Reindex tamamlandı: ${reindexStatus.processed} doküman`);
      } else if (reindexStatus.status === 'failed') {
        message.error(`Reindex başarısız: ${reindexStatus.error_message}`);
      }
    }
  }, [reindexStatus, reindexPolling]);

  const handleSearch = async (values) => {
    try {
      const result = await searchMutation.mutateAsync(values);
      setSearchResults(result);
      if (result.total > 0) {
        message.success(`✅ ${result.total} sonuç bulundu`);
      } else {
        message.warning('Sonuç bulunamadı');
      }
    } catch (error) {
      message.error('Arama başarısız: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* Configuration */}
      <Card title="⚙️ Konfigürasyon" loading={configLoading}>
        <Row gutter={16}>
          <Col span={12}>
            {config?.semantic_search_enabled ? (
              <Tag color="success" icon={<CheckCircleOutlined />}>
                ✅ Semantic Search: Enabled
              </Tag>
            ) : (
              <Tag color="warning" icon={<WarningOutlined />}>
                ⚠️ Semantic Search: Disabled
              </Tag>
            )}
          </Col>
          <Col span={12}>
            {config?.auto_indexing_enabled ? (
              <Tag color="success" icon={<CheckCircleOutlined />}>
                ✅ Auto-Indexing: Enabled
              </Tag>
            ) : (
              <Tag color="warning" icon={<WarningOutlined />}>
                ⚠️ Auto-Indexing: Disabled
              </Tag>
            )}
          </Col>
        </Row>
      </Card>

      {/* Collection Statistics */}
      <Card title="📊 Collection İstatistikleri" loading={statsLoading}>
        <Row gutter={16}>
          <Col span={8}>
            <Card size="small">
              <Statistic
                title="BA Documents"
                value={stats?.ba?.chunk_count || 0}
                suffix="chunks"
              />
              <Text type="secondary">
                {stats?.ba?.status === 'active' ? '✅' : '❌'}{' '}
                {stats?.ba?.status?.toUpperCase() || 'UNKNOWN'}
              </Text>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <Statistic
                title="TA Documents"
                value={stats?.ta?.chunk_count || 0}
                suffix="chunks"
              />
              <Text type="secondary">
                {stats?.ta?.status === 'active' ? '✅' : '❌'}{' '}
                {stats?.ta?.status?.toUpperCase() || 'UNKNOWN'}
              </Text>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <Statistic
                title="TC Documents"
                value={stats?.tc?.chunk_count || 0}
                suffix="chunks"
              />
              <Text type="secondary">
                {stats?.tc?.status === 'active' ? '✅' : '❌'}{' '}
                {stats?.tc?.status?.toUpperCase() || 'UNKNOWN'}
              </Text>
            </Card>
          </Col>
        </Row>

        <Divider />

        <Paragraph>
          📦 <strong>Toplam indexed chunks:</strong> {stats?.total_chunks || 0}
        </Paragraph>
      </Card>

      {/* Embedding Model */}
      <Card title="🤖 Embedding Model">
        <Text code>{config?.embedding_model}</Text>
        <br />
        <Text type="secondary">Multilingual support: Turkish + English</Text>
      </Card>

      {/* Reindex & Drive Config */}
      <Card title="🔄 Platform Reindex">
        <Row gutter={16} align="middle">
          <Col span={12}>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleReindex}
              loading={reindexMutation.isPending}
              disabled={reindexPolling}
            >
              Tüm Dokümanları Reindex Et
            </Button>
          </Col>
          <Col span={12}>
            {reindexPolling && reindexStatus?.status === 'running' && (
              <Space>
                <Spin size="small" />
                <Text>
                  {reindexStatus.processed}/{reindexStatus.total} doküman
                </Text>
                <Progress
                  percent={reindexStatus.total > 0 ? Math.round((reindexStatus.processed / reindexStatus.total) * 100) : 0}
                  size="small"
                  style={{ width: 180 }}
                />
              </Space>
            )}
            {!reindexPolling && reindexStatus?.status === 'completed' && (
              <Tag color="success">Son reindex: {reindexStatus.processed} doküman tamamlandı</Tag>
            )}
          </Col>
        </Row>

        <Divider />

        <Row gutter={16}>
          <Col span={8}>
            <Statistic title="BA Chunks" value={searchStats?.ba?.chunk_count || 0} />
          </Col>
          <Col span={8}>
            <Statistic title="TA Chunks" value={searchStats?.ta?.chunk_count || 0} />
          </Col>
          <Col span={8}>
            <Statistic title="TC Chunks" value={searchStats?.tc?.chunk_count || 0} />
          </Col>
        </Row>
        <Paragraph type="secondary" style={{ marginTop: 12 }}>
          Toplam indexed chunks: <strong>{searchStats?.total_chunks || 0}</strong>
        </Paragraph>
      </Card>

      {/* Drive Configuration */}
      <Card title="☁️ Google Drive Yapılandırması">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong>Drive Folder ID (opsiyonel)</Text>
          <Input
            placeholder="Shared Drive veya Folder ID girin"
            value={driveFolderId}
            onChange={(e) => setDriveFolderId(e.target.value)}
            style={{ maxWidth: 400 }}
          />
          <Paragraph type="secondary">
            Drive araması n8n webhook proxy üzerinden çalışır. Folder ID belirtilmezse tüm erişilebilir dosyalarda aranır.
          </Paragraph>
        </Space>
      </Card>

      {/* Test Semantic Search */}
      <Card title="🧪 Test Semantic Search">
        <Form form={searchForm} onFinish={handleSearch} layout="vertical">
          <Form.Item
            name="query"
            label="Test Query"
            rules={[{ required: true, message: 'Query gerekli' }]}
          >
            <Input placeholder="kullanıcı giriş ekranı" prefix={<SearchOutlined />} />
          </Form.Item>

          <Form.Item
            name="doc_type"
            label="Document Type"
            initialValue="ba"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="ba">Business Analysis</Select.Option>
              <Select.Option value="ta">Technical Analysis</Select.Option>
              <Select.Option value="tc">Test Cases</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="top_k" label="Top K Results" initialValue={5}>
            <Select>
              <Select.Option value={5}>5</Select.Option>
              <Select.Option value={10}>10</Select.Option>
              <Select.Option value={20}>20</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SearchOutlined />}
              loading={searchMutation.isPending}
            >
              Ara
            </Button>
          </Form.Item>
        </Form>

        {searchResults && (
          <>
            <Divider />
            <Title level={5}>Sonuçlar ({searchResults.total})</Title>

            {searchResults.results.length > 0 ? (
              <Collapse>
                {searchResults.results.map((result, idx) => (
                  <Collapse.Panel
                    header={
                      <Space>
                        <Text strong>#{idx + 1}</Text>
                        <Text>Document {result.document_id}</Text>
                        <Progress
                          type="circle"
                          percent={(result.similarity * 100).toFixed(0)}
                          width={40}
                          strokeColor={result.similarity >= 0.7 ? '#52c41a' : '#1890ff'}
                        />
                      </Space>
                    }
                    key={idx}
                  >
                    <Paragraph>
                      <strong>Matched Chunk:</strong>
                    </Paragraph>
                    <Text code style={{ whiteSpace: 'pre-wrap' }}>
                      {result.chunk_text.length > 300
                        ? result.chunk_text.slice(0, 300) + '...'
                        : result.chunk_text}
                    </Text>

                    <Divider />

                    <Descriptions size="small">
                      <Descriptions.Item label="Chunk Type">
                        {result.metadata?.chunk_type || 'unknown'}
                      </Descriptions.Item>
                      <Descriptions.Item label="Similarity">
                        {(result.similarity * 100).toFixed(1)}%
                      </Descriptions.Item>
                    </Descriptions>
                  </Collapse.Panel>
                ))}
              </Collapse>
            ) : (
              <Empty description="Sonuç bulunamadı" />
            )}
          </>
        )}
      </Card>

      {/* Storage Location */}
      <Card title="💾 Storage">
        <Text code>{config?.persist_directory}</Text>
        <br />
        <Text type="secondary">ChromaDB persistent storage location</Text>
      </Card>
    </Space>
  );
}
