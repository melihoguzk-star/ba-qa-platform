/**
 * Dashboard — Home page with live stats
 */
import { Card, Row, Col, Statistic, Spin, Alert } from 'antd';
import { FileTextOutlined, ProjectOutlined, RocketOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useProjects } from '../api/projects';
import { useDocuments } from '../api/documents';

export default function Dashboard() {
  const { data: projects, isLoading: projectsLoading, error: projectsError } = useProjects();
  const { data: documents, isLoading: documentsLoading } = useDocuments();

  const totalProjects = projects?.length || 0;
  const totalDocuments = documents?.length || 0;

  return (
    <div>
      <h1>Dashboard</h1>
      <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
        BA&QA Intelligence Platform'a hoş geldiniz
      </p>

      {projectsError && (
        <Alert
          message="API Bağlantı Hatası"
          description={`Backend API'ye bağlanılamıyor: ${projectsError.message}. FastAPI server'ın çalıştığından emin olun (localhost:8000)`}
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Row gutter={16}>
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
            <Statistic
              title="Pipeline Çalıştırma"
              value={0}
              prefix={<RocketOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Ortalama Skor"
              value={0}
              suffix="/ 100"
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <h3>Hoş Geldiniz! 🎉</h3>
        <p>
          Bu platform, BA/QA dokümanlarınızı yönetmenize, değerlendirmenize ve
          otomatik olarak oluşturmanıza yardımcı olur.
        </p>
        <p>
          <strong>Özellikler:</strong>
        </p>
        <ul>
          <li>BA ve TC doküman değerlendirme (AI destekli)</li>
          <li>BRD'den otomatik BA, TA ve TC üretimi</li>
          <li>Semantik doküman arama</li>
          <li>Smart document matching</li>
          <li>Design compliance kontrolü</li>
        </ul>

        {!projectsError && (
          <p style={{ marginTop: 16, color: '#52c41a' }}>
            ✓ Backend API bağlantısı başarılı
          </p>
        )}
      </Card>
    </div>
  );
}
