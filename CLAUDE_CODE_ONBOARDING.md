# Claude Code Onboarding - Treningsassistent

## 🎯 Prosjektoversikt

Dette er **Treningsassistent** - en intelligent treningsapp med AI-drevet øvelsesanbefaling. Appen kjører i produksjon på en remote server via Docker.

### Teknologi Stack
- **Backend:** FastAPI (Python) med PostgreSQL database
- **Frontend:** React med TypeScript, Vite, Tailwind CSS
- **Deployment:** Docker Compose på remote server (gull / 46.250.218.99)
- **AI-algoritme:** Øvelsesanbefaling basert på muskelprioritet, antagonistisk balanse og rotasjon

---

## 🏗️ Infrastruktur og Setup

### Working Directory Setup
Du kjører nå fra: `/home/silver/mounts/server`

Dette er **IKKE** en lokal mappe, men en **sshfs-mount** av produksjonsserveren!

```
┌────────────────────────────────────────────────────────┐
│              WSL (Lokal maskin)                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ~/mounts/server/  ←─ sshfs ─→  gull (10.0.0.20)     │
│  (working dir)                   /home/sivert/        │
│                                  treningsassistent     │
│                                                        │
│  ALLE ENDRINGER SKJER DIREKTE PÅ SERVEREN!            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Fordeler:**
- ✅ Ingen deploy-script nødvendig - endringer skjer live
- ✅ Git operasjoner fungerer direkte på serveren
- ✅ Kan se Docker containers, logs, etc. via MCP

**Viktig å vite:**
- Filer du redigerer er DIREKTE på produksjonsserveren
- Backend og frontend kjører i Docker containers på serveren
- Database er PostgreSQL i Docker på serveren

---

## 🔧 MCP Servere (Model Context Protocol)

### Konfigurerte MCP Servere

Filen `.mcp.json` i rotmappen konfigurerer 4 MCP-servere:

#### 1. **Postgres MCP**
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres",
           "postgres://postgres:Tr3n1ng_Pr0d_P4ssw0rd_2024!@localhost:15432/treningsassistent"]
}
```
- **Port 15432** = SSH tunnel til produksjons-database (port 5432 på serveren)
- Gir direkte tilgang til å kjøre SQL-queries mot produksjons-DB
- Bruk med varsomhet - dette er LIVE data!

#### 2. **Filesystem MCP**
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/silver/mounts/server"]
}
```
- Gir tilgang til filer via sshfs-mountet
- Peker til `/home/silver/mounts/server` (som er mounted fra serveren)

#### 3. **Docker MCP**
```json
{
  "command": "uvx",
  "args": ["mcp-server-docker"],
  "env": {
    "DOCKER_HOST": "ssh://gull"
  }
}
```
- **DOCKER_HOST** = ssh://gull (SSH alias til produksjonsserver)
- Gir tilgang til Docker containers, logs, networks, volumes på serveren
- Nyttig for å se container status, hente logs, etc.

#### 4. **FastAPI MCP**
```json
{
  "type": "sse",
  "url": "http://46.250.218.99:8000/mcp"
}
```
- Direkte HTTP-tilgang til FastAPI backend
- Kan teste API-endpoints, hente OpenAPI schema, etc.
- **Viktig:** Dette er produksjons-API-et!

### Troubleshooting MCP

**Hvis MCP-servere ikke vises:**
1. Restart Claude Code
2. Sjekk at `.mcp.json` finnes i rotmappen
3. Sjekk at alle dependencies er installert:
   ```bash
   npx -y @modelcontextprotocol/server-postgres --version
   npx -y @modelcontextprotocol/server-filesystem --version
   uvx mcp-server-docker --version
   ```

**Hvis Postgres MCP feiler:**
```bash
# Sjekk at SSH tunnel kjører
ss -tulpn | grep 15432
```

**Hvis Docker MCP feiler:**
```bash
# Test SSH-tilkobling
ssh gull "docker ps"
```

---

## 📂 Prosjektstruktur

```
/home/silver/mounts/server/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── database.py     # Database connection
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── App.tsx         # Main app
│   ├── package.json
│   └── Dockerfile
├── exercise_images/        # 1746 exercise images
├── exercises.json          # 873 exercises from free-exercise-db
├── docker-compose.yml      # Docker orchestration
├── .mcp.json              # MCP server configuration
├── .env                   # Development environment
├── .env.production        # Production environment (brukes nå!)
└── scripts/               # Utility scripts
```

---

## 🚀 Deployment og Services

### Docker Compose Services

Kjører på produksjonsserveren (gull):

```yaml
services:
  db:           # PostgreSQL 16-alpine
    Port: 5432  # Tilgjengelig via SSH tunnel på localhost:15432

  backend:      # FastAPI
    Port: 8000  # http://46.250.218.99:8000
    Health: curl http://localhost:8000/health

  frontend:     # Nginx med React build
    Port: 8080  # http://46.250.218.99:8080
    Health: curl http://localhost:80
```

### Sjekke Service Status

**Via Docker MCP:**
```
List containers, check logs, etc.
```

**Via SSH:**
```bash
ssh gull "docker ps"
ssh gull "docker logs treningsassistent-backend"
```

### Deploy nye endringer

**Backend:**
```bash
ssh gull "cd treningsassistent && docker compose build backend && docker compose up -d backend"
```

**Frontend:**
```bash
ssh gull "cd treningsassistent && docker compose build frontend && docker compose up -d frontend"
```

**Eller redeploy alt:**
```bash
ssh gull "cd treningsassistent && docker compose up -d --build"
```

---

## 💾 Database

### Connection Info
- **Host:** localhost (via SSH tunnel port 15432)
- **Database:** treningsassistent
- **User:** postgres
- **Password:** Tr3n1ng_Pr0d_P4ssw0rd_2024!

### Schema
- `brukere` - Users (invite-only registration)
- `invitasjoner` - Invitation codes
- `ovelser` - 873 exercises
- `ovelser_utfort` - Completed exercises log
- `muskler` - 17 muscle groups
- `antagonistiske_par` - Antagonistic muscle pairs
- `bruker_muskel_status` - User muscle training status
- `utstyr` - 12 equipment types
- `bruker_utstyr_profiler` - User equipment profiles

### Migrations
```bash
# Kjør migrations (i backend container)
ssh gull "docker exec treningsassistent-backend alembic upgrade head"
```

---

## 🎨 Frontend

### Tech Stack
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- React Router
- Axios (HTTP client)

### Viktige filer
- `src/App.tsx` - Main app component
- `src/services/api.ts` - API client
- `src/components/features/ExerciseCard.tsx` - Exercise display
- `src/pages/` - Page components

### Utviklingstips
- Frontend er bygget og served av Nginx i Docker
- For å se endringer må du rebuilde frontend:
  ```bash
  ssh gull "cd treningsassistent && docker compose build frontend && docker compose restart frontend"
  ```

---

## 🔐 Authentication

### JWT-basert auth
- Invite-only registrering
- Admin kan generere invitasjonskoder
- JWT tokens med expiry
- Brukes i Authorization header: `Bearer <token>`

### Test Users
Admin user finnes i databasen (se `brukere` tabellen)

---

## 🤖 AI-algoritmen

### Øvelsesanbefaling
Algoritmen velger neste øvelse basert på:

1. **Muskelprioritet** (60% vekt)
   - Tid siden muskel sist ble trent
   - Muskelgrupper som ikke er trent på lengst får høyest score

2. **Antagonistisk balanse** (25% vekt)
   - Balanserer motsatte muskelgrupper (bryst/rygg, biceps/triceps)
   - Gir bonus til antagonist hvis primær muskel er nylig trent

3. **Øvelsesrotasjon** (15% vekt)
   - Variasjon i øvelser for samme muskelgruppe
   - Unngår samme øvelse gjentatte ganger

4. **Utstyrsfiltrering**
   - Kun øvelser med tilgjengelig utstyr

### Endpoint
`GET /api/ovelser/neste-anbefaling`

Implementasjon: `backend/app/services/recommendation_service.py`

---

## 📚 Dokumentasjon

Viktige dokumentasjonsfiler i prosjektet:
- `README.md` - Prosjektintro
- `API.md` - Alle API endpoints
- `DEPLOYMENT.md` - Deploy guide
- `ENV.md` - Environment variables
- `claude.md` - Notat til Claude (deg!)
- `referansedok.md` - Muskelgrupper og antagonistiske par

---

## ⚡ Hurtigkommandoer

### SSH til server
```bash
ssh gull
```

### Se Docker logs
```bash
ssh gull "docker logs -f treningsassistent-backend"
ssh gull "docker logs -f treningsassistent-frontend"
```

### Git operasjoner
```bash
# Alt fungerer som normalt - du er i et git repo!
git status
git add .
git commit -m "beskrivelse"
git push
```

### Restart services
```bash
ssh gull "docker compose restart backend"
ssh gull "docker compose restart frontend"
```

---

## 🎯 Neste Steg

Når du starter et nytt task:

1. **Les claude.md** for kontekst om hva som er gjort tidligere
2. **Sjekk git status** for å se current state
3. **Bruk MCP-servere** for å utforske:
   - Docker MCP for service status
   - Postgres MCP for database queries
   - FastAPI MCP for API testing
4. **Husk:** Du jobber direkte på produksjonsserveren!

---

## 🆘 Hvis noe går galt

### Backend crasher
```bash
ssh gull "docker logs treningsassistent-backend"
ssh gull "docker compose restart backend"
```

### Database problemer
```bash
# Sjekk at SSH tunnel kjører
ss -tulpn | grep 15432

# Restart tunnel (hvis den finnes)
# Se ~/.ssh/config for tunnel-oppsett
```

### Frontend ikke bygger
```bash
ssh gull "docker logs treningsassistent-frontend"
ssh gull "docker compose build --no-cache frontend"
```

### MCP-servere fungerer ikke
1. Restart Claude Code
2. Sjekk `.mcp.json` konfigurasjon
3. Test dependencies manuelt

---

**Lykke til! 🚀**

_Denne guiden er lagret i `/home/silver/mounts/server/CLAUDE_CODE_ONBOARDING.md`_
