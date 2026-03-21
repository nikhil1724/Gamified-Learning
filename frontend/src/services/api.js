import axios from "axios";

export const BASE_URL = (process.env.REACT_APP_API_URL || "https://gamified-learning.onrender.com/api")
  .trim()
  .replace(/\/+$/, "");

console.log("API BASE URL:", BASE_URL);

const baseURL = BASE_URL.endsWith("/api") ? BASE_URL : `${BASE_URL}/api`;

const api = axios.create({
  baseURL,
  timeout: 60000,
});

export const publicApi = axios.create({
  baseURL,
  timeout: 60000,
});

export const getApiErrorMessage = (error, fallback = "Request failed.") => {
  if (!error) {
    return fallback;
  }

  if (error.code === "ECONNABORTED" || /timeout/i.test(error.message || "")) {
    return "Server waking up, please wait...";
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
    const isTimeout = error?.code === "ECONNABORTED" || /timeout/i.test(error?.message || "");
    const config = error?.config || {};
    if (isTimeout && !config.__timeoutRetried) {
      config.__timeoutRetried = true;
      return new Promise((resolve) => {
        setTimeout(() => resolve(api(config)), 1200);
      });
    }

    console.error("API request failed:", error);
    if (error?.response?.status === 401 || error?.response?.status === 422) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("auth:logout"));
    }

    error.userMessage = getApiErrorMessage(error);
    return Promise.reject(error);
  }
);

publicApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const isTimeout = error?.code === "ECONNABORTED" || /timeout/i.test(error?.message || "");
    const config = error?.config || {};
    if (isTimeout && !config.__timeoutRetried) {
      config.__timeoutRetried = true;
      return new Promise((resolve) => {
        setTimeout(() => resolve(publicApi(config)), 1200);
      });
    }

    console.error("Public API request failed:", error);
    error.userMessage = getApiErrorMessage(error);
    return Promise.reject(error);
  }
);

export default api;
