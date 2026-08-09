import axios, { AxiosInstance } from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_BASE_URL = "http://10.0.2.2:8000/api/v1";

const TOKEN_KEY = "kitabee_access_token";

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      AsyncStorage.removeItem(TOKEN_KEY);
    }
    return Promise.reject(error);
  }
);

export async function setAuthToken(token: string): Promise<void> {
  await AsyncStorage.setItem(TOKEN_KEY, token);
}

export async function clearAuthToken(): Promise<void> {
  await AsyncStorage.removeItem(TOKEN_KEY);
}