import apiClient from './api';
import type {
  MuscleHeatmapData,
  AntagonisticPair,
  VolumeOverTime,
  MuscleStatistics,
} from '../types/api';

export const statisticsService = {
  async getHeatmap(siste_dager: number = 30): Promise<{ muskler: MuscleHeatmapData[] }> {
    const response = await apiClient.get<{ muskler: MuscleHeatmapData[] }>(
      '/api/statistikk/heatmap',
      { params: { siste_dager } }
    );
    return response.data;
  },

  async getAntagonisticBalance(): Promise<AntagonisticPair[]> {
    const response = await apiClient.get<AntagonisticPair[]>(
      '/api/statistikk/antagonistisk-balanse'
    );
    return response.data;
  },

  async getVolumeOverTime(params?: {
    siste_dager?: number;
    gruppe_per?: 'dag' | 'uke' | 'maned';
  }): Promise<VolumeOverTime[]> {
    const response = await apiClient.get<VolumeOverTime[]>('/api/statistikk/volum-over-tid', {
      params,
    });
    return response.data;
  },

  async getMuscleStatistics(muskelId: number, siste_dager: number = 90): Promise<MuscleStatistics> {
    const response = await apiClient.get<MuscleStatistics>(
      `/api/statistikk/muskel/${muskelId}`,
      { params: { siste_dager } }
    );
    return response.data;
  },

  async getDashboard(): Promise<any> {
    const response = await apiClient.get('/api/statistikk/dashboard');
    return response.data;
  },
};
