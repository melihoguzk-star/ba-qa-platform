/**
 * Evaluation API — React Query hooks for BA/TC evaluation
 */
import { useMutation } from '@tanstack/react-query';
import client from './client';

/**
 * Evaluate BA document
 */
export const useEvaluateBA = () => {
  return useMutation({
    mutationFn: async (requestData) => {
      const { data } = await client.post('/evaluate/ba', requestData);
      return data;
    },
  });
};

/**
 * Evaluate TC document
 */
export const useEvaluateTC = () => {
  return useMutation({
    mutationFn: async (requestData) => {
      const { data } = await client.post('/evaluate/tc', requestData);
      return data;
    },
  });
};
