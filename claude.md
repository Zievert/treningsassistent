# Claude Development Context

## Utviklingsmiljø

**Platform:** Windows Subsystem for Linux 2 (WSL2)
- **Kernel:** Linux 6.6.87.2-microsoft-standard-WSL2
- **Distribusjon:** Ubuntu (antagelig)
- **Working Directory:** `/home/silver/prosjekter/trening`

## Prosjekt: Treningsassistent

En intelligent treningsassistent som tracker muskeltreningog foreslår øvelser basert på:
- Muskelprioritet (tid siden sist trent)
- Antagonistisk balanse (bryst/rygg, biceps/triceps, etc.)
- Øvelsesrotasjon for variasjon
- Tilgjengelig utstyr

### Teknologi Stack
- **Backend:** FastAPI 0.104.1 ✅ (Python 3.10.12)
- **Database:** PostgreSQL 14.19 ✅
- **ORM:** SQLAlchemy 2.0.23 ✅
- **Migreringer:** Alembic 1.12.1 ✅
- **Auth:** JWT tokens + bcrypt ✅
- **Data:** 873 exercises from free-exercise-db ✅
- **Frontend:** Ikke implementert ennå

## Prosjektstruktur

```
/home/silver/prosjekter/trening/
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
│   ├── .env                  ✅ (configured)
│   └── README.md             ✅ (complete documentation)
├── exercise_images/          ✅ (1746 images, 873 exercises)
├── exercises.json            ✅ (873 øvelser fra free-exercise-db)
├── referansedok.md           (komplett prosjektplan)
├── data_mapping.md           (JSON → Database mapping)
└── claude.md                 (dette dokumentet)
```

**Status:** Backend er 100% ferdig og fungerende! 🎉

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

## Neste steg (valgfritt)

**Frontend Development:**
- Web app (React/Vue/Svelte)
- Mobil app (React Native/Flutter)

**Backend Enhancements:**
- Unit tests med pytest
- Docker/Docker Compose setup
- Deployment guide for Ubuntu server
- Email sending for invitations
- Password reset endpoint

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

Dette prosjektet bruker tre MCP servere for å gi Claude Code direkte tilgang til database, API-endepunkter, og filsystemet.

### Konfigurert i `.mcp.json` (prosjektrot):

```json
{
  "mcpServers": {
    "postgres": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-postgres", "postgres://postgres:securepassword123@localhost/treningsassistent"]
    },
    "fastapi": {
      "type": "sse",
      "url": "http://localhost:8000/mcp"
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/silver/prosjekter/trening"]
    }
  }
}
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

**Database Connection Details:**
- **Database:** `treningsassistent`
- **User:** `postgres`
- **Password:** `securepassword123`
- **Host:** `localhost`
- **Port:** `5432` (standard, ikke spesifisert i connection string)
- **Connection String:** `postgres://postgres:securepassword123@localhost/treningsassistent`

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
- Kjøre SQL queries direkte mot databasen
- Liste tabeller og kolonner
- Inserte, oppdatere, og slette data
- Hente statistikk og analysere data

### FastAPI MCP Server

FastAPI MCP serveren gir Claude Code direkte tilgang til alle backend API-endepunkter.

**Server Details:**
- **Type:** SSE (Server-Sent Events)
- **URL:** `http://localhost:8000/mcp`
- **Package:** `fastapi-mcp==0.4.0` (installert i venv)
- **Oppsett:** 3 linjer i `backend/app/main.py`:
  ```python
  from fastapi_mcp import FastApiMCP
  mcp = FastApiMCP(app)
  mcp.mount()
  ```

**Start Backend Server:**
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

### Filesystem MCP Server

Filesystem MCP serveren gir Claude Code direkte tilgang til filsystemet for fil- og mappeoperasjoner.

**Server Details:**
- **Type:** stdio
- **Command:** `npx`
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Scope:** `/home/silver/prosjekter/trening` (hele prosjektmappen)

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
- Backend er 100% ferdig og fungerende! 🎉
- Følg arkitekturen beskrevet i `referansedok.md`
- Bruk `data_mapping.md` for å mappe exercises.json til database
- Fokus nå kan være på testing, optimering, eller frontend-utvikling
- PostgreSQL er satt opp og kjører
- Alle Python-kommandoer kjøres i WSL2 Linux-miljø
- **Tre MCP servere er konfigurert:**
  - **PostgreSQL MCP** (`postgres`) - Direkte SQL queries mot databasen
  - **FastAPI MCP** (`fastapi`) - Direkte tilgang til alle 40+ API-endepunkter via SSE
  - **Filesystem MCP** (`filesystem`) - Fil- og mappeoperasjoner i prosjektmappen
- MCP-konfigurasjon finnes i `.mcp.json` og `.claude/settings.local.json`
- Backend server må kjøre på `http://localhost:8000` for at FastAPI MCP skal fungere
- Restart Claude Code etter MCP-konfigurasjonsendringer
