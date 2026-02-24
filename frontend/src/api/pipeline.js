/**
 * Pipeline API — React Query hooks
 */
import { useQuery, useMutation } from '@tanstack/react-query';
import client from './client';

// Query keys
export const pipelineKeys = {
  all: ['pipeline'],
  runs: () => [...pipelineKeys.all, 'runs'],
  status: (runId) => [...pipelineKeys.all, 'status', runId],
};

/**
 * Get recent pipeline runs
 */
export const usePipelineRuns = (limit = 100) => {
  return useQuery({
    queryKey: [...pipelineKeys.runs(), limit],
    queryFn: async () => {
      const { data } = await client.get('/reports/pipeline-runs', {
        params: { limit },
      });
      return data;
    },
  });
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

/**
 * Get pipeline results
 */
export const usePipelineResults = (runId, options = {}) => {
  return useQuery({
    queryKey: [...pipelineKeys.status(runId), 'results'],
    queryFn: async () => {
      const { data } = await client.get(`/pipeline/${runId}/results`);
      return data;
    },
    enabled: !!runId,
    ...options,
  });
};

/**
 * Execute single stage (ba_gen, ta_gen, tc_gen)
 */
export const useExecuteStage = () => {
  return useMutation({
    mutationFn: async ({ runId, stage, feedback = '' }) => {
      const { data } = await client.post(`/pipeline/${runId}/execute-stage`, null, {
        params: { stage, feedback }
      });
      return data;
    },
  });
};

/**
 * Evaluate QA for a stage
 */
export const useEvaluateQA = () => {
  return useMutation({
    mutationFn: async ({ runId, stage, content, force_pass = false }) => {
      const { data } = await client.post(`/pipeline/${runId}/evaluate-qa`, content, {
        params: { stage, force_pass }
      });
      return data;
    },
  });
};

/**
 * Get checkpoint data
 */
export const useCheckpoint = (runId, stage, options = {}) => {
  return useQuery({
    queryKey: [...pipelineKeys.status(runId), 'checkpoint', stage],
    queryFn: async () => {
      const { data } = await client.get(`/pipeline/${runId}/checkpoint/${stage}`);
      return data;
    },
    enabled: !!runId && !!stage,
    ...options,
  });
};

/**
 * Save checkpoint data
 */
export const useSaveCheckpoint = () => {
  return useMutation({
    mutationFn: async ({ runId, stage, data }) => {
      const response = await client.post(`/pipeline/${runId}/checkpoint/${stage}`, data);
      return response.data;
    },
  });
};

/**
 * Download document (BA/TA/TC) in appropriate format
 */
export const downloadDocument = async (runId, docType) => {
  try {
    const response = await client.get(`/documents-export/${runId}/download/${docType}`, {
      responseType: 'blob'
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    // Set filename based on doc type
    const extension = docType === 'tc' ? 'xlsx' : 'docx';
    link.setAttribute('download', `${docType.toUpperCase()}_document.${extension}`);

    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

/**
 * Get document preview data
 */
export const useDocumentPreview = (runId, docType, options = {}) => {
  return useQuery({
    queryKey: [...pipelineKeys.status(runId), 'preview', docType],
    queryFn: async () => {
      const { data } = await client.get(`/documents-export/${runId}/preview/${docType}`);
      return data;
    },
    enabled: !!runId && !!docType,
    ...options,
  });
};
