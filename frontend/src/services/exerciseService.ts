import apiClient from './api';
import type {
  ExerciseRecommendation,
  Exercise,
  ExerciseListItem,
  LogExerciseRequest,
  LogExerciseResponse,
} from '../types/api';

export const exerciseService = {
  async getNextRecommendation(): Promise<ExerciseRecommendation> {
    const response = await apiClient.get<ExerciseRecommendation>('/api/ovelser/neste-anbefaling');
    return response.data;
  },

  async getAllExercises(params?: {
    kategori?: string;
    utstyr_id?: number;
    muskel_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<Exercise[]> {
    const response = await apiClient.get<Exercise[]>('/api/ovelser/alle', { params });
    return response.data;
  },

  async getAvailableExercises(params?: {
    muskel?: string;
    level?: string;
    force?: string;
    limit?: number;
  }): Promise<ExerciseListItem[]> {
    const response = await apiClient.get<ExerciseListItem[]>('/api/ovelser/tilgjengelige', { params });
    return response.data;
  },

  async getExerciseById(ovelseId: number): Promise<Exercise> {
    const response = await apiClient.get<Exercise>(`/api/ovelser/${ovelseId}`);
    return response.data;
  },

  async logExercise(data: LogExerciseRequest): Promise<LogExerciseResponse> {
    const response = await apiClient.post<LogExerciseResponse>('/api/ovelser/logg', data);
    return response.data;
  },
};
