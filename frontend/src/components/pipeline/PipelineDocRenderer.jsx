/**
 * PipelineDocRenderer — Pure render functions for BA/TA/TC document content
 * Extracted from BRDPipeline.jsx for reuse in Drawer and Board
 */
import { Table, Tag, Collapse } from 'antd';

export function renderBADocContent(content, token) {
  if (!content) return <p>İçerik bulunamadı</p>;
  const ekranlar = content.ekranlar || [];
  if (ekranlar.length === 0) {
    return <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(content, null, 2)}</pre>;
  }
  return (
    <div style={{ fontSize: 14 }}>
      {ekranlar.map((ekran, idx) => (
        <div key={idx} style={{ marginBottom: 24 }}>
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>
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
}

export function renderTADocContent(content, token) {
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
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>Genel Tanım</h3>
          <p><strong>Modül:</strong> {genel.modul_adi}</p>
          <p><strong>Stack:</strong> {Array.isArray(genel.teknoloji_stack) ? genel.teknoloji_stack.join(', ') : genel.teknoloji_stack}</p>
          <p><strong>Mimari:</strong> {genel.mimari_yaklasim}</p>
        </div>
      )}

      {endpointsDict && typeof endpointsDict === 'object' && !Array.isArray(endpointsDict) && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>API Endpoints</h3>
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
                  <div><strong>Response:</strong><pre style={{ background: token.colorSuccessBg, padding: 8, fontSize: 12 }}>{JSON.stringify(ep.response_success, null, 2)}</pre></div>
                )}
              </div>
            )
          }))} />
        </div>
      )}

      {endpointsList?.length > 0 && !endpointsDict && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>API Endpoints</h3>
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
                  <div><strong>Response:</strong><pre style={{ background: token.colorSuccessBg, padding: 8, fontSize: 12 }}>{JSON.stringify(ep.response_success || ep.response, null, 2)}</pre></div>
                )}
              </div>
            )
          }))} />
        </div>
      )}

      {dtos.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>DTO Yapıları</h3>
          {dtos.map((dto, idx) => (
            <div key={idx} style={{ marginBottom: 16 }}>
              <h4>{dto.dto_adi || dto.dto_name || dto.name}</h4>
              <p style={{ color: token.colorTextSecondary }}>{dto.aciklama || dto.description}</p>
              <Table
                dataSource={(dto.fields || []).map((f, i) => ({ ...f, key: i }))}
                columns={[
                  { title: 'Alan', dataIndex: 'field', key: 'field',
                    render: (_, record) => record.field || record.field_name || record.name },
                  { title: 'Tip', dataIndex: 'tip', key: 'type',
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
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>Validasyon Kuralları</h3>
          <ul>{validasyonlar.map((v, i) => (
            <li key={i}><strong>{v.id}</strong> [{v.field}]: {v.kural || v.rule}</li>
          ))}</ul>
        </div>
      )}

      {curls.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ borderBottom: `2px solid ${token.colorPrimary}`, paddingBottom: 8 }}>cURL Ornekleri</h3>
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
}

export function renderTCDocContent(content) {
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
}

export function renderDocContent(docType, content, token) {
  if (!docType) return null;
  const type = docType.toLowerCase();
  if (type === 'ba') return renderBADocContent(content, token);
  if (type === 'ta') return renderTADocContent(content, token);
  if (type === 'tc') return renderTCDocContent(content);
  return <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(content, null, 2)}</pre>;
}
