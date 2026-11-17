import axios, {
  type AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import { backendBaseUrl } from "../../utils/constants";
import { useAuthStore } from "../../store/useAuthStore";

declare module "axios" {
  export interface AxiosRequestConfig {
    skipAuthInterceptor?: boolean;
    _retry?: boolean;
  }
}

let refreshPromise: Promise<void> | null = null;

const api = axios.create({
  baseURL: backendBaseUrl,
  withCredentials: true,
});

const redirectToLogin = () => {
  useAuthStore.getState().clearUser();
  if (!window.location.pathname.startsWith("/login")) {
    window.location.replace("/login");
  }
};

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as
      | InternalAxiosRequestConfig
      | undefined;

    if (
      !originalRequest ||
      error.response?.status !== 401 ||
      originalRequest.skipAuthInterceptor ||
      originalRequest._retry
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = api
        .post("/auth/refresh", undefined, { skipAuthInterceptor: true })
        .then(() => undefined)
        .finally(() => {
          refreshPromise = null;
        });
    }

    try {
      await refreshPromise;
    } catch (refreshError) {
      redirectToLogin();
      return Promise.reject(refreshError);
    }

    return api(originalRequest);
  },
);

export default api;
