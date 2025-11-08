import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, Button } from '../components/common';

export const HomePage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Treningsassistent
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">
                Hei, {user?.brukernavn}!
              </span>
              <Button variant="ghost" onClick={logout}>
                Logg ut
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Velkommen til Treningsassistent! 💪
          </h2>
          <p className="text-gray-600 mb-4">
            Dette er hjemmesiden. Snart vil du kunne se øvelsesanbefalinger her.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Brukerinfo:</strong>
            </p>
            <ul className="mt-2 text-sm text-blue-700 space-y-1">
              <li>Brukernavn: {user?.brukernavn}</li>
              <li>E-post: {user?.epost}</li>
              <li>Rolle: {user?.rolle}</li>
              <li>Aktiv: {user?.aktiv ? 'Ja' : 'Nei'}</li>
            </ul>
          </div>
        </Card>
      </main>
    </div>
  );
};
