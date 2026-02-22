/**
 * API Client — Axios instance with interceptors
 */
import axios from 'axios';
import { handleNetworkError } from '../utils/errorHandler';

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
    // Handle network errors globally (offline, timeout, connection refused)
    if (!error.response) {
      handleNetworkError(error);
    } else {
      // Log API errors in development
      if (process.env.NODE_ENV === 'development') {
        console.error('API Error:', {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          data: error.response?.data,
        });
      }
    }
    return Promise.reject(error);
  }
);

export default client;
