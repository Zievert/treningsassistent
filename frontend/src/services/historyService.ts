import apiClient from './api';
import type { ExerciseLog, WorkoutSession } from '../types/api';

export const historyService = {
  async getHistory(params?: {
    siste_dager?: number;
    limit?: number;
  }): Promise<ExerciseLog[]> {
    const response = await apiClient.get<ExerciseLog[]>('/api/historikk/', { params });
    return response.data;
  },

  async getGroupedHistory(params?: {
    siste_dager?: number;
  }): Promise<WorkoutSession[]> {
    const response = await apiClient.get<WorkoutSession[]>('/api/historikk/gruppert', { params });
    return response.data;
  },

  async getRecentExercises(limit: number = 10): Promise<ExerciseLog[]> {
    const response = await apiClient.get<ExerciseLog[]>('/api/historikk/siste', {
      params: { limit },
    });
    return response.data;
  },

  async getWorkoutSession(dato: string): Promise<WorkoutSession> {
    const response = await apiClient.get<WorkoutSession>(`/api/historikk/treningsokt/${dato}`);
    return response.data;
  },
};
