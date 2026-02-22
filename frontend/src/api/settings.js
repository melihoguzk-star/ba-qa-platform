/**
 * Settings API Client
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from './client';

// ============================================================================
// Gemini Keys
// ============================================================================

export const useGeminiKeys = () => {
  return useQuery({
    queryKey: ['gemini-keys'],
    queryFn: async () => {
      const response = await client.get('/settings/gemini-keys');
      return response.data;
    },
  });
};

export const useTestGeminiKey = () => {
  return useMutation({
    mutationFn: async (keyIndex) => {
      const response = await client.post('/settings/gemini-keys/test', {
        key_index: keyIndex,
      });
      return response.data;
    },
  });
};

// ============================================================================
// Anthropic Key (Read-only from environment)
// ============================================================================

export const useAnthropicKey = () => {
  return useQuery({
    queryKey: ['anthropic-key'],
    queryFn: async () => {
      const response = await client.get('/settings/anthropic-key');
      return response.data;
    },
  });
};

// ============================================================================
// Rotation Settings
// ============================================================================

export const useRotationSettings = () => {
  return useQuery({
    queryKey: ['rotation-settings'],
    queryFn: async () => {
      const response = await client.get('/settings/rotation');
      return response.data;
    },
  });
};

export const useUpdateRotationSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (settings) => {
      const response = await client.put('/settings/rotation', settings);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['rotation-settings']);
    },
  });
};

export const useResetAllKeys = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await client.post('/settings/rotation/reset');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['usage-statistics']);
    },
  });
};

// ============================================================================
// Statistics
// ============================================================================

export const useUsageStatistics = () => {
  return useQuery({
    queryKey: ['usage-statistics'],
    queryFn: async () => {
      const response = await client.get('/settings/statistics');
      return response.data;
    },
  });
};

// ============================================================================
// Vector Store
// ============================================================================

export const useVectorStoreConfig = () => {
  return useQuery({
    queryKey: ['vector-store-config'],
    queryFn: async () => {
      const response = await client.get('/settings/vector-store/config');
      return response.data;
    },
  });
};

export const useVectorStoreStats = () => {
  return useQuery({
    queryKey: ['vector-store-stats'],
    queryFn: async () => {
      const response = await client.get('/settings/vector-store/stats');
      return response.data;
    },
  });
};

export const useTestVectorSearch = () => {
  return useMutation({
    mutationFn: async ({ query, doc_type, top_k = 5 }) => {
      const response = await client.post('/settings/vector-store/search', {
        query,
        doc_type,
        top_k,
      });
      return response.data;
    },
  });
};

// ============================================================================
// Smart Matching Analytics
// ============================================================================

export const useSmartMatchingAnalytics = (timeRange = 'all') => {
  return useQuery({
    queryKey: ['smart-matching-analytics', timeRange],
    queryFn: async () => {
      const response = await client.get('/settings/smart-matching/analytics', {
        params: { time_range: timeRange },
      });
      return response.data;
    },
  });
};
