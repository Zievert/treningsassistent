# API Documentation

Complete API reference for Treningsassistent backend.

**Base URL:** `http://localhost:8000` (development)

**Interactive Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

All protected endpoints require JWT token authentication.

### Headers

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

**POST** `/api/auth/login`

```json
{
  "brukernavn": "testuser",
  "passord": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Endpoints Overview

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user with invitation code | No |
| POST | `/api/auth/login` | Login and get JWT token | No |
| GET | `/api/auth/me` | Get current user info | Yes |

### Exercises (`/api/ovelser`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/ovelser/neste-anbefaling` | Get AI-powered exercise recommendation | Yes |
| GET | `/api/ovelser/alle` | Get all exercises (with filters) | Yes |
| GET | `/api/ovelser/{ovelse_id}` | Get exercise details | Yes |
| POST | `/api/ovelser/logg` | Log completed exercise | Yes |

### History (`/api/historikk`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/historikk/` | Get workout history grouped by date | Yes |
| GET | `/api/historikk/treningsokt/{dato}` | Get specific workout session | Yes |
| GET | `/api/historikk/siste` | Get recent logged exercises | Yes |

### Statistics (`/api/statistikk`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/statistikk/heatmap` | Muscle volume heatmap data | Yes |
| GET | `/api/statistikk/antagonistisk-balanse` | Antagonistic balance analysis | Yes |
| GET | `/api/statistikk/volum-over-tid` | Volume over time | Yes |
| GET | `/api/statistikk/muskel/{muskel_id}` | Detailed muscle statistics | Yes |
| GET | `/api/statistikk/dashboard` | Dashboard summary | Yes |

### Muscles (`/api/muskler`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/muskler/` | Get all muscles | Yes |
| GET | `/api/muskler/prioritet` | Get muscles with priority scores | Yes |
| GET | `/api/muskler/{muskel_id}` | Get muscle details | Yes |

### Equipment (`/api/utstyr`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/utstyr/alle` | Get all equipment types | Yes |
| GET | `/api/utstyr/profiler` | Get user's equipment profiles | Yes |
| GET | `/api/utstyr/profiler/aktiv` | Get active equipment profile | Yes |
| POST | `/api/utstyr/profiler` | Create equipment profile | Yes |
| PUT | `/api/utstyr/profiler/{profil_id}` | Update equipment profile | Yes |
| POST | `/api/utstyr/profiler/{profil_id}/aktivere` | Activate profile | Yes |
| DELETE | `/api/utstyr/profiler/{profil_id}` | Delete profile | Yes |

### Admin (`/api/admin`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/admin/invitasjoner` | Create invitation code | Admin |
| GET | `/api/admin/invitasjoner` | List all invitations | Admin |
| DELETE | `/api/admin/invitasjoner/{invitasjon_id}` | Delete invitation | Admin |
| GET | `/api/admin/brukere` | List all users | Admin |
| POST | `/api/admin/brukere/{bruker_id}/aktiver` | Activate user | Admin |
| POST | `/api/admin/brukere/{bruker_id}/deaktiver` | Deactivate user | Admin |
| POST | `/api/admin/brukere/{bruker_id}/gjor-admin` | Make user admin | Admin |
| GET | `/api/admin/stats` | System statistics | Admin |

## Detailed Endpoint Documentation

### Register User

**POST** `/api/auth/register`

Register a new user using an invitation code.

**Request Body:**
```json
{
  "brukernavn": "newuser",
  "passord": "securepassword",
  "invitasjonskode": "ABC123DEF"
}
```

**Response:** `200 OK`
```json
{
  "bruker_id": 2,
  "brukernavn": "newuser",
  "er_admin": false,
  "er_aktiv": true,
  "opprettet": "2025-11-08T10:30:00"
}
```

**Errors:**
- `400 Bad Request` - Invalid invitation code or username taken
- `422 Unprocessable Entity` - Validation error

---

### Login

**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "brukernavn": "testuser",
  "passord": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzYyNjQ0NTc1fQ.0rj_aRP9Q_EdFZyNeHwb2YqFBuQMs1zfrtjSZiYO2vM",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - User deactivated

---

### Get Exercise Recommendation

**GET** `/api/ovelser/neste-anbefaling`

Get AI-powered exercise recommendation based on muscle priority, antagonistic balance, and equipment availability.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "ovelse": {
    "ovelse_id": 123,
    "ovelse_navn": "Barbell Bench Press",
    "kategori": "strength",
    "utstyr": ["barbell", "bench"],
    "primær_muskel": "Pectoralis major",
    "sekundære_muskler": ["Triceps", "Anterior deltoid"],
    "instruksjoner": ["Step 1...", "Step 2..."],
    "bilder": ["/images/exercise-123-0.jpg", "/images/exercise-123-1.jpg"]
  },
  "prioritert_muskel": "Pectoralis major",
  "dager_siden_trent": 7.5,
  "prioritet_score": 95.4,
  "begrunnelse": "Bryst har høyest prioritet (7.5 dager siden sist trent). Antagonistisk balanse favoriserer bryst over rygg."
}
```

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - No exercises available for current equipment profile

---

### Log Exercise

**POST** `/api/ovelser/logg`

Log a completed exercise with sets, reps, and weight.

**Headers:**
```http
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "ovelse_id": 123,
  "sett": 3,
  "repetisjoner": 10,
  "vekt": 60.0
}
```

**Response:** `200 OK`
```json
{
  "utfort_id": 456,
  "ovelse_id": 123,
  "ovelse_navn": "Barbell Bench Press",
  "sett": 3,
  "repetisjoner": 10,
  "vekt": 60.0,
  "volum": 1800.0,
  "tidspunkt": "2025-11-08T14:30:00",
  "involverte_muskler": ["Pectoralis major", "Triceps", "Anterior deltoid"]
}
```

**Errors:**
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Exercise not found
- `422 Unprocessable Entity` - Invalid input (negative values, etc.)

---

### Get Workout History

**GET** `/api/historikk/`

Get workout history grouped by date.

**Headers:**
```http
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Number of dates to return (default: 30)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "treningsokter": [
    {
      "dato": "2025-11-08",
      "ovelser": [
        {
          "utfort_id": 456,
          "ovelse_navn": "Barbell Bench Press",
          "sett": 3,
          "repetisjoner": 10,
          "vekt": 60.0,
          "volum": 1800.0,
          "tidspunkt": "2025-11-08T14:30:00",
          "involverte_muskler": ["Pectoralis major", "Triceps", "Anterior deltoid"]
        }
      ],
      "total_ovelser": 1,
      "total_volum": 1800.0
    }
  ]
}
```

---

### Get Volume Over Time

**GET** `/api/statistikk/volum-over-tid`

Get total training volume over time for visualization.

**Headers:**
```http
Authorization: Bearer <token>
```

**Query Parameters:**
- `dager` (optional): Number of days to include (default: 30)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "dato": "2025-11-01",
      "total_volum": "12500.00",
      "antall_ovelser": 8
    },
    {
      "dato": "2025-11-02",
      "total_volum": "15200.00",
      "antall_ovelser": 10
    }
  ]
}
```

---

### Get Antagonistic Balance

**GET** `/api/statistikk/antagonistisk-balanse`

Get analysis of antagonistic muscle pair balance.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "par": [
    {
      "muskel_1_navn": "Pectoralis major",
      "muskel_2_navn": "Latissimus dorsi",
      "muskel_1_volum": "45000.00",
      "muskel_2_volum": "38000.00",
      "faktisk_ratio": "1.18",
      "onsket_ratio": "1.00",
      "balanse_status": "Ubalansert",
      "avvik_prosent": 18.42
    }
  ]
}
```

---

### Create Equipment Profile

**POST** `/api/utstyr/profiler`

Create a new equipment profile.

**Headers:**
```http
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "profil_navn": "Hjemme",
  "utstyr_ids": [1, 5, 8, 12]
}
```

**Response:** `200 OK`
```json
{
  "profil_id": 3,
  "profil_navn": "Hjemme",
  "er_aktiv": false,
  "utstyr": [
    {
      "utstyr_id": 1,
      "utstyr_navn": "barbell",
      "kategori": "weights"
    }
  ]
}
```

---

### Create Invitation Code (Admin Only)

**POST** `/api/admin/invitasjoner`

Create a new invitation code for user registration.

**Headers:**
```http
Authorization: Bearer <admin-token>
```

**Request Body:**
```json
{
  "maks_bruk": 1,
  "notater": "For ny bruker John"
}
```

**Response:** `200 OK`
```json
{
  "invitasjon_id": 5,
  "invitasjonskode": "ABC123DEF",
  "opprettet_av": "admin",
  "maks_bruk": 1,
  "antall_bruk": 0,
  "er_aktiv": true,
  "notater": "For ny bruker John",
  "opprettet": "2025-11-08T15:00:00"
}
```

**Errors:**
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - User is not admin

---

## Error Responses

All endpoints may return the following errors:

### 400 Bad Request
Invalid request data or business logic error.

```json
{
  "detail": "Invitasjonskode er ugyldig eller allerede brukt"
}
```

### 401 Unauthorized
Missing or invalid authentication token.

```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
User doesn't have permission to access this resource.

```json
{
  "detail": "Kun administratorer har tilgang"
}
```

### 404 Not Found
Requested resource doesn't exist.

```json
{
  "detail": "Øvelse ikke funnet"
}
```

### 422 Unprocessable Entity
Validation error in request data.

```json
{
  "detail": [
    {
      "loc": ["body", "sett"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 500 Internal Server Error
Server-side error.

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production deployment.

## CORS

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (alternative frontend port)

For production, update CORS origins in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing the API

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"brukernavn":"testuser","passord":"password123"}'

# Get recommendation (with token)
TOKEN="your-jwt-token-here"
curl -X GET http://localhost:8000/api/ovelser/neste-anbefaling \
  -H "Authorization: Bearer $TOKEN"

# Log exercise
curl -X POST http://localhost:8000/api/ovelser/logg \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ovelse_id":123,"sett":3,"repetisjoner":10,"vekt":60.0}'
```

### Using Postman

1. Import the OpenAPI spec from `http://localhost:8000/openapi.json`
2. Create an environment variable for the token
3. Add Authorization header: `Bearer {{token}}`

### Using Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"brukernavn": "testuser", "passord": "password123"}
)
token = response.json()["access_token"]

# Get recommendation
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/ovelser/neste-anbefaling",
    headers=headers
)
recommendation = response.json()
print(recommendation)
```

## WebSocket Support

Currently not implemented. Consider adding WebSocket support for real-time updates.

## API Versioning

Currently at v1 (implicit). All endpoints are under `/api/`. Future versions may use `/api/v2/` prefix.

## MCP Integration

The backend exposes an MCP (Model Context Protocol) endpoint at `/mcp` for direct server-sent events (SSE) access to the API.

**MCP URL:** `http://localhost:8000/mcp`

See `.mcp.json` in the project root for MCP configuration.
