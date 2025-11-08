# Deployment Guide - Treningsassistent

Dette dokumentet beskriver hvordan du deployer Treningsassistent til produksjonsserveren ved hjelp av Docker Compose.

## Forutsetninger

### På produksjonsserveren (gull)
- ✅ Docker 28.5.1+ installert
- ✅ Docker Compose installert
- ✅ SSH-tilgang konfigurert
- ✅ Minst 2GB RAM
- ✅ Minst 10GB ledig diskplass

### På utviklingsmaskinen
- ✅ Git installert
- ✅ SSH-tilgang til serveren konfigurert
- ✅ SSH-nøkkel: `/home/silver/prosjekter/trening/ssh/gull_id_ed25519`

## Deployment-arkitektur

```
┌─────────────────────────────────────────┐
│         Nginx (Port 80)                 │
│  - Serve frontend (React SPA)           │
│  - Proxy /api/* til backend             │
│  - Static file caching                  │
└──────────────┬──────────────────────────┘
               │
               │ /api/* requests
               │
┌──────────────▼──────────────────────────┐
│       Backend (Port 8000)               │
│  - FastAPI REST API                     │
│  - JWT authentication                   │
│  - AI exercise recommendations          │
└──────────────┬──────────────────────────┘
               │
               │ SQL queries
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL (Port 5432)             │
│  - User data                            │
│  - Exercise database (873 exercises)    │
│  - Workout history                      │
└─────────────────────────────────────────┘
```

## Steg-for-steg Deployment

### 1. Forbered miljøvariabler

```bash
# Generer sikker SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Kopier .env.production til .env og oppdater verdier
cp .env.production .env

# Rediger .env med sikre passord og nøkler
nano .env
```

**Viktig:** Oppdater følgende i `.env`:
- `POSTGRES_PASSWORD` - Sterkt databasepassord
- `SECRET_KEY` - Generert med kommandoen over

### 2. Kopier prosjekt til server

```bash
# Fra utviklingsmaskinen
cd /home/silver/prosjekter/trening

# Synkroniser filer til serveren (ekskluderer node_modules, venv, etc.)
rsync -avz --exclude='node_modules' \
           --exclude='venv' \
           --exclude='__pycache__' \
           --exclude='.git' \
           --exclude='*.pyc' \
           --exclude='dist' \
           --exclude='.env' \
           -e "ssh -i ssh/gull_id_ed25519" \
           . sivert@10.0.0.20:~/treningsassistent/
```

**Alternativt med Git:**
```bash
# På serveren
ssh gull
cd ~
git clone https://github.com/Zievert/treningsassistent.git
cd treningsassistent
```

### 3. Konfigurer .env på serveren

```bash
# SSH til serveren
ssh gull

# Naviger til prosjektmappen
cd ~/treningsassistent

# Opprett .env fra .env.production
cp .env.production .env

# Generer SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Rediger .env og oppdater SECRET_KEY og POSTGRES_PASSWORD
nano .env
```

### 4. Start applikasjonen

```bash
# På serveren (gull)
cd ~/treningsassistent

# Bygg og start alle containers
docker compose up -d

# Følg loggene
docker compose logs -f
```

**Forventede logger:**
```
treningsassistent-db-1       | database system is ready to accept connections
treningsassistent-backend-1  | Running database migrations...
treningsassistent-backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000
treningsassistent-frontend-1 | /docker-entrypoint.sh: Starting nginx
```

### 5. Verifiser deployment

```bash
# Sjekk at alle containers kjører
docker compose ps

# Forventer:
# NAME                          STATUS              PORTS
# treningsassistent-backend-1   Up (healthy)        0.0.0.0:8000->8000/tcp
# treningsassistent-db-1        Up (healthy)        0.0.0.0:5432->5432/tcp
# treningsassistent-frontend-1  Up (healthy)        0.0.0.0:80->80/tcp

# Test backend health
curl http://localhost:8000/health

# Test frontend health
curl http://localhost/health

# Test API
curl http://localhost/api/health
```

### 6. Initialiser database

```bash
# På serveren
cd ~/treningsassistent

# Kjør database import script
docker compose exec backend python scripts/import_data.py

# Opprett admin-bruker
docker compose exec backend python manage.py create-admin \
    --username admin \
    --password changeme \
    --email admin@example.com
```

### 7. Tilgang til applikasjonen

Applikasjonen er nå tilgjengelig på:
- **Frontend:** http://10.0.0.20/
- **API Dokumentasjon:** http://10.0.0.20/docs
- **API Direkte:** http://10.0.0.20/api/*

## Administrering

### Stoppe applikasjonen

```bash
docker compose down
```

### Stoppe og slette data

```bash
# ADVARSEL: Dette sletter ALL data!
docker compose down -v
```

### Oppdatere applikasjonen

```bash
# Fra utviklingsmaskinen - synkroniser oppdateringer
rsync -avz --exclude='node_modules' \
           --exclude='venv' \
           --exclude='__pycache__' \
           --exclude='.git' \
           --exclude='*.pyc' \
           --exclude='dist' \
           --exclude='.env' \
           -e "ssh -i ssh/gull_id_ed25519" \
           . sivert@10.0.0.20:~/treningsassistent/

# På serveren - rebuild og restart
ssh gull
cd ~/treningsassistent
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Se logger

```bash
# Alle containers
docker compose logs -f

# Kun backend
docker compose logs -f backend

# Siste 100 linjer
docker compose logs --tail=100
```

### Database backup

```bash
# Backup
docker compose exec db pg_dump -U postgres treningsassistent > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20250108.sql | docker compose exec -T db psql -U postgres treningsassistent
```

### Restart en spesifikk tjeneste

```bash
docker compose restart backend
docker compose restart frontend
docker compose restart db
```

## Feilsøking

### Backend starter ikke

```bash
# Sjekk logger
docker compose logs backend

# Vanlige problemer:
# - Database ikke klar: Vent 10 sekunder og restart
# - .env mangler: Sjekk at .env eksisterer
# - Migreringer feiler: Kjør manuelt
docker compose exec backend alembic upgrade head
```

### Frontend viser blank side

```bash
# Sjekk at build var vellykket
docker compose logs frontend

# Rebuild frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Database tilkoblingsfeil

```bash
# Sjekk at database er oppe
docker compose ps db

# Sjekk database logger
docker compose logs db

# Test database tilkobling
docker compose exec db psql -U postgres -d treningsassistent -c "SELECT 1"
```

### Port allerede i bruk

```bash
# Sjekk hva som bruker porten
sudo lsof -i :80
sudo lsof -i :8000

# Stopp konflikterende tjeneste eller endre port i docker-compose.yml
```

## Sikkerhet

### Anbefalte tiltak

1. **Bruk sterke passord**
   - Database: `POSTGRES_PASSWORD`
   - JWT: `SECRET_KEY`

2. **Begrens nettverkstilgang**
   ```bash
   # Eksempel: Kun tillat fra lokalt nettverk
   sudo ufw allow from 10.0.0.0/24 to any port 80
   ```

3. **Regelmessige backups**
   ```bash
   # Sett opp cron job for daglig backup
   0 2 * * * cd ~/treningsassistent && docker compose exec db pg_dump -U postgres treningsassistent > ~/backups/db_$(date +\%Y\%m\%d).sql
   ```

4. **Overvåk logger**
   ```bash
   # Sjekk for feilmeldinger daglig
   docker compose logs --since 24h | grep ERROR
   ```

5. **Oppdater Docker images**
   ```bash
   # Trekk siste images månedlig
   docker compose pull
   docker compose up -d
   ```

## Ytelse

### Anbefalte ressurser

- **Minimum:**
  - 2GB RAM
  - 2 CPU cores
  - 10GB disk

- **Anbefalt:**
  - 4GB RAM
  - 4 CPU cores
  - 20GB disk

### Optimalisering

```yaml
# Legg til i docker-compose.yml under services:
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

## Support

Ved problemer:
1. Sjekk logger: `docker compose logs -f`
2. Verifiser .env konfigurasjonen
3. Sjekk disk plass: `df -h`
4. Sjekk minne: `free -h`
5. Restart tjenesten: `docker compose restart`

## Neste steg

- [ ] Sett opp HTTPS med Let's Encrypt
- [ ] Konfigurer domenenavn
- [ ] Sett opp automatiske backups
- [ ] Konfigurer logging til fil
- [ ] Sett opp monitoring (Prometheus + Grafana)
