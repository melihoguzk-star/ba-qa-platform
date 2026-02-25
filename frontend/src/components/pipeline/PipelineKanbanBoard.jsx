/**
 * PipelineKanbanBoard — Board orchestration: progress bar + 3 lanes + Figma bridge + completion banner
 */
import { useState } from 'react';
import { Card, Progress, Tag, Button, Space, Divider, Typography, Input } from 'antd';
import {
  RocketOutlined,
  ThunderboltOutlined,
  EditOutlined,
  SafetyCertificateOutlined,
  CheckCircleOutlined,
  DownloadOutlined,
  EyeOutlined,
  SaveOutlined,
  ReloadOutlined,
  PictureOutlined,
  ArrowRightOutlined,
  LinkOutlined
} from '@ant-design/icons';
import PipelineLane from './PipelineLane';
import PipelineKanbanCard from './PipelineKanbanCard';
import { renderDocContent } from './PipelineDocRenderer';

const { Text } = Typography;

// Workflow steps — canonical order
const WORKFLOW_STEPS = [
  { key: 'upload', title: 'BRD Yükleme' },
  { key: 'ba_gen', title: 'BA Üretim' },
  { key: 'ba_review', title: 'BA İnceleme' },
  { key: 'ba_qa', title: 'BA QA' },
  { key: 'ta_gen', title: 'TA Üretim' },
  { key: 'ta_review', title: 'TA İnceleme' },
  { key: 'ta_qa', title: 'TA QA' },
  { key: 'figma_upload', title: 'Figma' },
  { key: 'tc_gen', title: 'TC Üretim' },
  { key: 'tc_review', title: 'TC İnceleme' },
  { key: 'tc_qa', title: 'TC QA' },
  { key: 'done', title: 'Tamamlandı' }
];

// 3 lanes — Figma is NOT in any lane, it's a separate bridge section
const LANE_CONFIG = [
  {
    title: 'Üretim',
    icon: <ThunderboltOutlined />,
    color: '#722ed1',
    steps: ['ba_gen', 'ta_gen', 'tc_gen']
  },
  {
    title: 'İnceleme',
    icon: <EditOutlined />,
    color: '#faad14',
    steps: ['ba_review', 'ta_review', 'tc_review']
  },
  {
    title: 'Kalite',
    icon: <SafetyCertificateOutlined />,
    color: '#52c41a',
    steps: ['ba_qa', 'ta_qa', 'tc_qa']
  }
];

function getStepStatus(stepKey, currentStepKey, pipelineStatus) {
  const stepIndex = WORKFLOW_STEPS.findIndex(s => s.key === stepKey);
  const currentIndex = WORKFLOW_STEPS.findIndex(s => s.key === currentStepKey);

  if (stepIndex < currentIndex) return 'completed';
  if (stepKey === currentStepKey) {
    if (pipelineStatus?.status === 'running') return 'running';
    if (pipelineStatus?.status === 'failed') return 'failed';
    if (pipelineStatus?.status === 'waiting_approval') return 'waiting_approval';
    return 'pending';
  }
  return 'pending';
}

// Figma step status helper
function getFigmaStatus(currentStepKey) {
  const figmaIdx = WORKFLOW_STEPS.findIndex(s => s.key === 'figma_upload');
  const currentIdx = WORKFLOW_STEPS.findIndex(s => s.key === currentStepKey);
  if (currentIdx > figmaIdx) return 'completed';
  if (currentStepKey === 'figma_upload') return 'active';
  return 'pending';
}

// Figma Bridge — inline section between TA QA and TC gen
function FigmaBridge({ figmaStatus, token, onStepAction, figmaLoading }) {
  const [figmaUrl, setFigmaUrl] = useState('');

  const handleFigmaSubmit = () => {
    onStepAction('figma_with_url', 'figma_upload', figmaUrl.trim());
  };

  const handleSkip = () => {
    onStepAction('execute', 'figma_upload');
  };

  return (
    <div style={{
      padding: '16px 20px',
      borderRadius: 8,
      border: `1px solid ${figmaStatus === 'active' ? '#722ed1' : token.colorBorder}`,
      background: figmaStatus === 'active'
        ? (token.colorBgElevated || '#fafafa')
        : figmaStatus === 'completed' ? (token.colorSuccessBg || '#f6ffed') : 'transparent',
      opacity: figmaStatus === 'pending' ? 0.5 : 1,
      transition: 'all 0.3s ease'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: figmaStatus === 'active' ? 12 : 0 }}>
        <PictureOutlined style={{
          fontSize: 20,
          color: figmaStatus === 'completed' ? '#52c41a' : figmaStatus === 'active' ? '#722ed1' : token.colorTextDisabled
        }} />
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text strong>Figma Tasarım Analizi</Text>
            <Tag color={
              figmaStatus === 'completed' ? 'success' :
              figmaStatus === 'active' ? 'purple' : 'default'
            }>
              {figmaStatus === 'completed' ? 'Tamamlandı' :
               figmaStatus === 'active' ? 'Aktif' : 'Bekliyor'}
            </Tag>
            <Text type="secondary" style={{ fontSize: 12 }}>
              TA QA sonrası — TC Üretim öncesi
            </Text>
          </div>
        </div>
        {figmaStatus === 'completed' && (
          <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 18 }} />
        )}
      </div>

      {figmaStatus === 'active' && (
        <div>
          <Text type="secondary" style={{ fontSize: 13, display: 'block', marginBottom: 12 }}>
            Figma tasarım URL'i girerek TC üretiminde UI-specific test case'ler oluşturabilirsiniz.
          </Text>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <Input
              prefix={<LinkOutlined style={{ color: token.colorTextQuaternary }} />}
              placeholder="https://figma.com/design/..."
              value={figmaUrl}
              onChange={e => setFigmaUrl(e.target.value)}
              style={{ flex: 1 }}
              onPressEnter={() => figmaUrl.trim() && handleFigmaSubmit()}
            />
            <Button
              type="primary"
              icon={<PictureOutlined />}
              onClick={handleFigmaSubmit}
              disabled={!figmaUrl.trim()}
              loading={figmaLoading}
            >
              Figma ile Devam Et
            </Button>
            <Button
              icon={<ArrowRightOutlined />}
              onClick={handleSkip}
              loading={figmaLoading}
            >
              Figma Olmadan Devam Et
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PipelineKanbanBoard({
  pipelineStatus,
  pipelineResults,
  currentStep,
  onStepAction,
  onReset,
  onDownload,
  onPreview,
  onSaveDocument,
  token,
  createDocLoading,
  figmaLoading
}) {
  // Calculate progress
  const currentIndex = WORKFLOW_STEPS.findIndex(s => s.key === currentStep);
  const totalSteps = WORKFLOW_STEPS.length;
  const progressPct = Math.round((currentIndex / (totalSteps - 1)) * 100);
  const isCompleted = currentStep === 'done';
  const figmaStatus = getFigmaStatus(currentStep);

  // Pipeline status tag
  const getStatusTag = () => {
    if (isCompleted) return <Tag color="success">Tamamlandı</Tag>;
    if (pipelineStatus?.status === 'running') return <Tag color="processing">Çalışıyor</Tag>;
    if (pipelineStatus?.status === 'failed') return <Tag color="error">Hata</Tag>;
    if (pipelineStatus?.status === 'waiting_approval') return <Tag color="warning">Onay Bekliyor</Tag>;
    return <Tag color="default">Hazır</Tag>;
  };

  return (
    <div>
      {/* Top bar: progress + status + reset */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <Space>
            <RocketOutlined style={{ fontSize: 20, color: token.colorPrimary }} />
            <Text strong style={{ fontSize: 16 }}>Pipeline İlerlemesi</Text>
            {getStatusTag()}
          </Space>
          {isCompleted && (
            <Button icon={<ReloadOutlined />} onClick={onReset}>
              Yeni Pipeline
            </Button>
          )}
        </div>
        <Progress
          percent={progressPct}
          strokeColor={{
            '0%': token.colorPrimary,
            '100%': '#52c41a'
          }}
          status={isCompleted ? 'success' : 'active'}
        />
      </Card>

      {/* Kanban Lanes */}
      <Card style={{ marginBottom: 16 }}>
        {LANE_CONFIG.map((lane) => (
          <PipelineLane
            key={lane.title}
            title={lane.title}
            icon={lane.icon}
            color={lane.color}
          >
            {lane.steps.map(stepKey => {
              const status = getStepStatus(stepKey, currentStep, pipelineStatus);
              const isActive = stepKey === currentStep;

              return (
                <PipelineKanbanCard
                  key={stepKey}
                  step={stepKey}
                  status={status}
                  isActive={isActive}
                  stageData={pipelineStatus?.stages?.[stepKey]}
                  token={token}
                  onAction={onStepAction}
                />
              );
            })}
          </PipelineLane>
        ))}

        {/* Figma Bridge — between TA QA and TC Üretim */}
        <Divider style={{ margin: '8px 0 16px' }} />
        <FigmaBridge
          figmaStatus={figmaStatus}
          token={token}
          onStepAction={onStepAction}
          figmaLoading={figmaLoading}
        />
      </Card>

      {/* Completion Banner */}
      {isCompleted && pipelineResults && (
        <Card
          style={{
            background: `linear-gradient(135deg, ${token.colorSuccessBg || '#f6ffed'} 0%, ${token.colorBgContainer} 100%)`,
            border: `2px solid #52c41a`
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            <h2 style={{ marginTop: 12 }}>Pipeline Tamamlandı!</h2>
            <Text type="secondary">Tüm dokümanlar başarıyla oluşturuldu</Text>
          </div>

          <Divider />

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
                      onClick={() => onPreview?.(docType, content)}
                    >
                      Önizle
                    </Button>
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={() => onDownload?.(docType)}
                    >
                      İndir ({docType === 'tc' ? 'XLSX' : 'DOCX'})
                    </Button>
                    <Button
                      icon={<SaveOutlined />}
                      onClick={() => onSaveDocument?.(docType, content)}
                      loading={createDocLoading}
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
                  {renderDocContent(docType, content, token)}
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
    </div>
  );
}
