# Environment Variables

This document describes all environment variables used in the Treningsassistent application.

## Backend Environment Variables

The backend uses a `.env` file located at `/backend/.env`. Copy from `.env.example` to get started.

### Database Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/dbname` | Yes |

**Format:** `postgresql://[user]:[password]@[host]:[port]/[database]`

**Development:**
```
DATABASE_URL=postgresql://postgres:securepassword123@localhost:5432/treningsassistent
```

**Production:** Use a secure password and consider using environment-specific credentials.

### JWT Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Secret key for JWT token signing | `your-secret-key-here` | Yes |
| `ALGORITHM` | JWT signing algorithm | `HS256` | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes | `1440` (24 hours) | Yes |

**Development:**
```
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Production:**
- Generate a strong random secret key (use `openssl rand -hex 32`)
- Never commit the actual secret key to version control
- Consider shorter token expiration for production (e.g., 60-120 minutes)

**Generate a secure secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Application Settings

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | `Treningsassistent` | No |
| `DEBUG` | Enable debug mode | `True` or `False` | No |

**Development:**
```
APP_NAME=Treningsassistent
DEBUG=True
```

**Production:**
```
APP_NAME=Treningsassistent
DEBUG=False
```

### Complete Backend .env Example

```bash
# Database
DATABASE_URL=postgresql://postgres:securepassword123@localhost:5432/treningsassistent

# JWT Secret (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# App Settings
APP_NAME=Treningsassistent
DEBUG=True
```

## Frontend Environment Variables

The frontend uses a `.env` file located at `/frontend/.env`. All frontend environment variables must be prefixed with `VITE_` to be exposed to the application.

### API Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` | Yes |

**Development:**
```
VITE_API_URL=http://localhost:8000
```

**Production:**
```
VITE_API_URL=https://api.yourdomain.com
```

### Complete Frontend .env Example

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and update the values:
   ```bash
   nano .env  # or use your preferred editor
   ```

4. **Important:** Update the following for production:
   - `DATABASE_URL`: Use production database credentials
   - `SECRET_KEY`: Generate a strong random key
   - `DEBUG`: Set to `False`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and update `VITE_API_URL`:
   ```bash
   nano .env  # or use your preferred editor
   ```

4. For production, update `VITE_API_URL` to your deployed backend URL.

## Security Best Practices

### Backend

1. **Never commit `.env` to version control**
   - `.env` is already in `.gitignore`
   - Only commit `.env.example` with placeholder values

2. **Use strong secret keys in production**
   - Generate random keys using `openssl rand -hex 32` or `secrets.token_urlsafe(32)`
   - Minimum 32 characters recommended

3. **Secure database credentials**
   - Use strong passwords (minimum 16 characters)
   - Consider using environment-specific database users with limited permissions
   - For production, use managed database services with SSL/TLS

4. **Disable debug mode in production**
   - Set `DEBUG=False` to prevent information leakage
   - Debug mode can expose sensitive information in error messages

5. **Use environment variables from hosting provider**
   - Most hosting platforms (Heroku, Railway, DigitalOcean) provide environment variable management
   - Use their UI/CLI to set variables instead of committing `.env` files

### Frontend

1. **Never expose sensitive data in frontend env vars**
   - Frontend environment variables are bundled into the JavaScript and can be inspected
   - Only store non-sensitive configuration (API URLs, feature flags)
   - Never store API keys, secrets, or credentials in frontend env vars

2. **Use appropriate API URLs**
   - Development: `http://localhost:8000`
   - Production: `https://api.yourdomain.com` (always use HTTPS)

## Environment-Specific Configuration

### Development

```bash
# Backend
DATABASE_URL=postgresql://postgres:securepassword123@localhost:5432/treningsassistent
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True

# Frontend
VITE_API_URL=http://localhost:8000
```

### Staging

```bash
# Backend
DATABASE_URL=postgresql://staginguser:stagingpass@staging-db.example.com:5432/treningsassistent_staging
SECRET_KEY=<generated-staging-secret>
DEBUG=False

# Frontend
VITE_API_URL=https://api-staging.yourdomain.com
```

### Production

```bash
# Backend
DATABASE_URL=postgresql://produser:strongpassword@prod-db.example.com:5432/treningsassistent
SECRET_KEY=<generated-production-secret>
DEBUG=False

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

## Troubleshooting

### Backend won't start

- **Error:** `sqlalchemy.exc.OperationalError: could not connect to server`
  - **Solution:** Check that PostgreSQL is running and `DATABASE_URL` is correct
  - Verify database exists: `psql -l`
  - Test connection: `psql <DATABASE_URL>`

- **Error:** `JWT token validation failed`
  - **Solution:** Ensure `SECRET_KEY` matches between backend and any existing tokens
  - Clear localStorage in frontend if you changed the secret key

### Frontend can't connect to backend

- **Error:** `Network Error` or `ERR_CONNECTION_REFUSED`
  - **Solution:** Verify backend is running on the URL specified in `VITE_API_URL`
  - Check CORS settings in backend (`app/main.py`)
  - Ensure `VITE_API_URL` doesn't have trailing slash

- **Environment variable not updating**
  - **Solution:** Restart Vite dev server after changing `.env`
  - Run `npm run dev` again to pick up new values
  - For production builds, rebuild with `npm run build`

## Additional Notes

### Vite Environment Variables

- Vite only exposes variables prefixed with `VITE_` to the client
- Environment variables are embedded at build time
- Changes require restarting the dev server or rebuilding for production

### PostgreSQL Connection Pooling

For production, consider using connection pooling parameters:
```
DATABASE_URL=postgresql://user:pass@host:5432/db?pool_size=10&max_overflow=20
```

### Docker Environment

If using Docker, pass environment variables using:
```bash
docker run -e DATABASE_URL=postgresql://... -e SECRET_KEY=... ...
```

Or use `docker-compose.yml` with `env_file` directive.
