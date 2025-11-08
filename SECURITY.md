# Security Configuration - Treningsassistent

Dette dokumentet beskriver sikkerhetskonfigurasjonen for Treningsassistent produksjonsserver.

## Oversikt

Sikkerhetsarkitekturen benytter "defense in depth" med flere lag av beskyttelse:

1. **Router NAT/Port Forwarding** - Første forsvarslinje
2. **UFW Firewall** - Server-nivå beskyttelse
3. **SSL/TLS Encryption** - Kryptert kommunikasjon
4. **Nginx Reverse Proxy** - Application-level routing
5. **Docker Isolation** - Container-nivå isolering

---

## 1. Router Port Forwarding

**Åpne porter i router (10.0.0.138):**

| Port | Protokoll | Destination | Formål |
|------|-----------|-------------|--------|
| 80   | TCP       | 10.0.0.20:80 | HTTP - Let's Encrypt + redirect til HTTPS |
| 443  | TCP       | 10.0.0.20:443 | HTTPS - All produksjonstrafikk |

**Lukkede porter:**
- ❌ Port 8080 (Docker frontend) - Ikke eksponert
- ❌ Port 8000 (Docker backend) - Ikke eksponert
- ❌ Port 5432 (PostgreSQL) - Ikke eksponert

---

## 2. UFW Firewall (Server-nivå)

### Status
```bash
ssh gull "sudo ufw status"
```

**Output:**
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), allow (routed)
```

### Aktive Regler

| Port/Service | Fra | Beskrivelse |
|--------------|-----|-------------|
| 22/tcp | Anywhere | SSH - Fjernstyringstilgang |
| 80/tcp | Anywhere | HTTP - Let's Encrypt og redirect |
| 443/tcp | Anywhere | HTTPS - Produksjonstrafikk (kryptert) |
| 8123/tcp | 10.0.0.0/24 | Home Assistant - Kun lokalt nettverk |

### UFW Kommandoer

**Vis status:**
```bash
ssh gull "sudo ufw status verbose"
```

**Vis nummererte regler:**
```bash
ssh gull "sudo ufw status numbered"
```

**Legg til ny regel:**
```bash
ssh gull "sudo ufw allow [port]/tcp comment 'Beskrivelse'"
```

**Fjern regel (etter nummer):**
```bash
ssh gull "sudo ufw delete [nummer]"
```

**Disable/Enable firewall:**
```bash
ssh gull "sudo ufw disable"  # Deaktiver
ssh gull "sudo ufw enable"   # Aktiver
```

### Docker-integrasjon

UFW er konfigurert til å fungere med Docker:

**Konfigurasjonsfil:** `/etc/default/ufw`
```bash
DEFAULT_FORWARD_POLICY="ACCEPT"
```

Dette tillater Docker containers å forwarde trafikk internt.

---

## 3. SSL/TLS Encryption

### Let's Encrypt Certificate

**Domene:** `silverha.hopto.org`

**Certificate Info:**
```bash
ssh gull "sudo certbot certificates"
```

**Sertifikat-filer:**
- Certificate: `/etc/letsencrypt/live/silverha.hopto.org/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/silverha.hopto.org/privkey.pem`

### Fornyelse

Certbot fornyer automatisk sertifikater som utløper innen 30 dager.

**Manuell fornyelse (hvis nødvendig):**
```bash
ssh gull "sudo certbot renew"
```

**Test fornyelse uten å faktisk fornye:**
```bash
ssh gull "sudo certbot renew --dry-run"
```

**Sjekk fornyelsestimer:**
```bash
ssh gull "sudo systemctl status certbot.timer"
```

### SSL Configuration i Nginx

**TLS Protokoller:** TLSv1.2, TLSv1.3
**Ciphers:** HIGH:!aNULL:!MD5
**Prefer Server Ciphers:** On

Se `/etc/nginx/sites-available/homeassistant` for komplett konfigurasjon.

---

## 4. Nginx Reverse Proxy

### Path-Based Routing

Nginx fungerer som reverse proxy med SSL termination:

| URL Path | Destination | Beskrivelse |
|----------|-------------|-------------|
| `/trening/api/*` | `http://localhost:8000/api/*` | Treningsassistent API |
| `/trening/*` | `http://localhost:8080/` | Treningsassistent Frontend |
| `/*` | `http://10.0.0.21:8123` | Home Assistant |

### HTTP til HTTPS Redirect

All HTTP-trafikk (port 80) redirectes automatisk til HTTPS (port 443):

```nginx
server {
    listen 80;
    server_name silverha.hopto.org;

    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}
```

### Nginx Konfigurasjon

**Konfigurasjonsfil:** `/etc/nginx/sites-available/homeassistant`

**Test konfigurasjonen:**
```bash
ssh gull "sudo nginx -t"
```

**Reload etter endringer:**
```bash
ssh gull "sudo systemctl reload nginx"
```

**Se status:**
```bash
ssh gull "sudo systemctl status nginx"
```

---

## 5. Application Security

### CORS (Cross-Origin Resource Sharing)

Backend tillater requests fra:
- `https://silverha.hopto.org` (produksjon)
- `http://localhost:5173` (lokal utvikling)
- `http://localhost:8080` (lokal testing)

Se `backend/app/main.py` for CORS-konfigurasjon.

### JWT Authentication

- Token-basert autentisering
- Tokens lagres i localStorage på frontend
- Bearer token sendes i Authorization header

---

## 6. Sikkerhetssjekkliste

**Daglig:**
- ✅ Containers kjører og er healthy
- ✅ UFW firewall er aktiv
- ✅ SSL-sertifikat er gyldig

**Månedlig:**
- ✅ Sjekk UFW logger: `ssh gull "sudo tail -f /var/log/ufw.log"`
- ✅ Sjekk Nginx access logs: `ssh gull "sudo tail -f /var/log/nginx/access.log"`
- ✅ Sjekk for security updates: `ssh gull "sudo apt update && apt list --upgradable"`

**Ved behov:**
- ✅ Review UFW regler
- ✅ Oppdater SSL-sertifikat (automatisk via certbot)
- ✅ Backup database

---

## 7. Feilsøking

### Firewall blokkerer tilgang

**Sjekk om UFW blokkerer:**
```bash
ssh gull "sudo ufw status verbose"
```

**Midlertidig disable for testing:**
```bash
ssh gull "sudo ufw disable"
# Test tilgang
ssh gull "sudo ufw enable"
```

### SSL Certificate Issues

**Sjekk certificate expiry:**
```bash
ssh gull "sudo certbot certificates"
```

**Manuell fornyelse:**
```bash
ssh gull "sudo certbot renew --force-renewal"
```

### Docker Container Communication Issues

**Sjekk at forward policy er ACCEPT:**
```bash
ssh gull "cat /etc/default/ufw | grep DEFAULT_FORWARD_POLICY"
```

**Skal være:**
```
DEFAULT_FORWARD_POLICY="ACCEPT"
```

---

## 8. Emergency Access

Hvis du låser deg ute fra serveren:

1. **Fysisk tilgang:** Koble til server via tastatur/skjerm
2. **Disable UFW:**
   ```bash
   sudo ufw disable
   ```
3. **Fix regler og re-enable:**
   ```bash
   sudo ufw enable
   ```

**VIKTIG:** Alltid ha SSH (port 22) tillatt før du aktiverer UFW!

---

## 9. Security Contacts

**Rapporter sikkerhetsproblemer til:**
- GitHub Issues: https://github.com/Zievert/treningsassistent/issues
- Email: sivert.hassel@gmail.com

---

## Changelog

### 2025-11-08
- ✅ Aktivert UFW firewall med regler for SSH, HTTP, HTTPS
- ✅ Konfigurert UFW for Docker-kompatibilitet
- ✅ Lukket direkte tilgang til Docker porter (8080, 8000)
- ✅ Implementert path-based routing via Nginx
- ✅ SSL/HTTPS aktivert for produksjonstrafikk
