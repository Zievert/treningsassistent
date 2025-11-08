# Treningsassistent Frontend

React + TypeScript frontend for Treningsassistent - AI-powered workout recommendation system.

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 7
- **Routing:** React Router v6
- **HTTP Client:** Axios with JWT interceptors
- **State Management:** React Context API (AuthContext, ToastContext)
- **Styling:** Tailwind CSS v3
- **Visualization:** Plotly.js (line charts, bar charts, grouped charts)
- **Forms:** React Hook Form + Zod validation
- **Animations:** CSS keyframes + Tailwind animations
- **Notifications:** Custom Toast system with auto-dismiss

## Project Structure

```
src/
├── components/
│   ├── common/             # Reusable UI components
│   │   ├── Button.tsx      # Primary button component
│   │   ├── Input.tsx       # Form input component
│   │   ├── Card.tsx        # Card container
│   │   ├── Alert.tsx       # Alert/notification box
│   │   ├── Skeleton.tsx    # Loading skeleton (pulse animation)
│   │   └── Confetti.tsx    # Celebration confetti effect
│   ├── layout/             # Layout components
│   │   ├── Navbar.tsx      # Navigation bar with hamburger menu
│   │   ├── MainLayout.tsx  # Main app layout wrapper
│   │   └── ProtectedRoute.tsx  # Route protection wrapper
│   └── features/           # Feature-specific components
│       ├── ExerciseCard.tsx         # Exercise display card
│       └── ExerciseLoggingForm.tsx  # Exercise logging form
├── pages/                  # Page components (7 total)
│   ├── LoginPage.tsx       # Login with JWT authentication
│   ├── RegisterPage.tsx    # Invite-only registration
│   ├── HomePage.tsx        # Exercise recommendation + logging
│   ├── HistoryPage.tsx     # Workout history by date
│   ├── StatisticsPage.tsx  # Plotly visualizations + PRs
│   ├── EquipmentPage.tsx   # Equipment profile CRUD
│   └── AdminPage.tsx       # Admin panel (admin-only)
├── services/               # API service layer
│   ├── api.ts             # Axios client with JWT interceptors
│   ├── authService.ts     # Authentication endpoints
│   ├── exerciseService.ts # Exercise endpoints
│   ├── historyService.ts  # History endpoints
│   ├── statisticsService.ts # Statistics endpoints
│   ├── equipmentService.ts  # Equipment endpoints
│   ├── muscleService.ts     # Muscle endpoints
│   └── adminService.ts      # Admin endpoints
├── context/               # React Context providers
│   ├── AuthContext.tsx    # Global auth state (user, login, logout)
│   └── ToastContext.tsx   # Global toast notifications
├── hooks/                 # Custom React hooks
│   └── useKeyboardShortcut.ts  # Keyboard shortcut handler
├── types/                 # TypeScript type definitions
│   └── api.ts            # API response/request types
└── utils/                 # Utility functions
    └── storage.ts        # LocalStorage helpers
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
- `getActiveProfile()` - Get active equipment profile
- `createProfile(data)` - Create new profile
- `updateProfile(id, data)` - Update profile
- `activateProfile(id)` - Activate profile
- `deleteProfile(id)` - Delete profile

### Muscles (`muscleService`)
- `getAllMuscles()` - Get all muscle groups
- `getMusclePriorities()` - Get muscle priorities for user
- `getAntagonisticPairs()` - Get antagonistic muscle pairs

### Admin (`adminService`)
- `createInvitation(data)` - Create invitation code
- `getInvitations()` - List all invitations
- `deleteInvitation(id)` - Delete invitation
- `getUsers()` - List all users
- `activateUser(id)` - Activate user
- `deactivateUser(id)` - Deactivate user
- `makeAdmin(id)` - Promote user to admin
- `getSystemStats()` - Get system statistics

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

## UI/UX Features

### Toast Notifications
- Global notification system with 4 types (success, error, warning, info)
- Auto-dismiss after 5 seconds (configurable)
- Smooth slide-in animation from right
- Multiple toasts stacked vertically
- Color-coded by type with appropriate icons

### Skeleton Loading States
- Pulse animation for loading states
- Pre-built patterns: SkeletonCard, SkeletonExerciseCard, SkeletonTable, SkeletonStatCard
- Better perceived performance than spinners
- Smooth transition when content loads

### Confetti Celebration
- Celebratory animation when exercises are logged
- 50 colorful particles with physics-based animation
- 3-second duration with fall and rotation
- Positive reinforcement for user actions

### Smooth Animations
- **Slide-in:** Elements slide from right with fade (0.3s)
- **Fade-in:** Gentle opacity transition (0.3s)
- **Scale-in:** Content scales up from 95% to 100% (0.2s)
- Applied to modals, cards, and page transitions

### Responsive Design
- Mobile-first approach with Tailwind breakpoints
- Hamburger menu on mobile devices
- Optimized for all screen sizes (mobile, tablet, desktop)
- Touch-friendly buttons and inputs

## Pages

### 1. Login Page (`/login`)
- JWT authentication with form validation
- Username and password fields
- Error handling for invalid credentials
- Link to registration page

### 2. Register Page (`/register`)
- Invite-only registration with invitation code
- Username, password, and invitation code fields
- Form validation with error messages
- Link back to login page

### 3. Home Page (`/`)
- **AI-powered exercise recommendation** with priority score
- Active equipment profile display
- Exercise logging form (sets, reps, weight)
- Confetti celebration on successful log
- Recent activity list (last 10 exercises)
- Relative timestamps ("5 min siden", "I går")

### 4. History Page (`/historikk`)
- Workout history grouped by date
- Collapsible date sections with totals
- Volume calculations (sets × reps × weight)
- Muscle tags for each exercise
- Date filtering and pagination

### 5. Statistics Page (`/statistikk`)
- **Volume over time** (Plotly line chart)
- **Most trained muscles** (Plotly horizontal bar chart)
- **Antagonistic balance** (Plotly grouped bar chart)
- Personal records section with top exercises
- Training trends and insights
- Date range filtering

### 6. Equipment Page (`/utstyr`)
- Full CRUD for equipment profiles
- Checkbox UI grouped by category (Weights, Machines, Cardio, etc.)
- "Select All" per category
- Create, edit, activate, and delete profiles
- Active profile indicator

### 7. Admin Page (`/admin`) (Admin-only)
- **System Statistics Dashboard:**
  - Total users, active users, total exercises
  - Total volume, active invitations
- **Invitation Management:**
  - Create invitation codes
  - List all invitations with usage status
  - Delete unused invitations
- **User Management:**
  - List all users with status
  - Activate/deactivate users
  - Promote users to admin

## Development Status

### ✅ Phase 1: Frontend Setup (COMPLETED)
- React 18 + TypeScript + Vite setup
- Tailwind CSS v3 configuration
- All dependencies installed
- Project structure created
- API service layer with JWT interceptors
- AuthContext for global auth state

### ✅ Phase 2: Authentication (COMPLETED)
- Login page with form validation
- Register page with invitation code
- Protected routes with automatic redirect
- JWT token storage in localStorage
- Axios interceptor for token injection

### ✅ Phase 3: Main Functionality (COMPLETED)
- Home page with AI exercise recommendation
- Exercise logging form
- History page with date grouping
- Volume calculations and muscle tracking

### ✅ Phase 4: Statistics & Visualization (COMPLETED)
- Statistics page with Plotly.js visualizations
- Volume over time line chart
- Muscle frequency horizontal bar chart
- Antagonistic balance grouped bar chart
- Personal records section
- Training trends analysis

### ✅ Phase 5: Equipment Management (COMPLETED)
- Equipment page with full CRUD
- Category-based checkbox UI
- Profile activation system
- Active profile display on home page

### ✅ Phase 6: Admin Panel (COMPLETED)
- Admin-only route protection
- System statistics dashboard
- Invitation management (create, list, delete)
- User management (activate, deactivate, make admin)

### ✅ Phase 7: UX Improvements (COMPLETED)
- Toast notification system (4 types, auto-dismiss)
- Skeleton loading components (pulse animation)
- Confetti celebration effect
- Smooth CSS animations (slide-in, fade-in, scale-in)
- Keyboard shortcut hook
- Responsive hamburger menu

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

## Features Summary

### Core Features
- 🎯 AI-powered exercise recommendations based on muscle priority and antagonistic balance
- 📊 Comprehensive statistics with Plotly.js visualizations
- 📝 Exercise logging with sets, reps, and weight tracking
- 📅 Workout history grouped by date with volume calculations
- 🏋️ Equipment profile management with category-based selection
- 👤 Invite-only user registration system
- 🔐 JWT-based authentication with automatic token refresh
- 👨‍💼 Admin panel for system management

### UX Features
- 🎉 Confetti celebration on exercise completion
- 🔔 Toast notifications for user feedback
- ⚡ Skeleton loading states for better perceived performance
- ✨ Smooth CSS animations throughout the app
- 📱 Fully responsive design (mobile, tablet, desktop)
- 🎨 Modern UI with Tailwind CSS

## License

MIT
