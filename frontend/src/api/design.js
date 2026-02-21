/**
 * Design Compliance API Client
 */
import { useMutation, useQuery } from '@tanstack/react-query';
import client from './client';

/**
 * Analyze design compliance (non-streaming)
 */
export const useAnalyzeDesign = () => {
  return useMutation({
    mutationFn: async (formData) => {
      const response = await client.post('/design/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout for vision AI
      });
      return response.data;
    },
  });
};

/**
 * Get available check types
 */
export const useCheckTypes = () => {
  return useQuery({
    queryKey: ['design-check-types'],
    queryFn: async () => {
      const response = await client.get('/design/check-types');
      return response.data.check_types;
    },
    staleTime: Infinity, // Check types don't change
  });
};

/**
 * Get supported vision models
 */
export const useVisionModels = () => {
  return useQuery({
    queryKey: ['design-models'],
    queryFn: async () => {
      const response = await client.get('/design/models');
      return response.data.models;
    },
    staleTime: Infinity, // Models don't change
  });
};

/**
 * Analyze design compliance with streaming progress
 *
 * @param {FormData} formData - Form data with ba_document, images, etc.
 * @param {Function} onProgress - Callback for progress events
 * @param {Function} onComplete - Callback for completion
 * @param {Function} onError - Callback for errors
 */
export const analyzeDesignStream = async (formData, { onProgress, onComplete, onError }) => {
  try {
    const response = await fetch(`${client.defaults.baseURL}/design/analyze-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = ''; // Buffer for incomplete chunks

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Parse SSE events (format: "data: {json}\n\n")
      // Split by double newline to get complete messages
      const messages = buffer.split('\n\n');

      // Keep the last incomplete message in buffer
      buffer = messages.pop() || '';

      // Process complete messages
      for (const message of messages) {
        const lines = message.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6); // Remove "data: " prefix
            try {
              const event = JSON.parse(jsonStr);

              if (event.event_type === 'complete') {
                onComplete?.(event.data);
              } else if (event.event_type === 'error') {
                onError?.(new Error(event.message));
              } else {
                onProgress?.(event);
              }
            } catch (e) {
              console.error('Failed to parse SSE event:', e, 'JSON:', jsonStr);
            }
          }
        }
      }
    }

    // Process any remaining buffered data
    if (buffer.trim()) {
      const lines = buffer.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6);
          try {
            const event = JSON.parse(jsonStr);
            if (event.event_type === 'complete') {
              onComplete?.(event.data);
            } else if (event.event_type === 'error') {
              onError?.(new Error(event.message));
            } else {
              onProgress?.(event);
            }
          } catch (e) {
            console.error('Failed to parse final SSE event:', e);
          }
        }
      }
    }
  } catch (error) {
    onError?.(error);
  }
};
