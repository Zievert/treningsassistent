import apiClient from './api';
import type { Muscle, MusclePriority, AntagonisticPair } from '../types/api';

export const muscleService = {
  async getAllMuscles(): Promise<Muscle[]> {
    const response = await apiClient.get<Muscle[]>('/api/muskler/');
    return response.data;
  },

  async getMusclePriorities(): Promise<MusclePriority[]> {
    const response = await apiClient.get<MusclePriority[]>('/api/muskler/prioritet');
    return response.data;
  },

  async getMuscleById(muskelId: number): Promise<Muscle> {
    const response = await apiClient.get<Muscle>(`/api/muskler/${muskelId}`);
    return response.data;
  },

  async getAntagonisticPairs(): Promise<AntagonisticPair[]> {
    const response = await apiClient.get<AntagonisticPair[]>('/api/muskler/antagonistiske-par');
    return response.data;
  },
};
