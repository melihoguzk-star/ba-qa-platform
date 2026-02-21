/**
 * Import — File upload and merge functionality
 */
import { useState } from 'react';
import {
  Card,
  Steps,
  Upload,
  Alert,
  Form,
  Select,
  Radio,
  Button,
  Space,
  message,
  Descriptions,
  Tree
} from 'antd';
import {
  InboxOutlined,
  FileTextOutlined,
  SaveOutlined,
  MergeCellsOutlined
} from '@ant-design/icons';
import { useUploadFile } from '../api/upload';
import { useProjects } from '../api/projects';
import { useDocuments, useCreateDocument, useUpdateDocument } from '../api/documents';

const { Dragger } = Upload;

export default function Import() {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [parseResult, setParseResult] = useState(null);
  const [importMode, setImportMode] = useState('new'); // 'new' or 'merge'
  const [form] = Form.useForm();

  const uploadMutation = useUploadFile();
  const { data: projects } = useProjects();
  const { data: documents } = useDocuments();
  const createMutation = useCreateDocument();
  const updateMutation = useUpdateDocument();

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

    return false;
  };

  const handleSave = async (values) => {
    try {
      if (importMode === 'new') {
        await createMutation.mutateAsync({
          name: parseResult?.metadata?.title || uploadedFile.name,
          doc_type: values.doc_type,
          project_id: values.project_id,
          content_json: parseResult?.content || {},
          tags: parseResult?.metadata?.tags || []
        });
        message.success('Doküman oluşturuldu');
      } else {
        // Merge mode
        const existingDoc = documents?.find(d => d.id === values.merge_document_id);
        const mergedContent = {
          ...existingDoc.content_json,
          ...parseResult?.content
        };
        await updateMutation.mutateAsync({
          id: values.merge_document_id,
          content_json: mergedContent
        });
        message.success('Doküman birleştirildi');
      }
      handleReset();
    } catch (error) {
      message.error('İşlem başarısız oldu');
    }
  };

  const handleReset = () => {
    setCurrentStep(0);
    setUploadedFile(null);
    setParseResult(null);
    setImportMode('new');
    form.resetFields();
  };

  const convertToTreeData = (obj, parentKey = '') => {
    if (!obj || typeof obj !== 'object') {
      return [];
    }

    return Object.entries(obj).map(([key, value], index) => {
      const nodeKey = parentKey ? `${parentKey}-${key}` : key;
      const isObject = typeof value === 'object' && value !== null && !Array.isArray(value);
      const isArray = Array.isArray(value);

      return {
        title: isObject || isArray ? 
          <span><strong>{key}</strong>: {isArray ? `[${value.length} items]` : '{...}'}</span> :
          <span><strong>{key}</strong>: {String(value)}</span>,
        key: nodeKey,
        children: isObject ? convertToTreeData(value, nodeKey) :
                  isArray ? value.map((item, i) => ({
                    title: typeof item === 'object' ? `[${i}] {...}` : `[${i}] ${item}`,
                    key: `${nodeKey}-${i}`,
                    children: typeof item === 'object' ? convertToTreeData(item, `${nodeKey}-${i}`) : undefined
                  })) : undefined
      };
    });
  };

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Doküman İçe Aktar</h1>

      <Steps
        current={currentStep}
        style={{ marginBottom: 32 }}
        items={[
          { title: 'Dosya Yükle', icon: <FileTextOutlined /> },
          { title: 'Parse Sonucu', icon: <FileTextOutlined /> },
          { title: 'Ayarlar', icon: <FileTextOutlined /> },
          { title: 'Kaydet', icon: <SaveOutlined /> }
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
              <InboxOutlined style={{ fontSize: 64, color: '#1890ff' }} />
            </p>
            <p className="ant-upload-text" style={{ fontSize: 18 }}>
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
              style={{ marginTop: 24 }}
            />
          )}
        </Card>
      )}

      {currentStep === 1 && parseResult && (
        <Card title="Parse Sonucu">
          {parseResult.warnings && parseResult.warnings.length > 0 && (
            <Alert
              message="Uyarılar"
              description={
                <ul style={{ margin: 0, paddingLeft: 20 }}>
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

          <Descriptions column={2} bordered style={{ marginBottom: 16 }}>
            <Descriptions.Item label="Dosya">{uploadedFile?.name}</Descriptions.Item>
            <Descriptions.Item label="Boyut">
              {(uploadedFile?.size / 1024).toFixed(2)} KB
            </Descriptions.Item>
            {parseResult.metadata?.confidence && (
              <Descriptions.Item label="Güven Skoru">
                {parseResult.metadata.confidence}%
              </Descriptions.Item>
            )}
            {parseResult.metadata?.title && (
              <Descriptions.Item label="Başlık">
                {parseResult.metadata.title}
              </Descriptions.Item>
            )}
          </Descriptions>

          <p style={{ marginBottom: 8 }}><strong>İçerik Yapısı:</strong></p>
          <div style={{
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 8,
            maxHeight: 400,
            overflow: 'auto'
          }}>
            {parseResult.content && (
              <Tree
                showLine
                defaultExpandAll
                treeData={convertToTreeData(parseResult.content)}
              />
            )}
          </div>

          <div style={{ marginTop: 16 }}>
            <Space>
              <Button onClick={handleReset}>İptal</Button>
              <Button type="primary" onClick={() => setCurrentStep(2)}>
                Devam Et
              </Button>
            </Space>
          </div>
        </Card>
      )}

      {currentStep === 2 && (
        <Card title="İçe Aktarma Modu">
          <Form
            form={form}
            layout="vertical"
            onFinish={() => setCurrentStep(3)}
          >
            <Form.Item label="Mod Seçimi">
              <Radio.Group value={importMode} onChange={(e) => setImportMode(e.target.value)}>
                <Space direction="vertical">
                  <Radio value="new">
                    <span><FileTextOutlined /> Yeni Doküman Oluştur</span>
                  </Radio>
                  <Radio value="merge">
                    <span><MergeCellsOutlined /> Mevcut Dokümanla Birleştir</span>
                  </Radio>
                </Space>
              </Radio.Group>
            </Form.Item>

            {importMode === 'new' ? (
              <>
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
              </>
            ) : (
              <Form.Item
                label="Birleştirilecek Doküman"
                name="merge_document_id"
                rules={[{ required: true, message: 'Doküman seçiniz' }]}
              >
                <Select
                  placeholder="Mevcut doküman seçin"
                  showSearch
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={documents?.map(d => ({
                    label: `${d.name} (${d.doc_type.toUpperCase()})`,
                    value: d.id
                  }))}
                />
              </Form.Item>
            )}

            <Form.Item>
              <Space>
                <Button onClick={() => setCurrentStep(1)}>Geri</Button>
                <Button type="primary" htmlType="submit">
                  Devam Et
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      )}

      {currentStep === 3 && (
        <Card title="Onay">
          <Alert
            message={importMode === 'new' ? 'Yeni Doküman Oluşturulacak' : 'Dokümanlar Birleştirilecek'}
            description={
              importMode === 'new' ?
                'Yüklediğiniz dosya yeni bir doküman olarak kütüphaneye eklenecek.' :
                'Yüklediğiniz dosyanın içeriği seçtiğiniz dokümanla birleştirilecek ve yeni bir versiyon oluşturulacak.'
            }
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Space>
            <Button onClick={() => setCurrentStep(2)}>Geri</Button>
            <Button onClick={handleReset}>İptal</Button>
            <Button
              type="primary"
              onClick={() => form.validateFields().then(handleSave)}
              loading={createMutation.isPending || updateMutation.isPending}
              icon={<SaveOutlined />}
            >
              {importMode === 'new' ? 'Oluştur' : 'Birleştir'}
            </Button>
          </Space>
        </Card>
      )}
    </div>
  );
}
