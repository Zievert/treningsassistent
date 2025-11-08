import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Card, Alert } from '../components/common';

interface RegisterFormData {
  brukernavn: string;
  epost: string;
  passord: string;
  bekreftPassord: string;
  invitasjonskode: string;
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { register: registerUser, isAuthenticated } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    defaultValues: {
      invitasjonskode: searchParams.get('code') || '',
    },
  });

  const passord = watch('passord');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      setIsLoading(true);

      // Remove bekreftPassord before sending to API
      const { bekreftPassord, ...registerData } = data;

      await registerUser(registerData);
      // Auto-login happens in registerUser, then redirect via useEffect
    } catch (err: any) {
      setError(
        err.message || 'Registrering feilet. Sjekk at invitasjonskoden er gyldig.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Opprett konto
          </h1>
          <p className="text-gray-600">
            Registrer deg med invitasjonskode
          </p>
        </div>

        {error && (
          <Alert
            type="error"
            message={error}
            onClose={() => setError(null)}
            className="mb-6"
          />
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Brukernavn"
            type="text"
            placeholder="Velg et brukernavn"
            error={errors.brukernavn?.message}
            {...register('brukernavn', {
              required: 'Brukernavn er påkrevd',
              minLength: {
                value: 3,
                message: 'Brukernavn må være minst 3 tegn',
              },
              maxLength: {
                value: 50,
                message: 'Brukernavn kan være maks 50 tegn',
              },
              pattern: {
                value: /^[a-zA-Z0-9_]+$/,
                message: 'Brukernavn kan kun inneholde bokstaver, tall og underscore',
              },
            })}
          />

          <Input
            label="E-post"
            type="email"
            placeholder="din@epost.no"
            error={errors.epost?.message}
            {...register('epost', {
              required: 'E-post er påkrevd',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Ugyldig e-postadresse',
              },
            })}
          />

          <Input
            label="Passord"
            type="password"
            placeholder="Minst 6 tegn"
            error={errors.passord?.message}
            {...register('passord', {
              required: 'Passord er påkrevd',
              minLength: {
                value: 6,
                message: 'Passord må være minst 6 tegn',
              },
            })}
          />

          <Input
            label="Bekreft passord"
            type="password"
            placeholder="Skriv passordet på nytt"
            error={errors.bekreftPassord?.message}
            {...register('bekreftPassord', {
              required: 'Bekreft passord',
              validate: (value) =>
                value === passord || 'Passordene matcher ikke',
            })}
          />

          <Input
            label="Invitasjonskode"
            type="text"
            placeholder="Skriv inn invitasjonskode"
            error={errors.invitasjonskode?.message}
            helperText="Du må ha en invitasjonskode for å registrere deg"
            {...register('invitasjonskode', {
              required: 'Invitasjonskode er påkrevd',
            })}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isLoading}
          >
            Registrer deg
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Har du allerede en konto?{' '}
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Logg inn her
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};
