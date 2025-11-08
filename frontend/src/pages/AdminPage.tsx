import React, { useState, useEffect } from 'react';
import { MainLayout } from '../components/layout';
import { Card, Alert, Button, Input } from '../components/common';
import { adminService } from '../services';
import type { Invitation, User, CreateInvitationRequest } from '../types/api';

interface AdminStats {
  total_brukere: number;
  aktive_brukere: number;
  admin_brukere: number;
  total_invitasjoner: number;
  ubrukte_invitasjoner: number;
  total_ovelser: number;
  total_muskler: number;
  total_utstyr: number;
  total_loggede_ovelser: number;
}

export const AdminPage: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Create invitation form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newInvitationEmail, setNewInvitationEmail] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      setIsLoading(true);

      const [statsData, invitationsData, usersData] = await Promise.all([
        adminService.getStats(),
        adminService.getInvitations(),
        adminService.getUsers(),
      ]);

      setStats(statsData);
      setInvitations(invitationsData);
      setUsers(usersData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke hente admindata');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateInvitation = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setError(null);
      const data: CreateInvitationRequest = newInvitationEmail
        ? { epost: newInvitationEmail }
        : {};

      const result = await adminService.createInvitation(data);
      setSuccess(`Invitasjon opprettet! Kode: ${result.invitasjonskode}`);
      setShowCreateForm(false);
      setNewInvitationEmail('');
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke opprette invitasjon');
    }
  };

  const handleDeleteInvitation = async (invitationId: number) => {
    if (!window.confirm('Er du sikker på at du vil slette denne invitasjonen?')) {
      return;
    }

    try {
      setError(null);
      await adminService.deleteInvitation(invitationId);
      setSuccess('Invitasjon slettet!');
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke slette invitasjon');
    }
  };

  const handleToggleUserActive = async (userId: number, currentlyActive: boolean) => {
    try {
      setError(null);
      if (currentlyActive) {
        await adminService.deactivateUser(userId);
        setSuccess('Bruker deaktivert!');
      } else {
        await adminService.activateUser(userId);
        setSuccess('Bruker aktivert!');
      }
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke endre brukerstatus');
    }
  };

  const handleMakeAdmin = async (userId: number) => {
    if (!window.confirm('Er du sikker på at du vil gjøre denne brukeren til administrator?')) {
      return;
    }

    try {
      setError(null);
      await adminService.makeAdmin(userId);
      setSuccess('Bruker gjort til administrator!');
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke gjøre bruker til admin');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('nb-NO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin-panel</h1>
          <p className="text-gray-600 mt-1">
            Administrer brukere, invitasjoner og systemstatistikk
          </p>
        </div>

        {/* Alerts */}
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

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
                <p className="text-gray-600">Laster admindata...</p>
              </div>
            </div>
          </Card>
        )}

        {!isLoading && stats && (
          <>
            {/* Statistics Dashboard */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Systemstatistikk
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-blue-600 font-medium">Totale brukere</p>
                  <p className="text-3xl font-bold text-blue-900">{stats.total_brukere}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-green-600 font-medium">Aktive brukere</p>
                  <p className="text-3xl font-bold text-green-900">{stats.aktive_brukere}</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-600 font-medium">Administratorer</p>
                  <p className="text-3xl font-bold text-purple-900">{stats.admin_brukere}</p>
                </div>
                <div className="bg-orange-50 rounded-lg p-4">
                  <p className="text-sm text-orange-600 font-medium">Invitasjoner</p>
                  <p className="text-3xl font-bold text-orange-900">{stats.total_invitasjoner}</p>
                  <p className="text-xs text-orange-700 mt-1">{stats.ubrukte_invitasjoner} ubrukt</p>
                </div>
                <div className="bg-indigo-50 rounded-lg p-4">
                  <p className="text-sm text-indigo-600 font-medium">Loggede øvelser</p>
                  <p className="text-3xl font-bold text-indigo-900">{stats.total_loggede_ovelser}</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 font-medium">Øvelser i database</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_ovelser}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 font-medium">Muskelgrupper</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_muskler}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 font-medium">Utstyrstyper</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_utstyr}</p>
                </div>
              </div>
            </Card>

            {/* Invitation Management */}
            <Card>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Invitasjonskoder
                </h2>
                {!showCreateForm && (
                  <Button variant="primary" onClick={() => setShowCreateForm(true)}>
                    + Opprett invitasjon
                  </Button>
                )}
              </div>

              {/* Create invitation form */}
              {showCreateForm && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <form onSubmit={handleCreateInvitation} className="space-y-4">
                    <Input
                      label="E-post (valgfritt)"
                      type="email"
                      value={newInvitationEmail}
                      onChange={(e) => setNewInvitationEmail(e.target.value)}
                      placeholder="bruker@example.com"
                      helperText="La stå tom for å opprette en generell invitasjonskode"
                    />
                    <div className="flex gap-3">
                      <Button type="submit" variant="primary">
                        Opprett invitasjon
                      </Button>
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => {
                          setShowCreateForm(false);
                          setNewInvitationEmail('');
                        }}
                      >
                        Avbryt
                      </Button>
                    </div>
                  </form>
                </div>
              )}

              {/* Invitations list */}
              {invitations.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Ingen invitasjoner funnet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Invitasjonskode
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          E-post
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Opprettet
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Utløper
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Handlinger
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {invitations.map((invitation) => (
                        <tr key={invitation.invitasjon_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                              {invitation.invitasjonskode}
                            </code>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {invitation.epost || '—'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded ${
                                invitation.brukt
                                  ? 'bg-gray-100 text-gray-800'
                                  : 'bg-green-100 text-green-800'
                              }`}
                            >
                              {invitation.brukt ? 'Brukt' : 'Aktiv'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(invitation.opprettet_dato)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {invitation.utloper_dato ? formatDate(invitation.utloper_dato) : '—'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleDeleteInvitation(invitation.invitasjon_id)}
                            >
                              Slett
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            {/* User Management */}
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Brukerhåndtering
              </h2>
              {users.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Ingen brukere funnet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Brukernavn
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          E-post
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Rolle
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Opprettet
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Handlinger
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.bruker_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {user.brukernavn}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{user.epost}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded ${
                                user.rolle === 'admin'
                                  ? 'bg-purple-100 text-purple-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {user.rolle}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded ${
                                user.aktiv
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {user.aktiv ? 'Aktiv' : 'Inaktiv'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(user.opprettet_dato)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                            {user.rolle !== 'admin' && (
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => handleMakeAdmin(user.bruker_id)}
                              >
                                Gjør til admin
                              </Button>
                            )}
                            <Button
                              variant={user.aktiv ? 'danger' : 'primary'}
                              size="sm"
                              onClick={() => handleToggleUserActive(user.bruker_id, user.aktiv)}
                            >
                              {user.aktiv ? 'Deaktiver' : 'Aktiver'}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </>
        )}
      </div>
    </MainLayout>
  );
};
