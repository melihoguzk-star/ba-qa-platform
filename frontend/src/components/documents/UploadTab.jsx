/**
 * UploadTab — File upload with drag & drop and parse preview
 */
import { useState } from 'react';
import { Upload, Card, Steps, Button, Select, Form, message, Alert } from 'antd';
import { InboxOutlined, FileTextOutlined } from '@ant-design/icons';
import { useUploadFile } from '../../api/upload';
import { useProjects } from '../../api/projects';
import { useCreateDocument } from '../../api/documents';

const { Dragger } = Upload;

export default function UploadTab() {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [parseResult, setParseResult] = useState(null);
  const [form] = Form.useForm();

  const uploadMutation = useUploadFile();
  const { data: projects } = useProjects();
  const createDocMutation = useCreateDocument();

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const result = await uploadMutation.mutateAsync(formData);
      setParseResult(result);
      setUploadedFile(file);
      setCurrentStep(1);
      message.success('Dosya başarıyla yüklendi ve parse edildi');
    } catch (error) {
      message.error('Dosya yüklenirken hata oluştu: ' + error.message);
    }

    return false; // Prevent default upload behavior
  };

  const handleSave = async (values) => {
    try {
      await createDocMutation.mutateAsync({
        name: parseResult?.metadata?.title || uploadedFile.name,
        doc_type: values.doc_type,
        project_id: values.project_id,
        content_json: parseResult?.content || {},
        tags: parseResult?.metadata?.tags || []
      });
      message.success('Doküman kaydedildi');
      handleReset();
    } catch (error) {
      message.error('Doküman kaydedilirken hata oluştu');
    }
  };

  const handleReset = () => {
    setCurrentStep(0);
    setUploadedFile(null);
    setParseResult(null);
    form.resetFields();
  };

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Doküman Yükle</h2>

      <Steps
        current={currentStep}
        style={{ marginBottom: 32 }}
        items={[
          { title: 'Dosya Yükle' },
          { title: 'Önizleme' },
          { title: 'Kaydet' }
        ]}
      />

      {currentStep === 0 && (
        <Card>
          <Dragger
            name="file"
            multiple={false}
            beforeUpload={handleUpload}
            showUploadList={false}
            accept=".docx,.pdf,.txt"
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            </p>
            <p className="ant-upload-text">
              Dosyayı buraya sürükleyin veya tıklayarak seçin
            </p>
            <p className="ant-upload-hint">
              Desteklenen formatlar: DOCX, PDF, TXT
            </p>
          </Dragger>

          {uploadMutation.isPending && (
            <Alert
              message="Dosya yükleniyor ve parse ediliyor..."
              type="info"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
        </Card>
      )}

      {currentStep === 1 && parseResult && (
        <Card>
          <h3>Parse Sonucu Önizleme</h3>

          {parseResult.warnings && parseResult.warnings.length > 0 && (
            <Alert
              message="Uyarılar"
              description={
                <ul>
                  {parseResult.warnings.map((warning, i) => (
                    <li key={i}>{warning}</li>
                  ))}
                </ul>
              }
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          <div style={{ marginBottom: 16 }}>
            <p><strong>Dosya:</strong> {uploadedFile?.name}</p>
            <p><strong>Boyut:</strong> {(uploadedFile?.size / 1024).toFixed(2)} KB</p>
            {parseResult.metadata?.confidence && (
              <p><strong>Güven Skoru:</strong> {parseResult.metadata.confidence}%</p>
            )}
          </div>

          <div style={{
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 8,
            maxHeight: 400,
            overflow: 'auto'
          }}>
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
              {JSON.stringify(parseResult.content, null, 2)}
            </pre>
          </div>

          <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
            <Button onClick={handleReset}>Yeni Dosya</Button>
            <Button type="primary" onClick={() => setCurrentStep(2)}>
              Devam Et
            </Button>
          </div>
        </Card>
      )}

      {currentStep === 2 && (
        <Card>
          <h3>Doküman Bilgilerini Girin</h3>

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSave}
            style={{ marginTop: 16 }}
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
              label="Doküman Tipi"
              name="doc_type"
              rules={[{ required: true, message: 'Doküman tipi seçiniz' }]}
            >
              <Select
                placeholder="Doküman tipi seçin"
                options={[
                  { label: 'BRD', value: 'brd' },
                  { label: 'BA', value: 'ba' },
                  { label: 'TA', value: 'ta' },
                  { label: 'TC', value: 'tc' }
                ]}
              />
            </Form.Item>

            <Form.Item>
              <div style={{ display: 'flex', gap: 8 }}>
                <Button onClick={() => setCurrentStep(1)}>Geri</Button>
                <Button onClick={handleReset}>İptal</Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={createDocMutation.isPending}
                  icon={<FileTextOutlined />}
                >
                  Kaydet
                </Button>
              </div>
            </Form.Item>
          </Form>
        </Card>
      )}
    </div>
  );
}
