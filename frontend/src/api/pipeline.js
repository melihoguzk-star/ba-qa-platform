/**
 * Pipeline API — React Query hooks
 */
import { useQuery, useMutation } from '@tanstack/react-query';
import client from './client';

// Query keys
export const pipelineKeys = {
  all: ['pipeline'],
  status: (runId) => [...pipelineKeys.all, 'status', runId],
};

/**
 * Start pipeline
 */
export const useStartPipeline = () => {
  return useMutation({
    mutationFn: async (requestData) => {
      const { data } = await client.post('/pipeline/start', requestData);
      return data;
    },
  });
};

/**
 * Get pipeline status (for polling)
 */
export const usePipelineStatus = (runId, options = {}) => {
  return useQuery({
    queryKey: pipelineKeys.status(runId),
    queryFn: async () => {
      const { data } = await client.get(`/pipeline/${runId}/status`);
      return data;
    },
    enabled: !!runId,
    refetchInterval: (data) => {
      // Stop polling when completed or failed
      if (!data) return false;
      if (data.status === 'completed' || data.status === 'failed') {
        return false;
      }
      return options.refetchInterval || 2000; // Poll every 2 seconds
    },
    ...options,
  });
};
