/**
 * Reports & Analytics Page
 *
 * Platform statistics and analysis history
 */
import { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  Space,
  Typography,
  Collapse,
  Tag,
  Progress,
  Button,
  Empty,
  Divider,
} from 'antd';
import {
  LineChartOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  FormatPainterOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useReportStats, useRecentAnalyses, exportAnalysesCSV } from '../api/reports';

const { Title, Text, Paragraph } = Typography;

export default function Reports() {
  const [timeRange, setTimeRange] = useState('all');
  const [analysisTypeFilter, setAnalysisTypeFilter] = useState(null);
  const [limit, setLimit] = useState(25);

  // Fetch data
  const { data: stats, isLoading: statsLoading } = useReportStats(timeRange);
  const { data: analysesData, isLoading: analysesLoading } = useRecentAnalyses({
    limit,
    analysis_type: analysisTypeFilter,
    time_range: timeRange,
  });

  const analyses = analysesData?.analyses || [];

  // Get stats by type
  const baStats = stats?.by_type?.find((s) => s.analysis_type === 'ba') || {};
  const tcStats = stats?.by_type?.find((s) => s.analysis_type === 'tc') || {};
  const designStats = stats?.by_type?.find((s) => s.analysis_type === 'design') || {};

  // Helper to get emoji for score
  const getScoreEmoji = (score) => {
    if (score >= 8) return '🟢';
    if (score >= 6) return '🟡';
    if (score >= 4) return '🟠';
    return '🔴';
  };

  // Helper to get progress color
  const getProgressColor = (score) => {
    if (score >= 8) return '#52c41a';
    if (score >= 6) return '#1890ff';
    if (score >= 4) return '#faad14';
    return '#f5222d';
  };

  // Helper to get type badge
  const getTypeBadge = (type) => {
    const badges = {
      ba: <Tag icon={<FileTextOutlined />} color="blue">BA</Tag>,
      tc: <Tag icon={<ExperimentOutlined />} color="purple">TC</Tag>,
      design: <Tag icon={<FormatPainterOutlined />} color="magenta">Design</Tag>,
      full: <Tag icon={<LineChartOutlined />} color="cyan">Full</Tag>,
    };
    return badges[type] || <Tag>{type}</Tag>;
  };

  // Handle export
  const handleExport = () => {
    exportAnalysesCSV({
      limit: 100,
      analysis_type: analysisTypeFilter,
      time_range: timeRange,
    });
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <LineChartOutlined /> Raporlar & Analiz Geçmişi
        </Title>
        <Paragraph type="secondary">
          Platform üzerinde yapılan tüm analizlerin detaylı özeti ve istatistikleri
        </Paragraph>
      </div>

      {/* Time Range Filter */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Space>
          <Text strong>Zaman Aralığı:</Text>
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
        </Space>
      </Card>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={statsLoading}>
            <Statistic
              title="Toplam Analiz"
              value={stats?.total || 0}
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              Tüm tipler
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={statsLoading}>
            <Statistic
              title="BA Analiz"
              value={baStats.c || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <Space direction="vertical" size={0}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                Ort: {baStats.avg_puan?.toFixed(0) || 0}/100 | Geçen: {baStats.gecen || 0}
              </Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={statsLoading}>
            <Statistic
              title="TC Analiz"
              value={tcStats.c || 0}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Space direction="vertical" size={0}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                Ort: {tcStats.avg_puan?.toFixed(0) || 0}/100 | Geçen: {tcStats.gecen || 0}
              </Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={statsLoading}>
            <Statistic
              title="Design Analiz"
              value={designStats.c || 0}
              prefix={<FormatPainterOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              Uyumluluk kontrolleri
            </Text>
          </Card>
        </Col>
      </Row>

      {/* Filters & Actions */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space>
              <Text strong>Filtreler:</Text>
              <Select
                placeholder="Tip Filtre"
                allowClear
                value={analysisTypeFilter}
                onChange={setAnalysisTypeFilter}
                style={{ width: 150 }}
                options={[
                  { label: 'BA', value: 'ba' },
                  { label: 'TC', value: 'tc' },
                  { label: 'Design', value: 'design' },
                  { label: 'Full', value: 'full' },
                ]}
              />
              <Select
                value={limit}
                onChange={setLimit}
                style={{ width: 100 }}
                options={[
                  { label: '10', value: 10 },
                  { label: '25', value: 25 },
                  { label: '50', value: 50 },
                  { label: '100', value: 100 },
                ]}
              />
            </Space>
          </Col>
          <Col>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              CSV İndir
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Analysis History */}
      <Title level={4}>
        <ClockCircleOutlined /> Analiz Geçmişi
      </Title>

      {analysesLoading ? (
        <Card loading />
      ) : analyses.length === 0 ? (
        <Empty description="Henüz analiz kaydı yok" />
      ) : (
        <Collapse
          items={analyses.map((analysis) => {
            const isPassed = analysis.gecti_mi;
            const score = analysis.genel_puan || 0;
            const result = JSON.parse(analysis.result_json || '{}');

            // Build label
            let label;
            if (analysis.analysis_type === 'design') {
              label = (
                <Space>
                  {getTypeBadge(analysis.analysis_type)}
                  <Text strong>{analysis.jira_key || '—'}</Text>
                  <Text type="secondary">{analysis.created_at?.slice(0, 16)}</Text>
                </Space>
              );
            } else {
              label = (
                <Space>
                  {getTypeBadge(analysis.analysis_type)}
                  <Text strong>{analysis.jira_key || '—'}</Text>
                  {isPassed ? (
                    <Tag icon={<CheckCircleOutlined />} color="success">
                      Geçti
                    </Tag>
                  ) : (
                    <Tag icon={<CloseCircleOutlined />} color="error">
                      Kaldı
                    </Tag>
                  )}
                  <Text strong>{score.toFixed(0)}/100</Text>
                  <Text type="secondary">{analysis.created_at?.slice(0, 16)}</Text>
                </Space>
              );
            }

            return {
              key: analysis.id,
              label,
              children: (
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  {/* Meta Info */}
                  <Row gutter={16}>
                    <Col span={8}>
                      <Text type="secondary">Tarih:</Text>
                      <div>{analysis.created_at?.slice(0, 16)}</div>
                    </Col>
                    <Col span={8}>
                      <Text type="secondary">Tetikleyen:</Text>
                      <div>{analysis.triggered_by || 'manual'}</div>
                    </Col>
                    <Col span={8}>
                      <Text type="secondary">Tip:</Text>
                      <div>{analysis.analysis_type.toUpperCase()}</div>
                    </Col>
                  </Row>

                  {/* Scores */}
                  {result.skorlar && (
                    <>
                      <Divider />
                      <Text strong>Skor Detayları:</Text>
                      <Row gutter={[16, 16]}>
                        {result.skorlar.map((skor, idx) => {
                          const score = skor.puan || 0;
                          return (
                            <Col xs={24} sm={12} lg={8} key={idx}>
                              <Card size="small">
                                <Space direction="vertical" style={{ width: '100%' }}>
                                  <div
                                    style={{
                                      display: 'flex',
                                      justifyContent: 'space-between',
                                      alignItems: 'center',
                                    }}
                                  >
                                    <Text>{skor.kriter.replace(/_/g, ' ')}</Text>
                                    <Text strong>
                                      {getScoreEmoji(score)} {score}/10
                                    </Text>
                                  </div>
                                  <Progress
                                    percent={(score / 10) * 100}
                                    strokeColor={getProgressColor(score)}
                                    showInfo={false}
                                  />
                                </Space>
                              </Card>
                            </Col>
                          );
                        })}
                      </Row>
                    </>
                  )}

                  {/* Detailed Report */}
                  {analysis.report_text && (
                    <>
                      <Divider />
                      <Text strong>Detaylı Rapor:</Text>
                      <Card size="small" style={{ backgroundColor: '#fafafa' }}>
                        <div
                          className="markdown-content"
                          style={{ maxHeight: 400, overflowY: 'auto' }}
                        >
                          {analysis.analysis_type === 'design' ? (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {analysis.report_text}
                            </ReactMarkdown>
                          ) : (
                            <pre
                              style={{
                                whiteSpace: 'pre-wrap',
                                fontFamily: 'monospace',
                                fontSize: 13,
                                lineHeight: 1.8,
                              }}
                            >
                              {analysis.report_text}
                            </pre>
                          )}
                        </div>
                      </Card>
                    </>
                  )}
                </Space>
              ),
            };
          })}
        />
      )}
    </div>
  );
}
