/**
 * Upload API — React Query hooks
 */
import { useMutation } from '@tanstack/react-query';
import client from './client';

/**
 * Upload file
 */
export const useUploadFile = () => {
  return useMutation({
    mutationFn: async (formData) => {
      const { data } = await client.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return data;
    },
  });
};
