import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("sai_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("sai_token");
        localStorage.removeItem("sai_user");
      }
      return Promise.reject(error);
    }

    if (error.response?.status === 422) {
      const detail = error.response.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((d: { msg: string }) => d.msg).join(", ")
        : typeof detail === "string"
          ? detail
          : "Data yang dikirim tidak valid.";
      return Promise.reject(new Error(message));
    }

    return Promise.reject(error);
  },
);

export default apiClient;
