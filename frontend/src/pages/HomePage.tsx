import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MainLayout } from '../components/layout';
import { ExerciseCard } from '../components/features/ExerciseCard';
import { ExerciseLoggingForm } from '../components/features/ExerciseLoggingForm';
import { Card, SkeletonExerciseCard, Confetti, Button } from '../components/common';
import { exerciseService, historyService, equipmentService } from '../services';
import { useToast } from '../context/ToastContext';
import type { ExerciseRecommendation, ExerciseLog, EquipmentProfile, ExerciseListItem, Exercise } from '../types';

export const HomePage: React.FC = () => {
  const [recommendation, setRecommendation] = useState<ExerciseRecommendation | null>(null);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [recentHistory, setRecentHistory] = useState<ExerciseLog[]>([]);
  const [activeProfile, setActiveProfile] = useState<EquipmentProfile | null>(null);
  const [isLoadingRecommendation, setIsLoadingRecommendation] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [availableExercises, setAvailableExercises] = useState<ExerciseListItem[]>([]);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);
  const toast = useToast();

  const fetchRecommendation = async () => {
    try {
      setIsLoadingRecommendation(true);
      const data = await exerciseService.getNextRecommendation();
      setRecommendation(data);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Kunne ikke hente øvelsesanbefaling');
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

  const fetchAvailableExercises = async () => {
    try {
      setIsLoadingExercises(true);
      const exercises = await exerciseService.getAvailableExercises({ limit: 50 });
      setAvailableExercises(exercises);
    } catch (err: any) {
      toast.error('Kunne ikke hente tilgjengelige øvelser');
    } finally {
      setIsLoadingExercises(false);
    }
  };

  const handleSelectExercise = async (exerciseId: number) => {
    try {
      const exercise = await exerciseService.getExerciseById(exerciseId);
      setSelectedExercise(exercise);
      setShowExerciseModal(false);
      toast.success('Øvelse valgt!');
    } catch (err: any) {
      toast.error('Kunne ikke hente øvelsesdetaljer');
    }
  };

  const handleOpenExerciseSelector = () => {
    setShowExerciseModal(true);
    fetchAvailableExercises();
  };

  const handleUseRecommendation = () => {
    setSelectedExercise(null);
  };

  const handleExerciseLogged = () => {
    // Show confetti celebration
    setShowConfetti(true);
    setTimeout(() => setShowConfetti(false), 100);

    // Show success toast
    toast.success('Øvelse logget! Bra jobbet!');

    // Reset selected exercise
    setSelectedExercise(null);

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

        {/* Confetti celebration */}
        <Confetti active={showConfetti} />

        {/* Loading state */}
        {isLoadingRecommendation && <SkeletonExerciseCard />}

        {/* Recommendation or Selected Exercise */}
        {!isLoadingRecommendation && recommendation && (
          <div className="space-y-6">
            {/* Exercise display */}
            {selectedExercise ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Valgt øvelse
                  </h2>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleUseRecommendation}
                  >
                    Bruk anbefaling
                  </Button>
                </div>
                <ExerciseCard
                  exercise={selectedExercise}
                  showDetails={true}
                />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Anbefalt øvelse
                  </h2>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleOpenExerciseSelector}
                  >
                    Velg annen øvelse
                  </Button>
                </div>
                <ExerciseCard
                  exercise={recommendation.ovelse}
                  prioritertMuskel={recommendation.prioritert_muskel}
                  dagerSidenTrent={recommendation.dager_siden_trent}
                  prioritetScore={recommendation.prioritet_score}
                  showDetails={true}
                />
              </div>
            )}

            {/* Logging form */}
            <ExerciseLoggingForm
              ovelseId={selectedExercise ? selectedExercise.ovelse_id : recommendation.ovelse.ovelse_id}
              ovelseName={selectedExercise ? selectedExercise.ovelse_navn : recommendation.ovelse.ovelse_navn}
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

        {/* Exercise Selector Modal */}
        {showExerciseModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden animate-scale-in">
              {/* Modal header */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">
                  Velg en øvelse
                </h2>
                <button
                  onClick={() => setShowExerciseModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Modal content */}
              <div className="px-6 py-4 overflow-y-auto max-h-[calc(80vh-120px)]">
                {isLoadingExercises ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    <p className="mt-2 text-gray-600">Laster øvelser...</p>
                  </div>
                ) : availableExercises.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-600">Ingen øvelser tilgjengelig med ditt utstyr.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {availableExercises.map((exercise) => (
                      <button
                        key={exercise.ovelse_id}
                        onClick={() => handleSelectExercise(exercise.ovelse_id)}
                        className="text-left p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all"
                      >
                        <div className="flex gap-4">
                          {/* Exercise image */}
                          {exercise.bilde_1_url && (
                            <img
                              src={exercise.bilde_1_url}
                              alt={exercise.ovelse_navn}
                              className="w-24 h-24 object-cover rounded"
                            />
                          )}

                          {/* Exercise info */}
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 mb-1">
                              {exercise.ovelse_navn}
                            </h3>

                            {/* Primary muscles */}
                            {exercise.primary_muscles.length > 0 && (
                              <div className="flex flex-wrap gap-1 mb-2">
                                {exercise.primary_muscles.map((muskel, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 bg-primary-100 text-primary-700 text-xs rounded"
                                  >
                                    {muskel}
                                  </span>
                                ))}
                              </div>
                            )}

                            {/* Equipment and level */}
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              {exercise.equipment && (
                                <span className="flex items-center gap-1">
                                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                  </svg>
                                  {exercise.equipment}
                                </span>
                              )}
                              {exercise.level && (
                                <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                                  {exercise.level}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Modal footer */}
              <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
                <Button
                  variant="outline"
                  onClick={() => setShowExerciseModal(false)}
                >
                  Avbryt
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
};
