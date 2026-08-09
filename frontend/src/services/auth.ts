import { api, setAuthToken, clearAuthToken } from './api';
import { useUserStore } from '../stores/userStore';

export const authService = {
  async login(credentials: LoginCredentials) {
    const response = await api.post('/auth/login', {
      email: credentials.email,
      password: credentials.password,
    });

    const token = response.data?.data?.access_token;

    if (!token) {
      throw new Error('Login failed');
    }

    await setAuthToken(token);

    const meResponse = await api.get('/users/me');
    const user = meResponse.data?.data;

    if (!user) {
      throw new Error('Failed to load user profile');
    }

    useUserStore.getState().setUser(user);
    return user;
  },

  async register(data: RegisterData) {
    await api.post('/auth/register', data);

    return this.login({
      email: data.email,
      password: data.password,
    });
  },

  async logout() {
    await clearAuthToken();
    useUserStore.getState().logout();
  },
};

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  name: string;
}