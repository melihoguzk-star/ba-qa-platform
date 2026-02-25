/**
 * BRD Pipeline — Orchestrator with Wizard + Kanban Board
 */
import { useState, useEffect } from 'react';
import { Modal, Button, message, theme } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
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
import PipelineWizard from '../components/pipeline/PipelineWizard';
import PipelineKanbanBoard from '../components/pipeline/PipelineKanbanBoard';
import PipelineDetailDrawer from '../components/pipeline/PipelineDetailDrawer';
import { renderDocContent } from '../components/pipeline/PipelineDocRenderer';

// Step definitions matching backend workflow
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
  // Phase: wizard → board
  const [phase, setPhase] = useState('wizard');
  const [pipelineRunId, setPipelineRunId] = useState(null);
  const [currentStepKey, setCurrentStepKey] = useState('upload');
  const [editedContent, setEditedContent] = useState(null);
  const [qaResult, setQaResult] = useState(null);
  const [wizardConfig, setWizardConfig] = useState(null);
  const [drawerState, setDrawerState] = useState({ open: false, mode: null, docType: null });
  const [previewModal, setPreviewModal] = useState({ visible: false, docType: null, content: null });

  // API hooks
  const { data: projects } = useProjects();
  const startMutation = useStartPipeline();
  const executeStageMutation = useExecuteStage();
  const evaluateQAMutation = useEvaluateQA();
  const saveCheckpointMutation = useSaveCheckpoint();
  const createDocMutation = useCreateDocument();
  const { token } = theme.useToken();

  const { data: pipelineStatus } = usePipelineStatus(pipelineRunId, {
    enabled: !!pipelineRunId,
    refetchInterval: 2000,
    staleTime: 0,
  });

  const currentStageForCheckpoint = currentStepKey.replace('_review', '_gen');
  const { data: checkpointData, refetch: refetchCheckpoint } = useCheckpoint(
    pipelineRunId,
    currentStageForCheckpoint,
    { enabled: !!pipelineRunId && currentStepKey.includes('_review') }
  );

  const { data: pipelineResults } = usePipelineResults(pipelineRunId, {
    enabled: !!pipelineRunId && currentStepKey === 'done'
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

  // Sync currentStepKey with backend — forward only
  useEffect(() => {
    if (!pipelineStatus?.current_stage) return;

    const backendStage = pipelineStatus.current_stage;

    if (pipelineStatus.status === 'completed' && currentStepKey !== 'done') {
      console.log(`[BRD Pipeline] Pipeline completed, navigating to done`);
      setCurrentStepKey('done');
      return;
    }

    if (backendStage !== currentStepKey && pipelineStatus.status === 'waiting_approval') {
      const backendIdx = WORKFLOW_STEPS.findIndex(s => s.key === backendStage);
      const currentIdx = WORKFLOW_STEPS.findIndex(s => s.key === currentStepKey);

      if (backendIdx <= currentIdx) return;

      console.log(`[BRD Pipeline] Stage transition: ${currentStepKey} → ${backendStage}`);
      setCurrentStepKey(backendStage);

      if (backendStage.includes('_review')) {
        setTimeout(() => refetchCheckpoint(), 500);
      }
    }
  }, [pipelineStatus, currentStepKey, refetchCheckpoint]);

  // Load checkpoint data into editor when entering review stage
  useEffect(() => {
    if (checkpointData && currentStepKey.includes('_review')) {
      setEditedContent(checkpointData);
    }
  }, [checkpointData, currentStepKey]);

  // --- Handlers ---

  const handleWizardComplete = async (config) => {
    setWizardConfig(config);
    try {
      const result = await startMutation.mutateAsync({
        project_id: config.project_id,
        project_name: config.project_name,
        brd_content: config.brd_content,
        stages: config.stages,
        figma_url: config.figma_url
      });

      setPipelineRunId(result.pipeline_run_id);
      setCurrentStepKey('ba_gen');
      setPhase('board');
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
      message.success(`${stage.replace('_gen', '').toUpperCase()} üretimi başlatıldı`);
    } catch (error) {
      message.error(`Üretilemedi: ${error.message}`);
    }
  };

  const handleApproveAndContinue = async () => {
    const currentStage = currentStepKey.replace('_review', '');

    if (editedContent) {
      try {
        await saveCheckpointMutation.mutateAsync({
          runId: pipelineRunId,
          stage: `${currentStage}_gen`,
          data: editedContent
        });
        message.success('Değişiklikler kaydedildi');
      } catch {
        message.error('Kayıt hatası');
        return;
      }
    }

    const qaStage = `${currentStage}_qa`;
    console.log(`[BRD Pipeline] Moving to QA stage: ${qaStage}`);
    setCurrentStepKey(qaStage);
    setQaResult(null);
    setDrawerState({ open: true, mode: 'qa', docType: currentStage });
  };

  const handleEvaluateQA = async (forcePass = false) => {
    const content = editedContent || checkpointData;
    if (!content) {
      message.error('İçerik bulunamadı');
      return;
    }

    try {
      const result = await evaluateQAMutation.mutateAsync({
        runId: pipelineRunId,
        stage: currentStepKey,
        content: content,
        force_pass: forcePass
      });

      setQaResult(result);

      if (result.passed) {
        message.success(`QA başarılı! Skor: ${result.score}`);
        if (forcePass) {
          console.log(`[BRD Pipeline] Force pass - backend will transition`);
          setDrawerState({ open: false, mode: null, docType: null });
        }
      } else {
        message.warning(`QA skoru düşük: ${result.score}. Düzenleyip tekrar deneyin veya zorla geçin.`);
      }
    } catch {
      message.error('QA değerlendirmesi başarısız');
    }
  };

  const handleForcePass = async () => {
    await handleEvaluateQA(true);
  };

  const handleRegenerate = async () => {
    if (!qaResult) {
      message.error('QA sonucu bulunamadı');
      return;
    }

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
    if (qaResult.skorlar?.length > 0) {
      feedback += `\nKriter Skorları:\n`;
      qaResult.skorlar.forEach(kriter => {
        if (kriter.puan < 6) {
          feedback += `- ${kriter.kriter}: ${kriter.puan}/10 - ${kriter.aciklama}\n`;
        }
      });
    }

    const stagePrefix = currentStepKey.replace('_qa', '');
    const genStage = `${stagePrefix}_gen`;

    try {
      message.loading(`${stagePrefix.toUpperCase()} yeniden üretiliyor...`, 0);
      await executeStageMutation.mutateAsync({
        runId: pipelineRunId,
        stage: genStage,
        feedback: feedback
      });

      setQaResult(null);
      setCurrentStepKey(genStage);
      setDrawerState({ open: false, mode: null, docType: null });
      message.destroy();
      message.success('Yeniden üretim başlatıldı');
    } catch {
      message.destroy();
      message.error('Yeniden üretim başlatılamadı');
    }
  };

  const handleGoBackToReview = () => {
    const reviewStage = currentStepKey.replace('_qa', '_review');
    setCurrentStepKey(reviewStage);
    setQaResult(null);
    setDrawerState({ open: true, mode: 'review', docType: currentStepKey.replace('_qa', '') });
  };

  const handleDownloadDocument = async (docType) => {
    try {
      message.loading(`${docType.toUpperCase()} indiriliyor...`, 0);
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
    setPreviewModal({ visible: true, docType: docType.toUpperCase(), content });
  };

  const handleSaveDocument = async (docType, content) => {
    try {
      await createDocMutation.mutateAsync({
        name: `${docType.toUpperCase()} - ${new Date().toLocaleDateString()}`,
        doc_type: docType,
        project_id: wizardConfig?.project_id,
        content_json: content
      });
      message.success(`${docType.toUpperCase()} dokümanı kütüphaneye kaydedildi`);
    } catch {
      message.error('Doküman kaydedilemedi');
    }
  };

  const handleReset = () => {
    setPhase('wizard');
    setPipelineRunId(null);
    setCurrentStepKey('upload');
    setEditedContent(null);
    setQaResult(null);
    setWizardConfig(null);
    setDrawerState({ open: false, mode: null, docType: null });
    setPreviewModal({ visible: false, docType: null, content: null });
  };

  // Card action dispatcher — third arg for extra data (e.g. figma URL)
  const handleStepAction = async (action, stepKey, extraData) => {
    if (action === 'execute') {
      // Handle figma skip — no URL, go straight to tc_gen
      if (stepKey === 'figma_upload') {
        setCurrentStepKey('tc_gen');
        handleExecuteStage('tc_gen');
        return;
      }
      handleExecuteStage(stepKey);
    } else if (action === 'figma_with_url') {
      // Save Figma URL as checkpoint, then proceed to tc_gen
      try {
        await saveCheckpointMutation.mutateAsync({
          runId: pipelineRunId,
          stage: 'figma_url',
          data: { url: extraData }
        });
        message.success('Figma URL kaydedildi');
        setCurrentStepKey('tc_gen');
        handleExecuteStage('tc_gen');
      } catch {
        message.error('Figma URL kaydedilemedi');
      }
    } else if (action === 'openDrawer') {
      if (stepKey.includes('_review')) {
        const docType = stepKey.replace('_review', '');
        setDrawerState({ open: true, mode: 'review', docType });
      } else if (stepKey.includes('_qa')) {
        const docType = stepKey.replace('_qa', '');
        setDrawerState({ open: true, mode: 'qa', docType });
      }
    }
  };

  // --- Render ---

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>BRD Pipeline</h1>

      {phase === 'wizard' ? (
        <PipelineWizard
          onComplete={handleWizardComplete}
          projects={projects}
          loading={startMutation.isPending}
        />
      ) : (
        <>
          <PipelineKanbanBoard
            pipelineStatus={pipelineStatus}
            pipelineResults={pipelineResults}
            currentStep={currentStepKey}
            onStepAction={handleStepAction}
            onReset={handleReset}
            onDownload={handleDownloadDocument}
            onPreview={handlePreviewDocument}
            onSaveDocument={handleSaveDocument}
            token={token}
            createDocLoading={createDocMutation.isPending}
            figmaLoading={saveCheckpointMutation.isPending || executeStageMutation.isPending}
          />

          <PipelineDetailDrawer
            open={drawerState.open}
            onClose={() => setDrawerState({ open: false, mode: null, docType: null })}
            mode={drawerState.mode}
            docType={drawerState.docType}
            content={editedContent || checkpointData}
            qaResult={qaResult}
            token={token}
            onApprove={handleApproveAndContinue}
            onEvaluateQA={handleEvaluateQA}
            onRegenerate={handleRegenerate}
            onForcePass={handleForcePass}
            onDownload={handleDownloadDocument}
            onPreview={handlePreviewDocument}
            onGoBackToReview={handleGoBackToReview}
            loading={{
              approve: saveCheckpointMutation.isPending,
              qa: evaluateQAMutation.isPending,
              regenerate: executeStageMutation.isPending
            }}
          />

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
                onClick={() => handleDownloadDocument(previewModal.docType?.toLowerCase())}
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
            <div style={{ padding: 16, borderRadius: 8, maxHeight: 600, overflow: 'auto' }}>
              {renderDocContent(previewModal.docType, previewModal.content, token)}
            </div>
          </Modal>
        </>
      )}
    </div>
  );
}
