# Treningsassistent Frontend

React + TypeScript frontend for Treningsassistent - AI-powered workout recommendation system.

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **State Management:** React Context API
- **Styling:** Tailwind CSS
- **Visualization:** Plotly.js + React-Plotly.js
- **Forms:** React Hook Form + Zod validation
- **UI Components:** Headless UI

## Project Structure

```
src/
├── components/
│   ├── common/          # Reusable UI components (Button, Input, Card, etc.)
│   ├── layout/          # Layout components (Header, Footer, Sidebar, etc.)
│   └── features/        # Feature-specific components
├── pages/               # Page components (Login, Home, Statistics, etc.)
├── services/            # API service layer
│   ├── api.ts          # Axios client with interceptors
│   ├── authService.ts   # Authentication endpoints
│   ├── exerciseService.ts
│   ├── historyService.ts
│   ├── statisticsService.ts
│   ├── equipmentService.ts
│   ├── muscleService.ts
│   └── adminService.ts
├── context/            # React Context providers
│   └── AuthContext.tsx # Global auth state
├── hooks/              # Custom React hooks
├── types/              # TypeScript type definitions
│   └── api.ts          # API response/request types
└── utils/              # Utility functions
    └── storage.ts      # LocalStorage helpers
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:

```
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## API Services

All API communication is handled through service modules in `src/services/`:

### Authentication (`authService`)
- `login(credentials)` - Login with username/password
- `register(data)` - Register new user with invitation code
- `getCurrentUser()` - Get current user info
- `logout()` - Logout (client-side)

### Exercises (`exerciseService`)
- `getNextRecommendation()` - Get AI-powered exercise recommendation
- `getAllExercises(params)` - Get all exercises with filters
- `getExerciseById(id)` - Get exercise details
- `logExercise(data)` - Log completed exercise

### History (`historyService`)
- `getHistory(params)` - Get workout history
- `getGroupedHistory(params)` - Get history grouped by date
- `getRecentExercises(limit)` - Get recent exercises

### Statistics (`statisticsService`)
- `getHeatmap(days)` - Get muscle heatmap data
- `getAntagonisticBalance()` - Get muscle balance analysis
- `getVolumeOverTime(params)` - Get volume over time data
- `getMuscleStatistics(id, days)` - Get per-muscle statistics

### Equipment (`equipmentService`)
- `getAllEquipment()` - Get all equipment types
- `getProfiles()` - Get user's equipment profiles
- `createProfile(data)` - Create new profile
- `activateProfile(id)` - Activate profile

### Muscles (`muscleService`)
- `getAllMuscles()` - Get all muscle groups
- `getMusclePriorities()` - Get muscle priorities for user
- `getAntagonisticPairs()` - Get antagonistic muscle pairs

### Admin (`adminService`)
- `createInvitation(data)` - Create invitation code
- `getInvitations()` - List all invitations
- `getUsers()` - List all users
- `makeAdmin(id)` - Promote user to admin

## Authentication

The app uses JWT token-based authentication:

1. Login credentials are sent to `/api/auth/login`
2. Backend returns JWT access token
3. Token is stored in localStorage
4. Axios interceptor adds `Authorization: Bearer {token}` to all requests
5. On 401 error, user is redirected to login and token is cleared

### Using Auth in Components

```typescript
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return <div>Hello {user?.brukernavn}!</div>;
}
```

## Development Status

### ✅ Phase 1: Frontend Setup (COMPLETED)
- React + TypeScript + Vite setup
- All dependencies installed
- Project structure created
- API service layer with JWT interceptors
- AuthContext for global auth state

### 📝 Phase 2: Authentication (Next)
- Login page
- Register page
- Protected routes

### 📝 Phase 3: Main Functionality
- Home page with exercise recommendation
- Exercise logging form
- History page

### 📝 Phase 4: Statistics & Visualization
- Statistics page with tabs
- Muscle heatmap (Plotly.js)
- Antagonistic balance gauges
- Volume over time graphs
- Equipment profiles page

### 📝 Phase 5: Admin & Polish
- Admin panel
- Responsive design
- Loading states & error handling

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## Backend Integration

This frontend connects to the FastAPI backend at `http://localhost:8000` (configurable via `.env`).

Make sure the backend is running before starting the frontend:

```bash
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Next Steps

1. Implement authentication pages (Login, Register)
2. Create protected route wrapper
3. Build main dashboard with exercise recommendation
4. Implement exercise logging
5. Add statistics visualization with Plotly.js
6. Create admin panel
7. Add responsive design and polish

## License

MIT
