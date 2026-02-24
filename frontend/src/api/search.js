/**
 * Search API — React Query hooks for hybrid search, Drive search, reindex
 */
import { useMutation, useQuery } from '@tanstack/react-query';
import client from './client';

/**
 * Search documents (hybrid search — platform / drive / both)
 */
export const useSearch = () => {
  return useMutation({
    mutationFn: async (searchRequest) => {
      const { data } = await client.post('/search', searchRequest);
      return data;
    },
  });
};

/**
 * Dedicated Drive search
 */
export const useDriveSearch = () => {
  return useMutation({
    mutationFn: async ({ query, folder_id, mime_type }) => {
      const { data } = await client.post('/search/drive', { query, folder_id, mime_type });
      return data;
    },
  });
};

/**
 * Trigger full platform reindex
 */
export const useReindexTrigger = () => {
  return useMutation({
    mutationFn: async () => {
      const { data } = await client.post('/search/reindex');
      return data;
    },
  });
};

/**
 * Poll reindex status
 */
export const useReindexStatus = (enabled = false) => {
  return useQuery({
    queryKey: ['reindex-status'],
    queryFn: async () => {
      const { data } = await client.get('/search/reindex/status');
      return data;
    },
    enabled,
    refetchInterval: (query) => {
      const data = query?.state?.data;
      if (data?.status === 'running') return 2000;
      return false;
    },
  });
};

/**
 * Get search / vector store stats
 */
export const useSearchStats = () => {
  return useQuery({
    queryKey: ['search-stats'],
    queryFn: async () => {
      const { data } = await client.get('/search/stats');
      return data;
    },
  });
};
