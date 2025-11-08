import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Card, Alert } from '../components/common';

interface LoginFormData {
  brukernavn: string;
  passord: string;
}

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      setIsLoading(true);
      await login(data);
      // Navigation happens automatically via useEffect when isAuthenticated becomes true
    } catch (err: any) {
      setError(err.message || 'Innlogging feilet. Sjekk brukernavn og passord.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Treningsassistent
          </h1>
          <p className="text-gray-600">
            Logg inn for å fortsette
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
            placeholder="Skriv inn brukernavn"
            error={errors.brukernavn?.message}
            {...register('brukernavn', {
              required: 'Brukernavn er påkrevd',
              minLength: {
                value: 3,
                message: 'Brukernavn må være minst 3 tegn',
              },
            })}
          />

          <Input
            label="Passord"
            type="password"
            placeholder="Skriv inn passord"
            error={errors.passord?.message}
            {...register('passord', {
              required: 'Passord er påkrevd',
              minLength: {
                value: 6,
                message: 'Passord må være minst 6 tegn',
              },
            })}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isLoading}
          >
            Logg inn
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Har du ikke en konto?{' '}
            <Link
              to="/register"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Registrer deg her
            </Link>
          </p>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Registrering krever invitasjonskode
          </p>
        </div>
      </Card>
    </div>
  );
};
