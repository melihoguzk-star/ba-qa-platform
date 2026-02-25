/**
 * Design Compliance Page
 *
 * Vision AI-powered design compliance checking
 * 4-agent pipeline: Requirements → Screen → Compliance → Report
 */
import { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Upload,
  Select,
  Checkbox,
  Progress,
  Typography,
  Space,
  Alert,
  Divider,
  Row,
  Col,
  Tabs,
  Tag,
  message,
  theme,
} from 'antd';
import {
  UploadOutlined,
  FileTextOutlined,
  PictureOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  useAnalyzeDesign,
  useCheckTypes,
  useVisionModels,
  analyzeDesignStream,
} from '../api/design';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

export default function DesignCompliance() {
  const [form] = Form.useForm();

  // State
  const [baDocument, setBaDocument] = useState('');
  const [imageFiles, setImageFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [streamingMode, setStreamingMode] = useState(true);

  // API hooks
  const { data: checkTypes = [] } = useCheckTypes();
  const { data: visionModels = [] } = useVisionModels();
  const analyzeMutation = useAnalyzeDesign();
  const { token } = theme.useToken();

  // Default checks
  const defaultChecks = checkTypes
    .filter((check) =>
      check.value.includes('Traceability') || check.value.includes('Eksik/Fazla')
    )
    .map((check) => check.value);

  // File upload configuration
  const uploadProps = {
    beforeUpload: (file) => {
      // Validate image type
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('Sadece görsel dosyaları yükleyebilirsiniz!');
        return Upload.LIST_IGNORE;
      }

      // Validate size (max 10MB)
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('Görsel boyutu 10MB\'dan küçük olmalıdır!');
        return Upload.LIST_IGNORE;
      }

      return false; // Prevent auto upload
    },
    onChange: (info) => {
      setImageFiles(info.fileList);
    },
    onRemove: (file) => {
      setImageFiles((prev) => prev.filter((f) => f.uid !== file.uid));
    },
    multiple: true,
    accept: 'image/*',
    listType: 'picture-card',
    maxCount: 20,
  };

  // Handle form submission
  const handleAnalyze = async (values) => {
    // Validate inputs
    if (!baDocument.trim()) {
      message.error('BA dokümanı boş olamaz!');
      return;
    }

    if (imageFiles.length === 0) {
      message.error('En az bir tasarım ekranı yüklemelisiniz!');
      return;
    }

    // Build FormData
    const formData = new FormData();
    formData.append('ba_document', baDocument);
    formData.append('project_name', values.project_name || '');
    formData.append('checks', (values.checks || defaultChecks).join(','));
    formData.append('extra_context', values.extra_context || '');
    formData.append('model', values.model || 'gemini-2.0-flash-exp');

    // Add image files
    imageFiles.forEach((file) => {
      formData.append('images', file.originFileObj);
    });

    // Analyze
    if (streamingMode) {
      // Streaming mode with SSE
      setIsAnalyzing(true);
      setProgress(0);
      setCurrentStep(null);
      setAnalysisResult(null);

      await analyzeDesignStream(formData, {
        onProgress: (event) => {
          setProgress(event.progress || 0);
          setCurrentStep(event.step);
          if (event.message) {
            message.info(event.message);
          }
        },
        onComplete: (data) => {
          setIsAnalyzing(false);
          setProgress(100);
          setAnalysisResult(data);
          message.success('Analiz tamamlandı!');
        },
        onError: (error) => {
          setIsAnalyzing(false);
          setProgress(0);
          message.error(`Analiz hatası: ${error.message}`);
        },
      });
    } else {
      // Non-streaming mode
      setIsAnalyzing(true);
      setProgress(50);
      setAnalysisResult(null);

      try {
        const result = await analyzeMutation.mutateAsync(formData);
        setAnalysisResult(result);
        setProgress(100);
        message.success('Analiz tamamlandı!');
      } catch (error) {
        message.error(`Analiz hatası: ${error.message}`);
      } finally {
        setIsAnalyzing(false);
      }
    }
  };

  // Step indicator
  const getStepIndicator = () => {
    const steps = [
      { key: 'requirements', label: 'Gereksinim Çıkarma', icon: <FileTextOutlined />, maxProgress: 30 },
      { key: 'screen_analysis', label: 'Ekran Analizi', icon: <PictureOutlined />, maxProgress: 55 },
      { key: 'compliance', label: 'Uyumluluk Kontrolü', icon: <CheckCircleOutlined />, maxProgress: 80 },
      { key: 'report', label: 'Rapor Oluşturma', icon: <FileTextOutlined />, maxProgress: 95 },
    ];

    const getStepStatus = (stepKey, stepMaxProgress) => {
      if (progress >= stepMaxProgress) return 'completed';
      if (currentStep === stepKey) return 'active';
      return 'pending';
    };

    return (
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
        <Row gutter={8}>
          {steps.map((step) => {
            const status = getStepStatus(step.key, step.maxProgress);
            return (
              <Col span={6} key={step.key}>
                <Card
                  size="small"
                  style={{
                    textAlign: 'center',
                    backgroundColor:
                      status === 'completed'
                        ? token.colorSuccessBg
                        : status === 'active'
                        ? token.colorPrimaryBg
                        : token.colorFillQuaternary,
                    borderColor:
                      status === 'completed'
                        ? '#52c41a'
                        : status === 'active'
                        ? '#1890ff'
                        : token.colorBorder,
                  }}
                >
                  <Space direction="vertical" size={4}>
                    {status === 'active' ? (
                      <LoadingOutlined spin style={{ color: '#1890ff' }} />
                    ) : status === 'completed' ? (
                      <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    ) : (
                      <span style={{ color: token.colorTextQuaternary }}>{step.icon}</span>
                    )}
                    <Text
                      style={{
                        fontSize: 12,
                        fontWeight: status === 'active' ? 600 : 400,
                        color:
                          status === 'completed'
                            ? '#52c41a'
                            : status === 'active'
                            ? '#1890ff'
                            : token.colorTextTertiary,
                      }}
                    >
                      {step.label}
                    </Text>
                  </Space>
                </Card>
              </Col>
            );
          })}
        </Row>
        <Progress
          percent={progress}
          status={isAnalyzing ? 'active' : progress === 100 ? 'success' : 'normal'}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
        />
      </Space>
    );
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>
        <RocketOutlined /> Design Compliance
      </Title>
      <Paragraph>
        Tasarım ekranlarını BA dokümanıyla karşılaştırarak uyumluluk kontrolü yapın.
        Vision AI tabanlı 4-agent pipeline kullanır.
      </Paragraph>

      <Row gutter={[16, 16]}>
        {/* Input Section */}
        <Col xs={24} lg={12}>
          <Card title="Analiz Parametreleri" bordered>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleAnalyze}
              initialValues={{
                checks: defaultChecks,
                model: 'gemini-2.0-flash-exp',
              }}
            >
              {/* Project Name */}
              <Form.Item
                label="Proje Adı"
                name="project_name"
                tooltip="Opsiyonel proje adı"
              >
                <Input placeholder="Örn: Mobile Banking App" />
              </Form.Item>

              {/* BA Document */}
              <Form.Item
                label="BA Dokümanı"
                required
                tooltip="İş analizi dokümanı metni"
              >
                <TextArea
                  value={baDocument}
                  onChange={(e) => setBaDocument(e.target.value)}
                  placeholder="BA dokümanı metnini buraya yapıştırın..."
                  rows={8}
                  style={{ fontFamily: 'monospace', fontSize: 12 }}
                />
                <Space style={{ marginTop: 8 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Karakter sayısı: {baDocument.length}
                  </Text>
                </Space>
              </Form.Item>

              {/* Design Images */}
              <Form.Item
                label="Tasarım Ekranları"
                required
                tooltip="Tasarım görselleri (max 20)"
              >
                <Upload {...uploadProps}>
                  <Button icon={<UploadOutlined />}>Görsel Yükle</Button>
                </Upload>
                <Text type="secondary" style={{ fontSize: 12, marginTop: 8 }}>
                  {imageFiles.length} görsel yüklendi (max 20)
                </Text>
              </Form.Item>

              {/* Check Types */}
              <Form.Item
                label="Kontrol Türleri"
                name="checks"
                tooltip="Yapılacak uyumluluk kontrolleri"
              >
                <Checkbox.Group style={{ width: '100%' }}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {checkTypes.map((check) => (
                      <Checkbox key={check.value} value={check.value}>
                        {check.value}
                      </Checkbox>
                    ))}
                  </Space>
                </Checkbox.Group>
              </Form.Item>

              {/* Vision Model */}
              <Form.Item
                label="Vision Model"
                name="model"
                tooltip="Kullanılacak AI modeli"
              >
                <Select>
                  {visionModels.map((model) => (
                    <Select.Option key={model.id} value={model.id}>
                      <Space>
                        {model.name} ({model.provider})
                        {model.recommended && (
                          <Tag color="green" style={{ fontSize: 10 }}>
                            Önerilen
                          </Tag>
                        )}
                      </Space>
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              {/* Extra Context */}
              <Form.Item
                label="Ek Bağlam"
                name="extra_context"
                tooltip="Opsiyonel ek bilgi veya talimatlar"
              >
                <TextArea
                  placeholder="Opsiyonel ek bağlam veya özel talimatlar..."
                  rows={3}
                />
              </Form.Item>

              {/* Streaming Mode */}
              <Form.Item>
                <Checkbox
                  checked={streamingMode}
                  onChange={(e) => setStreamingMode(e.target.checked)}
                >
                  Canlı ilerleme takibi (Streaming)
                </Checkbox>
              </Form.Item>

              {/* Submit Button */}
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isAnalyzing}
                  icon={<RocketOutlined />}
                  block
                  size="large"
                >
                  {isAnalyzing ? 'Analiz Ediliyor...' : 'Analizi Başlat'}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        {/* Results Section */}
        <Col xs={24} lg={12}>
          <Card title="Analiz Sonuçları" bordered>
            {isAnalyzing && streamingMode && getStepIndicator()}

            {!isAnalyzing && !analysisResult && (
              <Alert
                message="Sonuç Yok"
                description="Analiz sonuçları burada görüntülenecek. Lütfen parametreleri doldurup analizi başlatın."
                type="info"
                showIcon
              />
            )}

            {analysisResult && (
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* Summary */}
                <Card size="small" style={{ backgroundColor: token.colorPrimaryBg }}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Text strong>Proje:</Text>
                        <div>{analysisResult.project_name || 'Belirtilmedi'}</div>
                      </Col>
                      <Col span={12}>
                        <Text strong>Ekran Sayısı:</Text>
                        <div>{analysisResult.num_screens}</div>
                      </Col>
                    </Row>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Text strong>Tarih:</Text>
                        <div>{analysisResult.timestamp}</div>
                      </Col>
                      <Col span={12}>
                        <Text strong>Kontroller:</Text>
                        <div>{analysisResult.checks?.length || 0}</div>
                      </Col>
                    </Row>
                  </Space>
                </Card>

                {/* Agent Outputs */}
                <Tabs
                  defaultActiveKey="report"
                  items={[
                    {
                      key: 'report',
                      label: '📋 Final Rapor',
                      children: (
                        <Card size="small">
                          <div
                            className="markdown-content"
                            style={{
                              maxHeight: 500,
                              overflowY: 'auto',
                              padding: 16,
                              backgroundColor: token.colorFillQuaternary,
                            }}
                          >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysisResult.report_output}</ReactMarkdown>
                          </div>
                        </Card>
                      ),
                    },
                    {
                      key: 'compliance',
                      label: '✅ Uyumluluk',
                      children: (
                        <Card size="small">
                          <div
                            className="markdown-content"
                            style={{
                              maxHeight: 500,
                              overflowY: 'auto',
                              padding: 16,
                              backgroundColor: token.colorFillQuaternary,
                            }}
                          >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysisResult.compliance_output}</ReactMarkdown>
                          </div>
                        </Card>
                      ),
                    },
                    {
                      key: 'requirements',
                      label: '📝 Gereksinimler',
                      children: (
                        <Card size="small">
                          <div
                            className="markdown-content"
                            style={{
                              maxHeight: 500,
                              overflowY: 'auto',
                              padding: 16,
                              backgroundColor: token.colorFillQuaternary,
                            }}
                          >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {analysisResult.requirements_output}
                            </ReactMarkdown>
                          </div>
                        </Card>
                      ),
                    },
                    {
                      key: 'screens',
                      label: '🖼️ Ekran Analizi',
                      children: (
                        <Card size="small">
                          <div
                            className="markdown-content"
                            style={{
                              maxHeight: 500,
                              overflowY: 'auto',
                              padding: 16,
                              backgroundColor: token.colorFillQuaternary,
                            }}
                          >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysisResult.screen_output}</ReactMarkdown>
                          </div>
                        </Card>
                      ),
                    },
                    {
                      key: 'full',
                      label: '📄 Tam Rapor',
                      children: (
                        <Card size="small">
                          <div
                            className="markdown-content"
                            style={{
                              maxHeight: 500,
                              overflowY: 'auto',
                              padding: 16,
                              backgroundColor: token.colorFillQuaternary,
                            }}
                          >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysisResult.full_report}</ReactMarkdown>
                          </div>
                        </Card>
                      ),
                    },
                  ]}
                />

                {/* Download Button */}
                <Button
                  block
                  onClick={() => {
                    const blob = new Blob([analysisResult.full_report], {
                      type: 'text/markdown',
                    });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `design-compliance-${analysisResult.project_name || 'report'}-${Date.now()}.md`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                >
                  📥 Raporu İndir (.md)
                </Button>
              </Space>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
