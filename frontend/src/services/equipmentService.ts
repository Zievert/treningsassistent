import apiClient from './api';
import type { Equipment, EquipmentProfile, CreateEquipmentProfileRequest } from '../types/api';

export const equipmentService = {
  async getAllEquipment(): Promise<Equipment[]> {
    const response = await apiClient.get<Equipment[]>('/api/utstyr/alle');
    return response.data;
  },

  async getProfiles(): Promise<EquipmentProfile[]> {
    const response = await apiClient.get<EquipmentProfile[]>('/api/utstyr/profiler');
    return response.data;
  },

  async getActiveProfile(): Promise<EquipmentProfile> {
    const response = await apiClient.get<EquipmentProfile>('/api/utstyr/profiler/aktiv');
    return response.data;
  },

  async createProfile(data: CreateEquipmentProfileRequest): Promise<{ profil_id: number; success: boolean }> {
    const response = await apiClient.post('/api/utstyr/profiler', data);
    return response.data;
  },

  async updateProfile(profilId: number, data: CreateEquipmentProfileRequest): Promise<{ success: boolean }> {
    const response = await apiClient.put(`/api/utstyr/profiler/${profilId}`, data);
    return response.data;
  },

  async activateProfile(profilId: number): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/api/utstyr/profiler/${profilId}/aktivere`);
    return response.data;
  },

  async deleteProfile(profilId: number): Promise<{ success: boolean }> {
    const response = await apiClient.delete(`/api/utstyr/profiler/${profilId}`);
    return response.data;
  },
};
