# Treningsassistent Backend API

AI-powered workout recommendation system with muscle balance tracking.

## Features

- **Intelligent Exercise Recommendations**: Prioritizes muscles based on training history
- **Antagonistic Balance Tracking**: Prevents muscle imbalances by monitoring opposing muscle groups
- **Volume-Based Progress**: Tracks weighted volume (sets × reps × weight) for each muscle
- **Equipment Profiles**: Filter exercises based on available equipment
- **Comprehensive Statistics**: Heatmaps, balance analysis, and progress tracking
- **Invite-Only Authentication**: Secure JWT-based authentication with invitation codes

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 14
- **ORM**: SQLAlchemy 2.0.23
- **Authentication**: JWT with bcrypt password hashing
- **Data Source**: 873 exercises from [free-exercise-db](https://github.com/yuhonas/free-exercise-db)

## Setup Instructions

### 1. Database Setup

```bash
# PostgreSQL should already be installed and running
# Database: treningsapp
# User: treningsuser
# Password: securepassword123
```

### 2. Python Environment

```bash
# Virtual environment already created
source venv/bin/activate

# Dependencies already installed from requirements.txt
```

### 3. Database Migration

```bash
# Migration already applied (13 tables created)
# To reapply: alembic upgrade head
```

### 4. Import Exercise Data

```bash
# Data already imported (873 exercises, 17 muscles, 12 equipment types)
# To reimport: python scripts/import_data.py
```

## Running the Application

### Start the Server

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Management CLI

Create admin user:
```bash
python manage.py create-admin
```

Create invitation code:
```bash
python manage.py create-invitation
```

List users:
```bash
python manage.py list-users
```

List invitations:
```bash
python manage.py list-invitations
```

## Test Accounts

Test data has been created:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Regular User:**
- Username: `testuser`
- Password: `password123`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (requires invitation code)
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (client-side)

### Exercises
- `GET /api/ovelser/neste-anbefaling` - Get next recommended exercise
- `GET /api/ovelser/alle` - Get all exercises (with filters)
- `GET /api/ovelser/{ovelse_id}` - Get exercise details
- `POST /api/ovelser/logg` - Log completed exercise

### History
- `GET /api/historikk/` - Get workout history (grouped by date)
- `GET /api/historikk/treningsokt/{dato}` - Get specific workout session
- `GET /api/historikk/siste` - Get recent logged exercises

### Statistics
- `GET /api/statistikk/heatmap` - Muscle volume heatmap data
- `GET /api/statistikk/antagonistisk-balanse` - Antagonistic balance analysis
- `GET /api/statistikk/volum-over-tid` - Volume over time
- `GET /api/statistikk/muskel/{muskel_id}` - Detailed muscle statistics
- `GET /api/statistikk/dashboard` - Dashboard summary

### Muscles
- `GET /api/muskler/` - Get all muscles
- `GET /api/muskler/prioritet` - Get muscles with priority scores
- `GET /api/muskler/{muskel_id}` - Get muscle details

### Equipment Profiles
- `GET /api/utstyr/alle` - Get all equipment types
- `GET /api/utstyr/profiler` - Get user's equipment profiles
- `GET /api/utstyr/profiler/aktiv` - Get active profile
- `POST /api/utstyr/profiler` - Create equipment profile
- `PUT /api/utstyr/profiler/{profil_id}` - Update profile
- `DELETE /api/utstyr/profiler/{profil_id}` - Delete profile
- `POST /api/utstyr/profiler/{profil_id}/aktivere` - Activate profile

### Admin (Admin-only)
- `POST /api/admin/invitasjoner` - Create invitation code
- `GET /api/admin/invitasjoner` - List all invitations
- `DELETE /api/admin/invitasjoner/{id}` - Delete invitation
- `GET /api/admin/brukere` - List all users
- `POST /api/admin/brukere/{id}/deaktiver` - Deactivate user
- `POST /api/admin/brukere/{id}/aktiver` - Activate user
- `POST /api/admin/brukere/{id}/gjor-admin` - Promote to admin
- `GET /api/admin/stats` - System statistics

## Database Schema

**Global Tables:**
- `muskler` - 17 muscle groups
- `utstyr` - 12 equipment types
- `antagonistiske_par` - 5 antagonistic muscle pairs
- `ovelser` - 873 exercises
- `ovelse_muskler` - Exercise-muscle relationships (2574 records)
- `ovelse_utstyr` - Exercise-equipment relationships (796 records)

**User Tables:**
- `brukere` - User accounts
- `invitasjoner` - Invitation codes
- `bruker_muskel_status` - Muscle training status per user
- `bruker_ovelse_historikk` - Exercise usage tracking
- `ovelser_utfort` - Logged exercises
- `bruker_utstyr_profiler` - Equipment profiles

## Core Algorithm

### Priority Calculation
```python
priority_score = days_since_last_trained
# Never trained muscles get score of 1000.0
```

### Volume Calculation
```python
volume = sets × reps × weight
# Primary muscles: 100% of volume
# Secondary muscles: 50% of volume
```

### Recommendation Algorithm
1. Calculate priority for all muscles
2. Check antagonistic balance
3. Filter exercises by equipment
4. Return exercise for highest-priority balanced muscle

## Environment Variables

`.env` file (already configured):
```
DATABASE_URL=postgresql://treningsuser:securepassword123@localhost:5432/treningsapp
SECRET_KEY=T9H-9iL7-il20ZwxuyUxSB1sbiQh93n95ws5PcQxLW0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=Treningsassistent
DEBUG=True
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── api/                 # API endpoints
│   │   ├── auth.py
│   │   ├── ovelser.py
│   │   ├── historikk.py
│   │   ├── statistikk.py
│   │   ├── utstyr.py
│   │   ├── muskler.py
│   │   └── admin.py
│   ├── services/            # Business logic
│   │   ├── ai_forslag.py    # Recommendation algorithm
│   │   └── statistikk.py    # Statistics calculations
│   └── utils/
│       └── security.py      # Auth utilities
├── alembic/                 # Database migrations
├── scripts/
│   └── import_data.py       # Data import script
├── manage.py                # CLI tool
├── test_workflow.py         # Integration test
└── requirements.txt
```

## Testing

Run the workflow test:
```bash
python test_workflow.py
```

This test verifies:
- Admin creation
- Invitation generation
- User registration
- Equipment profile setup
- Exercise recommendation
- Exercise logging
- Muscle status tracking
- Statistics calculation

## Development Status

✅ **Completed:**
- Database setup and migrations
- All 873 exercises imported
- Complete API implementation
- Authentication system
- AI recommendation algorithm
- Statistics and tracking
- Management CLI
- Workflow testing

📝 **Optional Enhancements:**
- Unit tests with pytest
- API documentation beyond Swagger
- Frontend application
- Deployment scripts

## Notes

- The bcrypt version warning can be ignored - it's a minor passlib compatibility issue that doesn't affect functionality
- All passwords are hashed with bcrypt (cost factor 12)
- JWT tokens expire after 24 hours (1440 minutes)
- Exercise images are referenced from GitHub (not stored locally)

## License

MIT
