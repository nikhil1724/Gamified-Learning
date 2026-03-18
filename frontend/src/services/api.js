import axios from "axios";

const resolveBaseApiUrl = () => {
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
    if (error?.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("auth:logout"));
    }
    return Promise.reject(error);
  }
);

export default api;
