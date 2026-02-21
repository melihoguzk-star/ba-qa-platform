/**
 * TemplatesTab — Create document from template
 */
import { useState } from 'react';
import { Card, Form, Select, Input, Button, Space, message, Row, Col } from 'antd';
import { FileAddOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useProjects } from '../../api/projects';
import { useCreateDocument } from '../../api/documents';

const TEMPLATES = {
  brd: {
    name: 'BRD Şablonu',
    description: 'Business Requirements Document şablonu',
    structure: {
      version_table: { headers: ['Tarih', 'Yazar', 'Açıklama', 'Versiyon'], rows: [] },
      purpose: { section: '1.1 Amaç', content: '' },
      scope: { section: '2.1 Kapsam', content: '', diagrams: [], figma_links: [] },
      functional_analysis: { section: '3.1 Fonksiyonel Analiz', screens: [] }
    }
  },
  ba: {
    name: 'BA Şablonu',
    description: 'Business Analysis doküman şablonu',
    structure: {
      project_info: { name: '', description: '' },
      screens: [],
      flows: [],
      acceptance_criteria: []
    }
  },
  ta: {
    name: 'TA Şablonu',
    description: 'Test Analysis doküman şablonu',
    structure: {
      project_info: { name: '', description: '' },
      test_scenarios: [],
      test_coverage: { total: 0, covered: 0 }
    }
  },
  tc: {
    name: 'TC Şablonu',
    description: 'Test Case doküman şablonu',
    structure: {
      project_info: { name: '', description: '' },
      test_cases: [],
      preconditions: [],
      test_data: []
    }
  }
};

export default function TemplatesTab() {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [form] = Form.useForm();

  const { data: projects } = useProjects();
  const createMutation = useCreateDocument();

  const handleTemplateSelect = (value) => {
    setSelectedTemplate(value);
    form.setFieldsValue({ doc_type: value });
  };

  const handleSubmit = async (values) => {
    try {
      const template = TEMPLATES[values.doc_type];
      await createMutation.mutateAsync({
        name: values.name,
        doc_type: values.doc_type,
        project_id: values.project_id,
        content_json: template.structure,
        tags: ['template', values.doc_type]
      });
      message.success('Doküman şablondan oluşturuldu');
      form.resetFields();
      setSelectedTemplate(null);
    } catch (error) {
      message.error('Doküman oluşturulurken hata oluştu');
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Şablondan Doküman Oluştur</h2>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {Object.entries(TEMPLATES).map(([key, template]) => (
          <Col xs={24} sm={12} md={6} key={key}>
            <Card
              hoverable
              style={{
                border: selectedTemplate === key ? '2px solid #1890ff' : '1px solid #d9d9d9',
                cursor: 'pointer'
              }}
              onClick={() => handleTemplateSelect(key)}
            >
              <div style={{ textAlign: 'center' }}>
                <FileAddOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
                <h3>{template.name}</h3>
                <p style={{ color: '#8c8c8c', fontSize: 12 }}>
                  {template.description}
                </p>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {selectedTemplate && (
        <Card title="Doküman Bilgileri" extra={<InfoCircleOutlined />}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{ doc_type: selectedTemplate }}
          >
            <Form.Item
              label="Doküman Adı"
              name="name"
              rules={[{ required: true, message: 'Doküman adı gerekli' }]}
            >
              <Input placeholder="Doküman adını girin" />
            </Form.Item>

            <Form.Item
              label="Proje"
              name="project_id"
              rules={[{ required: true, message: 'Proje seçiniz' }]}
            >
              <Select
                placeholder="Proje seçin"
                options={projects?.map(p => ({ label: p.name, value: p.id }))}
              />
            </Form.Item>

            <Form.Item
              label="Doküman Tipi"
              name="doc_type"
            >
              <Select disabled>
                <Select.Option value={selectedTemplate}>
                  {TEMPLATES[selectedTemplate].name}
                </Select.Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={createMutation.isPending}
                  icon={<FileAddOutlined />}
                >
                  Oluştur
                </Button>
                <Button onClick={() => {
                  form.resetFields();
                  setSelectedTemplate(null);
                }}>
                  İptal
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      )}

      {!selectedTemplate && (
        <Card style={{ textAlign: 'center', padding: 40 }}>
          <InfoCircleOutlined style={{ fontSize: 48, color: '#8c8c8c', marginBottom: 16 }} />
          <p style={{ color: '#8c8c8c' }}>
            Yukarıdan bir şablon seçerek başlayın
          </p>
        </Card>
      )}
    </div>
  );
}
