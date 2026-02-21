/**
 * Documents API — React Query hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from './client';

// Query keys
export const documentKeys = {
  all: ['documents'],
  lists: () => [...documentKeys.all, 'list'],
  list: (filters) => [...documentKeys.lists(), filters],
  details: () => [...documentKeys.all, 'detail'],
  detail: (id) => [...documentKeys.details(), id],
  versions: (id) => [...documentKeys.detail(id), 'versions'],
};

/**
 * Get all documents
 */
export const useDocuments = (params = {}) => {
  return useQuery({
    queryKey: documentKeys.list(params),
    queryFn: async () => {
      const { data } = await client.get('/documents', { params });
      return data;
    },
  });
};

/**
 * Get single document
 */
export const useDocument = (id) => {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: async () => {
      const { data } = await client.get(`/documents/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

/**
 * Get document versions
 */
export const useDocumentVersions = (id) => {
  return useQuery({
    queryKey: documentKeys.versions(id),
    queryFn: async () => {
      const { data } = await client.get(`/documents/${id}/versions`);
      return data;
    },
    enabled: !!id,
  });
};

/**
 * Create document
 */
export const useCreateDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentData) => {
      const { data } = await client.post('/documents', documentData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
};

/**
 * Update document
 */
export const useUpdateDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...documentData }) => {
      const { data } = await client.put(`/documents/${id}`, documentData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(variables.id) });
    },
  });
};

/**
 * Delete document
 */
export const useDeleteDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      const { data } = await client.delete(`/documents/${id}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
};
