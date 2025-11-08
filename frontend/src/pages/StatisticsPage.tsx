import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { MainLayout } from '../components/layout';
import { Card, Alert, Button } from '../components/common';
import { statisticsService, historyService } from '../services';
import type { VolumeOverTime, AntagonisticPair, ExerciseLog } from '../types/api';

export const StatisticsPage: React.FC = () => {
  const [volumeData, setVolumeData] = useState<VolumeOverTime[]>([]);
  const [antagonisticData, setAntagonisticData] = useState<AntagonisticPair[]>([]);
  const [recentHistory, setRecentHistory] = useState<ExerciseLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<number>(30);

  useEffect(() => {
    fetchStatistics();
  }, [timeRange]);

  const fetchStatistics = async () => {
    try {
      setError(null);
      setIsLoading(true);

      const [volume, antagonistic, history] = await Promise.all([
        statisticsService.getVolumeOverTime(timeRange),
        statisticsService.getAntagonisticBalance(),
        historyService.getHistory({ siste_dager: timeRange, limit: 1000 }),
      ]);

      setVolumeData(volume);
      setAntagonisticData(antagonistic);
      setRecentHistory(history);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke hente statistikk');
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate personal records
  const calculatePersonalRecords = () => {
    const records: Record<string, { vekt: number; reps: number; dato: string }> = {};

    recentHistory.forEach((log) => {
      const currentRecord = records[log.ovelse_navn];
      if (!currentRecord || log.vekt > currentRecord.vekt) {
        records[log.ovelse_navn] = {
          vekt: log.vekt,
          reps: log.repetisjoner,
          dato: log.tidspunkt,
        };
      }
    });

    return Object.entries(records)
      .sort((a, b) => b[1].vekt - a[1].vekt)
      .slice(0, 5);
  };

  // Calculate muscle group frequency
  const calculateMuscleFrequency = () => {
    const muscleCount: Record<string, number> = {};

    recentHistory.forEach((log) => {
      log.involverte_muskler?.forEach((muskel) => {
        muscleCount[muskel] = (muscleCount[muskel] || 0) + 1;
      });
    });

    return Object.entries(muscleCount).sort((a, b) => b[1] - a[1]);
  };

  // Prepare volume chart data
  const getVolumeChartData = () => {
    if (volumeData.length === 0) return [];

    const dates = volumeData.map((d) => d.dato);
    const volumes = volumeData.map((d) => parseFloat(d.total_volum));

    return [
      {
        x: dates,
        y: volumes,
        type: 'scatter' as const,
        mode: 'lines+markers' as const,
        name: 'Total volum',
        line: { color: '#0284c7', width: 3 },
        marker: { size: 8 },
      },
    ];
  };

  // Prepare muscle frequency chart data
  const getMuscleFrequencyChartData = () => {
    const muscleFreq = calculateMuscleFrequency();
    const topMuscles = muscleFreq.slice(0, 10);

    return [
      {
        x: topMuscles.map((m) => m[1]),
        y: topMuscles.map((m) => m[0]),
        type: 'bar' as const,
        orientation: 'h' as const,
        marker: { color: '#0ea5e9' },
      },
    ];
  };

  // Prepare antagonistic balance chart data
  const getAntagonisticBalanceChartData = () => {
    if (antagonisticData.length === 0) return [];

    const labels = antagonisticData.map((pair) => `${pair.muskel_1_navn} vs ${pair.muskel_2_navn}`);
    const muskel1Data = antagonisticData.map((pair) => parseFloat(pair.muskel_1_volum));
    const muskel2Data = antagonisticData.map((pair) => parseFloat(pair.muskel_2_volum));

    return [
      {
        x: labels,
        y: muskel1Data,
        name: 'Muskel 1',
        type: 'bar' as const,
        marker: { color: '#10b981' },
      },
      {
        x: labels,
        y: muskel2Data,
        name: 'Muskel 2',
        type: 'bar' as const,
        marker: { color: '#f59e0b' },
      },
    ];
  };

  const personalRecords = calculatePersonalRecords();

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Statistikk</h1>
            <p className="text-gray-600 mt-1">Oversikt over din treningsprogress</p>
          </div>

          {/* Time range filters */}
          <div className="flex gap-2">
            <Button
              variant={timeRange === 7 ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setTimeRange(7)}
            >
              7 dager
            </Button>
            <Button
              variant={timeRange === 30 ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setTimeRange(30)}
            >
              30 dager
            </Button>
            <Button
              variant={timeRange === 90 ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setTimeRange(90)}
            >
              90 dager
            </Button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <Alert type="error" message={error} onClose={() => setError(null)} />
        )}

        {/* Loading */}
        {isLoading && (
          <Card>
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <svg
                  className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <p className="text-gray-600">Laster statistikk...</p>
              </div>
            </div>
          </Card>
        )}

        {!isLoading && (
          <>
            {/* Volume over time chart */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Volum over tid
              </h2>
              {volumeData.length > 0 ? (
                <Plot
                  data={getVolumeChartData()}
                  layout={{
                    autosize: true,
                    margin: { l: 50, r: 30, t: 30, b: 50 },
                    xaxis: { title: 'Periode' },
                    yaxis: { title: 'Total volum (kg)' },
                    hovermode: 'closest',
                    plot_bgcolor: '#f9fafb',
                    paper_bgcolor: 'white',
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%', height: '400px' }}
                />
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Ingen volumdata for valgt periode
                </p>
              )}
            </Card>

            {/* Muscle frequency chart */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Mest trente muskelgrupper
              </h2>
              {calculateMuscleFrequency().length > 0 ? (
                <Plot
                  data={getMuscleFrequencyChartData()}
                  layout={{
                    autosize: true,
                    margin: { l: 150, r: 30, t: 30, b: 50 },
                    xaxis: { title: 'Antall økter' },
                    yaxis: { title: '' },
                    plot_bgcolor: '#f9fafb',
                    paper_bgcolor: 'white',
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%', height: '500px' }}
                />
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Ingen treningsdata for valgt periode
                </p>
              )}
            </Card>

            {/* Antagonistic balance */}
            {antagonisticData.length > 0 && (
              <Card>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Muskelbalanse (Antagonistiske par)
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                  Sammenligning av trening mellom motstående muskelgrupper. Ideelt
                  sett bør søylene være relativt like for å unngå muskelubalanser.
                </p>
                <Plot
                  data={getAntagonisticBalanceChartData()}
                  layout={{
                    autosize: true,
                    barmode: 'group',
                    margin: { l: 50, r: 30, t: 30, b: 100 },
                    xaxis: { title: 'Antagonistisk par', tickangle: -45 },
                    yaxis: { title: 'Antall økter' },
                    plot_bgcolor: '#f9fafb',
                    paper_bgcolor: 'white',
                    showlegend: false,
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%', height: '400px' }}
                />
              </Card>
            )}

            {/* Personal records */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Personlige rekorder (siste {timeRange} dager)
              </h2>
              {personalRecords.length > 0 ? (
                <div className="space-y-3">
                  {personalRecords.map(([exercise, record]) => (
                    <div
                      key={exercise}
                      className="flex justify-between items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div>
                        <h3 className="font-medium text-gray-900">{exercise}</h3>
                        <p className="text-sm text-gray-600">
                          {new Date(record.dato).toLocaleDateString('nb-NO')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-primary-600">
                          {record.vekt} kg
                        </p>
                        <p className="text-sm text-gray-600">
                          {record.reps} repetisjoner
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Ingen personlige rekorder funnet i valgt periode
                </p>
              )}
            </Card>

            {/* Training insights */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Treningsinnsikt
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-gray-600">Total øvelser</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {recentHistory.length}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total volum</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {recentHistory
                      .reduce(
                        (sum, log) => sum + log.sett * log.repetisjoner * log.vekt,
                        0
                      )
                      .toLocaleString()}{' '}
                    kg
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Ulike muskelgrupper</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {calculateMuscleFrequency().length}
                  </p>
                </div>
              </div>
            </Card>
          </>
        )}
      </div>
    </MainLayout>
  );
};
