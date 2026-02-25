/**
 * Drive API — React Query hooks for dedicated Shared Drive search
 */
import { useMutation } from '@tanstack/react-query';
import client from './client';

/**
 * Search Shared Drive via dedicated /drive/search endpoint.
 * Uses mutation pattern (user-triggered search, not auto-fetch).
 */
export const useDriveSearch = () => {
  return useMutation({
    mutationFn: async ({ query, mime_type_filter }) => {
      const { data } = await client.post('/drive/search', {
        query,
        mime_type_filter: mime_type_filter || '',
      });
      return data;
    },
  });
};
