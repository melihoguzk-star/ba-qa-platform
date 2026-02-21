/**
 * BA Evaluation — JIRA task-based BA document evaluation
 * EXACTLY matches Streamlit pages/1_BA_Degerlendirme.py flow
 *
 * Flow:
 * 1. JIRA Scanner → Fetch BA task queue
 * 2. Document Reader → Auto-fetch Google Doc from selected task
 * 3. Quality Evaluator → AI-based 9-criteria evaluation
 * 4. Reporter → Display results + update JIRA
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
  Alert,
  Space,
  Table,
  Tag,
  message,
  Steps,
  Statistic,
  Row,
  Col,
  Divider
} from 'antd';
import {
  FileSearchOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { useJIRAStatus, useJIRAProjects, useJIRATasks } from '../api/jira';
import { useEvaluateBA } from '../api/evaluation';

const { Panel } = Collapse;

// Model options (matches Streamlit utils/config.py ALL_MODELS)
const MODEL_OPTIONS = [
  { label: 'Claude Opus 4.6', value: 'claude-opus-4-6' },
  { label: 'Claude Sonnet 4.5', value: 'claude-sonnet-4-5-20250929' },
  { label: 'Claude Sonnet 4', value: 'claude-sonnet-4-20250514' },
  { label: 'Claude Haiku 4.5', value: 'claude-haiku-4-5-20251001' },
  { label: 'Gemini 2.5 Flash (Default)', value: 'gemini-2.5-flash' },
  { label: 'Gemini 2.5 Pro', value: 'gemini-2.5-pro' },
  { label: 'Gemini 2.0 Flash', value: 'gemini-2.0-flash' },
];

// BA Criteria (matches utils/config.py BA_CRITERIA)
const BA_CRITERIA = [
  { key: 'completeness', label: 'Tamlık' },
  { key: 'wireframes', label: 'Wireframe / Ekran Tasarımları' },
  { key: 'flow_diagrams', label: 'Akış Diyagramları' },
  { key: 'requirement_quality', label: 'Gereksinim Kalitesi' },
  { key: 'acceptance_criteria', label: 'Kabul Kriterleri' },
  { key: 'consistency', label: 'Tutarlılık' },
  { key: 'business_rules', label: 'İş Kuralları Derinliği' },
  { key: 'error_handling', label: 'Hata Yönetimi' },
  { key: 'documentation_quality', label: 'Dokümantasyon Kalitesi' },
];

// Helper functions
const getScoreColor = (score) => {
  if (score >= 80) return '#52c41a';
  if (score >= 60) return '#faad14';
  return '#f5222d';
};

const getScoreEmoji = (score) => {
  if (score >= 8) return '🟢';
  if (score >= 6) return '🟡';
  return '🔴';
};

export default function BAEvaluation() {
  const [form] = Form.useForm();
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedTask, setSelectedTask] = useState(null);

  const { data: jiraStatus, isLoading: statusLoading } = useJIRAStatus();
  const { data: projects, refetch: refetchProjects } = useJIRAProjects();
  const { data: tasks, refetch: refetchTasks } = useJIRATasks(selectedProject, 'ba');
  const evaluateMutation = useEvaluateBA();

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
      width: 120,
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          icon={<PlayCircleOutlined />}
          onClick={() => handleEvaluate(record)}
          loading={evaluateMutation.isPending && selectedTask?.key === record.key}
        >
          Değerlendir
        </Button>
      )
    }
  ];

  const handleEvaluate = async (task) => {
    setSelectedTask(task);
    setEvaluationResult(null); // Clear previous results
    setCurrentStep(0);

    const requestData = {
      jira_task_key: task.key,
      model: selectedModel
    };

    try {
      // Simulate step progression
      setCurrentStep(0); // JIRA Scanner
      await new Promise(resolve => setTimeout(resolve, 500));

      setCurrentStep(1); // Document Reader
      await new Promise(resolve => setTimeout(resolve, 500));

      setCurrentStep(2); // Quality Evaluator (AI is processing)
      const result = await evaluateMutation.mutateAsync(requestData);

      setCurrentStep(3); // Reporter (showing results)
      setEvaluationResult(result);
      message.success('Değerlendirme tamamlandı');
    } catch (error) {
      // Keep task selected on error so user can see what failed
      console.error('Evaluation error:', error);
      setCurrentStep(0);

      const errorMsg = error.response?.data?.detail || error.message || 'Bilinmeyen hata';
      message.error('Değerlendirme başarısız oldu: ' + errorMsg, 10);

      // Show error in alert
      setEvaluationResult({
        error: true,
        errorMessage: errorMsg,
        score: 0,
        passed: false,
        feedback: 'Değerlendirme sırasında bir hata oluştu.',
        criteria_scores: []
      });
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
    setCurrentStep(0);
    // Refetch tasks to update the list (remove evaluated tasks)
    refetchTasks();
  };

  return (
    <div>
      <h1 style={{ marginBottom: 8 }}>📋 BA Doküman Değerlendirme</h1>
      <p style={{ color: '#8c8c8c', marginBottom: 24 }}>
        JIRA görevlerinden BA dokümanlarını otomatik analiz eder ve kalite puanı hesaplar
      </p>

      {/* Pipeline Badge */}
      <Alert
        message="🤖 4-Adım Pipeline: JIRA Scanner → Doc Reader → Quality Evaluator → Reporter"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* Model Selection */}
      <Card title="⚙️ Model Ayarları" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Select
              value={selectedModel}
              onChange={setSelectedModel}
              options={MODEL_OPTIONS}
              style={{ width: '100%' }}
              size="large"
            />
          </Col>
          <Col span={12}>
            <Alert
              message={`🤖 Seçili Model: ${MODEL_OPTIONS.find(m => m.value === selectedModel)?.label}`}
              type="info"
              showIcon
            />
          </Col>
        </Row>
      </Card>

      <Divider />

      {/* Conditional rendering based on state */}
      {evaluationResult ? (
        /* RESULTS DISPLAY */
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Error Display */}
          {evaluationResult.error ? (
            <Card title={`Değerlendirme Hatası: ${selectedTask?.key}`}>
              <Alert
                message="Değerlendirme Başarısız"
                description={evaluationResult.errorMessage}
                type="error"
                showIcon
                style={{ marginBottom: 16 }}
              />
              <Button onClick={handleReset} type="primary">
                Yeni Değerlendirme
              </Button>
            </Card>
          ) : (
            <>
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
            <Row gutter={24} style={{ textAlign: 'center' }}>
              <Col span={12}>
                <Statistic
                  title="Genel Puan"
                  value={evaluationResult.score}
                  suffix="/ 100"
                  valueStyle={{ color: getScoreColor(evaluationResult.score), fontSize: 48 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Sonuç"
                  value={evaluationResult.passed ? 'GEÇTİ' : 'GEÇMEDİ'}
                  valueStyle={{
                    color: evaluationResult.passed ? '#52c41a' : '#f5222d',
                    fontSize: 32
                  }}
                  prefix={evaluationResult.passed ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                />
              </Col>
            </Row>

            {evaluationResult.feedback && (
              <Alert
                message="Genel Değerlendirme"
                description={evaluationResult.feedback}
                type="info"
                showIcon
                style={{ marginTop: 24 }}
              />
            )}
          </Card>

          {/* Criteria Scores */}
          <Card title="📈 Kriter Bazlı Skorlar (9 Kriter)">
            <Collapse accordion>
              {evaluationResult.criteria_scores?.map((criterion, index) => {
                const criterionInfo = BA_CRITERIA.find(c => c.key === criterion.criterion);
                const score = criterion.score || 0;

                return (
                  <Panel
                    header={
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>
                          {getScoreEmoji(score)} {criterionInfo?.label || criterion.criterion}
                        </span>
                        <Progress
                          percent={score * 10}
                          steps={10}
                          strokeColor={getScoreColor(score * 10)}
                          style={{ width: 200, marginLeft: 16 }}
                        />
                      </div>
                    }
                    key={index}
                  >
                    <Descriptions column={1} bordered size="small">
                      <Descriptions.Item label="Skor">
                        {score} / 10
                      </Descriptions.Item>
                      <Descriptions.Item label="Durum">
                        {score >= 6 ? (
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
                );
              })}
            </Collapse>
          </Card>

          {/* Strengths & Weaknesses */}
          <Row gutter={16}>
            <Col span={12}>
              {evaluationResult.strengths && evaluationResult.strengths.length > 0 && (
                <Card title="✅ Güçlü Yanlar" size="small">
                  <ul>
                    {evaluationResult.strengths.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </Card>
              )}
            </Col>
            <Col span={12}>
              {evaluationResult.weaknesses && evaluationResult.weaknesses.length > 0 && (
                <Card title="❌ Kritik Eksikler" size="small">
                  <ul>
                    {evaluationResult.weaknesses.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </Card>
              )}
            </Col>
          </Row>

          {/* Suggestions */}
          {evaluationResult.suggestions && evaluationResult.suggestions.length > 0 && (
            <Card title="💡 İyileştirme Önerileri" size="small">
              <ol>
                {evaluationResult.suggestions.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ol>
            </Card>
          )}

              {/* Statistics */}
              {evaluationResult.statistics && Object.keys(evaluationResult.statistics).length > 0 && (
                <Card title="📊 İstatistikler" size="small">
                  <Descriptions column={2} bordered size="small">
                    {Object.entries(evaluationResult.statistics).map(([key, value]) => (
                      <Descriptions.Item label={key} key={key}>
                        {typeof value === 'object' ? JSON.stringify(value) : value}
                      </Descriptions.Item>
                    ))}
                  </Descriptions>
                </Card>
              )}
            </>
          )}
        </Space>
      ) : (
        /* NO RESULTS - Show JIRA selection or loading */
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* JIRA Status Check */}
          {statusLoading && <Card loading />}

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
          {selectedProject && !evaluateMutation.isPending && (
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

          {/* Loading State */}
          {evaluateMutation.isPending && (
            <Card>
              <Steps
                current={currentStep}
                items={[
                  { title: 'JIRA Tarayıcı', icon: <FileSearchOutlined /> },
                  { title: 'Doküman Okuyucu', icon: <FileSearchOutlined /> },
                  { title: 'Kalite Değerlendirici', icon: <RobotOutlined /> },
                  { title: 'Raporcu', icon: <CheckCircleOutlined /> }
                ]}
              />
              <Alert
                message="Değerlendirme devam ediyor..."
                description={`${selectedTask?.key} - ${selectedTask?.summary} dokümanı analiz ediliyor. Bu işlem 30-60 saniye sürebilir.`}
                type="info"
                showIcon
                style={{ marginTop: 24 }}
              />
            </Card>
          )}
        </Space>
      )}
    </div>
  );
}
