# Treningsassistent

AI-drevet treningsassistent med intelligent øvelsesanbefaling basert på muskelprioritet, antagonistisk balanse og øvelsesrotasjon.

## Konsept

En intelligent treningsassistent som hjelper med å strukturere styrketrening ved å:

- 🎯 **Tracke hvilke muskler som er trent og når**
- 🤖 **Foreslå neste øvelse basert på muskelprioritet**
- ⚖️ **Sikre balansert trening av alle muskelgrupper**
- 🔄 **Håndtere antagonistisk muskelbalanse** (bryst/rygg, biceps/triceps)
- 🎲 **Rotere øvelser for variasjon**
- 🏋️ **Tilpasse til tilgjengelig utstyr**

### Kjerneprinsipp

Systemet opererer som en **kontinuerlig treningsflyt** - ingen "økter" med start/stopp. Brukeren logger øvelser når som helst, og systemet holder kontinuerlig oversikt og foreslår alltid neste øvelse basert på current state.

## Teknologi Stack

### Backend (✅ Ferdig)

- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL 14
- **ORM:** SQLAlchemy 2.0.23
- **Migrations:** Alembic 1.12.1
- **Authentication:** JWT with bcrypt password hashing
- **Data Source:** 873 exercises from [free-exercise-db](https://github.com/yuhonas/free-exercise-db)

### Frontend (✅ Ferdig)

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 7
- **Styling:** Tailwind CSS v3
- **Routing:** React Router v6
- **HTTP Client:** Axios with JWT interceptors
- **State Management:** React Context API
- **Visualisering:** Plotly.js (line charts, bar charts, grouped charts)
- **Form Validation:** React Hook Form + Zod
- **Notifications:** Custom Toast system
- **Animations:** CSS keyframes + Tailwind animations

### Deployment (📝 Planlagt)

- **Server:** Ubuntu Server
- **Web Server:** Nginx (reverse proxy + static files)
- **Application Server:** Gunicorn/Uvicorn workers
- **SSL:** Let's Encrypt (Certbot)
- **Process Management:** Systemd service

## Prosjektstruktur

```
.
├── backend/                    # FastAPI backend (✅ Ferdig)
│   ├── app/
│   │   ├── api/               # 7 routers (auth, ovelser, historikk, statistikk, utstyr, muskler, admin)
│   │   ├── services/          # AI-algoritme og statistikk
│   │   ├── utils/             # Security (JWT & bcrypt)
│   │   ├── main.py            # FastAPI app
│   │   ├── models.py          # 12 SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── database.py        # Database connection
│   ├── alembic/               # Database migrations
│   ├── scripts/               # Data import scripts
│   ├── manage.py              # CLI for admin/invitations
│   ├── test_workflow.py       # Integration test
│   └── requirements.txt
├── frontend/                   # React frontend (✅ Ferdig)
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── common/        # Button, Input, Card, Alert, Skeleton, Confetti
│   │   │   ├── features/      # ExerciseCard, ExerciseLoggingForm
│   │   │   └── layout/        # Navbar, MainLayout, ProtectedRoute
│   │   ├── context/           # AuthContext, ToastContext
│   │   ├── hooks/             # useKeyboardShortcut
│   │   ├── pages/             # 7 pages (Login, Register, Home, History, Statistics, Equipment, Admin)
│   │   ├── services/          # API clients (auth, exercise, history, statistics, equipment, admin)
│   │   ├── types/             # TypeScript type definitions
│   │   ├── utils/             # Storage utilities
│   │   ├── App.tsx            # Main app component
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles + animations
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── exercise_images/           # 873 exercises, 1746 images
├── exercises.json             # Exercise database (free-exercise-db)
├── referansedok.md           # Complete project specification
├── data_mapping.md           # JSON → Database mapping
└── README.md                 # This file
```

## Kom i gang

### 1. Database Setup

```bash
# PostgreSQL må være installert og kjørende
# Database: treningsassistent
# User: postgres
# Password: securepassword123
```

### 2. Backend Setup

```bash
cd backend

# Aktiver virtual environment
source venv/bin/activate

# Installer dependencies (allerede gjort)
pip install -r requirements.txt

# Kjør migrations (allerede gjort)
alembic upgrade head

# Importer exercise data (allerede gjort)
python scripts/import_data.py
```

### 3. Kjør Backend Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API vil være tilgjengelig på:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 4. Frontend Setup

```bash
cd frontend

# Installer dependencies (allerede gjort)
npm install

# Start development server
npm run dev
```

Frontend vil være tilgjengelig på:
- **App:** http://localhost:5173

### 5. Test Accounts

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Regular User:**
- Username: `testuser`
- Password: `password123`

## Frontend Features

### Sider (7 totalt)

1. **Login Page** - JWT authentication med form validation
2. **Register Page** - Invite-only registrering med invitation code
3. **Home Page** - AI-drevet øvelsesanbefaling + loggføring + nylig aktivitet
4. **History Page** - Treningshistorikk gruppert per dato med volumberegninger
5. **Statistics Page** - Plotly-visualiseringer:
   - Volum over tid (line chart)
   - Mest trente muskelgrupper (horizontal bar chart)
   - Antagonistisk muskelbalanse (grouped bar chart)
   - Personlige rekorder
   - Treningstrender
6. **Equipment Page** - CRUD for utstyrsprofiler med kategori-basert velger
7. **Admin Page** (admin-only) - Invitasjonshåndtering, brukerhåndtering, systemstatistikk

### UI/UX Features

- **Toast Notifications** - Auto-dismissing toasts med 4 typer (success, error, warning, info)
- **Skeleton Loading** - Smooth loading states med pulse animasjon
- **Confetti Celebration** - Feiring når øvelser logges
- **Smooth Animations** - Slide-in, fade-in, scale-in animasjoner
- **Responsive Design** - Mobil-vennlig med hamburger-meny
- **Protected Routes** - Automatisk redirect til login
- **Admin-only Routes** - 403 error page for ikke-administratorer

### Komponenter

- **Common**: Button, Input, Card, Alert, Skeleton, Confetti
- **Features**: ExerciseCard, ExerciseLoggingForm
- **Layout**: Navbar, MainLayout, ProtectedRoute

## Kjernefunksjonalitet

### AI-Algoritme for Øvelsesanbefaling

Algoritmen kombinerer flere faktorer for å foreslå optimal neste øvelse:

#### 1. Muskel-prioritet (60% vekt)
- Beregner dager siden muskel sist ble trent
- Aldri-trente muskler får høyest prioritet
- Max 100 poeng

#### 2. Antagonistisk balanse (40% vekt)
- Sjekker balanse mellom antagonistiske muskelpar:
  - Bryst ↔ Rygg
  - Quadriceps ↔ Hamstrings
  - Biceps ↔ Triceps
  - Anterior deltoid ↔ Posterior deltoid
  - Abs ↔ Lower back
- Basert på **volum** (sett × reps × vekt), ikke bare frekvens
- Gir boost (+40 poeng) til undertrent muskel i par
- Gir penalty (-20 poeng) til overtrent muskel i par

#### 3. Øvelse-rotasjon
- Varierer øvelser for samme muskelgruppe
- Prioriterer øvelser som ikke er brukt på lenge
- Straffer overbrukte øvelser

#### 4. Utstyr-filtrering
- Filtrerer øvelser basert på brukerens aktive utstyrsprofil
- Støtter multiple profiler: "Gym", "Hjemme", "Reise"
- Fallback til kroppsvekt-øvelser hvis ingen match

### Volum-tracking

- **Primære muskler:** 100% av volum (sett × reps × vekt)
- **Sekundære muskler:** 50% av volum
- Eksempel: Barbell Bench Press
  - Pectoralis major (primær): 100% kreditt
  - Triceps (sekundær): 50% kreditt
  - Anterior deltoid (sekundær): 50% kreditt

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (requires invitation code)
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Exercises (Øvelser)
- `GET /api/ovelser/neste-anbefaling` - **Get AI-powered exercise recommendation**
- `GET /api/ovelser/alle` - Get all exercises (with filters)
- `GET /api/ovelser/{ovelse_id}` - Get exercise details
- `POST /api/ovelser/logg` - Log completed exercise

### History (Historikk)
- `GET /api/historikk/` - Get workout history (grouped by date)
- `GET /api/historikk/treningsokt/{dato}` - Get specific workout session
- `GET /api/historikk/siste` - Get recent logged exercises

### Statistics (Statistikk)
- `GET /api/statistikk/heatmap` - Muscle volume heatmap data
- `GET /api/statistikk/antagonistisk-balanse` - Antagonistic balance analysis
- `GET /api/statistikk/volum-over-tid` - Volume over time
- `GET /api/statistikk/muskel/{muskel_id}` - Detailed muscle statistics
- `GET /api/statistikk/dashboard` - Dashboard summary

### Muscles (Muskler)
- `GET /api/muskler/` - Get all muscles
- `GET /api/muskler/prioritet` - Get muscles with priority scores
- `GET /api/muskler/{muskel_id}` - Get muscle details

### Equipment (Utstyr)
- `GET /api/utstyr/alle` - Get all equipment types
- `GET /api/utstyr/profiler` - Get user's equipment profiles
- `GET /api/utstyr/profiler/aktiv` - Get active equipment profile
- `POST /api/utstyr/profiler` - Create equipment profile
- `PUT /api/utstyr/profiler/{profil_id}` - Update equipment profile
- `POST /api/utstyr/profiler/{profil_id}/aktivere` - Activate profile
- `DELETE /api/utstyr/profiler/{profil_id}` - Delete profile

### Admin (Admin-only)
- `POST /api/admin/invitasjoner` - Create invitation code
- `GET /api/admin/invitasjoner` - List all invitations
- `DELETE /api/admin/invitasjoner/{invitasjon_id}` - Delete invitation
- `GET /api/admin/brukere` - List all users
- `POST /api/admin/brukere/{bruker_id}/aktiver` - Activate user
- `POST /api/admin/brukere/{bruker_id}/deaktiver` - Deactivate user
- `POST /api/admin/brukere/{bruker_id}/gjor-admin` - Make user admin
- `GET /api/admin/stats` - System statistics

## Database Schema

### Global Tables (Shared by all users)
- `muskler` - 17 muscle groups
- `utstyr` - 12 equipment types
- `antagonistiske_par` - 5 antagonistic muscle pairs
- `ovelser` - 873 exercises
- `ovelse_muskler` - Exercise-muscle relationships (2574 records)
- `ovelse_utstyr` - Exercise-equipment relationships (796 records)

### User Tables
- `brukere` - User accounts
- `invitasjoner` - Invitation codes (invite-only registration)
- `bruker_muskel_status` - Muscle training status per user
- `bruker_ovelse_historikk` - Exercise usage tracking
- `ovelser_utfort` - Logged exercises
- `bruker_utstyr_profiler` - Equipment profiles

## Management CLI

```bash
cd backend

# Create admin user
python manage.py create-admin

# Create invitation code
python manage.py create-invitation

# List users
python manage.py list-users

# List invitations
python manage.py list-invitations
```

## Testing

```bash
# Run integration test
cd backend
python test_workflow.py
```

Test verifies:
- Admin creation
- Invitation generation
- User registration
- Equipment profile setup
- Exercise recommendation
- Exercise logging
- Muscle status tracking
- Statistics calculation

## MCP Integration

Prosjektet bruker Model Context Protocol (MCP) for direkte tilgang til database og API:

### PostgreSQL MCP
- Direct SQL queries against database
- Connection: `postgres://postgres:securepassword123@localhost/treningsassistent`

### FastAPI MCP
- Direct access to all 40+ API endpoints via SSE
- URL: `http://localhost:8000/mcp`

### Filesystem MCP
- File and directory operations in project folder

Se `.mcp.json` for konfigurasjon.

## Utviklingsstatus

### ✅ Ferdig (100% Complete)

**Backend:**
- ✅ Database setup og migrations
- ✅ Alle 873 øvelser importert med bilder
- ✅ Complete API implementation (40+ endpoints)
- ✅ Authentication system (JWT + invite-only)
- ✅ AI recommendation algorithm
- ✅ Statistics and tracking
- ✅ Management CLI
- ✅ Workflow testing

**Frontend:**
- ✅ React 18 + TypeScript + Vite setup
- ✅ Authentication (Login/Register med JWT)
- ✅ Hovedfunksjonalitet (Øvelsesanbefaling, Logging, Historikk)
- ✅ Statistikk & Visualisering (Plotly-grafer, Personlige rekorder)
- ✅ Utstyrshåndtering (CRUD for profiler)
- ✅ Admin-panel (Invitasjoner, Brukerhåndtering, Statistikk)
- ✅ UX-forbedringer (Toast, Skeletons, Animasjoner, Confetti)

### 📝 Neste steg (Valgfritt)
- **Mobile App:** React Native / Flutter
- **Unit Testing:** Jest + React Testing Library
- **E2E Testing:** Playwright / Cypress
- **Docker:** Docker Compose setup
- **Deployment:** Production deployment guide
- **Enhancements:** Email for invitations, password reset

## Datakilde

- **Exercise Database:** [free-exercise-db](https://github.com/yuhonas/free-exercise-db)
- **License:** Public domain (Unlicense)
- **873 exercises** med primære/sekundære muskler, utstyr, instruksjoner
- **1746 images** (2 per exercise)
- Statiske bilder - ingen GIFs i MVP

## Sikkerhet

- ✅ JWT tokens (24 timers expiry)
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ Invite-only registration
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Input validation (Pydantic schemas + React Hook Form)
- ✅ User isolation (all queries filter by user_id)
- ✅ Protected routes (client-side + server-side validation)
- ✅ Admin-only routes (role-based access control)
- 📝 HTTPS (Let's Encrypt) - for deployment
- 📝 Rate limiting - planned

## Bidrag

Dette er et privat prosjekt. Kontakt eier for tilgang.

## Lisens

MIT
