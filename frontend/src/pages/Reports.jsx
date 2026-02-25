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
  Tabs,
  message,
  Spin,
  theme,
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
  RocketOutlined,
  SyncOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useReportStats, useRecentAnalyses, usePipelineRuns, exportAnalysesCSV } from '../api/reports';
import { downloadDocument } from '../api/pipeline';

const { Title, Text, Paragraph } = Typography;

export default function Reports() {
  const [timeRange, setTimeRange] = useState('all');
  const [analysisTypeFilter, setAnalysisTypeFilter] = useState(null);
  const [limit, setLimit] = useState(25);
  const [downloadingKey, setDownloadingKey] = useState(null);

  // Fetch data
  const { data: pipelineRuns, isLoading: pipelineRunsLoading } = usePipelineRuns(20);
  const { data: stats, isLoading: statsLoading } = useReportStats(timeRange);
  const { data: analysesData, isLoading: analysesLoading } = useRecentAnalyses({
    limit,
    analysis_type: analysisTypeFilter,
    time_range: timeRange,
  });

  const analyses = analysesData?.analyses || [];
  const { token } = theme.useToken();

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

  // Handle document download with feedback
  const handleDownload = async (runId, docType) => {
    const key = `${runId}-${docType}`;
    setDownloadingKey(key);
    try {
      await downloadDocument(runId, docType);
      message.success(`${docType.toUpperCase()} dosyas\u0131 indiriliyor`);
    } catch (error) {
      const detail = error?.response?.data?.detail || error?.message || 'Bilinmeyen hata';
      message.error(`${docType.toUpperCase()} indirilemedi: ${detail}`);
    } finally {
      setDownloadingKey(null);
    }
  };

  // Handle export
  const handleExport = () => {
    exportAnalysesCSV({
      limit: 100,
      analysis_type: analysisTypeFilter,
      time_range: timeRange,
    });
  };

  // --- BRD Pipeline tab content ---
  const pipelineTabContent = pipelineRunsLoading ? (
    <div style={{ textAlign: 'center', padding: 40 }}><Spin /></div>
  ) : !pipelineRuns || pipelineRuns.length === 0 ? (
    <Empty description={'Hen\u00FCz pipeline \u00E7al\u0131\u015Ft\u0131r\u0131lmam\u0131\u015F'} />
  ) : (
    <Collapse
      accordion
      items={pipelineRuns.map((run) => {
        const statusTag = {
          completed: <Tag icon={<CheckCircleOutlined />} color="success">{'Tamamland\u0131'}</Tag>,
          failed: <Tag icon={<CloseCircleOutlined />} color="error">{'Ba\u015Far\u0131s\u0131z'}</Tag>,
          started: <Tag icon={<SyncOutlined spin />} color="processing">Devam Ediyor</Tag>,
        };

        return {
          key: run.id,
          label: (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', flexWrap: 'wrap', gap: 8 }}>
              <Space>
                <Text strong>{run.project_name || 'Proje'}</Text>
                {statusTag[run.status] || <Tag>{run.status}</Tag>}
              </Space>
              <Space>
                {run.available_docs?.includes('ba') && (
                  <Button
                    size="small"
                    type="link"
                    icon={downloadingKey === `${run.id}-ba` ? <LoadingOutlined /> : <DownloadOutlined />}
                    disabled={downloadingKey === `${run.id}-ba`}
                    onClick={(e) => { e.stopPropagation(); handleDownload(run.id, 'ba'); }}
                  >
                    BA
                  </Button>
                )}
                {run.available_docs?.includes('ta') && (
                  <Button
                    size="small"
                    type="link"
                    icon={downloadingKey === `${run.id}-ta` ? <LoadingOutlined /> : <DownloadOutlined />}
                    disabled={downloadingKey === `${run.id}-ta`}
                    onClick={(e) => { e.stopPropagation(); handleDownload(run.id, 'ta'); }}
                  >
                    TA
                  </Button>
                )}
                {run.available_docs?.includes('tc') && (
                  <Button
                    size="small"
                    type="link"
                    icon={downloadingKey === `${run.id}-tc` ? <LoadingOutlined /> : <DownloadOutlined />}
                    disabled={downloadingKey === `${run.id}-tc`}
                    onClick={(e) => { e.stopPropagation(); handleDownload(run.id, 'tc'); }}
                  >
                    TC
                  </Button>
                )}
                <Text type="secondary" style={{ fontSize: 12 }}>{run.created_at?.slice(0, 16)}</Text>
              </Space>
            </div>
          ),
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              {/* Scores */}
              <Row gutter={[16, 16]}>
                {run.ba_score != null && (
                  <Col xs={24} sm={8}>
                    <Text type="secondary">BA Skoru</Text>
                    <Progress
                      percent={Math.round(run.ba_score * 10)}
                      strokeColor={getProgressColor(run.ba_score)}
                      format={() => `${run.ba_score}/10`}
                    />
                  </Col>
                )}
                {run.ta_score != null && (
                  <Col xs={24} sm={8}>
                    <Text type="secondary">TA Skoru</Text>
                    <Progress
                      percent={Math.round(run.ta_score * 10)}
                      strokeColor={getProgressColor(run.ta_score)}
                      format={() => `${run.ta_score}/10`}
                    />
                  </Col>
                )}
                {run.tc_score != null && (
                  <Col xs={24} sm={8}>
                    <Text type="secondary">TC Skoru</Text>
                    <Progress
                      percent={Math.round(run.tc_score * 10)}
                      strokeColor={getProgressColor(run.tc_score)}
                      format={() => `${run.tc_score}/10`}
                    />
                  </Col>
                )}
                {run.ba_score == null && run.ta_score == null && run.tc_score == null && (
                  <Col span={24}>
                    <Text type="secondary">{'Hen\u00FCz skor bilgisi yok'}</Text>
                  </Col>
                )}
              </Row>

              {/* Download buttons */}
              {run.available_docs?.length > 0 && (
                <>
                  <Divider style={{ margin: '8px 0' }} />
                  <Space>
                    <Text type="secondary">{'D\u00F6k\u00FCmanlar:'}</Text>
                    {run.available_docs.includes('ba') && (
                      <Button
                        size="small"
                        icon={downloadingKey === `${run.id}-ba` ? <LoadingOutlined /> : <DownloadOutlined />}
                        loading={downloadingKey === `${run.id}-ba`}
                        onClick={() => handleDownload(run.id, 'ba')}
                      >
                        BA (DOCX)
                      </Button>
                    )}
                    {run.available_docs.includes('ta') && (
                      <Button
                        size="small"
                        icon={downloadingKey === `${run.id}-ta` ? <LoadingOutlined /> : <DownloadOutlined />}
                        loading={downloadingKey === `${run.id}-ta`}
                        onClick={() => handleDownload(run.id, 'ta')}
                      >
                        TA (DOCX)
                      </Button>
                    )}
                    {run.available_docs.includes('tc') && (
                      <Button
                        size="small"
                        icon={downloadingKey === `${run.id}-tc` ? <LoadingOutlined /> : <DownloadOutlined />}
                        loading={downloadingKey === `${run.id}-tc`}
                        onClick={() => handleDownload(run.id, 'tc')}
                      >
                        TC (XLSX)
                      </Button>
                    )}
                  </Space>
                </>
              )}
            </Space>
          ),
        };
      })}
    />
  );

  // --- Analiz tab content ---
  const analysisTabContent = (
    <>
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
              {'CSV \u0130ndir'}
            </Button>
          </Col>
        </Row>
      </Card>

      {analysesLoading ? (
        <div style={{ textAlign: 'center', padding: 40 }}><Spin /></div>
      ) : analyses.length === 0 ? (
        <Empty description={'Hen\u00FCz analiz kayd\u0131 yok'} />
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
                  <Text strong>{analysis.jira_key || '\u2014'}</Text>
                  <Text type="secondary">{analysis.created_at?.slice(0, 16)}</Text>
                </Space>
              );
            } else {
              label = (
                <Space>
                  {getTypeBadge(analysis.analysis_type)}
                  <Text strong>{analysis.jira_key || '\u2014'}</Text>
                  {isPassed ? (
                    <Tag icon={<CheckCircleOutlined />} color="success">
                      {'Ge\u00E7ti'}
                    </Tag>
                  ) : (
                    <Tag icon={<CloseCircleOutlined />} color="error">
                      {'Kald\u0131'}
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
                      <Text strong>{'Skor Detaylar\u0131:'}</Text>
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
                      <Text strong>{'Detayl\u0131 Rapor:'}</Text>
                      <Card size="small" style={{ backgroundColor: token.colorBgLayout }}>
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
    </>
  );

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <LineChartOutlined /> {'Raporlar & Analiz Ge\u00E7mi\u015Fi'}
        </Title>
        <Paragraph type="secondary">
          {'Platform \u00FCzerinde yap\u0131lan t\u00FCm analizlerin detayl\u0131 \u00F6zeti ve istatistikleri'}
        </Paragraph>
      </div>

      {/* Time Range Filter */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Space>
          <Text strong>{'Zaman Aral\u0131\u011F\u0131:'}</Text>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 150 }}
            options={[
              { label: 'Son 7 G\u00FCn', value: '7days' },
              { label: 'Son 30 G\u00FCn', value: '30days' },
              { label: 'Son 90 G\u00FCn', value: '90days' },
              { label: 'T\u00FCm\u00FC', value: 'all' },
            ]}
          />
        </Space>
      </Card>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={statsLoading}>
            <Statistic
              title="Toplam Analiz"
              value={stats?.total || 0}
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {'T\u00FCm tipler'}
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
                {`Ort: ${baStats.avg_puan?.toFixed(0) || 0}/100 | Ge\u00E7en: ${baStats.gecen || 0}`}
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
                {`Ort: ${tcStats.avg_puan?.toFixed(0) || 0}/100 | Ge\u00E7en: ${tcStats.gecen || 0}`}
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

      {/* Tabs: BRD Pipeline + Analiz */}
      <Tabs
        defaultActiveKey="pipeline"
        size="large"
        items={[
          {
            key: 'pipeline',
            label: (
              <span>
                <RocketOutlined /> {'BRD Pipeline Ge\u00E7mi\u015Fi'}
              </span>
            ),
            children: pipelineTabContent,
          },
          {
            key: 'analyses',
            label: (
              <span>
                <ClockCircleOutlined /> {'Analiz Ge\u00E7mi\u015Fi'}
              </span>
            ),
            children: analysisTabContent,
          },
        ]}
      />
    </div>
  );
}
