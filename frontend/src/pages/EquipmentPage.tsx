import React, { useState, useEffect } from 'react';
import { MainLayout } from '../components/layout';
import { Card, Alert, Button, Input } from '../components/common';
import { equipmentService } from '../services';
import type { Equipment, EquipmentProfile, CreateEquipmentProfileRequest } from '../types/api';

export const EquipmentPage: React.FC = () => {
  const [allEquipment, setAllEquipment] = useState<Equipment[]>([]);
  const [profiles, setProfiles] = useState<EquipmentProfile[]>([]);
  const [activeProfile, setActiveProfile] = useState<EquipmentProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [isCreating, setIsCreating] = useState(false);
  const [editingProfileId, setEditingProfileId] = useState<number | null>(null);
  const [formName, setFormName] = useState('');
  const [selectedEquipmentIds, setSelectedEquipmentIds] = useState<number[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      setIsLoading(true);

      const [equipment, profilesList] = await Promise.all([
        equipmentService.getAllEquipment(),
        equipmentService.getProfiles(),
      ]);

      setAllEquipment(equipment);
      setProfiles(profilesList);

      const active = profilesList.find(p => p.aktiv);
      setActiveProfile(active || null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke hente utstyr');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateNew = () => {
    setIsCreating(true);
    setEditingProfileId(null);
    setFormName('');
    setSelectedEquipmentIds([]);
  };

  const handleEdit = (profile: EquipmentProfile) => {
    setIsCreating(false);
    setEditingProfileId(profile.profil_id);
    setFormName(profile.profil_navn);
    setSelectedEquipmentIds(profile.utstyr.map(e => e.utstyr_id));
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingProfileId(null);
    setFormName('');
    setSelectedEquipmentIds([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formName.trim()) {
      setError('Profilnavn er påkrevd');
      return;
    }

    if (selectedEquipmentIds.length === 0) {
      setError('Velg minst ett utstyr');
      return;
    }

    try {
      setError(null);
      const data: CreateEquipmentProfileRequest = {
        profil_navn: formName,
        utstyr_ids: selectedEquipmentIds,
      };

      if (editingProfileId !== null) {
        await equipmentService.updateProfile(editingProfileId, data);
        setSuccess('Profil oppdatert!');
      } else {
        await equipmentService.createProfile(data);
        setSuccess('Profil opprettet!');
      }

      handleCancel();
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke lagre profil');
    }
  };

  const handleActivate = async (profileId: number) => {
    try {
      setError(null);
      await equipmentService.activateProfile(profileId);
      setSuccess('Profil aktivert!');
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke aktivere profil');
    }
  };

  const handleDelete = async (profileId: number) => {
    if (!window.confirm('Er du sikker på at du vil slette denne profilen?')) {
      return;
    }

    try {
      setError(null);
      await equipmentService.deleteProfile(profileId);
      setSuccess('Profil slettet!');
      await fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kunne ikke slette profil');
    }
  };

  const toggleEquipment = (equipmentId: number) => {
    setSelectedEquipmentIds(prev =>
      prev.includes(equipmentId)
        ? prev.filter(id => id !== equipmentId)
        : [...prev, equipmentId]
    );
  };

  const selectAllInCategory = (category: string) => {
    const categoryEquipment = allEquipment.filter(e => e.kategori === category);
    const allSelected = categoryEquipment.every(e => selectedEquipmentIds.includes(e.utstyr_id));

    if (allSelected) {
      // Deselect all in category
      setSelectedEquipmentIds(prev =>
        prev.filter(id => !categoryEquipment.some(e => e.utstyr_id === id))
      );
    } else {
      // Select all in category
      const newIds = categoryEquipment.map(e => e.utstyr_id);
      setSelectedEquipmentIds(prev => [...new Set([...prev, ...newIds])]);
    }
  };

  // Group equipment by category
  const equipmentByCategory = allEquipment.reduce((acc, equipment) => {
    const category = equipment.kategori || 'annet';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(equipment);
    return acc;
  }, {} as Record<string, Equipment[]>);

  const categoryNames: Record<string, string> = {
    kroppsvekt: 'Kroppsvekt',
    fri_vekt: 'Fri vekt',
    maskin: 'Maskiner',
    kabel: 'Kabel',
    annet: 'Annet',
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Utstyrsprofiler</h1>
            <p className="text-gray-600 mt-1">
              Administrer tilgjengelig treningsutstyr for bedre anbefalinger
            </p>
          </div>
          {!isCreating && editingProfileId === null && (
            <Button variant="primary" onClick={handleCreateNew}>
              + Ny profil
            </Button>
          )}
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
                <p className="text-gray-600">Laster utstyr...</p>
              </div>
            </div>
          </Card>
        )}

        {!isLoading && (
          <>
            {/* Active profile indicator */}
            {activeProfile && !isCreating && editingProfileId === null && (
              <Card>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">Aktiv profil:</h3>
                    <p className="text-lg text-primary-600 font-medium">{activeProfile.profil_navn}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {activeProfile.utstyr.length} utstyr tilgjengelig
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="secondary" size="sm" onClick={() => handleEdit(activeProfile)}>
                      Rediger
                    </Button>
                  </div>
                </div>
              </Card>
            )}

            {/* Create/Edit form */}
            {(isCreating || editingProfileId !== null) && (
              <Card>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">
                      {editingProfileId !== null ? 'Rediger profil' : 'Opprett ny profil'}
                    </h2>
                  </div>

                  {/* Profile name */}
                  <Input
                    label="Profilnavn"
                    type="text"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    placeholder="F.eks. Hjemmegym, Fullstendig, Minimalt"
                    required
                  />

                  {/* Equipment selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Velg tilgjengelig utstyr
                    </label>

                    <div className="space-y-4">
                      {Object.entries(equipmentByCategory).map(([category, equipment]) => {
                        const allInCategorySelected = equipment.every(e =>
                          selectedEquipmentIds.includes(e.utstyr_id)
                        );

                        return (
                          <div key={category} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                              <h3 className="font-semibold text-gray-900">
                                {categoryNames[category] || category}
                              </h3>
                              <button
                                type="button"
                                onClick={() => selectAllInCategory(category)}
                                className="text-sm text-primary-600 hover:text-primary-700"
                              >
                                {allInCategorySelected ? 'Fjern alle' : 'Velg alle'}
                              </button>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                              {equipment.map((eq) => (
                                <label
                                  key={eq.utstyr_id}
                                  className="flex items-center p-2 rounded hover:bg-gray-50 cursor-pointer"
                                >
                                  <input
                                    type="checkbox"
                                    checked={selectedEquipmentIds.includes(eq.utstyr_id)}
                                    onChange={() => toggleEquipment(eq.utstyr_id)}
                                    className="h-4 w-4 text-primary-600 rounded focus:ring-primary-500"
                                  />
                                  <span className="ml-2 text-sm text-gray-700 capitalize">
                                    {eq.utstyr_navn}
                                  </span>
                                </label>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Form actions */}
                  <div className="flex gap-3 pt-4 border-t border-gray-200">
                    <Button type="submit" variant="primary">
                      {editingProfileId !== null ? 'Oppdater profil' : 'Opprett profil'}
                    </Button>
                    <Button type="button" variant="secondary" onClick={handleCancel}>
                      Avbryt
                    </Button>
                  </div>
                </form>
              </Card>
            )}

            {/* List of profiles */}
            {!isCreating && editingProfileId === null && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-gray-900">Alle profiler</h2>
                {profiles.length === 0 ? (
                  <Card>
                    <div className="text-center py-8">
                      <p className="text-gray-500 mb-4">Ingen profiler funnet</p>
                      <Button variant="primary" onClick={handleCreateNew}>
                        Opprett din første profil
                      </Button>
                    </div>
                  </Card>
                ) : (
                  <div className="grid gap-4">
                    {profiles.map((profile) => (
                      <Card key={profile.profil_id} padding="md">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <h3 className="text-lg font-semibold text-gray-900">
                                {profile.profil_navn}
                              </h3>
                              {profile.aktiv && (
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                                  Aktiv
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              {profile.utstyr.length} utstyr tilgjengelig
                            </p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {profile.utstyr.slice(0, 5).map((eq) => (
                                <span
                                  key={eq.utstyr_id}
                                  className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded capitalize"
                                >
                                  {eq.utstyr_navn}
                                </span>
                              ))}
                              {profile.utstyr.length > 5 && (
                                <span className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded">
                                  +{profile.utstyr.length - 5} mer
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            {!profile.aktiv && (
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => handleActivate(profile.profil_id)}
                              >
                                Aktiver
                              </Button>
                            )}
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleEdit(profile)}
                            >
                              Rediger
                            </Button>
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleDelete(profile.profil_id)}
                            >
                              Slett
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </MainLayout>
  );
};
