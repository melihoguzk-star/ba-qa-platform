/**
 * BA Evaluation — JIRA task-based BA document evaluation
 * Flow: JIRA Project → Tasks → Auto-fetch Document → Evaluate
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
  Input,
  Table,
  Tag,
  message
} from 'antd';
import {
  FileSearchOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  PlayCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useJIRAStatus, useJIRAProjects, useJIRATasks } from '../api/jira';
import { useDocuments } from '../api/documents';
import { useEvaluateBA } from '../api/evaluation';

const { Panel } = Collapse;

export default function BAEvaluation() {
  const [form] = Form.useForm();
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null);

  const { data: jiraStatus, isLoading: statusLoading } = useJIRAStatus();
  const { data: projects, refetch: refetchProjects } = useJIRAProjects();
  const { data: tasks, refetch: refetchTasks } = useJIRATasks(selectedProject, 'ba');
  const { data: documents } = useDocuments({ doc_type: 'brd' });
  const evaluateMutation = useEvaluateBA();

  const handleEvaluate = async (task) => {
    try {
      setSelectedTask(task);

      const requestData = {
        jira_task_key: task.key,
        reference_document_id: form.getFieldValue('reference_document_id')
      };

      const result = await evaluateMutation.mutateAsync(requestData);
      setEvaluationResult(result);
      message.success('Değerlendirme tamamlandı');
    } catch (error) {
      message.error('Değerlendirme başarısız oldu: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(evaluationResult, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ba-evaluation-${selectedTask?.key}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setEvaluationResult(null);
    setSelectedTask(null);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#f5222d';
  };

  const taskColumns = [
    {
      title: 'Task Key',
      dataIndex: 'key',
      key: 'key',
      width: 120,
      render: (text) => <Tag color="blue">{text}</Tag>
    },
    {
      title: 'Summary',
      dataIndex: 'summary',
      key: 'summary',
      ellipsis: true
    },
    {
      title: 'Assignee',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 150
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120
    },
    {
      title: 'Action',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          icon={<PlayCircleOutlined />}
          onClick={() => handleEvaluate(record)}
        >
          Değerlendir
        </Button>
      )
    }
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 8 }}>BA Doküman Değerlendirme</h1>
      <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
        JIRA görevlerinden BA dokümanlarını otomatik analiz eder ve kalite puanı hesaplar
      </p>

      {!evaluationResult ? (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* JIRA Status Check */}
          {statusLoading && (
            <Card>
              <Skeleton active />
            </Card>
          )}

          {!statusLoading && !jiraStatus?.configured && (
            <Alert
              message="JIRA Yapılandırılmamış"
              description="JIRA entegrasyonu için .env dosyasına JIRA_EMAIL ve JIRA_API_TOKEN ekleyin."
              type="error"
              showIcon
            />
          )}

          {/* Step 1: Project Selection */}
          {jiraStatus?.configured && !selectedProject && (
            <Card
              title="1. JIRA Proje Seçimi"
              extra={
                <Button icon={<ReloadOutlined />} onClick={() => refetchProjects()}>
                  Yenile
                </Button>
              }
            >
              <Select
                placeholder="JIRA projesi seçin"
                style={{ width: '100%' }}
                onChange={setSelectedProject}
                options={projects?.map(p => ({
                  label: `${p.key} - ${p.name}`,
                  value: p.key
                }))}
                size="large"
              />
            </Card>
          )}

          {/* Step 2: Task Selection */}
          {selectedProject && !selectedTask && (
            <Card
              title={`2. Task Seçimi - ${selectedProject}`}
              extra={
                <Space>
                  <Button onClick={() => setSelectedProject(null)}>
                    Proje Değiştir
                  </Button>
                  <Button icon={<ReloadOutlined />} onClick={() => refetchTasks()}>
                    Yenile
                  </Button>
                </Space>
              }
            >
              {tasks && tasks.length > 0 ? (
                <>
                  <Alert
                    message={`${tasks.length} BA task bulundu`}
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />
                  <Table
                    dataSource={tasks}
                    columns={taskColumns}
                    rowKey="key"
                    pagination={false}
                    size="small"
                  />
                </>
              ) : (
                <Alert
                  message="Task bulunamadı"
                  description="Bu projede değerlendirilecek BA task bulunmuyor."
                  type="warning"
                  showIcon
                />
              )}
            </Card>
          )}

          {/* Optional: Reference Document */}
          {selectedProject && (
            <Card title="Opsiyonel: Referans Doküman">
              <Form.Item
                label="Referans BRD Dokümanı"
                name="reference_document_id"
              >
                <Select
                  placeholder="Karşılaştırma için BRD seçin (opsiyonel)"
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
            </Card>
          )}

          {/* Loading State */}
          {evaluateMutation.isPending && (
            <Card>
              <Skeleton active />
              <Alert
                message="Değerlendirme devam ediyor..."
                description={`${selectedTask?.key} - ${selectedTask?.summary} dokümanı analiz ediliyor. Bu işlem 30-60 saniye sürebilir.`}
                type="info"
                showIcon
                style={{ marginTop: 16 }}
              />
            </Card>
          )}
        </Space>
      ) : (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Overall Score */}
          <Card
            title={`Değerlendirme Sonucu: ${selectedTask?.key}`}
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
          <Card title="Kriter Bazlı Skorlar (9 Kriter)">
            <Collapse accordion>
              {evaluationResult.criteria_scores?.map((criterion, index) => (
                <Panel
                  header={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>{criterion.name || `Kriter ${index + 1}`}</span>
                      <Progress
                        percent={criterion.score * 10}
                        steps={10}
                        strokeColor={getScoreColor(criterion.score * 10)}
                        style={{ width: 200, marginLeft: 16 }}
                      />
                    </div>
                  }
                  key={index}
                >
                  <Descriptions column={1} bordered size="small">
                    <Descriptions.Item label="Skor">
                      {criterion.score} / 10
                    </Descriptions.Item>
                    <Descriptions.Item label="Durum">
                      {criterion.score >= 6 ? (
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
