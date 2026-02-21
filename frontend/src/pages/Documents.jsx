/**
 * Documents — Document Library with Projects, Documents, Upload, and Templates
 */
import { useState } from 'react';
import { Tabs } from 'antd';
import {
  ProjectOutlined,
  FileTextOutlined,
  UploadOutlined,
  FileAddOutlined
} from '@ant-design/icons';
import ProjectsTab from '../components/documents/ProjectsTab';
import DocumentsTab from '../components/documents/DocumentsTab';
import UploadTab from '../components/documents/UploadTab';
import TemplatesTab from '../components/documents/TemplatesTab';

export default function Documents() {
  const [activeTab, setActiveTab] = useState('projects');

  const items = [
    {
      key: 'projects',
      label: (
        <span>
          <ProjectOutlined />
          Projeler
        </span>
      ),
      children: <ProjectsTab />
    },
    {
      key: 'documents',
      label: (
        <span>
          <FileTextOutlined />
          Dokümanlar
        </span>
      ),
      children: <DocumentsTab />
    },
    {
      key: 'upload',
      label: (
        <span>
          <UploadOutlined />
          Doküman Yükle
        </span>
      ),
      children: <UploadTab />
    },
    {
      key: 'templates',
      label: (
        <span>
          <FileAddOutlined />
          Şablondan Oluştur
        </span>
      ),
      children: <TemplatesTab />
    }
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Doküman Kütüphanesi</h1>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={items}
        size="large"
      />
    </div>
  );
}
