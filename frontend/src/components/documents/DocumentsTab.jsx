/**
 * DocumentsTab — Documents list with filtering and detail drawer
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, Tag, Drawer, Descriptions, message, Popconfirm } from 'antd';
import { SearchOutlined, EyeOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useDocuments, useDeleteDocument } from '../../api/documents';
import { useProjects } from '../../api/projects';
import { ROUTES } from '../../utils/constants';

const { Search } = Input;

export default function DocumentsTab() {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');
  const [projectFilter, setProjectFilter] = useState(null);
  const [docTypeFilter, setDocTypeFilter] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);

  const { data: documents, isLoading } = useDocuments({
    project_id: projectFilter,
    doc_type: docTypeFilter
  });
  const { data: projects } = useProjects();
  const deleteMutation = useDeleteDocument();

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchText);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchText]);

  const handleDelete = async (id) => {
    try {
      await deleteMutation.mutateAsync(id);
      message.success('Doküman silindi');
      if (selectedDocument?.id === id) {
        setSelectedDocument(null);
      }
    } catch (error) {
      message.error('Doküman silinirken hata oluştu');
    }
  };

  const filteredDocuments = documents?.filter(doc =>
    !debouncedSearch ||
    doc.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
    doc.doc_type.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: (a, b) => a.id - b.id
    },
    {
      title: 'Doküman Adı',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => navigate(`${ROUTES.DOCUMENTS}/${record.id}`)}
          style={{ padding: 0 }}
        >
          {text}
        </Button>
      )
    },
    {
      title: 'Tip',
      dataIndex: 'doc_type',
      key: 'doc_type',
      width: 100,
      render: (type) => (
        <Tag color={
          type === 'brd' ? 'blue' :
          type === 'ba' ? 'green' :
          type === 'ta' ? 'orange' :
          'purple'
        }>
          {type.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'BRD', value: 'brd' },
        { text: 'BA', value: 'ba' },
        { text: 'TA', value: 'ta' },
        { text: 'TC', value: 'tc' }
      ],
      onFilter: (value, record) => record.doc_type === value
    },
    {
      title: 'Proje',
      dataIndex: 'project_id',
      key: 'project_id',
      width: 200,
      render: (projectId) => {
        const project = projects?.find(p => p.id === projectId);
        return project?.name || '-';
      }
    },
    {
      title: 'Versiyon',
      dataIndex: 'current_version',
      key: 'current_version',
      width: 100,
      render: (version) => `v${version}`
    },
    {
      title: 'Oluşturulma',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => new Date(text).toLocaleString('tr-TR'),
      sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at)
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => setSelectedDocument(record)}
          >
            Detay
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`${ROUTES.DOCUMENTS}/${record.id}`)}
          >
            Düzenle
          </Button>
          <Popconfirm
            title="Doküman silinecek"
            description="Bu dokümanı silmek istediğinizden emin misiniz?"
            onConfirm={() => handleDelete(record.id)}
            okText="Evet"
            cancelText="Hayır"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Sil
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2>Dokümanlar</h2>
      </div>

      <Space style={{ marginBottom: 16, width: '100%' }} wrap>
        <Search
          placeholder="Doküman ara..."
          allowClear
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 300 }}
          prefix={<SearchOutlined />}
        />
        <Select
          placeholder="Proje filtrele"
          allowClear
          style={{ width: 200 }}
          value={projectFilter}
          onChange={setProjectFilter}
          options={projects?.map(p => ({ label: p.name, value: p.id }))}
        />
        <Select
          placeholder="Tip filtrele"
          allowClear
          style={{ width: 150 }}
          value={docTypeFilter}
          onChange={setDocTypeFilter}
          options={[
            { label: 'BRD', value: 'brd' },
            { label: 'BA', value: 'ba' },
            { label: 'TA', value: 'ta' },
            { label: 'TC', value: 'tc' }
          ]}
        />
      </Space>

      <Table
        dataSource={filteredDocuments}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} doküman`
        }}
      />

      <Drawer
        title="Doküman Detayları"
        placement="right"
        width={600}
        open={!!selectedDocument}
        onClose={() => setSelectedDocument(null)}
      >
        {selectedDocument && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="ID">{selectedDocument.id}</Descriptions.Item>
            <Descriptions.Item label="Doküman Adı">{selectedDocument.name}</Descriptions.Item>
            <Descriptions.Item label="Tip">
              <Tag color={
                selectedDocument.doc_type === 'brd' ? 'blue' :
                selectedDocument.doc_type === 'ba' ? 'green' :
                selectedDocument.doc_type === 'ta' ? 'orange' :
                'purple'
              }>
                {selectedDocument.doc_type.toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Proje ID">{selectedDocument.project_id}</Descriptions.Item>
            <Descriptions.Item label="Versiyon">v{selectedDocument.current_version}</Descriptions.Item>
            <Descriptions.Item label="Google Doc ID">{selectedDocument.google_doc_id || '-'}</Descriptions.Item>
            <Descriptions.Item label="Oluşturulma">
              {new Date(selectedDocument.created_at).toLocaleString('tr-TR')}
            </Descriptions.Item>
            <Descriptions.Item label="Güncellenme">
              {new Date(selectedDocument.updated_at).toLocaleString('tr-TR')}
            </Descriptions.Item>
            <Descriptions.Item label="Etiketler">
              {selectedDocument.tags?.length > 0 ? (
                <Space wrap>
                  {selectedDocument.tags.map(tag => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                </Space>
              ) : '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
}
