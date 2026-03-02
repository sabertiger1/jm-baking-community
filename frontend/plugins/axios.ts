import axios from "axios";
import { alert } from "~/composables/use-toast";

export default defineNuxtPlugin(() => {
  const tokenName = useRuntimeConfig().public.AUTH_TOKEN;
  const axiosInstance = axios.create({
    // timeout removed to allow backend to handle timeouts
    baseURL: "/", // api calls already pass with /api
    withCredentials: true,
  });

  axiosInstance.interceptors.request.use(
    (config) => {
      const token = useCookie(tokenName).value;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    },
  );

  // Add response interceptor
  axiosInstance.interceptors.response.use(
    (response) => {
      if (response?.data?.message) alert.info(response.data.message as string);
      return response;
    },
    (error) => {
      const parserError = error?.response?.data?.detail?.details as string | undefined;
      if (parserError) {
        if (parserError === "BAD_RECIPE_DATA") {
          alert.error("导入失败：未识别到有效食谱数据。请使用“URL导入”粘贴页面链接，或在“HTML/JSON导入”中粘贴完整 HTML / schema.org Recipe JSON。");
        } else if (parserError === "CONNECTION_ERROR") {
          alert.error("导入失败：无法连接目标网页，请检查目标网站是否可访问。");
        } else if (parserError === "NO_RECIPE_DATA") {
          alert.error("导入失败：页面中没有可用的食谱结构化数据。");
        } else {
          alert.error(`导入失败：${parserError}`);
        }
      }
      if (typeof error?.response?.data?.detail === "string") {
        alert.error(error.response.data.detail as string);
      }
      if (error?.response?.data?.detail?.message) {
        alert.error(error.response.data.detail.message as string);
      };

      // If we receive a 401 Unauthorized response, clear the token cookie and redirect to login
      if (error?.response?.status === 401) {
        // If tokenCookie is not set, we may just be an unauthenticated user using the wrong API, so don't redirect
        const tokenCookie = useCookie(tokenName);
        if (tokenCookie.value) {
          tokenCookie.value = null;

          // Disable beforeunload warnings to prevent "Are you sure you want to leave?" popups
          window.onbeforeunload = null;
          window.location.href = "/login";
        }
      }

      return Promise.reject(error);
    },
  );

  return {
    provide: {
      axios: axiosInstance,
    },
  };
});
