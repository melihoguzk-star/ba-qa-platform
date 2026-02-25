/**
 * DriveSearchTab — Dedicated Google Shared Drive search with filters
 */
import { useState, useEffect } from 'react';
import {
  Input,
  Card,
  Space,
  Tag,
  Typography,
  Empty,
  Spin,
  Button,
  Table,
  Segmented,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  LinkOutlined,
  FileTextOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useDriveSearch } from '../../api/drive';

const { Text, Paragraph } = Typography;

// Debounce helper
function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// MIME type filter options for Segmented
const MIME_FILTERS = [
  { label: 'Tümü', value: 'all' },
  { label: 'Docs', value: 'docs' },
  { label: 'Sheets', value: 'sheets' },
  { label: 'Word', value: 'docx' },
  { label: 'PDF', value: 'pdf' },
];

// MIME type → icon + label mapping
const MIME_INFO = {
  'application/vnd.google-apps.document': { icon: <FileTextOutlined style={{ color: '#4285f4' }} />, label: 'Google Docs', color: 'blue' },
  'application/vnd.google-apps.spreadsheet': { icon: <FileExcelOutlined style={{ color: '#0f9d58' }} />, label: 'Google Sheets', color: 'green' },
  'application/vnd.google-apps.presentation': { icon: <FileOutlined style={{ color: '#f4b400' }} />, label: 'Slides', color: 'orange' },
  'application/pdf': { icon: <FilePdfOutlined style={{ color: '#ea4335' }} />, label: 'PDF', color: 'red' },
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { icon: <FileWordOutlined style={{ color: '#2b579a' }} />, label: 'Word', color: 'blue' },
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { icon: <FileExcelOutlined style={{ color: '#217346' }} />, label: 'Excel', color: 'green' },
  'application/msword': { icon: <FileWordOutlined style={{ color: '#2b579a' }} />, label: 'Word', color: 'blue' },
  'text/plain': { icon: <FileTextOutlined />, label: 'Metin', color: 'default' },
};

function getMimeInfo(mimeType = '') {
  if (MIME_INFO[mimeType]) return MIME_INFO[mimeType];
  if (mimeType.includes('document')) return { icon: <FileTextOutlined />, label: 'Doküman', color: 'default' };
  if (mimeType.includes('spreadsheet')) return { icon: <FileExcelOutlined />, label: 'Tablo', color: 'green' };
  if (mimeType.includes('pdf')) return { icon: <FilePdfOutlined />, label: 'PDF', color: 'red' };
  return { icon: <FileOutlined />, label: 'Dosya', color: 'default' };
}

// Format date for Turkish locale
function formatDate(dateStr) {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

// Format file size
function formatSize(bytes) {
  if (!bytes) return '-';
  const num = Number(bytes);
  if (isNaN(num)) return bytes;
  if (num < 1024) return `${num} B`;
  if (num < 1024 * 1024) return `${(num / 1024).toFixed(1)} KB`;
  return `${(num / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DriveSearchTab() {
  const [query, setQuery] = useState('');
  const [mimeFilter, setMimeFilter] = useState('all');
  const debouncedQuery = useDebounce(query, 500);

  const searchMutation = useDriveSearch();

  // Auto-search when debounced query or filter changes
  useEffect(() => {
    if (debouncedQuery.trim().length >= 2) {
      searchMutation.mutate({
        query: debouncedQuery.trim(),
        mime_type_filter: mimeFilter === 'all' ? '' : mimeFilter,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery, mimeFilter]);

  const results = searchMutation.data?.results || [];
  const resultCount = searchMutation.data?.count || 0;

  // Table columns
  const columns = [
    {
      title: 'Dosya Adı',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => {
        const mime = getMimeInfo(record.mimeType);
        return (
          <Space>
            {mime.icon}
            <a href={record.webViewLink} target="_blank" rel="noopener noreferrer">
              {name}
            </a>
          </Space>
        );
      },
    },
    {
      title: 'Tür',
      dataIndex: 'mimeType',
      key: 'mimeType',
      width: 130,
      render: (mimeType) => {
        const mime = getMimeInfo(mimeType);
        return <Tag color={mime.color}>{mime.label}</Tag>;
      },
    },
    {
      title: 'Değiştirilme',
      dataIndex: 'modifiedTime',
      key: 'modifiedTime',
      width: 120,
      render: (date) => (
        <Tooltip title={date ? new Date(date).toLocaleString('tr-TR') : ''}>
          <Space size={4}>
            <ClockCircleOutlined style={{ fontSize: 12 }} />
            <Text type="secondary" style={{ fontSize: 12 }}>{formatDate(date)}</Text>
          </Space>
        </Tooltip>
      ),
      sorter: (a, b) => new Date(a.modifiedTime || 0) - new Date(b.modifiedTime || 0),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Boyut',
      dataIndex: 'size',
      key: 'size',
      width: 90,
      render: (size) => <Text type="secondary" style={{ fontSize: 12 }}>{formatSize(size)}</Text>,
    },
    {
      title: '',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          icon={<LinkOutlined />}
          href={record.webViewLink}
          target="_blank"
          rel="noopener noreferrer"
          size="small"
        >
          Aç
        </Button>
      ),
    },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      {/* Search bar + filter */}
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Input
            placeholder="Shared Drive'da dosya ara..."
            prefix={<SearchOutlined />}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            allowClear
            size="large"
          />
          <Segmented
            options={MIME_FILTERS}
            value={mimeFilter}
            onChange={setMimeFilter}
          />
        </Space>
      </Card>

      {/* Loading */}
      {searchMutation.isPending && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 12 }}>Drive'da aranıyor...</Paragraph>
        </div>
      )}

      {/* Results */}
      {searchMutation.data && !searchMutation.isPending && (
        <Card
          title={
            <Space>
              <SearchOutlined />
              <span>{resultCount} sonuç bulundu</span>
              <Text type="secondary" style={{ fontSize: 12 }}>
                &quot;{searchMutation.data.query}&quot;
              </Text>
            </Space>
          }
          size="small"
        >
          {results.length === 0 ? (
            <Empty
              description="Shared Drive'da sonuç bulunamadı"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            <Table
              dataSource={results}
              columns={columns}
              rowKey="id"
              size="small"
              pagination={{
                pageSize: 20,
                showSizeChanger: false,
                showTotal: (total) => `Toplam ${total} dosya`,
              }}
            />
          )}
        </Card>
      )}

      {/* Error */}
      {searchMutation.isError && (
        <Card>
          <Empty
            description={
              <span>
                Arama sırasında hata oluştu.
                <br />
                <Text type="secondary">Lütfen tekrar deneyin.</Text>
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      )}

      {/* Empty initial state */}
      {!searchMutation.data && !searchMutation.isPending && !query && (
        <Card>
          <Empty
            description={
              <span>
                Shared Drive&apos;da dosya aramak için yukarıdaki alana bir sorgu girin.
                <br />
                <Text type="secondary">Google Docs, Sheets, Word, PDF dosyaları arasında arama yapabilirsiniz.</Text>
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      )}
    </Space>
  );
}
