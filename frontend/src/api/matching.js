/**
 * Matching API — Smart matching hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from './client';

/**
 * Hook to search for matching documents based on task description
 */
export const useSearchMatches = () => {
  return useMutation({
    mutationFn: async (data) => {
      const response = await client.post('/match/search', data);
      return response.data;
    },
  });
};

/**
 * Hook to get smart matching analytics
 */
export const useMatchAnalytics = (timeRange = 'all') => {
  return useQuery({
    queryKey: ['match-analytics', timeRange],
    queryFn: async () => {
      const response = await client.get('/match/analytics', {
        params: { time_range: timeRange },
      });
      return response.data;
    },
  });
};

/**
 * Hook to record a match interaction (accept/reject)
 */
export const useRecordMatch = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data) => {
      const response = await client.post('/match/record', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate analytics to refresh counts
      queryClient.invalidateQueries({ queryKey: ['match-analytics'] });
    },
  });
};
