/**
 * Dashboard — Home page
 */
import { Card, Row, Col, Statistic } from 'antd';
import { FileTextOutlined, ProjectOutlined, RocketOutlined, CheckCircleOutlined } from '@ant-design/icons';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
        BA&QA Intelligence Platform'a hoş geldiniz
      </p>

      <Row gutter={16}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Toplam Proje"
              value={0}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Toplam Doküman"
              value={0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
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
      </Card>
    </div>
  );
}
