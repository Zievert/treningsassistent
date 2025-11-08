# Claude Development Context

## 📖 Quick Start Guider

**Hvis du er ny i dette prosjektet, start her:**
- 📄 **QUICK_START.md** - 1-side oversikt for rask oppstart
- 📚 **CLAUDE_CODE_ONBOARDING.md** - Komplett onboarding guide (10+ sider)

Disse guidene gir deg alt du trenger for å komme i gang raskt!

---

## Utviklingsmiljø

**Platform:** Windows Subsystem for Linux 2 (WSL2)
- **Kernel:** Linux 6.6.87.2-microsoft-standard-WSL2
- **Distribusjon:** Ubuntu 22.04 LTS
- **Working Directory:** `/home/silver/mounts/server` ⚠️ **SSHFS MOUNT**

### ⚠️ VIKTIG: SSHFS Mount-miljø
**Du jobber DIREKTE på produksjonsserveren via sshfs!**

- **Lokal path:** `/home/silver/mounts/server`
- **Remote path:** `gull:/home/sivert/treningsassistent` (10.0.0.20)
- **Mount type:** sshfs (SSH Filesystem)
- **Alle file-endringer skjer LIVE på produksjonsserveren**
- **Ingen deploy nødvendig** - endringer er instant!

**Hvordan dette fungerer:**
```
WSL (lokal maskin)                    gull (produksjonsserver)
~/mounts/server/  ←─ sshfs ─→  /home/sivert/treningsassistent
(du er her)                           (faktisk lokasjon)
```

**Auto-mount ved oppstart:**
- Script: `~/scripts/mount-server.sh`
- Kjører automatisk via `~/.bashrc`
- Sjekk status: `mountpoint ~/mounts/server`

## Produksjonsserver

**Server:** gull (Ubuntu Server)
- **IP-adresse:** `10.0.0.20`
- **Brukernavn:** `sivert`
- **SSH-nøkkel:** `/home/silver/prosjekter/trening/ssh/gull_id_ed25519`
- **OS:** Ubuntu 24.04 LTS (Linux 6.8.0-86-generic)
- **Arkitektur:** x86_64

### Installert programvare
- ✅ **Python:** 3.12.3
- ✅ **Node.js:** v22.21.0
- ✅ **Docker:** 28.5.1
- ✅ **Docker Compose:** v2.32.4
- ✅ **PostgreSQL:** 16 (i Docker container)

### SSH-tilkobling
```bash
# Fra WSL2
ssh -i /home/silver/prosjekter/trening/ssh/gull_id_ed25519 sivert@10.0.0.20

# Forenklet med alias (legg til i ~/.ssh/config):
Host gull
    HostName 10.0.0.20
    User sivert
    IdentityFile /home/silver/prosjekter/trening/ssh/gull_id_ed25519
```

**Viktig:** SSH-nøkkelen må ha korrekte tillatelser (600):
```bash
chmod 600 /home/silver/prosjekter/trening/ssh/gull_id_ed25519
```

### Deployment Status

**Produksjonsappen kjører på gull (10.0.0.20) med Docker Compose:**

✅ **Alle services er healthy og kjører:**
- **Database:** PostgreSQL 16 på port 5432
- **Backend:** FastAPI på port 8000
- **Frontend:** React + Nginx på port 8080

**Aksess URLs:**
- Frontend: `http://10.0.0.20:8080/`
- Backend API: `http://10.0.0.20:8000/`
- API Dokumentasjon: `http://10.0.0.20:8000/docs`

**Deployment lokasjon på server:**
```bash
/home/sivert/treningsassistent/
```

**Nyttige kommandoer på server:**
```bash
# Sjekk status
ssh gull "cd treningsassistent && docker compose ps"

# Se logger
ssh gull "cd treningsassistent && docker compose logs -f backend"
ssh gull "cd treningsassistent && docker compose logs -f frontend"

# Restart services
ssh gull "cd treningsassistent && docker compose restart backend"
ssh gull "cd treningsassistent && docker compose restart frontend"

# Rebuild og deploy
ssh gull "cd treningsassistent && docker compose up -d --build"

# Stopp alt
ssh gull "cd treningsassistent && docker compose down"
```

## Prosjekt: Treningsassistent

En intelligent treningsassistent som tracker muskeltreningog foreslår øvelser basert på:
- Muskelprioritet (tid siden sist trent)
- Antagonistisk balanse (bryst/rygg, biceps/triceps, etc.)
- Øvelsesrotasjon for variasjon
- Tilgjengelig utstyr

### Teknologi Stack
- **Backend:** FastAPI 0.104.1 ✅ (Python 3.10.12 dev / 3.12 prod)
- **Database:** PostgreSQL 14.19 (dev) / 16 (prod) ✅
- **ORM:** SQLAlchemy 2.0.23 ✅
- **Migreringer:** Alembic 1.12.1 ✅
- **Auth:** JWT tokens + bcrypt ✅
- **Data:** 873 exercises from free-exercise-db ✅
- **Frontend:** React 19 + TypeScript + Vite + TailwindCSS ✅
- **Charts:** Plotly.js for statistikk-visualisering ✅
- **Deployment:** Docker Compose (PostgreSQL 16, FastAPI, React/Nginx) ✅

## Prosjektstruktur

```
/home/silver/mounts/server/  (sshfs → gull:/home/sivert/treningsassistent)
├── backend/
│   ├── app/
│   │   ├── api/              ✅ (7 routers: auth, ovelser, historikk, statistikk, utstyr, muskler, admin)
│   │   ├── services/         ✅ (ai_forslag.py, statistikk.py)
│   │   ├── utils/            ✅ (security.py - JWT & bcrypt)
│   │   ├── main.py           ✅ (FastAPI app med alle routers)
│   │   ├── models.py         ✅ (12 SQLAlchemy models)
│   │   ├── schemas.py        ✅ (Pydantic schemas)
│   │   └── database.py       ✅ (Database connection)
│   ├── alembic/
│   │   └── versions/         ✅ (initial migration - 13 tables)
│   ├── scripts/
│   │   └── import_data.py    ✅ (873 exercises imported)
│   ├── manage.py             ✅ (CLI for admin/invitations)
│   ├── test_workflow.py      ✅ (Integration test - passed!)
│   ├── requirements.txt      ✅
│   ├── Dockerfile            ✅ (Python 3.12-slim with curl for health checks)
│   ├── .env                  ✅ (configured)
│   └── README.md             ✅ (complete documentation)
├── frontend/
│   ├── src/
│   │   ├── pages/            ✅ (HomePage, ExercisePage, HistoryPage, StatisticsPage, EquipmentPage, AdminPage)
│   │   ├── components/       ✅ (layout, common, forms, stats)
│   │   ├── services/         ✅ (API clients for alle endpoints)
│   │   ├── contexts/         ✅ (AuthContext for JWT handling)
│   │   ├── types/            ✅ (TypeScript interfaces)
│   │   └── App.tsx           ✅ (React Router setup)
│   ├── Dockerfile            ✅ (Multi-stage: Node 22 build + nginx serve)
│   ├── nginx.conf            ✅ (Reverse proxy /api/* → backend:8000)
│   ├── package.json          ✅
│   ├── tsconfig.json         ✅
│   ├── vite.config.ts        ✅
│   └── tailwind.config.js    ✅
├── exercise_images/          ✅ (1746 images, 873 exercises)
├── exercises.json            ✅ (873 øvelser fra free-exercise-db)
├── docker-compose.yml        ✅ (PostgreSQL 16, backend, frontend with health checks)
├── .env.production           ✅ (Production environment template)
├── DEPLOYMENT.md             ✅ (Complete deployment guide)
├── referansedok.md           (komplett prosjektplan)
├── data_mapping.md           (JSON → Database mapping)
└── claude.md                 (dette dokumentet)
```

**Status:** 🎉 Fullstack-applikasjon komplett og deployed i produksjon!

## WSL-spesifikke hensyn

### Filsystem
- Tilgang til Windows-filer via `/mnt/c/`, `/mnt/d/`, etc.
- Bedre ytelse ved å holde prosjektfiler i Linux-filsystemet (`/home/`)
- Casing matters: Linux er case-sensitive, Windows er ikke

### Database
- PostgreSQL må kjøres enten:
  - I WSL (anbefalt for utvikling)
  - I Windows med port forwarding
  - I Docker container

### Networking
- WSL2 har egen IP-adresse (forskjellig fra Windows)
- localhost fungerer for de fleste tilfeller
- Kan aksessere Windows-porter fra WSL via localhost

### Verktøy tilgjengelig
- Python (sjekk versjon med `python3 --version`)
- Git (WSL-native)
- Standard Linux CLI-verktøy

## Viktige kommandoer

### Backend oppsett
```bash
# Aktiver virtual environment (når opprettet)
source backend/venv/bin/activate

# Installer dependencies
pip install -r backend/requirements.txt

# Kjør FastAPI dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database
```bash
# Opprett database (PostgreSQL må være installert)
sudo -u postgres createdb treningsapp
sudo -u postgres createuser treningsuser

# Alembic migrasjoner
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Testing database connection
```bash
psql -U treningsuser -d treningsapp -h localhost
```

## Backend Utvikling - Fullført! ✅

Alle backend-komponenter er implementert og testet:

1. ✅ **Database Models** (`backend/app/models.py`)
   - 12 SQLAlchemy models med alle relasjoner

2. ✅ **Alembic migrasjoner**
   - Initial migration (13 tabeller opprettet)

3. ✅ **Import script** (`backend/scripts/import_data.py`)
   - 17 muskler, 12 utstyr, 5 antagonistiske par
   - 873 øvelser med 2574 muskel-relasjoner og 796 utstyr-relasjoner

4. ✅ **FastAPI app** (`backend/app/main.py`)
   - Full app setup med CORS, exception handling, health checks
   - 7 routers med 40+ endpoints

5. ✅ **Auth system** (`backend/app/api/auth.py`)
   - JWT authentication, invite-only registration
   - Test accounts: admin/admin123, testuser/password123

6. ✅ **Core API endpoints**
   - `/api/ovelser/neste-anbefaling` - AI-powered recommendations
   - `/api/ovelser/logg` - Log exercises
   - `/api/historikk/*` - Workout history
   - `/api/statistikk/*` - Heatmap, balance, progress
   - `/api/muskler/*` - Muscle priorities
   - `/api/utstyr/*` - Equipment profiles
   - `/api/admin/*` - User & invitation management

7. ✅ **AI Algorithm** (`backend/app/services/ai_forslag.py`)
   - `beregn_prioritet()` - Priority scoring (days since trained)
   - `hent_neste_anbefaling()` - Main recommendation algorithm
   - `finn_ovelse_for_muskel()` - Exercise selection
   - `oppdater_muskel_status_etter_logg()` - State updates
   - Antagonistic balance checking

8. ✅ **Statistics Service** (`backend/app/services/statistikk.py`)
   - Volume calculations, balance analysis, progress tracking

9. ✅ **Management CLI** (`backend/manage.py`)
   - Create admin users, generate invitations, list users

10. ✅ **Tests**
    - Complete workflow test verified all functionality

## Docker Deployment

### Lokal Development med Docker

```bash
# Start alle services
docker compose up -d

# Rebuild etter kodeendringer
docker compose up -d --build

# Se logger
docker compose logs -f backend
docker compose logs -f frontend

# Stopp alt
docker compose down

# Fullstendig cleanup (inkludert volumes)
docker compose down -v
```

### Health Checks

Alle Docker containers har konfigurerte health checks:

**Database (PostgreSQL 16):**
```bash
docker exec treningsassistent-db pg_isready -U postgres -d treningsassistent
```

**Backend (FastAPI):**
```bash
docker exec treningsassistent-backend curl -f http://localhost:8000/health
```

**Frontend (Nginx):**
```bash
docker exec treningsassistent-frontend curl -f http://localhost/ -o /dev/null -s
```

**Viktig:**
- Backend health check krever `curl` (installert i Dockerfile)
- Frontend health check bruker `curl` (ikke `wget` som har connection issues)
- Health checks kjører automatisk hver 30. sekund

### Deployment til Produksjon

Se `DEPLOYMENT.md` for fullstendig guide. Kort versjon:

```bash
# 1. Kopier filer til server
scp -r . gull:~/treningsassistent/

# 2. Sett opp .env fil
ssh gull "cd treningsassistent && cp .env.production .env"
ssh gull "cd treningsassistent && nano .env"  # Edit SECRET_KEY

# 3. Start services
ssh gull "cd treningsassistent && docker compose up -d"

# 4. Verifiser
ssh gull "cd treningsassistent && docker compose ps"
```

## Frontend Development

### Frontend er komplett! ✅

**Implementerte pages:**
1. ✅ **HomePage** - AI-drevet øvelsesanbefaling og quick stats
2. ✅ **ExercisePage** - Søk/filtrer/velg øvelser manuelt
3. ✅ **HistoryPage** - Full treningshistorikk med sletting
4. ✅ **StatisticsPage** - Volum over tid, muskelfrekvens, personlige rekorder
5. ✅ **EquipmentPage** - Håndter utstyrsprofiler (Gym/Hjemme/Reise)
6. ✅ **AdminPage** - Brukerhåndtering og invitasjonskoder (kun admin)

**Nøkkelfeatures:**
- ✅ JWT authentication med AuthContext
- ✅ Protected routes (redirect til login hvis ikke autentisert)
- ✅ Responsive design med TailwindCSS
- ✅ API error handling med toast notifications
- ✅ TypeScript for type safety
- ✅ Chart visualizations med Plotly.js
- ✅ Exercise images fra /exercise_images/
- ✅ Real-time updates etter logg/endringer

**Test accounts:**
- Admin: `admin` / `admin123`
- User: `testuser` / `password123`

### Kjøre Frontend Lokalt

```bash
# Install dependencies
cd frontend
npm install

# Dev server med hot reload
npm run dev
# Åpner på http://localhost:5173

# Production build
npm run build
# Output til frontend/dist/

# Preview production build
npm run preview
```

**Viktig:** Backend må kjøre på `http://localhost:8000` for at frontend skal fungere.

## Neste steg (valgfritt)

**Testing:**
- Unit tests for frontend (Vitest)
- E2E tests (Playwright/Cypress)
- Backend unit tests med pytest

**Features:**
- Email sending for invitations
- Password reset endpoint
- Mobil app (React Native/Flutter)
- Export workout data (PDF/CSV)
- Social features (deling av øvelser)

## Tips for utvikling i WSL

- Bruk Windows-basert editor (VS Code med WSL extension) for best experience
- Database data lagres i Linux-filsystemet for bedre ytelse
- Unngå å redigere filer under `/mnt/c/` fra Linux-verktøy
- WSL kan restartes med `wsl --shutdown` (fra Windows PowerShell/CMD)

## Environment variables

Kopier `.env.example` til `.env` og tilpass:

```bash
cp backend/.env.example backend/.env
# Rediger .env med riktige database credentials og SECRET_KEY
```

## MCP (Model Context Protocol) Integration

Dette prosjektet bruker fire MCP servere for å gi Claude Code direkte tilgang til database, API-endepunkter, filsystem, og Docker på produksjonsserveren (gull).

**VIKTIG:** Alle MCP-servere (unntatt filesystem) er nå koblet til **produksjonsserveren gull** for å jobbe med ekte data.

### Konfigurert i `.mcp.json` (prosjektrot):

```json
{
  "mcpServers": {
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgres://postgres:Tr3n1ng_Pr0d_P4ssw0rd_2024!@localhost:15432/treningsassistent"]
    },
    "fastapi": {
      "type": "sse",
      "url": "http://46.250.218.99:8000/mcp"
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/silver/mounts/server"]
    },
    "docker": {
      "command": "uvx",
      "args": ["mcp-server-docker"],
      "env": {
        "DOCKER_HOST": "ssh://gull"
      }
    }
  }
}
```

**Viktig oppdateringer i MCP-konfigurasjon:**
- **Postgres MCP:** Bruker `npx` i stedet for `uvx`, kobler via SSH tunnel på `localhost:15432`
- **FastAPI MCP:** Peker direkte til produksjons-IP `http://46.250.218.99:8000/mcp`
- **Filesystem MCP:** Peker til `/home/silver/mounts/server` (sshfs-mounted path)
- **Docker MCP:** Bruker `DOCKER_HOST=ssh://gull` for remote Docker access

**SSH Tunnel for Postgres:**
Tunnelen startes automatisk i `~/scripts/mount-server.sh`, men kan også kjøres manuelt:
```bash
# Sjekk om tunnel kjører
ss -tulpn | grep 15432

# Start manuelt hvis nødvendig
ssh -f -N -L 15432:localhost:5432 gull
```

### Aktivert i `.claude/settings.local.json`:

```json
{
  "enabledMcpjsonServers": ["postgres", "fastapi", "filesystem"],
  ...
}
```

**Viktig:** Du må restarte Claude Code etter å ha endret MCP-konfigurasjonen.

### PostgreSQL MCP Server

**Database Connection Details (Produksjon på gull via SSH tunnel):**
- **Database:** `treningsassistent`
- **User:** `postgres`
- **Password:** `Tr3n1ng_Pr0d_P4ssw0rd_2024!`
- **Remote Host:** `gull` (10.0.0.20)
- **Remote Port:** `5432`
- **Local Tunnel Port:** `15432`
- **Connection String:** `postgres://postgres:Tr3n1ng_Pr0d_P4ssw0rd_2024!@localhost:15432/treningsassistent`

**SSH Tunnel Setup:**
PostgreSQL MCP serveren kobler til via en SSH-tunnel siden databasen er på en remote server.

Start SSH-tunnelen:
```bash
# Automatisk via script (anbefalt)
./scripts/start-postgres-tunnel.sh

# Eller manuelt
ssh -f -N -L 15432:localhost:5432 -i /home/silver/prosjekter/trening/ssh/gull_id_ed25519 sivert@10.0.0.20
```

Sjekk tunnel status:
```bash
# Se om tunnel kjører
ps aux | grep "ssh.*15432" | grep -v grep

# Test tilkobling
nc -z localhost 15432
```

Stopp tunnel:
```bash
pkill -f "ssh.*15432:localhost:5432"
```

**MCP Bruker:**
- PostgreSQL MCP serveren kjører som `postgres` (superuser)
- Full tilgang til `treningsassistent` databasen
- Bruker `uvx` (uv's executable runner) i stedet for `npx`

**Verifisere MCP Server:**
```bash
# I Claude Code, kjør:
/mcp

# Du skal se:
# postgres - @modelcontextprotocol/server-postgres
```

**Tilgjengelige MCP Tools:**
Når MCP serveren er aktiv kan Claude Code:
- Kjøre SQL queries direkte mot **produksjonsdatabasen** på gull
- Liste tabeller og kolonner
- Inserte, oppdatere, og slette data
- Hente statistikk og analysere data
- Jobber med **ekte produksjonsdata** (873 øvelser, alle brukere, treningshistorikk)

### FastAPI MCP Server

FastAPI MCP serveren gir Claude Code direkte tilgang til alle backend API-endepunkter.

**Server Details (Produksjon på gull):**
- **Type:** SSE (Server-Sent Events)
- **URL:** `http://46.250.218.99:8000/mcp` (direkte til produksjonsserver)
- **Server:** Produksjonsbackend på gull (10.0.0.20 / 46.250.218.99)
- **Package:** `fastapi-mcp>=0.4.0` (optional dependency)
- **Oppsett:** Conditional import i `backend/app/main.py`:
  ```python
  try:
      from fastapi_mcp import FastApiMCP
      HAS_MCP = True
  except ImportError:
      HAS_MCP = False

  if HAS_MCP:
      mcp = FastApiMCP(app)
      mcp.mount()
  ```

**SSH Tunnel Setup:**
FastAPI MCP serveren kobler til via en SSH-tunnel fra WSL til gull.

Start SSH-tunnelen:
```bash
# Manuelt:
ssh -f -N -L 18000:localhost:8000 gull

# Eller bruk scriptet:
./scripts/start-fastapi-tunnel.sh
```

Verifiser at tunnelen kjører:
```bash
ps aux | grep "ssh.*18000"
timeout 2 curl -N -H "Accept: text/event-stream" http://localhost:18000/mcp
```

Stopp tunnelen:
```bash
pkill -f "ssh.*18000:localhost:8000"
```

**Backend Server Status:**
```bash
cd ~/prosjekter/trening/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Eller i bakgrunn:
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

**Verifisere MCP Server:**
```bash
# I Claude Code, kjør:
/mcp

# Du skal se:
# ✅ postgres - Database queries
# ✅ fastapi - API endpoints (40+ endpoints)
```

**Tilgjengelige API Endpoints via MCP:**

**Authentication (`/api/auth`):**
- `POST /api/auth/register` - Registrer ny bruker (krever invitasjonskode)
- `POST /api/auth/login` - Login (returnerer JWT token)
- `GET /api/auth/me` - Hent innlogget bruker

**Exercises (`/api/ovelser`):**
- `GET /api/ovelser/neste-anbefaling` - AI-drevet øvelsesanbefaling (hovedfunksjon!)
- `GET /api/ovelser/alle` - Liste alle øvelser (støtter filtrering)
- `GET /api/ovelser/{ovelse_id}` - Hent enkeltøvelse med detaljer
- `POST /api/ovelser/logg` - Logg utført øvelse (oppdaterer muskel-status)

**History (`/api/historikk`):**
- `GET /api/historikk/siste-okter` - Siste treningsøkter
- `GET /api/historikk/ovelse/{ovelse_id}` - Historikk for spesifikk øvelse

**Statistics (`/api/statistikk`):**
- `GET /api/statistikk/heatmap` - Muskel-heatmap (sist trent per muskel)
- `GET /api/statistikk/antagonistisk-balanse` - Balanse mellom antagonistiske muskelpar
- `GET /api/statistikk/fremgang` - Fremgang over tid

**Equipment (`/api/utstyr`):**
- `GET /api/utstyr/profiler` - Hent brukerens utstyrsprofiler
- `POST /api/utstyr/profiler` - Opprett utstyrsprofil (Gym/Hjemme/Reise)
- `PUT /api/utstyr/profiler/{profil_id}/aktiver` - Aktiver profil
- `GET /api/utstyr/alle` - Liste alt tilgjengelig utstyr

**Muscles (`/api/muskler`):**
- `GET /api/muskler/alle` - Liste alle muskelgrupper
- `GET /api/muskler/prioritet` - Muskelprioritet for innlogget bruker
- `GET /api/muskler/antagonistiske-par` - Antagonistiske muskelpar

**Admin (`/api/admin`):**
- `POST /api/admin/invitasjoner` - Opprett invitasjonskode
- `GET /api/admin/brukere` - Liste alle brukere
- `DELETE /api/admin/brukere/{bruker_id}` - Slett bruker

**Test Accounts:**
- **Admin:** `admin` / `admin123`
- **User:** `testuser` / `password123`

**Eksempel - Teste API via MCP:**
```bash
# 1. Login for å få JWT token
# 2. Bruk token i Authorization header: "Bearer <token>"
# 3. Kall /api/ovelser/neste-anbefaling for å få AI-anbefaling
```

**Fordeler med FastAPI MCP:**
- ✅ Test API-endepunkter direkte fra Claude Code
- ✅ Debugge API-responser i sanntid
- ✅ Utforske data via både SQL (postgres) og REST API (fastapi)
- ✅ Verifisere business logic og AI-algoritmer
- ✅ Rask prototyping av nye features
- ✅ Automatisk oppdagelse av alle endpoints fra OpenAPI spec
- ✅ Bevarer request/response schemas og endpoint-dokumentasjon
- ✅ Direkte ASGI-kommunikasjon (ikke HTTP)

### Docker MCP Server

Docker MCP serveren gir Claude Code direkte tilgang til Docker-containere på gull-serveren via SSH.

**Server Details:**
- **Type:** stdio
- **Command:** `uvx` (requires uv package manager)
- **Package:** `mcp-server-docker`
- **Connection:** SSH til gull (10.0.0.20)
- **Environment:** `DOCKER_HOST=ssh://gull`

**Installasjon av uv (gjort):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Installeres til ~/.local/bin/uv og ~/.local/bin/uvx
```

**Tilgjengelige operasjoner:**
- **Container Operations:** list, create, run, recreate, start, fetch logs, stop, remove
- **Image Management:** list, pull, push, build, remove
- **Network Operations:** list, create, remove
- **Volume Operations:** list, create, remove
- **Resources:** Per-container performance stats (CPU, memory) og log streaming

**Eksempel bruk:**
```
List all containers on gull
Show logs for treningsassistent-backend
Restart the frontend container
Check CPU and memory usage for all containers
```

**Fordeler med Docker MCP:**
- ✅ Administrer Docker-containere på remote server uten bash-kommandoer
- ✅ Sanntids monitoring av container stats og logger
- ✅ Natural language for Docker-operasjoner
- ✅ Trygg tilgang via SSH (bruker eksisterende SSH-konfigurasjon)
- ✅ Full Docker API tilgang gjennom MCP

### Filesystem MCP Server

Filesystem MCP serveren gir Claude Code direkte tilgang til filsystemet for fil- og mappeoperasjoner.

**Server Details:**
- **Type:** stdio
- **Command:** `npx`
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Scope:** `/home/silver/mounts/server` (sshfs-mounted produksjonsserver)

**⚠️ VIKTIG:** Filesystem MCP opererer nå på sshfs-mountet path!
- Alle file-operasjoner skjer DIREKTE på produksjonsserveren
- Ingen synkronisering eller deploy nødvendig
- Endringer er instant og live

**Tilgjengelige operasjoner:**
- `read_text_file` / `read_media_file` - Les filer
- `write_file` / `edit_file` - Opprett og endre filer
- `create_directory` / `list_directory` - Håndter mapper
- `move_file` - Flytt eller rename filer/mapper
- `search_files` / `directory_tree` - Søk og utforsk
- `get_file_info` - Hent metadata
- `list_allowed_directories` - Vis tilgjengelige mapper

**Fordeler med Filesystem MCP:**
- ✅ Les/skriv/editer filer direkte uten Bash-kommandoer
- ✅ Søk i filer med kraftig søkefunksjonalitet
- ✅ Håndter mappestrukturer effektivt
- ✅ Få filinformasjon og metadata
- ✅ Trygg tilgang begrenset til prosjektmappen
- ✅ Bedre feilhåndtering enn traditionelle fil-kommandoer

## Kontekst for Claude

Når du hjelper med dette prosjektet:
- Fullstack-applikasjon komplett og deployed i produksjon! 🎉
- Følg arkitekturen beskrevet i `referansedok.md`
- Bruk `data_mapping.md` for å mappe exercises.json til database
- PostgreSQL er satt opp og kjører (både lokalt og i produksjon)
- Alle Python-kommandoer kjøres i WSL2 Linux-miljø
- **Fire MCP servere er konfigurert:**
  - **PostgreSQL MCP** (`postgres`) - Direkte SQL queries mot **produksjonsdatabasen på gull** (873 øvelser, ekte data)
  - **FastAPI MCP** (`fastapi`) - Direkte tilgang til alle 40+ API-endepunkter via SSE på **produksjonsserveren gull**
  - **Filesystem MCP** (`filesystem`) - Fil- og mappeoperasjoner i **lokal prosjektmappe** (WSL2)
  - **Docker MCP** (`docker`) - Docker container management på **gull-serveren via SSH**
- **Alle MCP-servere (unntatt filesystem) peker på produksjon (gull)**
- MCP-konfigurasjon finnes i `.mcp.json` (project-level)
- uv/uvx er installert i `~/.local/bin/` for Python pakke management
- **VIKTIG:** Restart Claude Code etter MCP-konfigurasjonsendringer
