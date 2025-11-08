import apiClient from './api';
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '../types/api';

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', {
      brukernavn: credentials.brukernavn,
      passord: credentials.passord,
    });
    return response.data;
  },

  async register(data: RegisterRequest): Promise<{ success: boolean; bruker_id: number }> {
    const response = await apiClient.post('/api/auth/register', data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    // Client-side logout (clear localStorage)
    // Backend doesn't have logout endpoint (JWT is stateless)
    return Promise.resolve();
  },
};
