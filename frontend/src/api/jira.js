/**
 * JIRA API — React Query hooks
 */
import { useQuery } from '@tanstack/react-query';
import client from './client';

// Query keys
export const jiraKeys = {
  all: ['jira'],
  projects: (email, token) => [...jiraKeys.all, 'projects', email],
  tasks: (projectKey, email, token, docType) => [...jiraKeys.all, 'tasks', projectKey, docType],
  taskDocument: (taskKey, email, token) => [...jiraKeys.all, 'task-doc', taskKey],
};

/**
 * Get JIRA projects
 */
export const useJIRAProjects = (email, token) => {
  return useQuery({
    queryKey: jiraKeys.projects(email, token),
    queryFn: async () => {
      const { data } = await client.get('/jira/projects', {
        params: { email, token }
      });
      return data;
    },
    enabled: !!email && !!token,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Get tasks from a JIRA project
 */
export const useJIRATasks = (projectKey, email, token, docType = null) => {
  return useQuery({
    queryKey: jiraKeys.tasks(projectKey, email, token, docType),
    queryFn: async () => {
      const { data } = await client.get('/jira/tasks', {
        params: {
          project_key: projectKey,
          email,
          token,
          doc_type: docType
        }
      });
      return data;
    },
    enabled: !!projectKey && !!email && !!token,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Get document linked to a JIRA task
 */
export const useJIRATaskDocument = (taskKey, email, token) => {
  return useQuery({
    queryKey: jiraKeys.taskDocument(taskKey, email, token),
    queryFn: async () => {
      const { data} = await client.get(`/jira/tasks/${taskKey}/document`, {
        params: { email, token }
      });
      return data;
    },
    enabled: !!taskKey && !!email && !!token,
  });
};
