/**
 * App — Root component with routing
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import trTR from 'antd/locale/tr_TR';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import BAEvaluation from './pages/BAEvaluation';
import Settings from './pages/Settings';
import { ROUTES } from './utils/constants';

export default function App() {
  return (
    <ConfigProvider
      locale={trTR}
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path={ROUTES.DOCUMENTS} element={<Documents />} />
            <Route path={ROUTES.BA_EVALUATION} element={<BAEvaluation />} />
            <Route path={ROUTES.SETTINGS} element={<Settings />} />
            {/* More routes will be added in later tasks */}
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}
