# Quick Start - Copy-paste dette til ny Claude Code session

## 📋 Hva du må vite

Hei Claude! Velkommen til Treningsassistent-prosjektet. Her er det viktigste du må vite:

### 🎯 Dette er et live produksjonsmiljø
- Du jobber **DIREKTE på produksjonsserveren** via sshfs-mount
- Working directory: `/home/silver/mounts/server` er mountet fra `gull:/home/sivert/treningsassistent`
- Alle file-endringer skjer live på serveren - ingen deploy nødvendig!

### 🔧 MCP Servere
Du har tilgang til 4 MCP-servere (konfigurert i `.mcp.json`):

1. **Postgres MCP** - Produksjons-database (localhost:15432 via SSH tunnel)
2. **Docker MCP** - Docker containers på produksjonsserver (via SSH til gull)
3. **Filesystem MCP** - Filer på serveren (via sshfs mount)
4. **FastAPI MCP** - Produksjons-API (localhost:8000 via SSH tunnel)

**VIKTIG - SSH Tunneler må kjøre:**
Før Claude Code starter må disse SSH-tunnelene være aktive:
```bash
# Postgres tunnel
ssh -f -N -L 15432:localhost:5432 gull

# FastAPI tunnel
ssh -f -N -L 8000:localhost:8000 gull
```

**Hvis MCP-servere ikke fungerer:**
1. Sjekk at SSH-tunnelene kjører: `ps aux | grep "ssh -f -N"`
2. Restart Claude Code så lastes `.mcp.json` på nytt
3. Docker MCP krever at `uv` er installert: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 📚 Komplett dokumentasjon
Les `CLAUDE_CODE_ONBOARDING.md` i rotmappen for:
- Full infrastruktur-oversikt
- MCP-server detaljer og troubleshooting
- Prosjektstruktur
- Database schema
- AI-algoritme forklaring
- Deploy-prosedyrer
- Hurtigkommandoer

Les `SECURITY.md` for sikkerhetskonfigurasjon:
- UFW firewall regler
- SSL/TLS sertifikater
- Nginx reverse proxy
- Port forwarding
- Sikkerhetssjekkliste

### 🚀 Teknologi Stack
- **Backend:** FastAPI + PostgreSQL (Docker containers)
- **Frontend:** React + TypeScript + Tailwind (Docker + Nginx)
- **AI:** Intelligent exercise recommendation algorithm
- **Data:** 873 exercises, 1746 images, 17 muscle groups

### ⚡ Hurtigkommandoer

```bash
# Sjekk Docker containers
# Bruk Docker MCP tools

# Sjekk database
# Bruk Postgres MCP tools

# Se git status
git status

# SSH til server
ssh gull

# Se backend logs
ssh gull "docker logs -f treningsassistent-backend"
```

### ⚠️ Viktig å huske
- Dette er PRODUKSJON - vær forsiktig med database-endringer
- Backend og frontend må rebuildes i Docker for å se endringer
- SSH tunnel på port 15432 gir tilgang til database
- Git-operasjoner fungerer som normalt

---

**Klar til å jobbe? Les `CLAUDE_CODE_ONBOARDING.md` for full dokumentasjon!**
