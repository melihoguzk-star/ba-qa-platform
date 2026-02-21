/**
 * API Client — Axios instance with interceptors
 */
import axios from 'axios';

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 120000, // 2 minutes for AI evaluation requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
client.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status } = error.response;
      if (status === 401) console.error('Unauthorized');
      else if (status === 500) console.error('Server error');
    }
    return Promise.reject(error);
  }
);

export default client;
