/**
 * BRD Pipeline — Step-by-step document generation with user approval
 */
import { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Select,
  Input,
  Checkbox,
  Button,
  Steps,
  Alert,
  Space,
  Progress,
  message,
  Upload,
  Spin,
  Modal,
  Divider,
  Table,
  Tag,
  Collapse,
  theme
} from 'antd';
import {
  RocketOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  FileTextOutlined,
  UploadOutlined,
  SaveOutlined,
  EyeOutlined,
  EditOutlined,
  ArrowRightOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useProjects } from '../api/projects';
import {
  useStartPipeline,
  usePipelineStatus,
  useExecuteStage,
  useEvaluateQA,
  useCheckpoint,
  useSaveCheckpoint,
  usePipelineResults,
  downloadDocument
} from '../api/pipeline';
import { useCreateDocument } from '../api/documents';
import mammoth from 'mammoth';

const { TextArea } = Input;

// Step definitions matching Streamlit workflow
const WORKFLOW_STEPS = [
  { key: 'upload', title: 'BRD Yükleme' },
  { key: 'ba_gen', title: 'BA Üretim' },
  { key: 'ba_review', title: 'BA İnceleme' },
  { key: 'ba_qa', title: 'BA QA' },
  { key: 'ta_gen', title: 'TA Üretim' },
  { key: 'ta_review', title: 'TA İnceleme' },
  { key: 'ta_qa', title: 'TA QA' },
  { key: 'figma_upload', title: 'Figma (Opsiyonel)' },
  { key: 'tc_gen', title: 'TC Üretim' },
  { key: 'tc_review', title: 'TC İnceleme' },
  { key: 'tc_qa', title: 'TC QA' },
  { key: 'done', title: 'Tamamlandı' }
];

export default function BRDPipeline() {
  const [form] = Form.useForm();
  const [currentStepKey, setCurrentStepKey] = useState('upload');
  const [pipelineRunId, setPipelineRunId] = useState(null);
  const [selectedStages, setSelectedStages] = useState(['ba', 'ta', 'tc']);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [editedContent, setEditedContent] = useState(null);
  const [qaResult, setQaResult] = useState(null);
  const [previewModal, setPreviewModal] = useState({ visible: false, docType: null, content: null });

  const { data: projects } = useProjects();
  const startMutation = useStartPipeline();
  const executeStageMutation = useExecuteStage();
  const evaluateQAMutation = useEvaluateQA();
  const saveCheckpointMutation = useSaveCheckpoint();
  const createDocMutation = useCreateDocument();
  const { token } = theme.useToken();

  const { data: pipelineStatus } = usePipelineStatus(pipelineRunId, {
    enabled: !!pipelineRunId,
    refetchInterval: 2000, // Always poll every 2 seconds when pipeline is active
    staleTime: 0, // Always refetch, don't use stale data
  });

  // Debug: log pipeline status changes
  useEffect(() => {
    if (pipelineStatus) {
      console.log('[BRD Pipeline] Status update:', {
        status: pipelineStatus.status,
        current_stage: pipelineStatus.current_stage,
        frontend_step: currentStepKey
      });
    }
  }, [pipelineStatus, currentStepKey]);

  // Get checkpoint data when in review stages
  const currentStageForCheckpoint = currentStepKey.replace('_review', '_gen');
  const { data: checkpointData, refetch: refetchCheckpoint } = useCheckpoint(
    pipelineRunId,
    currentStageForCheckpoint,
    {
      enabled: !!pipelineRunId && currentStepKey.includes('_review')
    }
  );

  const { data: pipelineResults } = usePipelineResults(pipelineRunId, {
    enabled: !!pipelineRunId && currentStepKey === 'done'
  });

  // Sync currentStepKey with backend status — only move FORWARD, never backward.
  // This prevents stale poll data from dragging the user back after manual navigation
  // (e.g., Figma skip → tc_gen, but old poll still shows figma_upload).
  useEffect(() => {
    if (!pipelineStatus?.current_stage) return;

    const backendStage = pipelineStatus.current_stage;

    // Handle completed state
    if (pipelineStatus.status === 'completed' && currentStepKey !== 'done') {
      console.log(`[BRD Pipeline] Pipeline completed, navigating to done`);
      setCurrentStepKey('done');
      return;
    }

    if (backendStage !== currentStepKey && pipelineStatus.status === 'waiting_approval') {
      const backendIdx = WORKFLOW_STEPS.findIndex(s => s.key === backendStage);
      const currentIdx = WORKFLOW_STEPS.findIndex(s => s.key === currentStepKey);

      // Only sync if backend is AHEAD of frontend (forward movement)
      if (backendIdx <= currentIdx) {
        return;
      }

      console.log(`[BRD Pipeline] Stage transition: ${currentStepKey} → ${backendStage}`);
      setCurrentStepKey(backendStage);

      // If transitioning to a review stage, refetch checkpoint data
      if (backendStage.includes('_review')) {
        setTimeout(() => {
          refetchCheckpoint();
        }, 500);
      }
    }
  }, [pipelineStatus, currentStepKey, refetchCheckpoint]);

  // Load checkpoint data into editor when entering review stage
  useEffect(() => {
    if (checkpointData && currentStepKey.includes('_review')) {
      setEditedContent(checkpointData);
    }
  }, [checkpointData, currentStepKey]);

  const handleStart = async (values) => {
    if (selectedStages.length === 0) {
      message.error('En az bir doküman türü seçmelisiniz');
      return;
    }

    if (!values.brd_content || values.brd_content.trim() === '') {
      message.error('BRD içeriği boş olamaz');
      return;
    }

    try {
      const selectedProject = projects?.find(p => p.id === values.project_id);
      const project_name = selectedProject?.name || `Project ${values.project_id}`;

      const result = await startMutation.mutateAsync({
        project_id: values.project_id,
        project_name: project_name,
        brd_content: values.brd_content,
        stages: selectedStages,
        figma_url: values.figma_url || null
      });

      setPipelineRunId(result.pipeline_run_id);
      setCurrentStepKey('ba_gen');
      message.success('Pipeline oluşturuldu. BA üretimi başlatabilirsiniz.');
    } catch (error) {
      console.error('Pipeline start error:', error);
      message.error(error.response?.data?.detail || 'Pipeline başlatılamadı');
    }
  };

  const handleExecuteStage = async (stage) => {
    try {
      await executeStageMutation.mutateAsync({
        runId: pipelineRunId,
        stage: stage
      });
      message.success(`${stage.toUpperCase()} üretimi başlatıldı`);
    } catch (error) {
      message.error(`${stage.toUpperCase()} üretilemedi: ${error.message}`);
    }
  };

  const handleApproveAndContinue = async () => {
    const currentStage = currentStepKey.replace('_review', '');

    // Save edited content if changed
    if (editedContent) {
      try {
        await saveCheckpointMutation.mutateAsync({
          runId: pipelineRunId,
          stage: `${currentStage}_gen`,
          data: editedContent
        });
        message.success('Değişiklikler kaydedildi');
      } catch (error) {
        message.error('Kayıt hatası');
        return;
      }
    }

    // Move to QA stage (user will click evaluate button there)
    const qaStage = `${currentStage}_qa`;
    console.log(`[BRD Pipeline] Moving to QA stage: ${qaStage}`);
    setCurrentStepKey(qaStage);
    setQaResult(null); // Clear previous QA result
  };

  const handleEvaluateQA = async (forcePass = false) => {
    const currentStage = currentStepKey; // e.g., 'ba_qa'
    const content = editedContent || checkpointData;

    if (!content) {
      message.error('İçerik bulunamadı');
      return;
    }

    try {
      const result = await evaluateQAMutation.mutateAsync({
        runId: pipelineRunId,
        stage: currentStage,
        content: content,
        force_pass: forcePass
      });

      setQaResult(result);

      if (result.passed) {
        message.success(`QA başarılı! Skor: ${result.score}`);

        // Only auto-transition if force_pass (user clicked "Sonraki Aşamaya Geç")
        if (forcePass) {
          // Move to next stage - backend handles this via evaluate_stage_qa
          console.log(`[BRD Pipeline] Force pass - backend will transition to next stage`);
          // Backend already transitioned, useEffect will sync
        } else {
          // Show results, user will click "Sonraki Aşamaya Geç" button
          console.log(`[BRD Pipeline] QA passed, showing results. User must click next button.`);
        }
      } else {
        message.warning(`QA skoru düşük: ${result.score}. İçeriği düzenleyip tekrar deneyin veya zorla geçin.`);
      }
    } catch (error) {
      message.error('QA değerlendirmesi başarısız');
    }
  };

  const handleRegenerate = async (qaStage) => {
    // Extract feedback from QA result
    if (!qaResult) {
      message.error('QA sonucu bulunamadı');
      return;
    }

    // Format feedback from QA evaluation
    let feedback = '';

    if (qaResult.genel_degerlendirme) {
      feedback += `Genel Değerlendirme: ${qaResult.genel_degerlendirme}\n\n`;
    }

    if (qaResult.iyilestirme_onerileri) {
      feedback += `İyileştirme Önerileri:\n`;
      if (Array.isArray(qaResult.iyilestirme_onerileri)) {
        qaResult.iyilestirme_onerileri.forEach((oneri, i) => {
          feedback += `${i + 1}. ${oneri}\n`;
        });
      } else {
        feedback += qaResult.iyilestirme_onerileri;
      }
    }

    if (qaResult.skorlar && qaResult.skorlar.length > 0) {
      feedback += `\nKriter Skorları:\n`;
      qaResult.skorlar.forEach(kriter => {
        if (kriter.puan < 6) { // Only include failing criteria
          feedback += `- ${kriter.kriter}: ${kriter.puan}/10 - ${kriter.aciklama}\n`;
        }
      });
    }

    // Determine which generation stage to run (ba_qa -> ba_gen, etc.)
    const stagePrefix = qaStage.replace('_qa', '');
    const genStage = `${stagePrefix}_gen`;

    try {
      message.loading(`${stagePrefix.toUpperCase()} yeniden üretiliyor...`, 0);

      await executeStageMutation.mutateAsync({
        runId: pipelineRunId,
        stage: genStage,
        feedback: feedback
      });

      // Clear QA result and move to generation stage
      setQaResult(null);
      setCurrentStepKey(genStage);

      message.destroy();
      message.success('Yeniden üretim başlatıldı');
    } catch (error) {
      message.destroy();
      message.error('Yeniden üretim başlatılamadı');
    }
  };

  const handleDownloadDocument = async (docType) => {
    try {
      message.loading(`${docType.toUpperCase()} dokümanı indiriliyor...`, 0);
      await downloadDocument(pipelineRunId, docType);
      message.destroy();
      message.success(`${docType.toUpperCase()} dokümanı indirildi`);
    } catch (error) {
      message.destroy();
      message.error('İndirme başarısız');
      console.error('Download error:', error);
    }
  };

  const handlePreviewDocument = (docType, content) => {
    setPreviewModal({
      visible: true,
      docType: docType.toUpperCase(),
      content: content
    });
  };

  const handleFileUpload = async (file) => {
    try {
      const fileExtension = file.name.split('.').pop().toLowerCase();

      if (fileExtension === 'txt') {
        // Plain text file - read as text
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target.result;
          form.setFieldsValue({ brd_content: content });
          setUploadedFile(file);
          message.success(`${file.name} yüklendi`);
        };
        reader.readAsText(file);
      } else if (fileExtension === 'docx') {
        // DOCX file - parse with mammoth.js
        message.loading(`${file.name} parse ediliyor...`, 0);

        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });

        message.destroy(); // Remove loading message

        if (result.value) {
          form.setFieldsValue({ brd_content: result.value });
          setUploadedFile(file);
          message.success(`${file.name} başarıyla yüklendi (${result.value.length} karakter)`);

          // Show warnings if any
          if (result.messages && result.messages.length > 0) {
            console.warn('DOCX parse warnings:', result.messages);
          }
        } else {
          message.error('DOCX dosyası boş veya okunamadı');
          setUploadedFile(null);
        }
      } else if (fileExtension === 'pdf') {
        // PDF not supported yet
        message.warning(
          'PDF dosyaları şu anda desteklenmiyor. ' +
          'Lütfen içeriği kopyalayıp textarea\'ya yapıştırın.',
          5
        );
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
    setCurrentStepKey('upload');
    setPipelineRunId(null);
    setUploadedFile(null);
    setEditedContent(null);
    setQaResult(null);
    form.resetFields();
  };

  const renderBADocContent = (content) => {
    if (!content) return <p>İçerik bulunamadı</p>;
    const ekranlar = content.ekranlar || [];
    if (ekranlar.length === 0) {
      return <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(content, null, 2)}</pre>;
    }
    return (
      <div style={{ fontSize: 14 }}>
        {ekranlar.map((ekran, idx) => (
          <div key={idx} style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>
              {idx + 1}. {ekran.ekran_adi}
            </h3>
            {ekran.aciklama && <p style={{ color: token.colorTextSecondary }}>{ekran.aciklama}</p>}

            {ekran.is_akisi_diyagrami?.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <h4>İş Akışı Diyagramı</h4>
                <ol>{ekran.is_akisi_diyagrami.map((adim, i) => <li key={i}>{adim}</li>)}</ol>
              </div>
            )}

            {ekran.fonksiyonel_gereksinimler?.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <h4>Fonksiyonel Gereksinimler</h4>
                <Table
                  dataSource={ekran.fonksiyonel_gereksinimler.map((fr, i) => ({ ...fr, key: i }))}
                  columns={[
                    { title: 'ID', dataIndex: 'id', key: 'id', width: 100 },
                    { title: 'Tanım', dataIndex: 'tanim', key: 'tanim' }
                  ]}
                  pagination={false}
                  size="small"
                  bordered
                />
              </div>
            )}

            {ekran.is_kurallari?.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <h4>İş Kuralları</h4>
                <ul>{ekran.is_kurallari.map((k, i) => (
                  <li key={i}><strong>{k.kural}</strong>{k.detay && ` — ${k.detay}`}</li>
                ))}</ul>
              </div>
            )}

            {ekran.kabul_kriterleri?.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <h4>Kabul Kriterleri</h4>
                <Table
                  dataSource={ekran.kabul_kriterleri.map((kr, i) => ({ ...kr, key: i }))}
                  columns={[
                    { title: 'ID', dataIndex: 'id', key: 'id', width: 100 },
                    { title: 'Kriter', dataIndex: 'kriter', key: 'kriter' }
                  ]}
                  pagination={false}
                  size="small"
                  bordered
                />
              </div>
            )}

            {ekran.validasyonlar?.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <h4>Validasyonlar</h4>
                <Table
                  dataSource={ekran.validasyonlar.map((v, i) => ({ ...v, key: i }))}
                  columns={[
                    { title: 'Alan', dataIndex: 'alan', key: 'alan', width: 150 },
                    { title: 'Kısıt', dataIndex: 'kisit', key: 'kisit' },
                    { title: 'Hata Mesajı', dataIndex: 'hata_mesaji', key: 'hata_mesaji' }
                  ]}
                  pagination={false}
                  size="small"
                  bordered
                />
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderTADocContent = (content) => {
    if (!content) return <p>İçerik bulunamadı</p>;
    const ta = content.teknik_analiz || content;

    const genel = ta.genel_tanim;
    const endpointsDict = ta.endpoint_detaylari;
    const endpointsList = ta.api_endpoints;
    const dtos = ta.dto_veri_yapilari || ta.dtos || [];
    const validasyonlar = ta.validasyon_kurallari || ta.validation_rules || [];
    const curls = ta.mock_curl_ornekleri || ta.curl_ornekleri || [];

    const hasContent = genel || endpointsDict || endpointsList?.length || dtos.length;
    if (!hasContent) {
      return <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(content, null, 2)}</pre>;
    }

    return (
      <div style={{ fontSize: 14 }}>
        {genel && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>Genel Tanım</h3>
            <p><strong>Modül:</strong> {genel.modul_adi}</p>
            <p><strong>Stack:</strong> {Array.isArray(genel.teknoloji_stack) ? genel.teknoloji_stack.join(', ') : genel.teknoloji_stack}</p>
            <p><strong>Mimari:</strong> {genel.mimari_yaklasim}</p>
          </div>
        )}

        {endpointsDict && typeof endpointsDict === 'object' && !Array.isArray(endpointsDict) && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>API Endpoints</h3>
            <Collapse items={Object.entries(endpointsDict).map(([path, ep], idx) => ({
              key: idx,
              label: <span><Tag color="blue">{ep.method || 'GET'}</Tag> {path}</span>,
              children: (
                <div>
                  <p>{ep.aciklama}</p>
                  {ep.request_body && (
                    <div><strong>Request:</strong><pre style={{ background: token.colorBgLayout, padding: 8, fontSize: 12 }}>{JSON.stringify(ep.request_body, null, 2)}</pre></div>
                  )}
                  {ep.response_success && (
                    <div><strong>Response:</strong><pre style={{ background: '#f0fff0', padding: 8, fontSize: 12 }}>{JSON.stringify(ep.response_success, null, 2)}</pre></div>
                  )}
                </div>
              )
            }))} />
          </div>
        )}

        {endpointsList?.length > 0 && !endpointsDict && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>API Endpoints</h3>
            <Collapse items={endpointsList.map((ep, idx) => ({
              key: idx,
              label: <span><Tag color="blue">{ep.method || ep.http_method || 'GET'}</Tag> {ep.endpoint || ep.path || ep.url}</span>,
              children: (
                <div>
                  <p>{ep.aciklama || ep.description}</p>
                  {ep.request_body && (
                    <div><strong>Request:</strong><pre style={{ background: token.colorBgLayout, padding: 8, fontSize: 12 }}>{JSON.stringify(ep.request_body, null, 2)}</pre></div>
                  )}
                  {(ep.response_success || ep.response) && (
                    <div><strong>Response:</strong><pre style={{ background: '#f0fff0', padding: 8, fontSize: 12 }}>{JSON.stringify(ep.response_success || ep.response, null, 2)}</pre></div>
                  )}
                </div>
              )
            }))} />
          </div>
        )}

        {dtos.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>DTO Yapıları</h3>
            {dtos.map((dto, idx) => (
              <div key={idx} style={{ marginBottom: 16 }}>
                <h4>{dto.dto_adi || dto.dto_name || dto.name}</h4>
                <p style={{ color: token.colorTextSecondary }}>{dto.aciklama || dto.description}</p>
                <Table
                  dataSource={(dto.fields || []).map((f, i) => ({ ...f, key: i }))}
                  columns={[
                    { title: 'Alan', dataIndex: f => f.field || f.field_name || f.name, key: 'field',
                      render: (_, record) => record.field || record.field_name || record.name },
                    { title: 'Tip', dataIndex: f => f.tip || f.data_type || f.type, key: 'type',
                      render: (_, record) => <Tag>{record.tip || record.data_type || record.type}</Tag> },
                    { title: 'Validasyon', dataIndex: 'validasyon', key: 'val',
                      render: (_, record) => record.validasyon || record.validation || '' }
                  ]}
                  pagination={false}
                  size="small"
                  bordered
                />
              </div>
            ))}
          </div>
        )}

        {validasyonlar.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>Validasyon Kuralları</h3>
            <ul>{validasyonlar.map((v, i) => (
              <li key={i}><strong>{v.id}</strong> [{v.field}]: {v.kural || v.rule}</li>
            ))}</ul>
          </div>
        )}

        {curls.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ borderBottom: '2px solid #1890ff', paddingBottom: 8 }}>cURL Ornekleri</h3>
            {curls.map((c, i) => (
              <div key={i} style={{ marginBottom: 12 }}>
                <strong>{c.endpoint_adi || c.endpoint_name}</strong>
                <pre style={{ background: token.colorBgLayout, padding: 8, fontSize: 12 }}>{c.curl}</pre>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderTCDocContent = (content) => {
    if (!content) return <p>İçerik bulunamadı</p>;
    const testCases = content.test_cases || [];
    if (testCases.length === 0) {
      return <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(content, null, 2)}</pre>;
    }

    const columns = [
      { title: 'ID', dataIndex: 'test_case_id', key: 'test_case_id', width: 110, fixed: 'left' },
      { title: 'Öncelik', dataIndex: 'priority', key: 'priority', width: 90,
        render: (val) => {
          const colors = { High: 'red', Medium: 'orange', Low: 'green', Yüksek: 'red', Orta: 'orange', Düşük: 'green' };
          return <Tag color={colors[val] || 'default'}>{val}</Tag>;
        }
      },
      { title: 'Test Alanı', dataIndex: 'test_area', key: 'test_area', width: 140 },
      { title: 'Test Case', dataIndex: 'testcase', key: 'testcase', width: 250 },
      { title: 'Test Adımları', dataIndex: 'test_steps', key: 'test_steps', width: 300,
        render: (val) => <div style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{val}</div>
      },
      { title: 'Beklenen Sonuç', dataIndex: 'expected_result', key: 'expected_result', width: 250 },
      { title: 'Test Verisi', dataIndex: 'test_data', key: 'test_data', width: 180 }
    ];

    return (
      <Table
        dataSource={testCases.map((tc, i) => ({ ...tc, key: i }))}
        columns={columns}
        pagination={{ pageSize: 20, showSizeChanger: true }}
        scroll={{ x: 1400 }}
        size="small"
        bordered
      />
    );
  };

  const renderDocContent = (docType, content) => {
    if (!docType) return null;
    const type = docType.toLowerCase();
    if (type === 'ba') return renderBADocContent(content);
    if (type === 'ta') return renderTADocContent(content);
    if (type === 'tc') return renderTCDocContent(content);
    return <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(content, null, 2)}</pre>;
  };

  const getCurrentStepIndex = () => {
    return WORKFLOW_STEPS.findIndex(s => s.key === currentStepKey);
  };

  // Render content based on current step
  const renderStepContent = () => {
    switch (currentStepKey) {
      case 'upload':
        return renderUploadStep();
      case 'ba_gen':
      case 'ta_gen':
      case 'tc_gen':
        return renderGenerationStep(currentStepKey);
      case 'ba_review':
      case 'ta_review':
      case 'tc_review':
        return renderReviewStep(currentStepKey);
      case 'ba_qa':
      case 'ta_qa':
      case 'tc_qa':
        return renderQAStep(currentStepKey);
      case 'figma_upload':
        return renderFigmaStep();
      case 'done':
        return renderDoneStep();
      default:
        return null;
    }
  };

  const renderUploadStep = () => (
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
            showSearch
            optionFilterProp="label"
            options={projects?.map(p => ({ label: p.name, value: p.id }))}
            loading={!projects}
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

        <Form.Item label="Dosya Yükle">
          <Upload
            beforeUpload={handleFileUpload}
            accept=".docx,.pdf,.txt"
            maxCount={1}
            fileList={uploadedFile ? [uploadedFile] : []}
            onRemove={() => setUploadedFile(null)}
          >
            <Button icon={<UploadOutlined />}>BRD Dosyası Yükle</Button>
          </Upload>
        </Form.Item>

        <Form.Item
          label="Figma Tasarım URL (Opsiyonel)"
          name="figma_url"
        >
          <Input placeholder="https://figma.com/design/..." />
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
          <Button
            type="primary"
            htmlType="submit"
            loading={startMutation.isPending}
            icon={<RocketOutlined />}
            size="large"
          >
            Pipeline Başlat
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );

  const renderGenerationStep = (stage) => {
    // Show spinner if backend is running (any stage — only one runs at a time)
    const isRunning = pipelineStatus?.status === 'running';
    const isFailed = pipelineStatus?.status === 'failed';
    const label = stage.replace('_gen', '').toUpperCase();

    return (
      <Card title={`${label} Doküman Üretimi`}>
        {isFailed ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="Üretim Başarısız"
              description={`${label} dokümanı üretilirken bir hata oluştu. Tekrar deneyin.`}
              type="error"
              showIcon
              icon={<CloseCircleOutlined />}
            />
            <Button
              type="primary"
              size="large"
              icon={<ReloadOutlined />}
              onClick={() => handleExecuteStage(stage)}
              loading={executeStageMutation.isPending}
            >
              Tekrar Dene
            </Button>
          </Space>
        ) : isRunning ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Spin size="large" />
            <Alert
              message="Üretiliyor..."
              description={`${label} dokümanı Claude tarafından üretiliyor. Bu işlem 30-60 saniye sürebilir.`}
              type="info"
              showIcon
            />
          </Space>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="Hazır"
              description={`${label} dokümanını üretmek için butona tıklayın.`}
              type="info"
              showIcon
            />
            <Button
              type="primary"
              size="large"
              icon={<RocketOutlined />}
              onClick={() => handleExecuteStage(stage)}
              loading={executeStageMutation.isPending}
            >
              {label} Üret
            </Button>
          </Space>
        )}
      </Card>
    );
  };

  const renderReviewStep = (stage) => {
    const docType = stage.replace('_review', '').toUpperCase();

    return (
      <Card title={`${docType} İnceleme ve Düzenleme`}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            message="İnceleme Zamanı"
            description={`${docType} dokümanını aşağıda inceleyebilir ve gerekirse düzenleyebilirsiniz. Onayladığınızda QA değerlendirmesine geçilecek.`}
            type="success"
            showIcon
            icon={<EditOutlined />}
          />

          <div style={{
            border: `1px solid ${token.colorBorder}`,
            borderRadius: 8,
            padding: 16,
            maxHeight: 500,
            overflow: 'auto',
            background: token.colorBgContainer
          }}>
            {renderDocContent(docType, editedContent || checkpointData)}
          </div>

          <Space>
            <Button
              icon={<EyeOutlined />}
              onClick={() => handlePreviewDocument(docType.toLowerCase(), editedContent || checkpointData)}
            >
              Önizle
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => handleDownloadDocument(docType.toLowerCase())}
            >
              İndir ({docType === 'TC' ? 'XLSX' : 'DOCX'})
            </Button>
            <Button
              type="primary"
              size="large"
              icon={<ArrowRightOutlined />}
              onClick={handleApproveAndContinue}
              loading={saveCheckpointMutation.isPending}
            >
              Onayla ve QA'ya Geç
            </Button>
          </Space>
        </Space>
      </Card>
    );
  };

  const renderQAStep = (stage) => {
    const docType = stage.replace('_qa', '').toUpperCase();

    return (
      <Card title={`${docType} Kalite Değerlendirmesi`}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {!qaResult ? (
            <>
              <Alert
                message="QA Değerlendirmesi"
                description={`${docType} dokümanı Gemini tarafından değerlendirilecek. Geçme skoru: 60+`}
                type="info"
                showIcon
              />
              <Space>
                <Button
                  type="primary"
                  size="large"
                  onClick={() => handleEvaluateQA(false)}
                  loading={evaluateQAMutation.isPending}
                >
                  QA Değerlendirmesi Yap
                </Button>
                <Button
                  size="large"
                  onClick={() => handleEvaluateQA(true)}
                  loading={evaluateQAMutation.isPending}
                >
                  QA'yı Atla (Force Pass)
                </Button>
              </Space>
            </>
          ) : (
            <>
              <Alert
                message={qaResult.passed ? '✅ QA Başarılı!' : '⚠️ QA Başarısız'}
                description={`Genel Puan: ${qaResult.score || qaResult.genel_puan || 0}/100`}
                type={qaResult.passed || qaResult.gecti_mi ? 'success' : 'warning'}
                showIcon
                icon={qaResult.passed || qaResult.gecti_mi ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
              />

              <div>
                <p><strong>Genel Skor:</strong></p>
                <Progress
                  percent={qaResult.score || qaResult.genel_puan || 0}
                  strokeColor={(qaResult.score || qaResult.genel_puan || 0) >= 60 ? '#52c41a' : '#f5222d'}
                />
              </div>

              {/* Detailed criteria scores */}
              {qaResult.skorlar && qaResult.skorlar.length > 0 && (
                <div>
                  <p><strong>Kriter Detayları:</strong></p>
                  {qaResult.skorlar.map((kriter, i) => (
                    <div key={i} style={{ marginBottom: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span><strong>{kriter.kriter}:</strong></span>
                        <span>{kriter.puan}/10</span>
                      </div>
                      <Progress
                        percent={(kriter.puan / 10) * 100}
                        strokeColor={kriter.puan >= 6 ? '#52c41a' : '#f5222d'}
                        showInfo={false}
                        size="small"
                      />
                      <div style={{ fontSize: '12px', color: token.colorTextSecondary, marginTop: 4 }}>
                        {typeof kriter.aciklama === 'string' ? kriter.aciklama : JSON.stringify(kriter.aciklama)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* General assessment */}
              {qaResult.genel_degerlendirme && (
                <div>
                  <p><strong>Genel Değerlendirme:</strong></p>
                  <p style={{ whiteSpace: 'pre-wrap' }}>{qaResult.genel_degerlendirme}</p>
                </div>
              )}

              {/* Strengths */}
              {qaResult.guclu_yanlar && qaResult.guclu_yanlar.length > 0 && (
                <div>
                  <p><strong>✅ Güçlü Yanlar:</strong></p>
                  <ul>
                    {qaResult.guclu_yanlar.map((item, i) => (
                      <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Critical issues */}
              {qaResult.kritik_eksikler && qaResult.kritik_eksikler.length > 0 && (
                <div>
                  <p><strong>❌ Kritik Eksikler:</strong></p>
                  <ul>
                    {qaResult.kritik_eksikler.map((item, i) => (
                      <li key={i} style={{ color: '#f5222d' }}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Improvement suggestions */}
              {qaResult.iyilestirme_onerileri && qaResult.iyilestirme_onerileri.length > 0 && (
                <div>
                  <p><strong>💡 İyileştirme Önerileri:</strong></p>
                  <ol>
                    {qaResult.iyilestirme_onerileri.map((item, i) => (
                      <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Statistics */}
              {qaResult.istatistikler && (
                <div>
                  <p><strong>📊 İstatistikler:</strong></p>
                  <div style={{ fontSize: '12px' }}>
                    {Object.entries(qaResult.istatistikler).map(([key, value]) => (
                      <div key={key}>• {key}: {typeof value === 'object' ? JSON.stringify(value) : value}</div>
                    ))}
                  </div>
                </div>
              )}

              <Space>
                {qaResult.passed || qaResult.gecti_mi ? (
                  <Button
                    type="primary"
                    size="large"
                    icon={<ArrowRightOutlined />}
                    onClick={() => handleEvaluateQA(true)} // Force pass to trigger backend transition
                    loading={evaluateQAMutation.isPending}
                  >
                    Sonraki Aşamaya Geç
                  </Button>
                ) : (
                  <>
                    <Button
                      icon={<ReloadOutlined />}
                      onClick={() => handleRegenerate(stage)}
                      loading={executeStageMutation.isPending}
                    >
                      🔄 Revize Et (Yeniden Üret)
                    </Button>
                    <Button onClick={() => setCurrentStepKey(stage.replace('_qa', '_review'))}>
                      Geri Dön ve Düzenle
                    </Button>
                    <Button type="primary" onClick={() => handleEvaluateQA(true)}>
                      Yine de Devam Et
                    </Button>
                  </>
                )}
              </Space>
            </>
          )}
        </Space>
      </Card>
    );
  };

  const renderFigmaStep = () => {
    const handleSkipFigma = async () => {
      console.log('[Skip Figma] Starting TC generation, runId:', pipelineRunId);

      if (!pipelineRunId) {
        message.error('Pipeline ID bulunamadı');
        return;
      }

      // Navigate to tc_gen IMMEDIATELY — don't wait for API response.
      // The useEffect forward-only guard prevents stale poll data from bouncing back.
      setCurrentStepKey('tc_gen');

      try {
        await executeStageMutation.mutateAsync({
          runId: pipelineRunId,
          stage: 'tc_gen'
        });
        console.log('[Skip Figma] TC generation started');
        message.success('TC üretimi başlatıldı');
      } catch (error) {
        message.error('TC üretimi başlatılamadı: ' + (error.message || 'Bilinmeyen hata'));
        console.error('[Skip Figma] Error:', error.response?.data || error);
      }
    };

    return (
      <Card title="Figma Tasarım Analizi (Opsiyonel)">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="Figma Tasarımları"
            description="TC üretimi için Figma tasarımlarını analiz edebilirsiniz. Atlamak isterseniz direkt TC üretimine geçin."
            type="info"
            showIcon
          />
          <Space>
            <Button
              type="primary"
              onClick={handleSkipFigma}
              loading={executeStageMutation.isPending}
            >
              Figma Olmadan Devam Et
            </Button>
          </Space>
        </Space>
      </Card>
    );
  };

  const renderDoneStep = () => (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card
        title="Pipeline Tamamlandı!"
        extra={<CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />}
      >
        <Alert
          message="Başarılı"
          description="Tüm dokümanlar başarıyla oluşturuldu. Aşağıdan dokümanları inceleyebilir ve kütüphaneye kaydedebilirsiniz."
          type="success"
          showIcon
        />

        <Divider />

        <Button onClick={handleReset} style={{ marginTop: 16 }}>
          Yeni Pipeline
        </Button>
      </Card>

      {pipelineResults && (
        <Card title="Üretilen Dokümanlar">
          {Object.entries(pipelineResults)
            .filter(([key]) => ['ba', 'ta', 'tc'].includes(key))
            .map(([docType, content]) => (
              <Card
                key={docType}
                type="inner"
                title={docType.toUpperCase()}
                style={{ marginBottom: 16 }}
                extra={
                  <Space>
                    <Button
                      icon={<EyeOutlined />}
                      onClick={() => handlePreviewDocument(docType, content)}
                    >
                      Önizle
                    </Button>
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={() => handleDownloadDocument(docType)}
                    >
                      İndir ({docType === 'tc' ? 'XLSX' : 'DOCX'})
                    </Button>
                    <Button
                      icon={<SaveOutlined />}
                      onClick={() => handleSaveDocument(docType, content)}
                      loading={createDocMutation.isPending}
                    >
                      Kütüphaneye Kaydet
                    </Button>
                  </Space>
                }
              >
                <div style={{
                  padding: 16,
                  borderRadius: 8,
                  maxHeight: 400,
                  overflow: 'auto'
                }}>
                  {renderDocContent(docType, content)}
                </div>

                {pipelineResults.scores && pipelineResults.scores[docType] > 0 && (
                  <div style={{ marginTop: 16 }}>
                    <p><strong>QA Skoru:</strong></p>
                    <Progress
                      percent={pipelineResults.scores[docType]}
                      strokeColor={pipelineResults.scores[docType] >= 60 ? '#52c41a' : '#f5222d'}
                    />
                  </div>
                )}
              </Card>
            ))}
        </Card>
      )}
    </Space>
  );

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>BRD Pipeline</h1>

      <Card style={{ marginBottom: 24 }}>
        <Steps
          current={getCurrentStepIndex()}
          items={WORKFLOW_STEPS.map(step => ({
            title: step.title,
            status: step.key === currentStepKey ? 'process' :
                   WORKFLOW_STEPS.indexOf(step) < getCurrentStepIndex() ? 'finish' : 'wait'
          }))}
          size="small"
        />
      </Card>

      {renderStepContent()}

      {/* Document Preview Modal */}
      <Modal
        title={`${previewModal.docType} Doküman Önizleme`}
        open={previewModal.visible}
        onCancel={() => setPreviewModal({ visible: false, docType: null, content: null })}
        width={1000}
        footer={[
          <Button
            key="download"
            type="primary"
            icon={<DownloadOutlined />}
            onClick={() => {
              const docType = previewModal.docType.toLowerCase();
              handleDownloadDocument(docType);
            }}
          >
            İndir ({previewModal.docType === 'TC' ? 'XLSX' : 'DOCX'})
          </Button>,
          <Button
            key="close"
            onClick={() => setPreviewModal({ visible: false, docType: null, content: null })}
          >
            Kapat
          </Button>
        ]}
      >
        <div style={{
          padding: 16,
          borderRadius: 8,
          maxHeight: 600,
          overflow: 'auto'
        }}>
          {renderDocContent(previewModal.docType, previewModal.content)}
        </div>
      </Modal>
    </div>
  );
}
