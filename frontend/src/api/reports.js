/**
 * Reports & Analytics API Client
 */
import { useQuery } from '@tanstack/react-query';
import client from './client';

/**
 * Get platform statistics
 */
export const useReportStats = (timeRange = 'all') => {
  return useQuery({
    queryKey: ['report-stats', timeRange],
    queryFn: async () => {
      const response = await client.get('/reports/stats', {
        params: { time_range: timeRange },
      });
      return response.data;
    },
  });
};

/**
 * Get recent analyses with filters
 */
export const useRecentAnalyses = (filters = {}) => {
  const { limit = 25, analysis_type, time_range = 'all' } = filters;

  return useQuery({
    queryKey: ['recent-analyses', limit, analysis_type, time_range],
    queryFn: async () => {
      const response = await client.get('/reports/analyses', {
        params: {
          limit,
          analysis_type: analysis_type || undefined,
          time_range,
        },
      });
      return response.data;
    },
  });
};

/**
 * Export analyses as CSV
 * This returns the download URL, not using React Query
 */
export const exportAnalysesCSV = (filters = {}) => {
  const { limit = 100, analysis_type, time_range = 'all' } = filters;

  const params = new URLSearchParams({
    limit: limit.toString(),
    time_range,
  });

  if (analysis_type) {
    params.append('analysis_type', analysis_type);
  }

  // Trigger download
  const url = `${client.defaults.baseURL}/reports/export/csv?${params.toString()}`;
  window.open(url, '_blank');
};
