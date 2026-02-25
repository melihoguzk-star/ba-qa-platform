/**
 * PipelineDetailDrawer — Right-side drawer for Review and QA operations
 */
import { Drawer, Button, Space, Alert, Progress, Tag } from 'antd';
import {
  ArrowRightOutlined,
  DownloadOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { renderDocContent } from './PipelineDocRenderer';

export default function PipelineDetailDrawer({
  open,
  onClose,
  mode,
  docType,
  content,
  qaResult,
  token,
  onApprove,
  onEvaluateQA,
  onRegenerate,
  onForcePass,
  onDownload,
  onPreview,
  onGoBackToReview,
  loading
}) {
  const label = docType?.toUpperCase() || '';

  const renderReviewMode = () => (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Alert
        message="İnceleme Zamanı"
        description={`${label} dokümanını aşağıda inceleyebilirsiniz. Onayladığınızda QA değerlendirmesine geçilecek.`}
        type="success"
        showIcon
      />

      <div style={{
        border: `1px solid ${token.colorBorder}`,
        borderRadius: 8,
        padding: 16,
        maxHeight: 500,
        overflow: 'auto',
        background: token.colorBgContainer
      }}>
        {renderDocContent(docType, content, token)}
      </div>

      <Space wrap>
        <Button
          icon={<EyeOutlined />}
          onClick={() => onPreview?.(docType, content)}
        >
          Önizle
        </Button>
        <Button
          icon={<DownloadOutlined />}
          onClick={() => onDownload?.(docType)}
        >
          İndir ({label === 'TC' ? 'XLSX' : 'DOCX'})
        </Button>
        <Button
          type="primary"
          size="large"
          icon={<ArrowRightOutlined />}
          onClick={onApprove}
          loading={loading?.approve}
        >
          Onayla ve QA'ya Geç
        </Button>
      </Space>
    </Space>
  );

  const renderQAMode = () => (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {!qaResult ? (
        <>
          <Alert
            message="QA Değerlendirmesi"
            description={`${label} dokümanı Gemini tarafından değerlendirilecek. Geçme skoru: 60+`}
            type="info"
            showIcon
          />
          <Space>
            <Button
              type="primary"
              size="large"
              onClick={() => onEvaluateQA?.(false)}
              loading={loading?.qa}
            >
              QA Değerlendirmesi Yap
            </Button>
            <Button
              size="large"
              onClick={() => onEvaluateQA?.(true)}
              loading={loading?.qa}
            >
              QA'yı Atla (Force Pass)
            </Button>
          </Space>
        </>
      ) : (
        <>
          <Alert
            message={qaResult.passed ? 'QA Başarılı!' : 'QA Başarısız'}
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
                  <div style={{ fontSize: 12, color: token.colorTextSecondary, marginTop: 4 }}>
                    {typeof kriter.aciklama === 'string' ? kriter.aciklama : JSON.stringify(kriter.aciklama)}
                  </div>
                </div>
              ))}
            </div>
          )}

          {qaResult.genel_degerlendirme && (
            <div>
              <p><strong>Genel Değerlendirme:</strong></p>
              <p style={{ whiteSpace: 'pre-wrap' }}>{qaResult.genel_degerlendirme}</p>
            </div>
          )}

          {qaResult.guclu_yanlar && qaResult.guclu_yanlar.length > 0 && (
            <div>
              <p><strong>Güçlü Yanlar:</strong></p>
              <ul>
                {qaResult.guclu_yanlar.map((item, i) => (
                  <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                ))}
              </ul>
            </div>
          )}

          {qaResult.kritik_eksikler && qaResult.kritik_eksikler.length > 0 && (
            <div>
              <p><strong>Kritik Eksikler:</strong></p>
              <ul>
                {qaResult.kritik_eksikler.map((item, i) => (
                  <li key={i} style={{ color: '#f5222d' }}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                ))}
              </ul>
            </div>
          )}

          {qaResult.iyilestirme_onerileri && qaResult.iyilestirme_onerileri.length > 0 && (
            <div>
              <p><strong>İyileştirme Önerileri:</strong></p>
              <ol>
                {qaResult.iyilestirme_onerileri.map((item, i) => (
                  <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                ))}
              </ol>
            </div>
          )}

          {qaResult.istatistikler && (
            <div>
              <p><strong>İstatistikler:</strong></p>
              <div style={{ fontSize: 12 }}>
                {Object.entries(qaResult.istatistikler).map(([key, value]) => (
                  <div key={key}>• {key}: {typeof value === 'object' ? JSON.stringify(value) : value}</div>
                ))}
              </div>
            </div>
          )}

          <Space wrap>
            {qaResult.passed || qaResult.gecti_mi ? (
              <Button
                type="primary"
                size="large"
                icon={<ArrowRightOutlined />}
                onClick={() => onForcePass?.()}
                loading={loading?.qa}
              >
                Sonraki Aşamaya Geç
              </Button>
            ) : (
              <>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => onRegenerate?.()}
                  loading={loading?.regenerate}
                >
                  Revize Et (Yeniden Üret)
                </Button>
                <Button onClick={() => onGoBackToReview?.()}>
                  Geri Dön ve Düzenle
                </Button>
                <Button type="primary" onClick={() => onForcePass?.()}>
                  Yine de Devam Et
                </Button>
              </>
            )}
          </Space>
        </>
      )}
    </Space>
  );

  return (
    <Drawer
      title={`${label} ${mode === 'review' ? 'İnceleme' : 'Kalite Değerlendirmesi'}`}
      placement="right"
      width={720}
      open={open}
      onClose={onClose}
      destroyOnClose
    >
      {mode === 'review' ? renderReviewMode() : renderQAMode()}
    </Drawer>
  );
}
