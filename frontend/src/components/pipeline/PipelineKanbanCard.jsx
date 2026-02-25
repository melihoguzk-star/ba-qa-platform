/**
 * PipelineKanbanCard — Individual step card for the Kanban board
 */
import { useState, useEffect, useRef } from 'react';
import { Card, Tag, Button, Typography } from 'antd';
import {
  ClockCircleOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EditOutlined,
  RocketOutlined,
  ReloadOutlined,
  EyeOutlined
} from '@ant-design/icons';

const { Text } = Typography;

const STEP_LABELS = {
  upload: 'BRD Yükleme',
  ba_gen: 'BA Üretim',
  ba_review: 'BA İnceleme',
  ba_qa: 'BA QA',
  ta_gen: 'TA Üretim',
  ta_review: 'TA İnceleme',
  ta_qa: 'TA QA',
  figma_upload: 'Figma',
  tc_gen: 'TC Üretim',
  tc_review: 'TC İnceleme',
  tc_qa: 'TC QA',
  done: 'Tamamlandı'
};

const STATUS_CONFIG = {
  pending: {
    borderColor: null, // will use token.colorBorder
    icon: <ClockCircleOutlined />,
    tagColor: 'default',
    tagText: 'Bekliyor',
    cssClass: ''
  },
  running: {
    borderColor: null, // will use token.colorPrimary
    icon: <LoadingOutlined spin />,
    tagColor: 'processing',
    tagText: 'Çalışıyor',
    cssClass: 'pipeline-card-running'
  },
  completed: {
    borderColor: '#52c41a',
    icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
    tagColor: 'success',
    tagText: 'Tamamlandı',
    cssClass: ''
  },
  failed: {
    borderColor: '#f5222d',
    icon: <CloseCircleOutlined style={{ color: '#f5222d' }} />,
    tagColor: 'error',
    tagText: 'Başarısız',
    cssClass: ''
  },
  waiting_approval: {
    borderColor: '#faad14',
    icon: <EditOutlined style={{ color: '#faad14' }} />,
    tagColor: 'warning',
    tagText: 'İnceleme Bekliyor',
    cssClass: 'pipeline-card-attention'
  }
};

function formatElapsed(seconds) {
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

export default function PipelineKanbanCard({ step, status, isActive, stageData, elapsed: elapsedProp, onAction, token }) {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (status === 'running' && stageData?.started_at) {
      const startTime = new Date(stageData.started_at).getTime();

      const tick = () => {
        const now = Date.now();
        setElapsed(Math.floor((now - startTime) / 1000));
      };
      tick();
      intervalRef.current = setInterval(tick, 1000);

      return () => clearInterval(intervalRef.current);
    } else if (status === 'running') {
      // No started_at, use simple counter
      setElapsed(0);
      intervalRef.current = setInterval(() => {
        setElapsed(prev => prev + 1);
      }, 1000);
      return () => clearInterval(intervalRef.current);
    } else {
      setElapsed(0);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  }, [status, stageData?.started_at]);

  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  const borderColor = config.borderColor || (status === 'running' ? token.colorPrimary : token.colorBorder);
  const isGenStep = step.endsWith('_gen');
  const isReviewStep = step.endsWith('_review');
  const isQAStep = step.endsWith('_qa');

  const renderAction = () => {
    switch (status) {
      case 'pending':
      case 'waiting_approval':
        // Gen steps: show "Üret" when active
        if (isActive && isGenStep) {
          return (
            <Button
              type="primary"
              size="small"
              icon={<RocketOutlined />}
              onClick={() => onAction('execute', step)}
            >
              Üret
            </Button>
          );
        }
        // Review/QA steps: show "İncele" when waiting_approval
        if (isActive && status === 'waiting_approval' && (isReviewStep || isQAStep)) {
          return (
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onAction('openDrawer', step)}
            >
              İncele
            </Button>
          );
        }
        return null;

      case 'running':
        return (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <LoadingOutlined spin style={{ color: token.colorPrimary }} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {formatElapsed(elapsed)}
            </Text>
          </div>
        );

      case 'completed':
        return (
          <Text type="secondary" style={{ fontSize: 12 }}>
            <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 4 }} />
            {stageData?.completed_at ? 'Tamamlandı' : 'Bitti'}
          </Text>
        );

      case 'failed':
        return (
          <Button
            danger
            size="small"
            icon={<ReloadOutlined />}
            onClick={() => onAction('execute', step)}
          >
            Tekrar Dene
          </Button>
        );

      default:
        return null;
    }
  };

  return (
    <Card
      size="small"
      className={config.cssClass}
      style={{
        width: 200,
        borderLeft: `4px solid ${borderColor}`,
        opacity: status === 'pending' && !isActive ? 0.6 : 1,
        transition: 'all 0.3s ease'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <Text strong style={{ fontSize: 13 }}>
          {config.icon} {STEP_LABELS[step] || step}
        </Text>
      </div>
      <div style={{ marginBottom: 8 }}>
        <Tag color={config.tagColor} style={{ fontSize: 11 }}>{config.tagText}</Tag>
      </div>
      <div>{renderAction()}</div>
    </Card>
  );
}
