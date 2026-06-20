import axios, {
  type AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios';
import { backendBaseUrl } from '../../utils/constants';
import { useAuthStore } from '../../store/useAuthStore';

declare module 'axios' {
  export interface AxiosRequestConfig {
    skipAuthInterceptor?: boolean;
    _retry?: boolean;
  }
}

let isRefreshing = false;
let failedQueue: {
  resolve: (value: void | PromiseLike<void>) => void;
  reject: (reason: unknown) => void;
}[] = [];

const api = axios.create({
  baseURL: backendBaseUrl,
  withCredentials: true,
});

const processQueue = (error: AxiosError | null = null): void => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve();
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      skipAuthInterceptor?: boolean;
      _retry?: boolean;
    };

    if (error.response?.status === 401 && originalRequest.skipAuthInterceptor) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && originalRequest._retry) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && originalRequest.url?.includes('/auth/refresh')) {
      useAuthStore.getState().clearUser();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise<void>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err: AxiosError) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await api.post('/auth/refresh');
        isRefreshing = false;
        processQueue();
        return api(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        processQueue(refreshError as AxiosError);
        useAuthStore.getState().clearUser();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
