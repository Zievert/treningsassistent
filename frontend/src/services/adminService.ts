import apiClient from './api';
import type { Invitation, CreateInvitationRequest, User } from '../types/api';

export const adminService = {
  // Invitations
  async createInvitation(data?: CreateInvitationRequest): Promise<{ invitasjonskode: string; utloper_dato?: string }> {
    const response = await apiClient.post('/api/admin/invitasjoner', data || {});
    return response.data;
  },

  async getInvitations(): Promise<Invitation[]> {
    const response = await apiClient.get<Invitation[]>('/api/admin/invitasjoner');
    return response.data;
  },

  async deleteInvitation(invitasjonId: number): Promise<{ success: boolean }> {
    const response = await apiClient.delete(`/api/admin/invitasjoner/${invitasjonId}`);
    return response.data;
  },

  // Users
  async getUsers(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/api/admin/brukere');
    return response.data;
  },

  async deactivateUser(brukerId: number): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/api/admin/brukere/${brukerId}/deaktiver`);
    return response.data;
  },

  async activateUser(brukerId: number): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/api/admin/brukere/${brukerId}/aktiver`);
    return response.data;
  },

  async makeAdmin(brukerId: number): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/api/admin/brukere/${brukerId}/gjor-admin`);
    return response.data;
  },

  async getStats(): Promise<any> {
    const response = await apiClient.get('/api/admin/stats');
    return response.data;
  },
};
