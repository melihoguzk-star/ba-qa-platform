/**
 * ProjectsTab — Projects list with create/edit modal
 */
import { useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import {
  useProjects,
  useCreateProject,
  useUpdateProject,
  useDeleteProject
} from '../../api/projects';

export default function ProjectsTab() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [form] = Form.useForm();

  const { data: projects, isLoading } = useProjects();
  const createMutation = useCreateProject();
  const updateMutation = useUpdateProject();
  const deleteMutation = useDeleteProject();

  const handleCreate = () => {
    setEditingProject(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (record) => {
    setEditingProject(record);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id) => {
    try {
      await deleteMutation.mutateAsync(id);
      message.success('Proje silindi');
    } catch (error) {
      message.error('Proje silinirken hata oluştu');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingProject) {
        await updateMutation.mutateAsync({ id: editingProject.id, ...values });
        message.success('Proje güncellendi');
      } else {
        await createMutation.mutateAsync(values);
        message.success('Proje oluşturuldu');
      }
      setIsModalOpen(false);
      form.resetFields();
    } catch (error) {
      message.error('İşlem başarısız oldu');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: (a, b) => a.id - b.id
    },
    {
      title: 'Proje Adı',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name)
    },
    {
      title: 'Açıklama',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
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
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Düzenle
          </Button>
          <Popconfirm
            title="Proje silinecek"
            description="Bu projeyi silmek istediğinizden emin misiniz?"
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
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>Projeler</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Yeni Proje
        </Button>
      </div>

      <Table
        dataSource={projects}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} proje`
        }}
      />

      <Modal
        title={editingProject ? 'Proje Düzenle' : 'Yeni Proje'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            label="Proje Adı"
            name="name"
            rules={[{ required: true, message: 'Proje adı gerekli' }]}
          >
            <Input placeholder="Proje adını girin" />
          </Form.Item>

          <Form.Item
            label="Açıklama"
            name="description"
            rules={[{ required: true, message: 'Açıklama gerekli' }]}
          >
            <Input.TextArea
              rows={4}
              placeholder="Proje açıklamasını girin"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
