/**
 * Dashboard — Home page with live stats
 */
import { Card, Row, Col, Statistic, Spin, Alert, Timeline, Button, Space, theme } from 'antd';
import {
  FileTextOutlined,
  ProjectOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  PlusOutlined,
  UploadOutlined,
  ThunderboltOutlined,
  FileSearchOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { useProjects } from '../api/projects';
import { useDocuments } from '../api/documents';
import { usePipelineRuns } from '../api/pipeline';
import { useReportStats } from '../api/reports';
import { ROUTES } from '../utils/constants';

export default function Dashboard() {
  const navigate = useNavigate();
  const { token } = theme.useToken();
  const { data: projects, isLoading: projectsLoading, error: projectsError } = useProjects();
  const { data: documents, isLoading: documentsLoading } = useDocuments();
  const { data: pipelineRuns, isLoading: pipelineLoading } = usePipelineRuns();
  const { data: reportStats, isLoading: statsLoading } = useReportStats('all');

  const totalProjects = projects?.length || 0;
  const totalDocuments = documents?.length || 0;
  const totalPipelineRuns = pipelineRuns?.length || 0;

  // Calculate average score from BA and TC evaluations (exclude 0-scored entries)
  const avgScore = (() => {
    if (!reportStats?.by_type) return 0;
    const scoredTypes = reportStats.by_type.filter(
      (t) => (t.analysis_type === 'ba' || t.analysis_type === 'tc') && t.avg_puan > 0
    );
    if (scoredTypes.length === 0) return 0;
    const totalWeighted = scoredTypes.reduce((sum, t) => sum + (t.avg_puan * t.c), 0);
    const totalCount = scoredTypes.reduce((sum, t) => sum + t.c, 0);
    return totalCount > 0 ? Math.round(totalWeighted / totalCount) : 0;
  })();

  // Group documents by type
  const docsByType = documents?.reduce((acc, doc) => {
    acc[doc.doc_type] = (acc[doc.doc_type] || 0) + 1;
    return acc;
  }, {}) || {};

  // Donut chart config
  const DOC_TYPE_CONFIG = {
    ba: { label: 'BA', color: '#52c41a' },
    tc: { label: 'TC', color: '#722ed1' },
    ta: { label: 'TA', color: '#fa8c16' },
    brd: { label: 'BRD', color: '#1890ff' },
  };

  const chartData = Object.entries(docsByType).map(([type, count]) => ({
    name: (DOC_TYPE_CONFIG[type]?.label || type.toUpperCase()),
    value: count,
    color: DOC_TYPE_CONFIG[type]?.color || '#8c8c8c',
    pct: totalDocuments > 0 ? ((count / totalDocuments) * 100).toFixed(1) : '0',
  }));

  // Recent activities (combine projects, documents, pipeline runs)
  const recentActivities = [
    ...(projects?.slice(0, 3).map(p => ({
      type: 'project',
      title: `Proje oluşturuldu: ${p.name}`,
      time: p.created_at,
      color: 'green'
    })) || []),
    ...(documents?.slice(0, 3).map(d => ({
      type: 'document',
      title: `Doküman eklendi: ${d.title}`,
      time: d.created_at,
      color: 'blue'
    })) || []),
    ...(pipelineRuns?.slice(0, 3).map(r => ({
      type: 'pipeline',
      title: `Pipeline çalıştırıldı`,
      time: r.created_at,
      color: 'purple'
    })) || [])
  ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 5);

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ marginBottom: 8 }}>Dashboard</h1>
        <p style={{ color: token.colorTextTertiary, marginBottom: 0 }}>
          BA&QA Intelligence Platform'a hoş geldiniz
        </p>
      </div>

      {projectsError && (
        <Alert
          message="API Bağlantı Hatası"
          description={`Backend API'ye bağlanılamıyor: ${projectsError.message}. FastAPI server'ın çalıştığından emin olun (localhost:8000)`}
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Statistics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Spin spinning={projectsLoading}>
              <Statistic
                title="Toplam Proje"
                value={totalProjects}
                prefix={<ProjectOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Spin>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Spin spinning={documentsLoading}>
              <Statistic
                title="Toplam Doküman"
                value={totalDocuments}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Spin>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Spin spinning={pipelineLoading}>
              <Statistic
                title="Pipeline Çalıştırma"
                value={totalPipelineRuns}
                prefix={<RocketOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Spin>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Spin spinning={statsLoading}>
              <Statistic
                title="Ortalama Skor"
                value={avgScore}
                suffix="/ 100"
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: avgScore >= 60 ? '#3f8600' : '#cf1322' }}
              />
            </Spin>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card
        title="Hızlı İşlemler"
        style={{ marginTop: 24 }}
        extra={<ThunderboltOutlined style={{ color: '#faad14' }} />}
      >
        <Space wrap>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate(ROUTES.BA_EVALUATION)}
          >
            Yeni Değerlendirme
          </Button>
          <Button
            icon={<RocketOutlined />}
            onClick={() => navigate(ROUTES.BRD_PIPELINE)}
          >
            Pipeline Başlat
          </Button>
          <Button
            icon={<UploadOutlined />}
            onClick={() => navigate(ROUTES.IMPORT)}
          >
            Doküman Yükle
          </Button>
          <Button
            icon={<FileSearchOutlined />}
            onClick={() => navigate(ROUTES.SMART_MATCHING)}
          >
            Smart Matching
          </Button>
        </Space>
      </Card>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {/* Document Distribution — Donut Chart */}
        <Col xs={24} lg={12}>
          <Card
            title="Doküman Dağılımı"
            loading={documentsLoading}
          >
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {chartData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} />
                    ))}
                  </Pie>
                  {/* Center label */}
                  <text x="50%" y="46%" textAnchor="middle" dominantBaseline="middle"
                    style={{ fontSize: 28, fontWeight: 700, fill: token.colorText }}>
                    {totalDocuments}
                  </text>
                  <text x="50%" y="56%" textAnchor="middle" dominantBaseline="middle"
                    style={{ fontSize: 12, fill: token.colorTextTertiary }}>
                    toplam
                  </text>
                  <Tooltip
                    formatter={(value, name) => [`${value} doküman`, name]}
                    contentStyle={{ backgroundColor: token.colorBgElevated, borderColor: token.colorBorderSecondary }}
                  />
                  <Legend
                    formatter={(value, entry) => {
                      const item = chartData.find((d) => d.name === value);
                      return `${value} - ${item?.value || 0} doküman (%${item?.pct || 0})`;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p style={{ color: token.colorTextTertiary, textAlign: 'center', padding: '40px 0' }}>
                Henüz doküman bulunmuyor
              </p>
            )}
          </Card>
        </Col>

        {/* Recent Activities */}
        <Col xs={24} lg={12}>
          <Card
            title="Son Aktiviteler"
            extra={<ClockCircleOutlined />}
          >
            {recentActivities.length > 0 ? (
              <Timeline
                items={recentActivities.map(activity => ({
                  color: activity.color,
                  children: (
                    <div>
                      <div>{activity.title}</div>
                      <div style={{ fontSize: 12, color: token.colorTextTertiary, marginTop: 4 }}>
                        {new Date(activity.time).toLocaleString('tr-TR')}
                      </div>
                    </div>
                  )
                }))}
              />
            ) : (
              <p style={{ color: token.colorTextTertiary, textAlign: 'center', padding: '40px 0' }}>
                Henüz aktivite bulunmuyor
              </p>
            )}
          </Card>
        </Col>
      </Row>

      {/* Welcome Card */}
      <Card style={{ marginTop: 24 }}>
        <h3>Platform Özellikleri</h3>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <ul style={{ lineHeight: 2 }}>
              <li>BA ve TC doküman değerlendirme (AI destekli)</li>
              <li>BRD'den otomatik BA, TA ve TC üretimi</li>
              <li>Semantik doküman arama</li>
            </ul>
          </Col>
          <Col xs={24} md={12}>
            <ul style={{ lineHeight: 2 }}>
              <li>Smart document matching</li>
              <li>Design compliance kontrolü</li>
              <li>Versiyon yönetimi ve karşılaştırma</li>
            </ul>
          </Col>
        </Row>

        {!projectsError && (
          <Alert
            message="Backend API bağlantısı başarılı"
            type="success"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>
    </div>
  );
}
