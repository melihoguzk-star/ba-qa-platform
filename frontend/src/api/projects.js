/**
 * Projects API — React Query hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from './client';

// Query keys
export const projectKeys = {
  all: ['projects'],
  lists: () => [...projectKeys.all, 'list'],
  list: (filters) => [...projectKeys.lists(), filters],
  details: () => [...projectKeys.all, 'detail'],
  detail: (id) => [...projectKeys.details(), id],
};

/**
 * Get all projects
 */
export const useProjects = (params = {}) => {
  return useQuery({
    queryKey: projectKeys.list(params),
    queryFn: async () => {
      const { data } = await client.get('/projects', { params });
      return data;
    },
  });
};

/**
 * Get single project
 */
export const useProject = (id) => {
  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: async () => {
      const { data } = await client.get(`/projects/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

/**
 * Create project
 */
export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (projectData) => {
      const { data } = await client.post('/projects', projectData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
};

/**
 * Update project
 */
export const useUpdateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...projectData }) => {
      const { data } = await client.put(`/projects/${id}`, projectData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(variables.id) });
    },
  });
};

/**
 * Delete project
 */
export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      const { data } = await client.delete(`/projects/${id}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
};
