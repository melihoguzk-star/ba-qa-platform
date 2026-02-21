/**
 * App — Root component with routing and providers
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import trTR from 'antd/locale/tr_TR';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Import from './pages/Import';
import BAEvaluation from './pages/BAEvaluation';
import TCEvaluation from './pages/TCEvaluation';
import DesignCompliance from './pages/DesignCompliance';
import BRDPipeline from './pages/BRDPipeline';
import SmartMatching from './pages/SmartMatch/SmartMatching';
import Settings from './pages/Settings';
import { ROUTES } from './utils/constants';

// Create TanStack Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
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
              <Route path={ROUTES.IMPORT} element={<Import />} />
              <Route path={ROUTES.BA_EVALUATION} element={<BAEvaluation />} />
              <Route path={ROUTES.TC_EVALUATION} element={<TCEvaluation />} />
              <Route path={ROUTES.DESIGN_COMPLIANCE} element={<DesignCompliance />} />
              <Route path={ROUTES.BRD_PIPELINE} element={<BRDPipeline />} />
              <Route path={ROUTES.SMART_MATCHING} element={<SmartMatching />} />
              <Route path={ROUTES.SETTINGS} element={<Settings />} />
              {/* More routes will be added in Phase 3 */}
            </Route>
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}
