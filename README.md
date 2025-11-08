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

### Frontend (📝 Planlagt)

- **Framework:** React
- **Visualisering:** Plotly.js (heatmaps, grafer)
- **HTTP Client:** Axios
- **State Management:** React Context / Redux

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

### 4. Test Accounts

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Regular User:**
- Username: `testuser`
- Password: `password123`

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
- `POST /api/utstyr/profiler` - Create equipment profile
- `PUT /api/utstyr/profiler/{profil_id}/aktivere` - Activate profile

### Admin (Admin-only)
- `POST /api/admin/invitasjoner` - Create invitation code
- `GET /api/admin/brukere` - List all users
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

### ✅ Ferdig (Backend 100%)
- Database setup og migrations
- Alle 873 øvelser importert med bilder
- Complete API implementation (40+ endpoints)
- Authentication system (JWT + invite-only)
- AI recommendation algorithm
- Statistics and tracking
- Management CLI
- Workflow testing

### 📝 Neste steg
- **Frontend Development:** React web app
- **Mobile App:** React Native / Flutter
- **Testing:** Unit tests med pytest
- **Deployment:** Docker/Docker Compose setup
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
- ✅ Input validation (Pydantic schemas)
- ✅ User isolation (all queries filter by user_id)
- 📝 HTTPS (Let's Encrypt) - for deployment
- 📝 Rate limiting - planned

## Bidrag

Dette er et privat prosjekt. Kontakt eier for tilgang.

## Lisens

MIT
