/**
 * Search API — React Query hooks
 */
import { useMutation } from '@tanstack/react-query';
import client from './client';

/**
 * Search documents (hybrid search)
 */
export const useSearch = () => {
  return useMutation({
    mutationFn: async (searchRequest) => {
      const { data } = await client.post('/search', searchRequest);
      return data;
    },
  });
};
