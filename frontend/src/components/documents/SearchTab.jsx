/**
 * SearchTab — Semantic + Drive search across documents
 */
import { useState, useCallback, useEffect } from 'react';
import {
  Input,
  Select,
  Card,
  Space,
  Tag,
  Typography,
  Empty,
  Spin,
  Progress,
  Button,
  Row,
  Col,
  Segmented,
  List,
  message,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  GoogleOutlined,
  LinkOutlined,
  ReloadOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useSearch, useReindexTrigger, useReindexStatus } from '../../api/search';
import { useProjects } from '../../api/projects';

const { Text, Paragraph } = Typography;

// Debounce helper
function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// Doc type colors
const DOC_TYPE_COLOR = { BA: 'blue', TA: 'green', TC: 'orange', BRD: 'purple' };

// Drive mime type icons
function driveMimeIcon(mimeType = '') {
  if (mimeType.includes('document')) return '📄';
  if (mimeType.includes('spreadsheet')) return '📊';
  if (mimeType.includes('presentation')) return '📽️';
  if (mimeType.includes('pdf')) return '📕';
  if (mimeType.includes('folder')) return '📁';
  return '📎';
}

export default function SearchTab() {
  const [query, setQuery] = useState('');
  const [source, setSource] = useState('Platform');
  const [docTypeFilter, setDocTypeFilter] = useState(null);
  const [projectFilter, setProjectFilter] = useState(null);
  const [reindexPolling, setReindexPolling] = useState(false);

  const debouncedQuery = useDebounce(query, 500);

  // API hooks
  const searchMutation = useSearch();
  const reindexMutation = useReindexTrigger();
  const { data: reindexStatus } = useReindexStatus(reindexPolling);
  const { data: projects } = useProjects();

  // Map Segmented label → API source value
  const sourceMap = { Platform: 'platform', Drive: 'drive', 'Tümü': 'both' };

  // Auto search on debounced query change
  useEffect(() => {
    if (debouncedQuery.trim().length >= 2) {
      searchMutation.mutate({
        query: debouncedQuery,
        source: sourceMap[source],
        doc_type_filter: docTypeFilter || undefined,
        project_filter: projectFilter || undefined,
        limit: 20,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery, source, docTypeFilter, projectFilter]);

  // Stop polling when reindex completes
  useEffect(() => {
    if (reindexStatus && reindexStatus.status !== 'running') {
      setReindexPolling(false);
      if (reindexStatus.status === 'completed') {
        message.success(`Reindex tamamlandı: ${reindexStatus.processed} doküman`);
      } else if (reindexStatus.status === 'failed') {
        message.error(`Reindex başarısız: ${reindexStatus.error_message}`);
      }
    }
  }, [reindexStatus]);

  const handleReindex = async () => {
    try {
      await reindexMutation.mutateAsync();
      setReindexPolling(true);
      message.info('Reindex başlatıldı...');
    } catch (err) {
      if (err?.response?.status === 409) {
        message.warning('Reindex zaten çalışıyor');
        setReindexPolling(true);
      } else {
        message.error('Reindex başlatılamadı');
      }
    }
  };

  const results = searchMutation.data;
  const platformResults = results?.platform_results || [];
  const driveResults = results?.drive_results || [];
  const showPlatform = source === 'Platform' || source === 'Tümü';
  const showDrive = source === 'Drive' || source === 'Tümü';

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      {/* Search bar + filters */}
      <Card>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={10}>
            <Input
              placeholder="Doküman veya içerik ara..."
              prefix={<SearchOutlined />}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              allowClear
              size="large"
            />
          </Col>
          <Col xs={24} md={6}>
            <Segmented
              options={['Platform', 'Drive', 'Tümü']}
              value={source}
              onChange={setSource}
              block
            />
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="Doküman Tipi"
              allowClear
              style={{ width: '100%' }}
              value={docTypeFilter}
              onChange={setDocTypeFilter}
              options={[
                { value: 'BA', label: 'BA' },
                { value: 'TA', label: 'TA' },
                { value: 'TC', label: 'TC' },
                { value: 'BRD', label: 'BRD' },
              ]}
            />
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="Proje"
              allowClear
              style={{ width: '100%' }}
              value={projectFilter}
              onChange={setProjectFilter}
              options={(projects || []).map((p) => ({
                value: p.id,
                label: p.name,
              }))}
            />
          </Col>
        </Row>
      </Card>

      {/* Loading */}
      {searchMutation.isPending && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 12 }}>Aranıyor...</Paragraph>
        </div>
      )}

      {/* Results */}
      {results && !searchMutation.isPending && (
        <>
          {/* Execution time */}
          <Text type="secondary">
            {results.total_found} sonuç ({results.execution_time_ms?.toFixed(0)}ms)
          </Text>

          {/* Platform Results */}
          {showPlatform && (
            <Card
              title={
                <span>
                  <DatabaseOutlined /> Platform Sonuçları ({platformResults.length})
                </span>
              }
              size="small"
            >
              {platformResults.length === 0 ? (
                <Empty
                  description={
                    <span>
                      Platform'da sonuç bulunamadı.{' '}
                      <Button type="link" size="small" onClick={handleReindex} loading={reindexMutation.isPending}>
                        Reindex başlat
                      </Button>
                    </span>
                  }
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              ) : (
                <List
                  dataSource={platformResults}
                  renderItem={(item) => (
                    <List.Item
                      key={item.document_id}
                      extra={
                        <Progress
                          type="circle"
                          percent={Math.round(item.score * 100)}
                          width={48}
                          strokeColor={item.score >= 0.7 ? '#52c41a' : item.score >= 0.4 ? '#faad14' : '#1890ff'}
                        />
                      }
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <a href={`/documents/${item.document_id}`}>
                              <FileTextOutlined /> {item.title}
                            </a>
                            <Tag color={DOC_TYPE_COLOR[item.doc_type?.toUpperCase()] || 'default'}>
                              {item.doc_type?.toUpperCase()}
                            </Tag>
                          </Space>
                        }
                        description={
                          item.snippet && (
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {item.snippet.length > 200 ? item.snippet.slice(0, 200) + '...' : item.snippet}
                            </Text>
                          )
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </Card>
          )}

          {/* Drive Results */}
          {showDrive && (
            <Card
              title={
                <span>
                  <GoogleOutlined /> Drive Sonuçları ({driveResults.length})
                </span>
              }
              size="small"
            >
              {driveResults.length === 0 ? (
                <Empty description="Drive'da sonuç bulunamadı" image={Empty.PRESENTED_IMAGE_SIMPLE} />
              ) : (
                <List
                  dataSource={driveResults}
                  renderItem={(item) => (
                    <List.Item
                      key={item.file_id}
                      extra={
                        <Button
                          type="link"
                          icon={<LinkOutlined />}
                          href={item.webViewLink}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Drive'da Aç
                        </Button>
                      }
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <span>{driveMimeIcon(item.mimeType)}</span>
                            <Text strong>{item.name}</Text>
                          </Space>
                        }
                        description={
                          <Space>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {item.mimeType?.split('.').pop()}
                            </Text>
                            {item.modifiedTime && (
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                {new Date(item.modifiedTime).toLocaleDateString('tr-TR')}
                              </Text>
                            )}
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </Card>
          )}
        </>
      )}

      {/* Reindex progress */}
      {reindexPolling && reindexStatus?.status === 'running' && (
        <Card size="small">
          <Space>
            <Spin size="small" />
            <Text>
              Reindex: {reindexStatus.processed}/{reindexStatus.total} doküman
            </Text>
            <Progress
              percent={reindexStatus.total > 0 ? Math.round((reindexStatus.processed / reindexStatus.total) * 100) : 0}
              size="small"
              style={{ width: 200 }}
            />
          </Space>
        </Card>
      )}

      {/* Empty initial state */}
      {!results && !searchMutation.isPending && !query && (
        <Card>
          <Empty
            description={
              <span>
                Arama yapmak için yukarıdaki alana bir sorgu girin.
                <br />
                <Text type="secondary">Platform dokümanları ve Google Drive dosyaları arasında arama yapabilirsiniz.</Text>
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      )}
    </Space>
  );
}
