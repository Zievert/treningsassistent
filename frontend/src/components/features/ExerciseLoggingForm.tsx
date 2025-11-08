import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input, Card, Alert } from '../common';
import { exerciseService } from '../../services';
import type { LogExerciseRequest } from '../../types';

interface ExerciseLoggingFormProps {
  ovelseId: number;
  ovelseName: string;
  onSuccess?: () => void;
}

interface FormData {
  sett: number;
  repetisjoner: number;
  vekt: number;
}

export const ExerciseLoggingForm: React.FC<ExerciseLoggingFormProps> = ({
  ovelseId,
  ovelseName,
  onSuccess,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    try {
      setError(null);
      setSuccess(false);
      setIsLoading(true);

      const logData: LogExerciseRequest = {
        ovelse_id: ovelseId,
        sett: data.sett,
        repetisjoner: data.repetisjoner,
        vekt: data.vekt,
      };

      await exerciseService.logExercise(logData);

      setSuccess(true);
      reset();

      // Call onSuccess callback after a short delay
      setTimeout(() => {
        if (onSuccess) {
          onSuccess();
        }
      }, 500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke logge øvelse');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        📝 Logg øvelse: {ovelseName}
      </h3>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError(null)}
          className="mb-4"
        />
      )}

      {success && (
        <Alert
          type="success"
          message="Øvelse logget! Henter ny anbefaling..."
          className="mb-4"
        />
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Sett"
            type="number"
            placeholder="3"
            error={errors.sett?.message}
            {...register('sett', {
              required: 'Sett er påkrevd',
              min: {
                value: 1,
                message: 'Må være minst 1',
              },
              max: {
                value: 50,
                message: 'Kan være maks 50',
              },
              valueAsNumber: true,
            })}
          />

          <Input
            label="Repetisjoner"
            type="number"
            placeholder="10"
            error={errors.repetisjoner?.message}
            {...register('repetisjoner', {
              required: 'Repetisjoner er påkrevd',
              min: {
                value: 1,
                message: 'Må være minst 1',
              },
              max: {
                value: 500,
                message: 'Kan være maks 500',
              },
              valueAsNumber: true,
            })}
          />

          <Input
            label="Vekt (kg)"
            type="number"
            step="0.5"
            placeholder="50"
            error={errors.vekt?.message}
            {...register('vekt', {
              required: 'Vekt er påkrevd',
              min: {
                value: 0,
                message: 'Må være 0 eller mer',
              },
              max: {
                value: 1000,
                message: 'Kan være maks 1000 kg',
              },
              valueAsNumber: true,
            })}
          />
        </div>

        <div className="flex gap-2">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isLoading}
          >
            {isLoading ? 'Logger...' : 'Logg og hent neste øvelse'}
          </Button>
        </div>

        <p className="text-xs text-gray-500 text-center">
          Volum: {'{sett}'} × {'{reps}'} × {'{vekt}'} = Totalvolum
        </p>
      </form>
    </Card>
  );
};
