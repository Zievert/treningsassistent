// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

// Auth Types
export interface LoginRequest {
  brukernavn: string;
  passord: string;
}

export interface RegisterRequest {
  brukernavn: string;
  passord: string;
  epost: string;
  invitasjonskode: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  bruker_id: number;
  brukernavn: string;
  epost: string;
  rolle: 'admin' | 'bruker';
  opprettet_dato: string;
  aktiv: boolean;
}

// Exercise Types
export interface Exercise {
  ovelse_id: number;
  ovelse_navn: string;
  gif_url?: string;
  video_url?: string;
  instruksjoner?: string;
  tips?: string[];
  vanlige_feil?: string[];
  primare_muskler: Muscle[];
  sekundare_muskler: Muscle[];
  utstyr_krav: Equipment[];
}

export interface ExerciseRecommendation {
  ovelse: Exercise;
  prioritert_muskel: string;
  dager_siden_trent: number | null;
  prioritet_score: number;
}

export interface LogExerciseRequest {
  ovelse_id: number;
  sett: number;
  repetisjoner: number;
  vekt: number;
}

export interface LogExerciseResponse {
  success: boolean;
  neste_anbefaling?: ExerciseRecommendation;
}

// Muscle Types
export interface Muscle {
  muskel_id: number;
  muskel_navn: string;
  hovedkategori: string;
  underkategori?: string;
}

export interface MusclePriority extends Muscle {
  prioritet_score: number;
  dager_siden_trent: number | null;
  antall_ganger_trent: number;
  total_volum: number;
}

export interface AntagonisticPair {
  muskel_1_navn: string;
  muskel_2_navn: string;
  muskel_1_volum: string;
  muskel_2_volum: string;
  faktisk_ratio: string;
  onsket_ratio: string;
  balanse_status: string;
  avvik_prosent: number;
}

// Equipment Types
export interface Equipment {
  utstyr_id: number;
  utstyr_navn: string;
  kategori?: string;
}

export interface EquipmentProfile {
  profil_id: number;
  bruker_id: number;
  profil_navn: string;
  aktiv: boolean;
  utstyr: Equipment[];
}

export interface CreateEquipmentProfileRequest {
  profil_navn: string;
  utstyr_ids: number[];
}

// History Types
export interface ExerciseLog {
  utfort_id: number;
  ovelse_navn: string;
  sett: number;
  repetisjoner: number;
  vekt: number;
  tidspunkt: string;
  involverte_muskler: string[];
}

export interface WorkoutSession {
  dato: string;
  ovelser: ExerciseLog[];
  total_varighet_estimert?: number;
}

// Statistics Types
export interface MuscleHeatmapData {
  muskel_navn: string;
  hovedkategori: string;
  trenings_datoer: string[];
}

export interface VolumeOverTime {
  dato: string;
  total_volum: string;
  antall_ovelser: number;
}

export interface MuscleStatistics {
  muskel_navn: string;
  antall_ganger_trent: number;
  sist_trent_dato: string | null;
  trenings_historikk: {
    dato: string;
    ovelse_navn: string;
    volum: number;
  }[];
}

// Admin Types
export interface Invitation {
  invitasjon_id: number;
  invitasjonskode: string;
  opprettet_dato: string;
  utloper_dato?: string;
  epost?: string;
  brukt: boolean;
}

export interface CreateInvitationRequest {
  epost?: string;
}
