import React, { useState, useEffect } from 'react';
import { MainLayout } from '../components/layout';
import { Card, Alert, Button } from '../components/common';
import { historyService } from '../services';
import type { ExerciseLog } from '../types';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<ExerciseLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [daysFilter, setDaysFilter] = useState<number>(30);

  const fetchHistory = async () => {
    try {
      setError(null);
      setIsLoading(true);
      const data = await historyService.getHistory({
        siste_dager: daysFilter,
        limit: 100,
      });
      setHistory(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke hente historikk');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [daysFilter]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('nb-NO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('nb-NO', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Group history by date
  const groupedHistory = history.reduce((acc, log) => {
    const date = new Date(log.tidspunkt).toDateString();
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(log);
    return acc;
  }, {} as Record<string, ExerciseLog[]>);

  const sortedDates = Object.keys(groupedHistory).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime()
  );

  // Calculate total volume for a date
  const calculateDayVolume = (logs: ExerciseLog[]) => {
    return logs.reduce((sum, log) => sum + (log.sett * log.repetisjoner * log.vekt), 0);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Treningshistorikk
            </h1>
            <p className="text-gray-600 mt-1">
              Oversikt over alle dine loggede øvelser
            </p>
          </div>

          {/* Filter buttons */}
          <div className="flex gap-2">
            <Button
              variant={daysFilter === 7 ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setDaysFilter(7)}
            >
              7 dager
            </Button>
            <Button
              variant={daysFilter === 30 ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setDaysFilter(30)}
            >
              30 dager
            </Button>
            <Button
              variant={daysFilter === 90 ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setDaysFilter(90)}
            >
              90 dager
            </Button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <Alert
            type="error"
            message={error}
            onClose={() => setError(null)}
          />
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
                <p className="text-gray-600">Laster historikk...</p>
              </div>
            </div>
          </Card>
        )}

        {/* Empty state */}
        {!isLoading && history.length === 0 && (
          <Card>
            <div className="text-center py-12">
              <svg
                className="mx-auto h-24 w-24 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ingen historikk funnet
              </h3>
              <p className="text-gray-500 mb-4">
                Du har ikke logget noen øvelser de siste {daysFilter} dagene.
              </p>
              <Button variant="primary" onClick={() => window.location.href = '/'}>
                Gå til hjemmesiden
              </Button>
            </div>
          </Card>
        )}

        {/* History grouped by date */}
        {!isLoading && sortedDates.length > 0 && (
          <div className="space-y-6">
            {sortedDates.map((date) => {
              const logs = groupedHistory[date];
              const totalVolume = calculateDayVolume(logs);

              return (
                <Card key={date} padding="none">
                  {/* Date header */}
                  <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900">
                          {formatDate(logs[0].tidspunkt)}
                        </h2>
                        <p className="text-sm text-gray-600">
                          {logs.length} {logs.length === 1 ? 'øvelse' : 'øvelser'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Total volum</p>
                        <p className="text-xl font-bold text-primary-600">
                          {totalVolume.toLocaleString()} kg
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Exercises */}
                  <div className="divide-y divide-gray-200">
                    {logs.map((log) => (
                      <div
                        key={log.utfort_id}
                        className="px-6 py-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h3 className="font-medium text-gray-900">
                                {log.ovelse_navn}
                              </h3>
                              <span className="text-xs text-gray-500">
                                {formatTime(log.tidspunkt)}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              {log.sett} sett × {log.repetisjoner} reps × {log.vekt} kg
                            </p>
                            {log.involverte_muskler && log.involverte_muskler.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {log.involverte_muskler.map((muskel, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded"
                                  >
                                    {muskel}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="text-right ml-4">
                            <p className="text-sm font-semibold text-gray-900">
                              {(log.sett * log.repetisjoner * log.vekt).toLocaleString()} kg
                            </p>
                            <p className="text-xs text-gray-500">volum</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* Stats summary */}
        {!isLoading && history.length > 0 && (
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Oppsummering ({daysFilter} dager)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600">Total øvelser</p>
                <p className="text-2xl font-bold text-gray-900">{history.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Treningsdager</p>
                <p className="text-2xl font-bold text-gray-900">{sortedDates.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total volum</p>
                <p className="text-2xl font-bold text-gray-900">
                  {history.reduce((sum, log) => sum + (log.sett * log.repetisjoner * log.vekt), 0).toLocaleString()} kg
                </p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </MainLayout>
  );
};
