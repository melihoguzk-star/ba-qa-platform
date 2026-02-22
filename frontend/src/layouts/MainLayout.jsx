/**
 * Main Layout — Sidebar + Header + Content
 */
import { useEffect } from 'react';
import { Layout, Menu, Breadcrumb, Button, Drawer, Grid } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  ImportOutlined,
  CheckCircleOutlined,
  ExperimentOutlined,
  FormatPainterOutlined,
  RocketOutlined,
  SearchOutlined,
  BarChartOutlined,
  SettingOutlined,
  ApartmentOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAppStore } from '../stores/appStore';
import { ROUTES } from '../utils/constants';

const { Header, Sider, Content } = Layout;

const menuItems = [
  {
    key: ROUTES.HOME,
    icon: <HomeOutlined />,
    label: 'Dashboard',
  },
  {
    key: ROUTES.DOCUMENTS,
    icon: <FileTextOutlined />,
    label: 'Dokümanlar',
  },
  {
    key: ROUTES.IMPORT,
    icon: <ImportOutlined />,
    label: 'Import',
  },
  {
    key: ROUTES.BA_EVALUATION,
    icon: <CheckCircleOutlined />,
    label: 'BA Değerlendirme',
  },
  {
    key: ROUTES.TC_EVALUATION,
    icon: <ExperimentOutlined />,
    label: 'TC Değerlendirme',
  },
  {
    key: ROUTES.DESIGN_COMPLIANCE,
    icon: <FormatPainterOutlined />,
    label: 'Design Compliance',
  },
  {
    key: ROUTES.BRD_PIPELINE,
    icon: <RocketOutlined />,
    label: 'BRD Pipeline',
  },
  {
    key: ROUTES.SMART_MATCHING,
    icon: <SearchOutlined />,
    label: 'Smart Matching',
  },
  {
    key: ROUTES.REPORTS,
    icon: <BarChartOutlined />,
    label: 'Raporlar',
  },
  {
    key: ROUTES.ARCHITECTURE,
    icon: <ApartmentOutlined />,
    label: 'Mimari',
  },
  {
    key: ROUTES.SETTINGS,
    icon: <SettingOutlined />,
    label: 'Ayarlar',
  },
];

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed, setSidebarCollapsed } = useAppStore();
  const screens = Grid.useBreakpoint();

  // Auto-collapse sidebar on mobile/tablet
  const isMobile = !screens.lg;
  const showDrawer = isMobile;
  const siderWidth = sidebarCollapsed ? 80 : 250;

  // Auto-close drawer on mobile when screen size changes
  useEffect(() => {
    if (isMobile && !sidebarCollapsed) {
      setSidebarCollapsed(true); // Close drawer on mobile by default
    }
  }, [isMobile]);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleMenuClick = ({ key }) => {
    navigate(key);
    // Close drawer on mobile after navigation
    if (isMobile && !sidebarCollapsed) {
      toggleSidebar();
    }
  };

  // Sidebar logo component
  const SidebarLogo = () => (
    <div
      style={{
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: sidebarCollapsed && !isMobile ? 18 : 20,
        fontWeight: 'bold',
        color: '#1890ff',
        borderBottom: '1px solid #f0f0f0',
      }}
    >
      {sidebarCollapsed && !isMobile ? 'BA' : 'BA&QA Platform'}
    </div>
  );

  // Sidebar menu component
  const SidebarMenu = () => (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={handleMenuClick}
      style={{ borderRight: 0 }}
    />
  );

  // Generate breadcrumb items from current path
  const pathSnippets = location.pathname.split('/').filter((i) => i);
  const breadcrumbItems = [
    {
      title: <HomeOutlined />,
    },
    ...pathSnippets.map((snippet, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      const menuItem = menuItems.find((item) => item.key === url);
      return {
        title: menuItem?.label || snippet,
      };
    }),
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Desktop Sidebar */}
      {!showDrawer && (
        <Sider
          collapsible
          collapsed={sidebarCollapsed}
          onCollapse={toggleSidebar}
          theme="light"
          width={250}
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
          }}
        >
          <SidebarLogo />
          <SidebarMenu />
        </Sider>
      )}

      {/* Mobile Drawer */}
      {showDrawer && (
        <Drawer
          placement="left"
          open={!sidebarCollapsed}
          onClose={toggleSidebar}
          bodyStyle={{ padding: 0 }}
          width={250}
        >
          <SidebarLogo />
          <SidebarMenu />
        </Drawer>
      )}

      <Layout style={{ marginLeft: isMobile ? 0 : siderWidth, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: isMobile ? '0 12px' : '0 24px',
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? 8 : 16 }}>
            <Button
              type="text"
              icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={toggleSidebar}
            />
            {!screens.xs && <Breadcrumb items={breadcrumbItems} />}
          </div>

          <div>
            {/* Future: Search, notifications, user menu */}
          </div>
        </Header>

        <Content
          style={{
            margin: isMobile ? '12px' : '24px',
            padding: isMobile ? 16 : 24,
            minHeight: 280,
            background: '#fff',
            borderRadius: 8,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
