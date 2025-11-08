import React, { useState } from 'react';
import type { Exercise } from '../../types';
import { Card } from '../common';

interface ExerciseCardProps {
  exercise: Exercise;
  prioritertMuskel?: string;
  dagerSidenTrent?: number | null;
  prioritetScore?: number;
  showDetails?: boolean;
}

export const ExerciseCard: React.FC<ExerciseCardProps> = ({
  exercise,
  prioritertMuskel,
  dagerSidenTrent,
  prioritetScore,
  showDetails = true,
}) => {
  const [showInstructions, setShowInstructions] = useState(false);
  const [imageError, setImageError] = useState(false);

  const imageUrl = exercise.bilde_1_url;

  // Separate primary and secondary muscles
  const primaryMuscles = exercise.muskler.filter(m => m.muskel_type === 'primar');
  const secondaryMuscles = exercise.muskler.filter(m => m.muskel_type === 'sekundar');

  return (
    <Card className="overflow-hidden">
      <div className="md:flex">
        {/* Image section */}
        <div className="md:w-1/3 bg-gray-100 flex items-center justify-center p-4">
          {imageUrl && !imageError ? (
            <img
              src={imageUrl}
              alt={exercise.ovelse_navn}
              className="max-w-full h-auto rounded"
              onError={() => setImageError(true)}
            />
          ) : (
            <div className="text-center text-gray-400 py-12">
              <svg
                className="mx-auto h-24 w-24 mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="text-sm">Bilde ikke tilgjengelig</p>
            </div>
          )}
        </div>

        {/* Content section */}
        <div className="md:w-2/3 p-6">
          {/* Exercise name */}
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {exercise.ovelse_navn}
          </h2>

          {/* Priority info */}
          {prioritertMuskel && (
            <div className="mb-4 p-3 bg-primary-50 border border-primary-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-primary-900 font-medium">
                    🎯 Fokus: {prioritertMuskel}
                  </p>
                  {dagerSidenTrent !== null && dagerSidenTrent !== undefined && (
                    <p className="text-xs text-primary-700 mt-1">
                      {dagerSidenTrent === 0
                        ? 'Trent i dag'
                        : dagerSidenTrent === 1
                        ? 'Trent i går'
                        : `${dagerSidenTrent} dager siden sist trent`}
                    </p>
                  )}
                </div>
                {prioritetScore !== undefined && (
                  <div className="text-right">
                    <p className="text-xs text-primary-700">Prioritet</p>
                    <p className="text-lg font-bold text-primary-900">
                      {Math.round(prioritetScore)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Muscles */}
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">
              Muskler
            </h3>
            <div className="space-y-1">
              {primaryMuscles.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-gray-500">Primær:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {primaryMuscles.map((muskel) => (
                      <span
                        key={muskel.muskel_id}
                        className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                      >
                        {muskel.muskel_navn}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {secondaryMuscles.length > 0 && (
                <div className="mt-2">
                  <span className="text-xs font-medium text-gray-500">Sekundær:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {secondaryMuscles.map((muskel) => (
                      <span
                        key={muskel.muskel_id}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {muskel.muskel_navn}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Equipment */}
          {exercise.utstyr && exercise.utstyr.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Utstyr
              </h3>
              <div className="flex flex-wrap gap-1">
                {exercise.utstyr.map((utstyr) => (
                  <span
                    key={utstyr.utstyr_id}
                    className="px-2 py-1 bg-gray-200 text-gray-800 text-xs rounded-full"
                  >
                    {utstyr.utstyr_navn}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Instructions (collapsible) */}
          {showDetails && exercise.instruksjoner && (
            <div className="mt-4 border-t pt-4">
              <button
                onClick={() => setShowInstructions(!showInstructions)}
                className="flex items-center justify-between w-full text-left"
              >
                <h3 className="text-sm font-semibold text-gray-700">
                  Instruksjoner
                </h3>
                <svg
                  className={`h-5 w-5 text-gray-500 transition-transform ${
                    showInstructions ? 'transform rotate-180' : ''
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              {showInstructions && (
                <div className="mt-2 text-sm text-gray-600 whitespace-pre-line">
                  {exercise.instruksjoner}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};
