# Data Mapping: Free Exercise DB → Vår Database

## Oversikt
Kartlegging mellom free-exercise-db JSON-struktur og vår PostgreSQL database-struktur.

---

## 1. MUSKLER (Global tabell)

**Fra free-exercise-db:**
```json
"primaryMuscles": ["quadriceps"],
"secondaryMuskles": ["glutes", "hamstrings"]
```

**Til vår struktur:**
```sql
CREATE TABLE muskler (
    muskel_id SERIAL PRIMARY KEY,
    muskel_navn VARCHAR(100) NOT NULL UNIQUE,
    muskel_navn_no VARCHAR(100),  -- Norsk oversettelse (legges til senere)
    hovedkategori VARCHAR(50) NOT NULL,
    underkategori VARCHAR(50)
);
```

**Mapping-tabell (17 muskler):**
| free-exercise-db | muskel_navn | muskel_navn_no | hovedkategori | underkategori |
|------------------|-------------|----------------|---------------|---------------|
| chest | Chest | Bryst | overkropp_push | bryst |
| shoulders | Shoulders | Skuldre | overkropp_push | skulder |
| triceps | Triceps | Triceps | overkropp_push | armer |
| lats | Lats | Rygg (bred) | overkropp_pull | rygg |
| middle back | Middle Back | Rygg (midt) | overkropp_pull | rygg |
| lower back | Lower Back | Korsrygg | overkropp_pull | rygg |
| biceps | Biceps | Biceps | overkropp_pull | armer |
| forearms | Forearms | Underarmer | overkropp_pull | armer |
| traps | Traps | Trapesius | overkropp_pull | skulder |
| neck | Neck | Nakke | overkropp_pull | nakke |
| quadriceps | Quadriceps | Lårmuskler (foran) | ben | lår |
| hamstrings | Hamstrings | Lårmuskler (bak) | ben | lår |
| glutes | Glutes | Setemuskel | ben | sete |
| calves | Calves | Legger | ben | legg |
| adductors | Adductors | Innadføring | ben | lår |
| abductors | Abductors | Utadføring | ben | hofte |
| abdominals | Abdominals | Mage | core | abs |

---

## 2. UTSTYR (Global tabell)

**Fra free-exercise-db:**
```json
"equipment": "barbell"
```

**Til vår struktur:**
```sql
CREATE TABLE utstyr (
    utstyr_id SERIAL PRIMARY KEY,
    utstyr_navn VARCHAR(100) NOT NULL UNIQUE,
    utstyr_navn_no VARCHAR(100),
    kategori VARCHAR(50)
);
```

**Mapping-tabell (12 utstyr-typer):**
| free-exercise-db | utstyr_navn | utstyr_navn_no | kategori |
|------------------|-------------|----------------|----------|
| body only | Body Only | Kroppsvekt | kroppsvekt |
| barbell | Barbell | Vektstang | fri_vekt |
| dumbbell | Dumbbell | Manualer | fri_vekt |
| kettlebells | Kettlebells | Kettlebells | fri_vekt |
| e-z curl bar | E-Z Curl Bar | E-Z Stang | fri_vekt |
| cable | Cable | Kabel | kabel |
| machine | Machine | Maskin | maskin |
| bands | Resistance Bands | Strikk | annet |
| exercise ball | Exercise Ball | Treningsball | annet |
| foam roll | Foam Roller | Massasjerulle | annet |
| medicine ball | Medicine Ball | Medisinball | annet |
| other | Other | Annet | annet |

---

## 3. ØVELSER (Global tabell)

**Fra free-exercise-db:**
```json
{
  "id": "Barbell_Bench_Press",
  "name": "Barbell Bench Press",
  "force": "push",
  "level": "intermediate",
  "mechanic": "compound",
  "equipment": "barbell",
  "primaryMuscles": ["chest"],
  "secondaryMuscles": ["triceps", "shoulders"],
  "instructions": ["Step 1...", "Step 2..."],
  "category": "strength",
  "images": ["Barbell_Bench_Press/0.jpg", "Barbell_Bench_Press/1.jpg"]
}
```

**Til vår struktur:**
```sql
CREATE TABLE ovelser (
    ovelse_id SERIAL PRIMARY KEY,
    ovelse_navn VARCHAR(200) NOT NULL UNIQUE,
    ovelse_navn_no VARCHAR(200),  -- Norsk oversettelse (senere)
    force VARCHAR(20),  -- 'push', 'pull', 'static', NULL
    level VARCHAR(20),  -- 'beginner', 'intermediate', 'expert'
    mechanic VARCHAR(20),  -- 'compound', 'isolation', NULL
    category VARCHAR(50),  -- 'strength', 'stretching', 'cardio', etc.
    gif_url TEXT,  -- NULL for nå (kun statiske bilder)
    video_url TEXT,  -- NULL for nå
    instruksjoner TEXT,  -- JSON array som TEXT
    bilde_1_url TEXT,
    bilde_2_url TEXT,
    kilde_id VARCHAR(100)  -- Original ID fra free-exercise-db
);
```

**Transformasjoner:**
- `id` → `kilde_id` (bevare original ID)
- `name` → `ovelse_navn`
- `instructions` (array) → `instruksjoner` (JSON string)
- `images[0]` → `bilde_1_url`
- `images[1]` → `bilde_2_url` (hvis finnes)

---

## 4. OVELSE_MUSKLER (Junction table)

**Fra free-exercise-db:**
```json
"primaryMuscles": ["chest"],
"secondaryMuscles": ["triceps", "shoulders"]
```

**Til vår struktur:**
```sql
CREATE TABLE ovelse_muskler (
    ovelse_id INTEGER REFERENCES ovelser(ovelse_id) ON DELETE CASCADE,
    muskel_id INTEGER REFERENCES muskler(muskel_id),
    muskel_type VARCHAR(20) NOT NULL,  -- 'primar' eller 'sekundar'
    PRIMARY KEY (ovelse_id, muskel_id)
);
```

**Transformasjon:**
1. Lookup muskel_id for hver muskel i `primaryMuscles`
2. Insert rad med `muskel_type = 'primar'`
3. Lookup muskel_id for hver muskel i `secondaryMuscles`
4. Insert rad med `muskel_type = 'sekundar'`

---

## 5. OVELSE_UTSTYR (Junction table)

**Fra free-exercise-db:**
```json
"equipment": "barbell"
```

**Til vår struktur:**
```sql
CREATE TABLE ovelse_utstyr (
    ovelse_id INTEGER REFERENCES ovelser(ovelse_id) ON DELETE CASCADE,
    utstyr_id INTEGER REFERENCES utstyr(utstyr_id),
    PRIMARY KEY (ovelse_id, utstyr_id)
);
```

**Transformasjon:**
1. Lookup utstyr_id for `equipment` verdien
2. Insert rad med ovelse_id og utstyr_id

---

## 6. FELT VI IKKE BRUKER (Kan legges til senere)

**Fra free-exercise-db:**
- `tips` - Ikke i datasett (kan legges til manuelt senere)
- `vanlige_feil` - Ikke i datasett (kan legges til manuelt senere)

---

## 7. BILDE-HÅNDTERING

**Original struktur:**
```json
"images": ["Barbell_Bench_Press/0.jpg", "Barbell_Bench_Press/1.jpg"]
```

**Strategi:**
1. Last ned bilder fra GitHub repo
2. Konverter til WebP for mindre størrelse
3. Last opp til CDN (Cloudflare Images eller lignende)
4. Lagre CDN-URL i `bilde_1_url` og `bilde_2_url`

**Alternativ for MVP:**
- Bruk GitHub raw URLs direkte (ikke optimalt for produksjon):
  ```
  https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/Barbell_Bench_Press/0.jpg
  ```

---

## 8. NULL-VERDIER HÅNDTERING

**Felt som kan være NULL:**
- `force` (3.3% av øvelser)
- `mechanic` (10.0% av øvelser)
- `equipment` (8.8% av øvelser)

**Strategi:**
- Tillat NULL i database
- Vis "Ikke spesifisert" i frontend
- Prioriter manuell oppdatering av populære øvelser over tid

---

## 9. IMPORT-REKKEFØLGE

**Steg 1: Populer globale tabeller (må gjøres først)**
1. `muskler` - 17 rader
2. `utstyr` - 12 rader

**Steg 2: Populer øvelser**
3. `ovelser` - 873 rader

**Steg 3: Populer relasjoner**
4. `ovelse_muskler` - ~1500-2000 rader (estimat)
5. `ovelse_utstyr` - ~873 rader (1 per øvelse minimum)

---

## 10. SQL EKSEMPEL

**Insert muskel:**
```sql
INSERT INTO muskler (muskel_navn, muskel_navn_no, hovedkategori, underkategori)
VALUES ('Chest', 'Bryst', 'overkropp_push', 'bryst');
```

**Insert øvelse:**
```sql
INSERT INTO ovelser (
    ovelse_navn, force, level, mechanic, category,
    instruksjoner, bilde_1_url, bilde_2_url, kilde_id
)
VALUES (
    'Barbell Bench Press',
    'push',
    'intermediate',
    'compound',
    'strength',
    '["Step 1...", "Step 2..."]',
    'https://raw.githubusercontent.com/.../0.jpg',
    'https://raw.githubusercontent.com/.../1.jpg',
    'Barbell_Bench_Press'
);
```

**Insert muskel-relasjon:**
```sql
-- Primær muskel
INSERT INTO ovelse_muskler (ovelse_id, muskel_id, muskel_type)
VALUES (1, 6, 'primar');  -- 6 = Chest

-- Sekundær muskel
INSERT INTO ovelse_muskler (ovelse_id, muskel_id, muskel_type)
VALUES (1, 16, 'sekundar');  -- 16 = Triceps
```

**Insert utstyr-relasjon:**
```sql
INSERT INTO ovelse_utstyr (ovelse_id, utstyr_id)
VALUES (1, 2);  -- 2 = Barbell
```
