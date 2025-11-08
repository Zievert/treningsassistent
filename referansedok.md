TRENINGSASSISTENT - Komplett prosjektplan
1. PROSJEKTOVERSIKT
Konsept
En intelligent treningsassistent som hjelper brukere med å strukturere styrketrening ved å:

Tracke hvilke muskler som er trent og når
Foreslå neste øvelse basert på muskelprioritet
Sikre balansert trening av alle muskelgrupper
Håndtere antagonistisk muskelbalanse
Rotere øvelser for variasjon
Tilpasse til tilgjengelig utstyr

Kjerneprinsipp
Systemet opererer som en kontinuerlig treningsflyt - ingen "økter" med start/stopp. Brukeren logger øvelser når som helst, og systemet holder kontinuerlig oversikt og foreslår alltid neste øvelse basert på current state.

2. TEKNOLOGI STACK
Backend

Framework: FastAPI (Python 3.11+)
Database: PostgreSQL 15+
ORM: SQLAlchemy
Migreringer: Alembic
Autentisering: JWT tokens + bcrypt password hashing
API-dokumentasjon: Automatisk via FastAPI (Swagger UI)

Frontend

Framework: React
Visualisering: Plotly.js (heatmaps, grafer)
HTTP Client: Axios
State Management: React Context eller Redux (avgjøres senere)

Deployment (Ubuntu Server)

Web Server: Nginx (reverse proxy + static files)
Application Server: Gunicorn/Uvicorn workers
SSL: Let's Encrypt (Certbot)
Backup: Automatisk PostgreSQL backup (cron + pg_dump)
Process Management: Systemd service

Datakilde for øvelser

Free Exercise DB (GitHub: yuhonas/free-exercise-db)
- 873 øvelser med primære/sekundære muskler, utstyr, instruksjoner
- Statisk JSON-fil (ikke API) - lastes ned og importeres til lokal database
- Public domain (Unlicense) - gratis for kommersiell bruk
- Statiske bilder (2620 filer)
- Ingen GIFs i MVP (kan legges til senere via YouTube-integrasjon eller kjøp)
- GitHub: https://github.com/yuhonas/free-exercise-db
- JSON URL: https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json


3. DATABASE-STRUKTUR
Global tabeller (deles av alle brukere)
MUSKLER
sqlCREATE TABLE muskler (
    muskel_id SERIAL PRIMARY KEY,
    muskel_navn VARCHAR(100) NOT NULL UNIQUE,
    hovedkategori VARCHAR(50) NOT NULL,  -- 'overkropp_push', 'overkropp_pull', 'ben', 'core'
    underkategori VARCHAR(50)  -- 'bryst', 'rygg', 'armer', 'skulder', etc.
);
Eksempel-data:

Pectoralis major (overkropp_push, bryst)
Latissimus dorsi (overkropp_pull, rygg)
Biceps brachii (overkropp_pull, armer)
Triceps (overkropp_push, armer)
Quadriceps (ben, lår)
Hamstrings (ben, lår)
Gastrocnemius (ben, legg)
Rectus abdominis (core, abs)
etc.

ANTAGONISTISKE_PAR
sqlCREATE TABLE antagonistiske_par (
    par_id SERIAL PRIMARY KEY,
    muskel_1_id INTEGER REFERENCES muskler(muskel_id),
    muskel_2_id INTEGER REFERENCES muskler(muskel_id),
    onsket_ratio DECIMAL DEFAULT 1.0  -- Ønsket balanse (1.0 = 1:1)
);
Eksempel-par:

Pectoralis ↔ Latissimus (1:1)
Quadriceps ↔ Hamstrings (1:1)
Biceps ↔ Triceps (1:1)
Anterior deltoid ↔ Posterior deltoid (1:1)
Rectus abdominis ↔ Lower back (1:1)

UTSTYR
sqlCREATE TABLE utstyr (
    utstyr_id SERIAL PRIMARY KEY,
    utstyr_navn VARCHAR(100) NOT NULL UNIQUE,
    kategori VARCHAR(50)  -- 'fri_vekt', 'maskin', 'kroppsvekt', 'kabel', etc.
);
Eksempel-utstyr:

Kroppsvekt
Vektstang (Barbell)
Dumbbells
Benk
Pull-up bar
Squat rack
Kabelmaskin
Leg press maskin
Leg curl maskin
Smith machine
Kettlebells
Resistance bands
etc.

OVELSER
sqlCREATE TABLE ovelser (
    ovelse_id SERIAL PRIMARY KEY,
    ovelse_navn VARCHAR(200) NOT NULL UNIQUE,
    gif_url TEXT,
    video_url TEXT,
    instruksjoner TEXT,
    tips TEXT[],  -- Array av strings
    vanlige_feil TEXT[]  -- Array av strings
);

-- Junction table: Kobler øvelser til muskler
CREATE TABLE ovelse_muskler (
    ovelse_id INTEGER REFERENCES ovelser(ovelse_id) ON DELETE CASCADE,
    muskel_id INTEGER REFERENCES muskler(muskel_id),
    muskel_type VARCHAR(20) NOT NULL,  -- 'primar' eller 'sekundar'
    PRIMARY KEY (ovelse_id, muskel_id)
);

-- Junction table: Kobler øvelser til utstyr
CREATE TABLE ovelse_utstyr (
    ovelse_id INTEGER REFERENCES ovelser(ovelse_id) ON DELETE CASCADE,
    utstyr_id INTEGER REFERENCES utstyr(utstyr_id),
    PRIMARY KEY (ovelse_id, utstyr_id)
);
Eksempel data-struktur:
json// ovelser tabell
{
  "ovelse_id": 1,
  "ovelse_navn": "Barbell Bench Press",
  "gif_url": "https://...",
  "instruksjoner": "1. Ligg på benken...",
  "tips": ["Hold albuene i 45° vinkel", ...]
}

// ovelse_muskler tabell
[
  { "ovelse_id": 1, "muskel_id": 1, "muskel_type": "primar" },      // Pectoralis major
  { "ovelse_id": 1, "muskel_id": 4, "muskel_type": "sekundar" },    // Triceps
  { "ovelse_id": 1, "muskel_id": 15, "muskel_type": "sekundar" }    // Anterior deltoid
]

// ovelse_utstyr tabell
[
  { "ovelse_id": 1, "utstyr_id": 2 },  // Vektstang
  { "ovelse_id": 1, "utstyr_id": 4 }   // Benk
]
Bruker-tabeller
BRUKERE
sqlCREATE TABLE brukere (
    bruker_id SERIAL PRIMARY KEY,
    brukernavn VARCHAR(50) NOT NULL UNIQUE,
    passord_hash VARCHAR(255) NOT NULL,
    epost VARCHAR(255) NOT NULL UNIQUE,
    opprettet_dato TIMESTAMP DEFAULT NOW(),
    aktiv BOOLEAN DEFAULT TRUE,
    rolle VARCHAR(20) DEFAULT 'bruker'  -- 'admin' eller 'bruker'
);
INVITASJONER
sqlCREATE TABLE invitasjoner (
    invitasjon_id SERIAL PRIMARY KEY,
    invitasjonskode VARCHAR(50) NOT NULL UNIQUE,
    opprettet_av_bruker_id INTEGER REFERENCES brukere(bruker_id),
    epost VARCHAR(255),
    brukt BOOLEAN DEFAULT FALSE,
    opprettet_dato TIMESTAMP DEFAULT NOW(),
    utloper_dato TIMESTAMP
);
BRUKER_MUSKEL_STATUS
sqlCREATE TABLE bruker_muskel_status (
    status_id SERIAL PRIMARY KEY,
    bruker_id INTEGER REFERENCES brukere(bruker_id),
    muskel_id INTEGER REFERENCES muskler(muskel_id),
    sist_trent_dato TIMESTAMP,
    antall_ganger_trent INTEGER DEFAULT 0,
    total_volum DECIMAL DEFAULT 0,  -- Akkumulert volum (sett × reps × vekt), vektet for primær/sekundær
    UNIQUE(bruker_id, muskel_id)
);
BRUKER_OVELSE_HISTORIKK
sqlCREATE TABLE bruker_ovelse_historikk (
    historikk_id SERIAL PRIMARY KEY,
    bruker_id INTEGER REFERENCES brukere(bruker_id),
    ovelse_id INTEGER REFERENCES ovelser(ovelse_id),
    sist_brukt_dato TIMESTAMP,
    antall_ganger_brukt INTEGER DEFAULT 0,
    UNIQUE(bruker_id, ovelse_id)
);
OVELSER_UTFORT
sqlCREATE TABLE ovelser_utfort (
    utfort_id SERIAL PRIMARY KEY,
    bruker_id INTEGER REFERENCES brukere(bruker_id),
    ovelse_id INTEGER REFERENCES ovelser(ovelse_id),
    sett INTEGER NOT NULL,
    repetisjoner INTEGER NOT NULL,
    vekt DECIMAL NOT NULL,
    tidspunkt TIMESTAMP DEFAULT NOW()
);
BRUKER_UTSTYR_PROFILER
sqlCREATE TABLE bruker_utstyr_profiler (
    profil_id SERIAL PRIMARY KEY,
    bruker_id INTEGER REFERENCES brukere(bruker_id),
    profil_navn VARCHAR(50) NOT NULL,  -- 'Gym', 'Hjemme', 'Reise'
    utstyr_ids INTEGER[] NOT NULL,  -- Array av utstyr_ids
    aktiv BOOLEAN DEFAULT FALSE,
    UNIQUE(bruker_id, profil_navn)
);

4. ALGORITME-LOGIKK (Regelbasert AI)
4.1 Muskel-prioritet beregning
pythondef beregn_prioritet(muskel, bruker_id):
    """
    Beregn prioritetsscore (0-140 poeng)
    """

    # BASIS: Tid siden sist trent (60% vekt, maks 100 poeng)
    if muskel.sist_trent_dato is None:
        tid_poeng = 100  # Aldri trent
    else:
        dager = (datetime.now() - muskel.sist_trent_dato).days
        tid_poeng = min(dager * 10, 100)

    # ANTAGONISTISK BALANSE (40% vekt, -20 til +40 poeng)
    # Basert på VOLUM (sett × reps × vekt) i stedet for bare frekvens
    antagonist_poeng = 0
    par = finn_antagonistisk_par(muskel)

    if par:
        muskel_volum = muskel.total_volum
        antagonist_volum = par.total_volum

        # Beregn ratio basert på volum
        if antagonist_volum == 0 and muskel_volum == 0:
            ratio = 1.0  # Begge utrente
        elif antagonist_volum == 0:
            ratio = 999  # Muskel overtrent
        else:
            ratio = muskel_volum / antagonist_volum

        # Tildel poeng basert på ratio
        if ratio < 0.85:
            antagonist_poeng = 40  # Sterk boost - undertrent
        elif ratio < 0.95:
            antagonist_poeng = 20  # Moderat boost
        elif ratio > 1.15:
            antagonist_poeng = -20  # Penalty - overtrent
        elif ratio > 1.05:
            antagonist_poeng = -10  # Liten penalty
        else:
            antagonist_poeng = 0  # Balansert (0.95-1.05)

    total_score = tid_poeng + antagonist_poeng
    return max(total_score, 0)  # Aldri negativ
4.2 Hovedalgoritme - Hent neste anbefaling
pythondef hent_neste_anbefaling(bruker_id):
    """
    Beregn og returner neste anbefalte øvelse
    """
    
    # 1. Hent alle brukerens muskler
    alle_muskler = hent_bruker_muskler(bruker_id)
    
    # 2. Beregn prioritet for hver muskel
    for muskel in alle_muskler:
        muskel.prioritet_score = beregn_prioritet(muskel, bruker_id)
    
    # 3. Sorter etter prioritet
    sortert = sorted(alle_muskler, key=lambda m: m.prioritet_score, reverse=True)
    
    # 4. Hvis alle har samme score (ny bruker), shuffle for variasjon
    if alle_har_samme_score(sortert):
        random.shuffle(sortert)
    
    # 5. Prøv å finne øvelse for topp 10 muskler (fallback hvis ingen match)
    neste_ovelse = None
    for muskel in sortert[:10]:
        neste_ovelse = finn_ovelse_for_muskel(muskel, bruker_id)
        if neste_ovelse is not None:
            fokus_muskel = muskel
            break
    
    # 6. Returner anbefaling
    return {
        'ovelse': neste_ovelse,
        'prioritert_muskel': fokus_muskel.muskel_navn,
        'dager_siden_trent': beregn_dager_siden(fokus_muskel.sist_trent_dato),
        'prioritet_score': fokus_muskel.prioritet_score
    }
4.3 Øvelse-valg med rotasjon og utstyr-filtrering
pythondef finn_ovelse_for_muskel(muskel, bruker_id):
    """
    Finn beste øvelse for en muskel med rotasjon og utstyr-filtrering
    """

    # 1. Hent brukerens tilgjengelige utstyr (fra aktiv profil)
    bruker_utstyr = hent_aktiv_utstyr_profil(bruker_id)

    # 2. Finn kandidat-øvelser (primær muskel + utstyr match)
    # Query med JOIN på ovelse_muskler og ovelse_utstyr
    kandidater = db.query(Ovelse).join(
        OvelseMuskler, OvelseMuskler.ovelse_id == Ovelse.ovelse_id
    ).filter(
        OvelseMuskler.muskel_id == muskel.muskel_id,
        OvelseMuskler.muskel_type == 'primar'
    ).all()

    # Filtrer for utstyr (sjekk at ALT nødvendig utstyr er tilgjengelig)
    kandidater = [
        o for o in kandidater
        if har_nodvendig_utstyr(o.ovelse_id, bruker_utstyr)
    ]

    # 3. Hvis ingen match, prøv kroppsvekt-øvelser
    if len(kandidater) == 0:
        kandidater = db.query(Ovelse).join(
            OvelseMuskler, OvelseMuskler.ovelse_id == Ovelse.ovelse_id
        ).join(
            OvelseUtstyr, OvelseUtstyr.ovelse_id == Ovelse.ovelse_id
        ).filter(
            OvelseMuskler.muskel_id == muskel.muskel_id,
            OvelseMuskler.muskel_type == 'primar',
            OvelseUtstyr.utstyr_id == 1  # 1 = Kroppsvekt
        ).all()

    # 4. Hvis fortsatt ingen match, returner None (hovedalgoritme velger neste muskel)
    if len(kandidater) == 0:
        return None

    # 5. Hent brukerens øvelse-historikk
    bruker_historikk = hent_bruker_ovelse_historikk(bruker_id)

    # 6. Beregn rotasjonsscore for hver kandidat
    scored_kandidater = []
    for ovelse in kandidater:
        historikk = bruker_historikk.get(ovelse.ovelse_id)

        if historikk is None:
            rotasjon_score = 1000  # Aldri brukt = høyest prioritet
        else:
            dager_siden = (datetime.now() - historikk.sist_brukt_dato).days
            rotasjon_score = dager_siden * 10

            # Straff overbrukte øvelser
            gjennomsnitt = beregn_gjennomsnitt_bruk(bruker_id)
            if historikk.antall_ganger_brukt > gjennomsnitt * 1.5:
                rotasjon_score *= 0.5

        scored_kandidater.append({
            'ovelse': ovelse,
            'score': rotasjon_score
        })

    # 7. Velg beste (høyest rotasjonsscore)
    scored_kandidater.sort(key=lambda x: x['score'], reverse=True)
    return scored_kandidater[0]['ovelse']


def har_nodvendig_utstyr(ovelse_id, bruker_utstyr_liste):
    """Sjekk om bruker har alt nødvendig utstyr for en øvelse"""
    krav = db.query(OvelseUtstyr.utstyr_id).filter(
        OvelseUtstyr.ovelse_id == ovelse_id
    ).all()
    krav_ids = [k[0] for k in krav]
    return all(utstyr_id in bruker_utstyr_liste for utstyr_id in krav_ids)
4.4 Logging av øvelse
pythondef logg_ovelse(bruker_id, ovelse_id, sett, reps, vekt):
    """
    Logg øvelse og oppdater alle relaterte data
    """

    # 1. Beregn total volum for denne loggingen
    volum = sett * reps * vekt

    # 2. Opprett ny rad i OVELSER_UTFORT
    utfort = OvelseUtfort(
        bruker_id=bruker_id,
        ovelse_id=ovelse_id,
        sett=sett,
        repetisjoner=reps,
        vekt=vekt,
        tidspunkt=datetime.now()
    )
    db.add(utfort)

    # 3. Oppdater BRUKER_OVELSE_HISTORIKK (for rotasjon)
    historikk = db.query(BrukerOvelseHistorikk).filter(
        BrukerOvelseHistorikk.bruker_id == bruker_id,
        BrukerOvelseHistorikk.ovelse_id == ovelse_id
    ).first()

    if historikk:
        historikk.sist_brukt_dato = datetime.now()
        historikk.antall_ganger_brukt += 1
    else:
        historikk = BrukerOvelseHistorikk(
            bruker_id=bruker_id,
            ovelse_id=ovelse_id,
            sist_brukt_dato=datetime.now(),
            antall_ganger_brukt=1
        )
        db.add(historikk)

    # 4. Hent alle involverte muskler via JOIN (både primære og sekundære)
    muskler = db.query(
        OvelseMuskler.muskel_id,
        OvelseMuskler.muskel_type
    ).filter(
        OvelseMuskler.ovelse_id == ovelse_id
    ).all()

    # 5. Oppdater BRUKER_MUSKEL_STATUS for ALLE involverte muskler
    # VIKTIG: Vekt primære (1.0) og sekundære (0.5) muskler forskjellig
    for muskel_id, muskel_type in muskler:
        # Beregn vektet volum
        if muskel_type == 'primar':
            vektet_volum = volum * 1.0  # Full kreditt
        else:  # sekundar
            vektet_volum = volum * 0.5  # Halv kreditt

        status = db.query(BrukerMuskelStatus).filter(
            BrukerMuskelStatus.bruker_id == bruker_id,
            BrukerMuskelStatus.muskel_id == muskel_id
        ).first()

        if status:
            status.sist_trent_dato = datetime.now()
            status.antall_ganger_trent += 1
            status.total_volum += vektet_volum
        else:
            status = BrukerMuskelStatus(
                bruker_id=bruker_id,
                muskel_id=muskel_id,
                sist_trent_dato=datetime.now(),
                antall_ganger_trent=1,
                total_volum=vektet_volum
            )
            db.add(status)

    # 6. Commit alle endringer
    db.commit()

    # 7. Returner neste anbefaling umiddelbart
    return hent_neste_anbefaling(bruker_id)
```

---

## 5. API ENDEPUNKTER

### Autentisering
```
POST /api/auth/login
Body: { brukernavn, passord }
Response: { access_token, token_type: "bearer" }

POST /api/auth/register
Body: { brukernavn, passord, epost, invitasjonskode }
Response: { success: true, bruker_id }

GET /api/auth/me
Headers: Authorization: Bearer {token}
Response: { bruker_id, brukernavn, epost, rolle }
```

### Admin (kun admin-rolle)
```
POST /api/admin/invitasjoner
Body: { epost }
Response: { invitasjonskode, utloper_dato }

GET /api/admin/invitasjoner
Response: [ liste av invitasjoner ]

GET /api/admin/brukere
Response: [ liste av brukere ]
```

### Øvelser
```
GET /api/ovelser/neste-anbefaling
Headers: Authorization: Bearer {token}
Response: {
  ovelse_id,
  ovelse_navn,
  gif_url,
  prioritert_muskel,
  dager_siden_trent,
  prioritet_score,
  primare_muskler: [...],
  sekundare_muskler: [...],
  utstyr_krav: [...]
}

GET /api/ovelser/alle
Query: ?kategori=overkropp_push&utstyr_id=2
Response: [ liste av øvelser ]

GET /api/ovelser/{ovelse_id}
Response: {
  ovelse_id,
  ovelse_navn,
  gif_url,
  video_url,
  instruksjoner,
  tips: [...],
  vanlige_feil: [...],
  primare_muskler: [...],
  sekundare_muskler: [...],
  utstyr_krav: [...]
}

POST /api/ovelser/logg
Headers: Authorization: Bearer {token}
Body: {
  ovelse_id,
  sett,
  reps,
  vekt
}
Response: {
  success: true,
  neste_anbefaling: { ... }
}
```

### Historikk
```
GET /api/historikk
Query: ?siste_dager=7&limit=50
Headers: Authorization: Bearer {token}
Response: [
  {
    utfort_id,
    ovelse_navn,
    sett,
    reps,
    vekt,
    tidspunkt,
    involverte_muskler: [...]
  },
  ...
]

GET /api/historikk/gruppert
Query: ?siste_dager=30
Response: [
  {
    dato: "2025-11-06",
    ovelser: [ liste av øvelser den dagen ],
    total_varighet_estimert: 55  // minutter
  },
  ...
]
```

### Statistikk
```
GET /api/statistikk/heatmap
Query: ?siste_dager=30
Headers: Authorization: Bearer {token}
Response: {
  muskler: [
    {
      muskel_navn,
      hovedkategori,
      trenings_datoer: ["2025-11-01", "2025-11-04", ...]
    },
    ...
  ]
}

GET /api/statistikk/antagonistisk
Headers: Authorization: Bearer {token}
Response: [
  {
    muskel_1: "Pectoralis major",
    muskel_2: "Latissimus dorsi",
    muskel_1_volum: 8400,  // Total vektet volum (sett × reps × vekt)
    muskel_2_volum: 7200,
    ratio: 1.17,
    onsket_ratio: 1.0,
    status: "ok"  // eller "ubalansert"
  },
  ...
]

GET /api/statistikk/volum
Query: ?siste_dager=90&gruppe_per=uke
Headers: Authorization: Bearer {token}
Response: [
  {
    periode: "2025-uke-44",
    total_volum: 12500,  // kg (sett × reps × vekt)
    per_kategori: {
      "overkropp_push": 4200,
      "overkropp_pull": 3800,
      "ben": 4000,
      "core": 500
    }
  },
  ...
]

GET /api/statistikk/muskel/{muskel_id}
Query: ?siste_dager=90
Response: {
  muskel_navn,
  antall_ganger_trent,
  sist_trent_dato,
  trenings_historikk: [
    { dato, ovelse_navn, volum },
    ...
  ]
}
```

### Utstyr
```
GET /api/bruker/utstyr/profiler
Headers: Authorization: Bearer {token}
Response: [
  {
    profil_id,
    profil_navn: "Gym",
    aktiv: true,
    utstyr: [
      { utstyr_id, utstyr_navn, kategori },
      ...
    ]
  },
  ...
]

POST /api/bruker/utstyr/profiler
Body: {
  profil_navn: "Hjemme",
  utstyr_ids: [1, 3, 4, 12]
}
Response: { profil_id, success: true }

PUT /api/bruker/utstyr/profiler/{profil_id}
Body: {
  profil_navn: "Gym oppdatert",
  utstyr_ids: [1, 2, 3, 4, 5, 6, 7]
}
Response: { success: true }

PUT /api/bruker/utstyr/profiler/{profil_id}/aktiver
Response: { success: true }

DELETE /api/bruker/utstyr/profiler/{profil_id}
Response: { success: true }

GET /api/utstyr/alle
Response: [
  { utstyr_id, utstyr_navn, kategori },
  ...
]
```

### Muskler
```
GET /api/muskler/alle
Response: [
  {
    muskel_id,
    muskel_navn,
    hovedkategori,
    underkategori
  },
  ...
]

GET /api/muskler/prioritet
Headers: Authorization: Bearer {token}
Response: [
  {
    muskel_navn,
    prioritet_score,
    dager_siden_trent,
    antall_ganger_trent,
    total_volum  // Vektet volum (sett × reps × vekt)
  },
  ...
]  // Sortert etter prioritet
```

---

## 6. BRUKERGRENSESNITT (React)

### Side-struktur
```
/login              - Login-side (offentlig)
/register?code=xxx  - Registrering med invitasjonskode (offentlig)
/                   - Hovedside med øvelse-anbefaling (krever innlogging)
/historikk          - Treningshistorikk
/statistikk         - Grafer og analyse
/innstillinger      - Brukerinnstillinger og utstyr-profiler
/admin              - Admin-panel (kun admin-rolle)
```

### Hovedskjerm (/)
```
┌─────────────────────────────────────────┐
│  💪 TRENINGSASSISTENT                   │
│  📍 [Gym ▼] Quick toggle profil         │
│                                          │
│  🎯 DIN NESTE ANBEFALTE ØVELSE:        │
│  ╔════════════════════════════════════╗ │
│  ║  [GIF Animasjon]                   ║ │
│  ║  Barbell Bench Press               ║ │
│  ║  Fokus: Pectoralis major           ║ │
│  ║  (5 dager siden sist)              ║ │
│  ║  [ℹ️ Detaljer] [▶️ Video]          ║ │
│  ╚════════════════════════════════════╝ │
│                                          │
│  📝 LOGG ØVELSE:                        │
│  Øvelse: [Barbell Bench Press ▼]        │
│  Sett:   [___]                          │
│  Reps:   [___]                          │
│  Vekt:   [___] kg                       │
│  [✅ Logg og vis neste]                 │
│                                          │
│  ─────────────────────────────────      │
│  📊 Siste 24 timer:                     │
│  • Lat Pulldown (4×10 @ 70kg) - 2t      │
│  • Tricep Pushdown (3×12 @ 25kg) - 2t  │
│  [Se full historikk]                    │
└─────────────────────────────────────────┘
```

### Statistikk-side (/statistikk)

**Faner:**
1. **Heatmap**: Oversikt over alle muskler siste 30/60/90 dager
2. **Antagonistisk balanse**: Gauge meters for muskelpar
3. **Volum over tid**: Grafer for total volum og per kategori
4. **Muskel-detalj**: Drill-down per muskel med kurver

---

## 7. SIKKERHET

### Autentisering
- JWT tokens med 24 timers expiry
- Bcrypt password hashing (cost factor 12)
- HTTPS obligatorisk (Let's Encrypt)

### SQL Injection beskyttelse
- SQLAlchemy ORM (parameteriserte queries)
- Pydantic validering på alle inputs
- ALDRI bruk string concatenation for SQL

### CORS
- Kun tillat requests fra eget domene
- FastAPI CORS middleware konfigurert

### Rate Limiting
- Login endpoint: 5 forsøk per 15 minutter
- API endpoints: 100 requests per minutt per bruker

### Input Validering
- Pydantic schemas validerer alle requests
- Type checking og lengde-begrensninger
- Sanitering av bruker-input

### Bruker-isolering
- Alle queries filtrerer på bruker_id fra JWT token
- Brukere kan ALDRI se andre brukeres data
- Admin kan se oversikt, men ikke endre brukeres treningsdata

---

## 8. DEPLOYMENT

### Server-struktur (Ubuntu)
```
/var/www/treningsapp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   ├── api/
│   │   │   ├── ovelser.py
│   │   │   ├── statistikk.py
│   │   │   ├── auth.py
│   │   │   ├── admin.py
│   │   │   └── utstyr.py
│   │   ├── services/
│   │   │   ├── ai_forslag.py
│   │   │   ├── exercise_api.py
│   │   │   └── statistikk.py
│   │   └── utils/
│   │       └── security.py
│   ├── requirements.txt
│   ├── alembic/
│   └── .env
├── frontend/
│   ├── build/  (production build)
│   └── src/
└── scripts/
    ├── backup.sh
    └── manage.py  (CLI for admin bruker, etc)
Nginx konfigurasjon
nginxserver {
    listen 443 ssl;
    server_name dinserver.com;

    ssl_certificate /etc/letsencrypt/live/dinserver.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dinserver.com/privkey.pem;

    # Frontend (React build)
    location / {
        root /var/www/treningsapp/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Systemd service
ini[Unit]
Description=Treningsassistent API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/treningsapp/backend
Environment="PATH=/var/www/treningsapp/backend/venv/bin"
ExecStart=/var/www/treningsapp/backend/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000 --workers 4

[Install]
WantedBy=multi-user.target
Backup script (cron)
bash#!/bin/bash
# /var/www/treningsapp/scripts/backup.sh

BACKUP_DIR="/var/backups/treningsapp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="treningsapp"
DB_USER="treningsuser"

# Backup database
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Behold kun siste 30 dager
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Valgfritt: Upload til cloud storage
# aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz s3://mybucket/
```

**Cron job:**
```
0 3 * * * /var/www/treningsapp/scripts/backup.sh
Første admin-bruker
python# manage.py
import typer
from app.database import SessionLocal
from app.models import Bruker
from app.utils.security import hash_password

app = typer.Typer()

@app.command()
def create_admin():
    """Opprett første admin-bruker"""
    brukernavn = typer.prompt("Brukernavn")
    epost = typer.prompt("Epost")
    passord = typer.prompt("Passord", hide_input=True)
    
    db = SessionLocal()
    
    admin = Bruker(
        brukernavn=brukernavn,
        epost=epost,
        passord_hash=hash_password(passord),
        rolle="admin",
        aktiv=True
    )
    db.add(admin)
    db.commit()
    
    typer.echo(f"✅ Admin-bruker '{brukernavn}' opprettet!")

if __name__ == "__main__":
    app()
Kjør:
bashpython manage.py create-admin

9. VIKTIGE IMPLEMENTASJONSDETALJER
Øvelse-database populering

**Datakilde:** Free Exercise DB (yuhonas/free-exercise-db)
- Last ned exercises.json fra GitHub
- 873 øvelser med primære/sekundære muskler, utstyr, instruksjoner
- Statiske bilder (ingen GIFs i MVP)
- Import via Python-script til PostgreSQL

**Import-prosess:**
1. Populer globale tabeller: `muskler` (17 rader), `utstyr` (12 rader)
2. Importer øvelser til `ovelser` tabell (873 rader)
3. Populer junction tables: `ovelse_muskler` og `ovelse_utstyr`
4. Last ned og host bilder (valgfritt - kan bruke GitHub raw URLs i MVP)

**Senere forbedringer:**
- GIF-animasjoner via YouTube-integrasjon eller kjøp (Gym Visual, IconScout)
- Egne videoer/tips for populære øvelser
- Norsk oversettelse av topp 100-200 øvelser

Muskel-taksonomi

**MVP-tilnærming:**
- Bruk simple muskel-navn fra Free Exercise DB (chest, shoulders, biceps, etc.)
- 17 muskelgrupper totalt
- Mapping til norske navn (f.eks. chest → Bryst, shoulders → Skuldre)

**Senere utvidelse:**
- Mappe til anatomiske navn (chest → Pectoralis major, etc.)
- Splitte composite muskler (shoulders → anterior/medial/posterior deltoid)
- Bruk anerkjent anatomi-standard (ACE Fitness, ExRx.net)

Baseline og forverring

Defineres i egen instans etter brainstorming
Brukerdefinerbare mål per muskelgruppe
Visualisering av "på/foran/bak schedule"

Visualisering

Heatmap: Plotly.js heatmap chart
Antagonistisk balanse: Custom gauge components
Volum: Line/bar charts med Plotly.js
Alle grafer interaktive


10. FREMTIDIGE FORBEDRINGER (ikke i MVP)

 Progressive overload tracking og forslag
 Periodisering-funksjoner
 Sosiale features (dele resultater, sammenligne)
 Treningspartnere / felles økter
 Mobil app (React Native)
 Offline mode med synkronisering
 Integrasjon med wearables
 AI-genererte treningsprogrammer (ML-basert)
 Kosthold-tracking
 Skade-forebygging varsler


11. TESTING
Backend

Pytest for unit tests
Test alle API endpoints
Test algoritme-logikk med mock data
Test SQL injection beskyttelse

Frontend

Jest + React Testing Library
Component tests
Integration tests

Manuell testing

Fullstendig user journey test
Cross-browser testing (Chrome, Firefox, Safari)
Mobile responsive testing
Performance testing (sideload tid, API responstid)


OPPSUMMERING
Dette prosjektet er en regelbasert, intelligent treningsassistent som:

Tracker muskeltrening kontinuerlig (ingen "økter")
Foreslår neste øvelse basert på muskel-prioritet, antagonistisk balanse og rotasjon
Tilpasser til brukerens tilgjengelige utstyr
Visualiserer progresjon og balanse
Fungerer som en personlig treningsguide

Teknologi: FastAPI + PostgreSQL + React + Nginx på Ubuntu server
Kjernealgoritme: Muskel-prioritet (tid + antagonist) → Finn øvelse (utstyr + rotasjon) → Logg → Oppdater alt → Repeat
Sikkerhet: JWT auth, invite-only, bcrypt, SQL injection beskyttelse, HTTPS
Deployment: Systemd service, Nginx reverse proxy, automatiske backups

---

VIKTIGE ENDRINGER FRA ORIGINAL DESIGN

1. **Normalisert database-struktur**
   - Øvelser bruker nå junction tables (ovelse_muskler, ovelse_utstyr) i stedet for INTEGER[] arrays
   - Bedre ytelse for filtrering og søk
   - Enklere å vedlikeholde og utvide

2. **Volum-basert antagonistisk balanse**
   - Balanse beregnes basert på total_volum (sett × reps × vekt) i stedet for bare antall_ganger_trent
   - Mer nøyaktig representasjon av faktisk belastning
   - Eksempel: 5 tunge sett vs 5 lette sett gir forskjellig balanse

3. **Vekting av primære vs sekundære muskler**
   - Primære muskler får full kreditt (1.0 × volum) når en øvelse logges
   - Sekundære muskler får halv kreditt (0.5 × volum)
   - Forhindrer at sekundære muskler "dominerer" prioritetsscoren

Dette dokumentet er klar for Claude Code å bruke som referanse under utvikling.