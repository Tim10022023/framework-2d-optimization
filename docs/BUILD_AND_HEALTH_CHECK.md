# Build & Health Check Guide

This project includes automated build validation and health checks to ensure consistency and reliability.

## Quick Reference

| Task | Command |
|------|---------|
| Full build validation | `python scripts/build.py` |
| Check service health | `python scripts/health_check.py` |
| Complete integration test | `python scripts/full_health_check.py` |
| Verify workspace setup | `python scripts/verify_workspace.py` |

## Build Pipeline

### Full Build (`scripts/build.py`)

Comprehensive validation before Docker deployment:

```powershell
python scripts/build.py
```

**What it does:**
1. **Backend validation**
   - Install pip dependencies
   - Run pytest test suite
2. **Frontend validation**
   - Install npm dependencies
   - Run ESLint (style check)
   - Run TypeScript compiler (type check)
   - Run npm build (production build)
3. **Docker build**
   - Build backend image
   - Build frontend image

**When to use:**
- Before pushing to production
- Before creating Docker images
- As part of CI/CD pipeline
- Fails fast on any error (nothing gets committed/built if tests fail)

### Backend Validation

```powershell
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Tests include:
- API endpoints functionality
- Health check endpoint
- Session management
- Function evaluation

### Frontend Validation

```powershell
cd frontend
npm install
npm run lint                # ESLint
npx tsc --noEmit          # TypeScript check
npm run build              # Production build
```

Catches:
- TypeScript type errors
- Style violations (ESLint)
- Build errors

## Health Checks

### Quick Health Check (`scripts/health_check.py`)

Verify running services:

```powershell
docker compose up
python scripts/health_check.py
```

**What it checks:**
- Backend API responds at http://localhost:8000
- Frontend accessible at http://localhost:5173
- Health endpoint returns 200 status

**Output:**
```
✅ Backend API is healthy
✅ Frontend is healthy
✅ All services are running
```

### Full Integration Test (`scripts/full_health_check.py`)

Complete validation from scratch:

```powershell
python scripts/full_health_check.py
```

**What it does:**
1. Starts Docker Compose
2. Waits for services to be ready (30s timeout)
3. Verifies both backend and frontend
4. Checks health endpoints
5. Reports overall system health

**Use when:** Need complete validation including Docker startup

## Deployment Workflow

### 1. Validate Code
```powershell
python scripts/build.py
```

If all checks pass ✅, proceed. If any fail ❌, fix errors first.

### 2. Start Services
```powershell
docker compose up
```

### 3. Verify Health
```powershell
python scripts/health_check.py
```

All three checks should show ✅.

### 4. Export Images (Production)
```powershell
docker image save opt2d-backend:latest -o backend.tar
docker image save opt2d-frontend:latest -o frontend.tar
```

### 5. Deploy
Copy tar files to server and load:
```bash
docker image load -i backend.tar
docker image load -i frontend.tar
docker compose -f docker-compose.upload.yaml up
```

## What Gets Checked

### Build Time Checks
- Python syntax and imports
- npm package integrity
- TypeScript type safety
- ESLint style rules
- All pytest tests pass
- Docker image builds successfully

### Runtime Checks (Every 10s)
- Backend `/health` endpoint responds
- Frontend serves HTTP 200
- Containers don't exit unexpectedly

### Manual Checks (On Demand)
- Services respond to requests
- API endpoints return correct data
- Database is persisted
- Frontend can connect to backend

## Environment

Scripts handle:
- ✅ Windows (PowerShell)
- ✅ macOS (bash/zsh)
- ✅ Linux (bash/sh)

Windows users: Emoji output automatically disabled for terminal compatibility.

## Troubleshooting

### "pytest not found"
```powershell
cd backend
python -m pytest tests/ -v
```

### Docker not running
```powershell
# Start Docker Desktop (Windows/macOS)
# Or start Docker daemon (Linux)
docker ps  # Verify it works
```

### Port already in use
Backend: 8000, Frontend: 5173
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill process if needed
Stop-Process -Id <PID>
```

### Services won't start
1. Check disk space: `docker system df`
2. Clean old images: `docker system prune`
3. Rebuild: `docker compose up --build`

## CI/CD Integration

These scripts are designed for automated pipelines:

### GitHub Actions Example
```yaml
- name: Validate Build
  run: python scripts/build.py

- name: Start Services
  run: docker compose up -d

- name: Health Check
  run: python scripts/health_check.py
```

### GitLab CI Example
```yaml
build:
  script:
    - python scripts/build.py
    - docker compose up -d
    - python scripts/health_check.py
```

## See Also

- [scripts/README.md](../scripts/README.md) - Script usage guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Project structure
- [DEVELOPMENT.md](DEVELOPMENT.md) - Technical details
