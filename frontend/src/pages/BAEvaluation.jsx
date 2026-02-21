/**
 * BA Evaluation — BA document evaluation page
 */
import { useState } from 'react';
import {
  Card,
  Form,
  Select,
  Button,
  Progress,
  Descriptions,
  Collapse,
  Skeleton,
  Alert,
  Space,
  Upload,
  message
} from 'antd';
import {
  FileSearchOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UploadOutlined
} from '@ant-design/icons';
import { useDocuments } from '../api/documents';
import { useEvaluateBA } from '../api/evaluation';

const { Panel } = Collapse;

export default function BAEvaluation() {
  const [form] = Form.useForm();
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [selectedMethod, setSelectedMethod] = useState('existing'); // 'existing' or 'upload'

  const { data: documents } = useDocuments({ doc_type: 'ba' });
  const evaluateMutation = useEvaluateBA();

  const handleEvaluate = async (values) => {
    try {
      const requestData = {
        document_id: selectedMethod === 'existing' ? values.document_id : undefined,
        content_json: undefined, // TODO: implement for file upload
        reference_document_id: values.reference_document_id
      };

      const result = await evaluateMutation.mutateAsync(requestData);
      setEvaluationResult(result);
      message.success('Değerlendirme tamamlandı');
    } catch (error) {
      message.error('Değerlendirme başarısız oldu');
    }
  };

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(evaluationResult, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ba-evaluation-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setEvaluationResult(null);
    form.resetFields();
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#f5222d';
  };

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>BA Doküman Değerlendirme</h1>

      {!evaluationResult ? (
        <Card title="Değerlendirme Ayarları" extra={<FileSearchOutlined />}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleEvaluate}
          >
            <Form.Item label="Değerlendirme Yöntemi">
              <Select
                value={selectedMethod}
                onChange={setSelectedMethod}
                options={[
                  { label: 'Mevcut Doküman', value: 'existing' },
                  { label: 'Dosya Yükle', value: 'upload' }
                ]}
              />
            </Form.Item>

            {selectedMethod === 'existing' ? (
              <Form.Item
                label="BA Dokümanı"
                name="document_id"
                rules={[{ required: true, message: 'Doküman seçiniz' }]}
              >
                <Select
                  placeholder="Değerlendirilecek dokümanı seçin"
                  showSearch
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={documents?.map(d => ({
                    label: `${d.name} (v${d.current_version})`,
                    value: d.id
                  }))}
                />
              </Form.Item>
            ) : (
              <Form.Item
                label="Dosya Yükle"
                name="upload"
              >
                <Upload.Dragger
                  beforeUpload={() => false}
                  maxCount={1}
                  accept=".docx,.pdf"
                >
                  <p className="ant-upload-drag-icon">
                    <UploadOutlined />
                  </p>
                  <p className="ant-upload-text">Dosya yüklemek için tıklayın veya sürükleyin</p>
                  <p className="ant-upload-hint">DOCX veya PDF formatında BA dokümanı</p>
                </Upload.Dragger>
              </Form.Item>
            )}

            <Form.Item
              label="Referans Doküman (Opsiyonel)"
              name="reference_document_id"
            >
              <Select
                placeholder="Karşılaştırma için referans doküman seçin"
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                options={documents?.map(d => ({
                  label: `${d.name} (v${d.current_version})`,
                  value: d.id
                }))}
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={evaluateMutation.isPending}
                icon={<FileSearchOutlined />}
                size="large"
              >
                Değerlendir
              </Button>
            </Form.Item>
          </Form>

          {evaluateMutation.isPending && (
            <div style={{ marginTop: 24 }}>
              <Skeleton active />
              <Alert
                message="Değerlendirme devam ediyor..."
                description="AI model dokümanı analiz ediyor. Bu işlem 30-60 saniye sürebilir."
                type="info"
                showIcon
                style={{ marginTop: 16 }}
              />
            </div>
          )}
        </Card>
      ) : (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Overall Score */}
          <Card
            title="Genel Değerlendirme"
            extra={
              <Space>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={handleExportJSON}
                >
                  JSON İndir
                </Button>
                <Button onClick={handleReset}>Yeni Değerlendirme</Button>
              </Space>
            }
          >
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <Progress
                type="circle"
                percent={evaluationResult.score}
                size={180}
                strokeColor={getScoreColor(evaluationResult.score)}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: 48, fontWeight: 'bold' }}>{percent}</div>
                    <div style={{ fontSize: 14, color: '#8c8c8c' }}>/ 100</div>
                  </div>
                )}
              />
              <div style={{ marginTop: 24, fontSize: 18 }}>
                {evaluationResult.passed ? (
                  <span style={{ color: '#52c41a' }}>
                    <CheckCircleOutlined /> Doküman Geçti
                  </span>
                ) : (
                  <span style={{ color: '#f5222d' }}>
                    <CloseCircleOutlined /> Doküman İyileştirmeye İhtiyaç Duyuyor
                  </span>
                )}
              </div>
            </div>

            {evaluationResult.feedback && (
              <Alert
                message="Genel Geri Bildirim"
                description={evaluationResult.feedback}
                type="info"
                showIcon
                style={{ marginTop: 24 }}
              />
            )}
          </Card>

          {/* Criteria Scores */}
          <Card title="Kriter Bazlı Skorlar">
            <Collapse accordion>
              {evaluationResult.criteria_scores?.map((criterion, index) => (
                <Panel
                  header={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>{criterion.name || `Kriter ${index + 1}`}</span>
                      <Progress
                        percent={criterion.score}
                        steps={10}
                        strokeColor={getScoreColor(criterion.score)}
                        style={{ width: 200, marginLeft: 16 }}
                      />
                    </div>
                  }
                  key={index}
                >
                  <Descriptions column={1} bordered size="small">
                    <Descriptions.Item label="Skor">
                      {criterion.score} / 100
                    </Descriptions.Item>
                    <Descriptions.Item label="Durum">
                      {criterion.score >= 60 ? (
                        <span style={{ color: '#52c41a' }}>
                          <CheckCircleOutlined /> Yeterli
                        </span>
                      ) : (
                        <span style={{ color: '#f5222d' }}>
                          <CloseCircleOutlined /> İyileştirme Gerekli
                        </span>
                      )}
                    </Descriptions.Item>
                    {criterion.feedback && (
                      <Descriptions.Item label="Geri Bildirim">
                        {criterion.feedback}
                      </Descriptions.Item>
                    )}
                    {criterion.suggestions && criterion.suggestions.length > 0 && (
                      <Descriptions.Item label="Öneriler">
                        <ul style={{ margin: 0, paddingLeft: 20 }}>
                          {criterion.suggestions.map((suggestion, i) => (
                            <li key={i}>{suggestion}</li>
                          ))}
                        </ul>
                      </Descriptions.Item>
                    )}
                  </Descriptions>
                </Panel>
              ))}
            </Collapse>
          </Card>
        </Space>
      )}
    </div>
  );
}
