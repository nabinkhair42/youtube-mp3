import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from './routes';

// Create axios instance with default config
export const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Add request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    // You can add auth token here if needed
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle global error responses
    const errorMessage = error.response?.data?.detail || 'An error occurred';
    console.error('API Error:', errorMessage);
    return Promise.reject(error);
  }
);

// Create and configure the React Query client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30 * 1000, // 30 seconds
    },
  },
});

export default axiosInstance;
