/**
 * PipelineWizard — 3-step configuration wizard for BRD Pipeline
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
  Upload,
  Space,
  Alert,
  Descriptions,
  message
} from 'antd';
import {
  RocketOutlined,
  UploadOutlined,
  SettingOutlined,
  FileTextOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined
} from '@ant-design/icons';
import mammoth from 'mammoth';

const { TextArea } = Input;

const WIZARD_STEPS = [
  { title: 'Proje Seçimi', icon: <RocketOutlined /> },
  { title: 'BRD İçerik', icon: <FileTextOutlined /> },
  { title: 'Yapılandırma', icon: <SettingOutlined /> }
];

export default function PipelineWizard({ onComplete, projects, loading }) {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [selectedStages, setSelectedStages] = useState(['ba', 'ta', 'tc']);

  const handleFileUpload = async (file) => {
    try {
      const fileExtension = file.name.split('.').pop().toLowerCase();

      if (fileExtension === 'txt') {
        const reader = new FileReader();
        reader.onload = (e) => {
          form.setFieldsValue({ brd_content: e.target.result });
          setUploadedFile(file);
          message.success(`${file.name} yüklendi`);
        };
        reader.readAsText(file);
      } else if (fileExtension === 'docx') {
        message.loading(`${file.name} parse ediliyor...`, 0);
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        message.destroy();

        if (result.value) {
          form.setFieldsValue({ brd_content: result.value });
          setUploadedFile(file);
          message.success(`${file.name} başarıyla yüklendi (${result.value.length} karakter)`);
          if (result.messages?.length > 0) {
            console.warn('DOCX parse warnings:', result.messages);
          }
        } else {
          message.error('DOCX dosyası boş veya okunamadı');
          setUploadedFile(null);
        }
      } else if (fileExtension === 'pdf') {
        message.warning('PDF dosyaları şu anda desteklenmiyor. Lütfen içeriği kopyalayıp yapıştırın.', 5);
        setUploadedFile(null);
      } else {
        message.error('Desteklenmeyen dosya formatı. .txt veya .docx dosyası yükleyin.');
        setUploadedFile(null);
      }
    } catch (error) {
      console.error('File upload error:', error);
      message.error(`Dosya okunamadı: ${error.message}`);
      setUploadedFile(null);
    }
    return false;
  };

  const handleNext = async () => {
    try {
      if (currentStep === 0) {
        await form.validateFields(['project_id']);
      } else if (currentStep === 1) {
        await form.validateFields(['brd_content']);
      }
      setCurrentStep(prev => prev + 1);
    } catch {
      // validation failed
    }
  };

  const handleBack = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleStart = () => {
    if (selectedStages.length === 0) {
      message.error('En az bir doküman türü seçmelisiniz');
      return;
    }

    const values = form.getFieldsValue(true);
    if (!values.brd_content?.trim()) {
      message.error('BRD içeriği boş olamaz');
      return;
    }

    if (!values.project_id) {
      message.error('Proje seçilmedi');
      return;
    }

    const selectedProject = projects?.find(p => p.id === values.project_id);

    onComplete?.({
      project_id: values.project_id,
      project_name: selectedProject?.name || `Project ${values.project_id}`,
      brd_content: values.brd_content,
      stages: selectedStages,
      figma_url: values.figma_url || null
    });
  };

  // Summary component that reads form values via Form.useWatch to stay reactive
  const SummaryPanel = () => {
    const projectId = Form.useWatch('project_id', form);
    const brdContent = Form.useWatch('brd_content', form);
    const figmaUrl = Form.useWatch('figma_url', form);
    const selectedProject = projects?.find(p => p.id === projectId);
    const contentLength = brdContent?.length || 0;

    return (
      <Descriptions title="Özet" bordered column={1} size="small" style={{ marginTop: 24 }}>
        <Descriptions.Item label="Proje">
          {selectedProject?.name || 'Seçilmedi'}
        </Descriptions.Item>
        <Descriptions.Item label="BRD İçerik">
          {contentLength > 0 ? `${contentLength} karakter` : 'Girilmedi'}
        </Descriptions.Item>
        <Descriptions.Item label="Doküman Türleri">
          {selectedStages.map(s => s.toUpperCase()).join(', ') || 'Seçilmedi'}
        </Descriptions.Item>
        <Descriptions.Item label="Figma URL">
          {figmaUrl || 'Yok'}
        </Descriptions.Item>
      </Descriptions>
    );
  };

  return (
    <Card>
      <Steps
        current={currentStep}
        items={WIZARD_STEPS}
        style={{ marginBottom: 32 }}
      />

      <Form
        form={form}
        layout="vertical"
        preserve={true}
        style={{ minHeight: 300 }}
      >
        {/* All steps rendered simultaneously, hidden with display:none to preserve form values */}
        <div style={{ display: currentStep === 0 ? 'block' : 'none' }}>
          <Alert
            message="Proje Seçimi"
            description="Pipeline'ın bağlı olacağı projeyi seçin. Üretilen dokümanlar bu projeye kaydedilecek."
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />
          <Form.Item
            label="Proje"
            name="project_id"
            rules={[{ required: true, message: 'Proje seçiniz' }]}
          >
            <Select
              placeholder="Proje seçin"
              showSearch
              optionFilterProp="label"
              options={projects?.map(p => ({ label: p.name, value: p.id }))}
              loading={!projects}
              size="large"
            />
          </Form.Item>
        </div>

        <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
          <Alert
            message="BRD İçeriği"
            description="BRD doküman içeriğini yapıştırın veya dosya yükleyin. Bu içerik BA, TA ve TC dokümanlarının temelini oluşturacak."
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />
          <Form.Item
            label="BRD İçeriği"
            name="brd_content"
            rules={[{ required: true, message: 'BRD içeriği gerekli' }]}
          >
            <TextArea
              rows={12}
              placeholder="BRD doküman içeriğini buraya yapıştırın veya dosya yükleyin..."
            />
          </Form.Item>
          <Form.Item label="Dosya Yükle">
            <Upload
              beforeUpload={handleFileUpload}
              accept=".docx,.pdf,.txt"
              maxCount={1}
              fileList={uploadedFile ? [uploadedFile] : []}
              onRemove={() => setUploadedFile(null)}
            >
              <Button icon={<UploadOutlined />}>BRD Dosyası Yükle (.docx, .txt)</Button>
            </Upload>
          </Form.Item>
        </div>

        <div style={{ display: currentStep === 2 ? 'block' : 'none' }}>
          <Alert
            message="Yapılandırma"
            description="Üretilecek doküman türlerini ve opsiyonel Figma URL'ini belirleyin."
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />

          <Form.Item label="Üretilecek Dokümanlar">
            <Checkbox.Group
              value={selectedStages}
              onChange={setSelectedStages}
            >
              <Space direction="vertical">
                <Checkbox value="ba">BA (Business Analysis)</Checkbox>
                <Checkbox value="ta">TA (Technical Analysis)</Checkbox>
                <Checkbox value="tc">TC (Test Cases)</Checkbox>
              </Space>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            label="Figma Tasarım URL (Opsiyonel)"
            name="figma_url"
          >
            <Input placeholder="https://figma.com/design/..." />
          </Form.Item>

          <SummaryPanel />
        </div>
      </Form>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
        <div>
          {currentStep > 0 && (
            <Button icon={<ArrowLeftOutlined />} onClick={handleBack}>
              Geri
            </Button>
          )}
        </div>
        <div>
          {currentStep < 2 ? (
            <Button type="primary" icon={<ArrowRightOutlined />} onClick={handleNext}>
              İleri
            </Button>
          ) : (
            <Button
              type="primary"
              icon={<RocketOutlined />}
              size="large"
              onClick={handleStart}
              loading={loading}
            >
              Pipeline Başlat
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
