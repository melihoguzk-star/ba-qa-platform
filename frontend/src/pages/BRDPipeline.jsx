/**
 * BRD Pipeline — Automated document generation from BRD
 */
import { useState } from 'react';
import {
  Card,
  Form,
  Select,
  Input,
  Checkbox,
  Button,
  Steps,
  Alert,
  Tabs,
  Space,
  Progress,
  message,
  Upload
} from 'antd';
import {
  RocketOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  FileTextOutlined,
  UploadOutlined,
  SaveOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useProjects } from '../api/projects';
import { useStartPipeline, usePipelineStatus } from '../api/pipeline';
import { useCreateDocument } from '../api/documents';

const { TextArea } = Input;

const PIPELINE_STAGES = [
  { key: 'brd_analysis', title: 'BRD Analiz' },
  { key: 'ba_generation', title: 'BA Üretim' },
  { key: 'ba_qa', title: 'BA QA' },
  { key: 'ta_generation', title: 'TA Üretim' },
  { key: 'ta_qa', title: 'TA QA' },
  { key: 'tc_generation', title: 'TC Üretim' },
  { key: 'tc_qa', title: 'TC QA' }
];

export default function BRDPipeline() {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0); // 0: Setup, 1: Running, 2: Completed
  const [pipelineRunId, setPipelineRunId] = useState(null);
  const [selectedStages, setSelectedStages] = useState(['ba', 'ta', 'tc']);

  const { data: projects } = useProjects();
  const startMutation = useStartPipeline();
  const { data: pipelineStatus } = usePipelineStatus(pipelineRunId, {
    enabled: !!pipelineRunId && currentStep === 1
  });
  const createDocMutation = useCreateDocument();

  const handleStart = async (values) => {
    try {
      const result = await startMutation.mutateAsync({
        project_id: values.project_id,
        brd_content: values.brd_content,
        stages: selectedStages
      });
      setPipelineRunId(result.pipeline_run_id);
      setCurrentStep(1);
      message.success('Pipeline başlatıldı');
    } catch (error) {
      message.error('Pipeline başlatılamadı');
    }
  };

  const handleSaveDocument = async (docType, content) => {
    try {
      const projectId = form.getFieldValue('project_id');
      await createDocMutation.mutateAsync({
        name: `${docType.toUpperCase()} - ${new Date().toLocaleDateString()}`,
        doc_type: docType,
        project_id: projectId,
        content_json: content
      });
      message.success(`${docType.toUpperCase()} dokümanı kütüphaneye kaydedildi`);
    } catch (error) {
      message.error('Doküman kaydedilemedi');
    }
  };

  const handleReset = () => {
    setCurrentStep(0);
    setPipelineRunId(null);
    form.resetFields();
  };

  const getCurrentStageIndex = () => {
    if (!pipelineStatus?.current_stage) return -1;
    return PIPELINE_STAGES.findIndex(s => s.key === pipelineStatus.current_stage);
  };

  const getStageStatus = (index) => {
    const currentIndex = getCurrentStageIndex();
    if (index < currentIndex) return 'finish';
    if (index === currentIndex) {
      if (pipelineStatus?.status === 'failed') return 'error';
      return 'process';
    }
    return 'wait';
  };

  // Auto-advance to completed when pipeline finishes
  if (pipelineStatus && currentStep === 1 &&
      (pipelineStatus.status === 'completed' || pipelineStatus.status === 'failed')) {
    setTimeout(() => setCurrentStep(2), 500);
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>BRD Pipeline</h1>

      {currentStep === 0 && (
        <Card title="Pipeline Konfigürasyonu" extra={<RocketOutlined />}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleStart}
          >
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
              label="BRD İçeriği"
              name="brd_content"
              rules={[{ required: true, message: 'BRD içeriği gerekli' }]}
            >
              <TextArea
                rows={10}
                placeholder="BRD doküman içeriğini buraya yapıştırın veya dosya yükleyin..."
              />
            </Form.Item>

            <Form.Item label="Üretilecek Dokümanlar">
              <Checkbox.Group
                value={selectedStages}
                onChange={setSelectedStages}
              >
                <Space direction="vertical">
                  <Checkbox value="ba">BA (Business Analysis)</Checkbox>
                  <Checkbox value="ta">TA (Test Analysis)</Checkbox>
                  <Checkbox value="tc">TC (Test Cases)</Checkbox>
                </Space>
              </Checkbox.Group>
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={startMutation.isPending}
                  icon={<RocketOutlined />}
                  size="large"
                >
                  Pipeline Başlat
                </Button>
                <Upload
                  beforeUpload={() => false}
                  accept=".docx,.pdf"
                  maxCount={1}
                >
                  <Button icon={<UploadOutlined />}>BRD Dosyası Yükle</Button>
                </Upload>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      )}

      {currentStep === 1 && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Pipeline Durumu">
            <Steps
              current={getCurrentStageIndex()}
              items={PIPELINE_STAGES.map((stage, index) => ({
                title: stage.title,
                status: getStageStatus(index),
                icon: getStageStatus(index) === 'process' ? <LoadingOutlined /> :
                      getStageStatus(index) === 'finish' ? <CheckCircleOutlined /> :
                      getStageStatus(index) === 'error' ? <CloseCircleOutlined /> : undefined
              }))}
              size="small"
            />

            <div style={{ marginTop: 24 }}>
              <Progress
                percent={pipelineStatus?.progress_pct || 0}
                status={pipelineStatus?.status === 'failed' ? 'exception' : 'active'}
              />
            </div>

            {pipelineStatus?.error && (
              <Alert
                message="Pipeline Hatası"
                description={pipelineStatus.error}
                type="error"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}

            <div style={{ marginTop: 16 }}>
              <p><strong>Durum:</strong> {pipelineStatus?.status || 'starting'}</p>
              <p><strong>Mevcut Aşama:</strong> {pipelineStatus?.current_stage || '-'}</p>
              <p><strong>Tamamlanan:</strong> {pipelineStatus?.stages_completed?.join(', ') || '-'}</p>
            </div>
          </Card>

          {pipelineStatus?.logs && pipelineStatus.logs.length > 0 && (
            <Card title="Pipeline Logları">
              <div style={{
                background: '#000',
                color: '#0f0',
                padding: 16,
                borderRadius: 8,
                maxHeight: 300,
                overflow: 'auto',
                fontFamily: 'monospace',
                fontSize: 12
              }}>
                {pipelineStatus.logs.map((log, i) => (
                  <div key={i}>{log}</div>
                ))}
              </div>
            </Card>
          )}
        </Space>
      )}

      {currentStep === 2 && pipelineStatus && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card
            title={pipelineStatus.status === 'completed' ? 'Pipeline Tamamlandı' : 'Pipeline Başarısız'}
            extra={
              pipelineStatus.status === 'completed' ?
                <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} /> :
                <CloseCircleOutlined style={{ fontSize: 24, color: '#f5222d' }} />
            }
          >
            {pipelineStatus.status === 'completed' ? (
              <Alert
                message="Başarılı"
                description="Tüm dokümanlar başarıyla oluşturuldu. Aşağıdan dokümanları inceleyebilir ve kütüphaneye kaydedebilirsiniz."
                type="success"
                showIcon
              />
            ) : (
              <Alert
                message="Hata"
                description={pipelineStatus.error || 'Pipeline tamamlanamadı'}
                type="error"
                showIcon
              />
            )}

            <Button
              onClick={handleReset}
              style={{ marginTop: 16 }}
            >
              Yeni Pipeline
            </Button>
          </Card>

          {pipelineStatus.status === 'completed' && pipelineStatus.results && (
            <Card title="Üretilen Dokümanlar">
              <Tabs
                items={Object.entries(pipelineStatus.results).map(([docType, content]) => ({
                  key: docType,
                  label: docType.toUpperCase(),
                  children: (
                    <div>
                      <Space style={{ marginBottom: 16 }}>
                        <Button
                          icon={<SaveOutlined />}
                          onClick={() => handleSaveDocument(docType, content)}
                          loading={createDocMutation.isPending}
                        >
                          Kütüphaneye Kaydet
                        </Button>
                        <Button icon={<EyeOutlined />}>Önizle</Button>
                        <Button icon={<FileTextOutlined />}>Export</Button>
                      </Space>

                      <div style={{
                        background: '#f5f5f5',
                        padding: 16,
                        borderRadius: 8,
                        maxHeight: 400,
                        overflow: 'auto'
                      }}>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                          {JSON.stringify(content, null, 2)}
                        </pre>
                      </div>

                      {content.qa_score && (
                        <div style={{ marginTop: 16 }}>
                          <p><strong>QA Skoru:</strong></p>
                          <Progress
                            percent={content.qa_score}
                            strokeColor={content.qa_score >= 60 ? '#52c41a' : '#f5222d'}
                          />
                        </div>
                      )}
                    </div>
                  )
                }))}
              />
            </Card>
          )}
        </Space>
      )}
    </div>
  );
}
