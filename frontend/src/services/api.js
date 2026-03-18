import axios from "axios";

export const resolveBaseApiUrl = () => {
  const envApiUrl = (process.env.REACT_APP_API_URL || "").trim();
  if (envApiUrl) {
    return envApiUrl;
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return "http://127.0.0.1:5000";
    }

    return window.location.origin;
  }

  return "http://127.0.0.1:5000";
};

const rawApiUrl = resolveBaseApiUrl();
const normalizedApiUrl = rawApiUrl.replace(/\/+$/, "");
const baseURL = normalizedApiUrl.endsWith("/api")
  ? normalizedApiUrl
  : `${normalizedApiUrl}/api`;

const api = axios.create({
  baseURL,
  timeout: 15000,
});

export const publicApi = axios.create({
  baseURL,
  timeout: 15000,
});

export const getApiErrorMessage = (error, fallback = "Request failed.") => {
  if (!error) {
    return fallback;
  }

  const response = error.response?.data;
  if (typeof response === "string" && response.trim()) {
    return response;
  }

  if (response?.message) {
    return response.message;
  }

  if (response?.error) {
    return response.error;
  }

  if (error.message) {
    return error.message;
  }

  return fallback;
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (timezone) {
    config.headers["X-User-Timezone"] = timezone;
  }
  return config;
});

publicApi.interceptors.request.use((config) => {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (timezone) {
    config.headers["X-User-Timezone"] = timezone;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 || error?.response?.status === 422) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("auth:logout"));
    }

    error.userMessage = getApiErrorMessage(error);
    return Promise.reject(error);
  }
);

export default api;
