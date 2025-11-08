import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MainLayout } from '../components/layout';
import { ExerciseCard } from '../components/features/ExerciseCard';
import { ExerciseLoggingForm } from '../components/features/ExerciseLoggingForm';
import { Card, Alert } from '../components/common';
import { exerciseService, historyService, equipmentService } from '../services';
import type { ExerciseRecommendation, ExerciseLog, EquipmentProfile } from '../types';

export const HomePage: React.FC = () => {
  const [recommendation, setRecommendation] = useState<ExerciseRecommendation | null>(null);
  const [recentHistory, setRecentHistory] = useState<ExerciseLog[]>([]);
  const [activeProfile, setActiveProfile] = useState<EquipmentProfile | null>(null);
  const [isLoadingRecommendation, setIsLoadingRecommendation] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendation = async () => {
    try {
      setError(null);
      setIsLoadingRecommendation(true);
      const data = await exerciseService.getNextRecommendation();
      setRecommendation(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke hente øvelsesanbefaling');
    } finally {
      setIsLoadingRecommendation(false);
    }
  };

  const fetchRecentHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const data = await historyService.getRecentExercises(10);
      setRecentHistory(data);
    } catch (err: any) {
      console.error('Kunne ikke hente historikk:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const fetchActiveProfile = async () => {
    try {
      const profile = await equipmentService.getActiveProfile();
      setActiveProfile(profile);
    } catch (err: any) {
      console.error('Kunne ikke hente aktiv profil:', err);
    }
  };

  useEffect(() => {
    fetchRecommendation();
    fetchRecentHistory();
    fetchActiveProfile();
  }, []);

  const handleExerciseLogged = () => {
    // Refresh both recommendation and history after logging
    fetchRecommendation();
    fetchRecentHistory();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Akkurat nå';
    if (diffMins < 60) return `${diffMins} min siden`;
    if (diffHours < 24) return `${diffHours} timer siden`;
    if (diffDays === 1) return 'I går';
    if (diffDays < 7) return `${diffDays} dager siden`;
    return date.toLocaleDateString('nb-NO');
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Din neste øvelse
          </h1>
          <p className="text-gray-600 mt-1">
            AI-drevet anbefaling basert på muskelprioritet og balanse
          </p>
        </div>

        {/* Active equipment profile */}
        {activeProfile && (
          <Card>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg
                  className="h-10 w-10 text-primary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                <div>
                  <p className="text-sm text-gray-600">Aktiv utstyrsprofil:</p>
                  <p className="font-semibold text-gray-900">{activeProfile.profil_navn}</p>
                  <p className="text-xs text-gray-500">
                    {activeProfile.utstyr.length} utstyr tilgjengelig
                  </p>
                </div>
              </div>
              <Link
                to="/utstyr"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Endre →
              </Link>
            </div>
          </Card>
        )}

        {/* Error */}
        {error && (
          <Alert
            type="error"
            message={error}
            onClose={() => setError(null)}
          />
        )}

        {/* Loading state */}
        {isLoadingRecommendation && (
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
                <p className="text-gray-600">Henter anbefaling...</p>
              </div>
            </div>
          </Card>
        )}

        {/* Recommendation */}
        {!isLoadingRecommendation && recommendation && (
          <div className="space-y-6">
            <ExerciseCard
              exercise={recommendation.ovelse}
              prioritertMuskel={recommendation.prioritert_muskel}
              dagerSidenTrent={recommendation.dager_siden_trent}
              prioritetScore={recommendation.prioritet_score}
              showDetails={true}
            />

            <ExerciseLoggingForm
              ovelseId={recommendation.ovelse.ovelse_id}
              ovelseName={recommendation.ovelse.ovelse_navn}
              onSuccess={handleExerciseLogged}
            />
          </div>
        )}

        {/* Recent history */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Nylig aktivitet
          </h2>

          {isLoadingHistory ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                Laster historikk...
              </div>
            </Card>
          ) : recentHistory.length === 0 ? (
            <Card>
              <div className="text-center py-8">
                <p className="text-gray-500 mb-2">
                  Ingen øvelser logget ennå
                </p>
                <p className="text-sm text-gray-400">
                  Logg din første øvelse ovenfor for å komme i gang!
                </p>
              </div>
            </Card>
          ) : (
            <Card padding="none">
              <div className="divide-y divide-gray-200">
                {recentHistory.map((log) => (
                  <div
                    key={log.utfort_id}
                    className="p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          {log.ovelse_navn}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {log.sett} sett × {log.repetisjoner} reps × {log.vekt} kg
                          <span className="mx-2">•</span>
                          <span className="font-medium">
                            Volum: {(log.sett * log.repetisjoner * log.vekt).toLocaleString()} kg
                          </span>
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
                        <p className="text-xs text-gray-500">
                          {formatDate(log.tidspunkt)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </MainLayout>
  );
};
