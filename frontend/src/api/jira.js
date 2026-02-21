/**
 * JIRA API — React Query hooks
 * Uses server-side credentials from environment variables
 */
import { useQuery } from '@tanstack/react-query';
import client from './client';

// Query keys
export const jiraKeys = {
  all: ['jira'],
  status: () => [...jiraKeys.all, 'status'],
  projects: () => [...jiraKeys.all, 'projects'],
  tasks: (projectKey, docType) => [...jiraKeys.all, 'tasks', projectKey, docType],
  taskDocument: (taskKey) => [...jiraKeys.all, 'task-doc', taskKey],
};

/**
 * Get JIRA configuration status
 */
export const useJIRAStatus = () => {
  return useQuery({
    queryKey: jiraKeys.status(),
    queryFn: async () => {
      const { data } = await client.get('/jira/status');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Get JIRA projects
 * Uses credentials from backend configuration
 */
export const useJIRAProjects = () => {
  return useQuery({
    queryKey: jiraKeys.projects(),
    queryFn: async () => {
      const { data } = await client.get('/jira/projects');
      return data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Get tasks from a JIRA project
 * Uses credentials from backend configuration
 */
export const useJIRATasks = (projectKey, docType = null) => {
  return useQuery({
    queryKey: jiraKeys.tasks(projectKey, docType),
    queryFn: async () => {
      const { data } = await client.get('/jira/tasks', {
        params: {
          project_key: projectKey,
          doc_type: docType
        }
      });
      return data;
    },
    enabled: !!projectKey,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Get document linked to a JIRA task
 * Uses credentials from backend configuration
 */
export const useJIRATaskDocument = (taskKey) => {
  return useQuery({
    queryKey: jiraKeys.taskDocument(taskKey),
    queryFn: async () => {
      const { data } = await client.get(`/jira/tasks/${taskKey}/document`);
      return data;
    },
    enabled: !!taskKey,
  });
};
