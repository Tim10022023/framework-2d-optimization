# 2026-03-25: Deployment Structure Refactoring

## Summary

Refactored deployment workflow to separate **build artifacts** from **deployment configuration**, improving clarity and maintainability for server deployments via Portainer.

## Changes Made

### 1. Deployment Separation (`docker-compose.upload.yaml`)

**Before:** Single `docker-compose.yaml` used for both local development and server deployment.

**After:** Two distinct files:
- `docker-compose.yaml` - Local development (builds from source)
- `docker-compose.upload.yaml` - Server deployment (uses pre-built images)

**Why:** Allows building images locally, exporting as tar files, and importing them on the server without needing source code or npm/pip on the server.

### 2. Enhanced Deployment Guide

Updated `docs/deployment_portainer.md` with:
- **Workflow overview** - explains tar file import process
- **Prerequisites checklist** - what you need before deployment
- **Step-by-step instructions** - from tar import to verification
- **Environment variable reference** - all required vars documented
- **Troubleshooting section** - common deployment issues and solutions
- **Verification checklist** - complete functional tests to run post-deployment

### 3. Build & Deployment Workflow

**Local (Developer Machine):**
```powershell
# Run once to build and test everything
python scripts/build.py

# Export images as tar files
docker save -o opt2d-backend-latest.tar opt2d-backend:latest
docker save -o opt2d-frontend-latest.tar opt2d-frontend:latest
```

**Server (via Portainer):**
1. Import tar files via Docker Images → Load
2. Create stack using `docker-compose.upload.yaml`
3. Set environment variables (BACKEND_CORS_ORIGINS, VITE_API_URL, VITE_PUBLIC_APP_URL, VITE_TEACHER_PIN)
4. Deploy and verify with functional tests

### 4. Configuration Clarity

- **Build arguments**: Clearly separated in `docker-compose.yaml` for local builds
- **Runtime environment**: Clearly documented in `docker-compose.upload.yaml` for server
- **Volume persistence**: Documented that `opt2d_data` volume persists database across restarts

## File Structure

```
framework-2d-optimization/
├─ docker-compose.yaml              # Local dev (builds from source)
├─ docker-compose.upload.yaml       # Server deployment (pre-built images)
├─ scripts/build.py                 # Full build pipeline
├─ docs/deployment_portainer.md     # Enhanced deployment guide
└─ docs/updates/                    # Session update logs
```

## Deployment Checklist

Before uploading tar files to server, verify:
- [ ] Run `python scripts/build.py` - all tests pass
- [ ] Backend tests: 7/7 passing
- [ ] Frontend linting & type-check: no errors
- [ ] Docker images built: `opt2d-backend:latest` and `opt2d-frontend:latest`
- [ ] `docker compose up` runs locally without errors
- [ ] Both services healthy (health checks passing)
- [ ] Export tar files and verify file sizes match expected (backend ~180MB, frontend ~65MB)

## Server Deployment Checklist

Once tar files are on server:
- [ ] Load images in Portainer
- [ ] Create stack from `docker-compose.upload.yaml`
- [ ] Set environment variables
- [ ] Deploy stack
- [ ] Verify services healthy in Portainer UI
- [ ] Test frontend accessibility
- [ ] Test backend health endpoint
- [ ] Run functional tests (session create, join, evaluate, reveal, export)
- [ ] Verify database persistence (restart and check data still exists)

## Next Steps

1. User verifies everything works locally
2. Run final `python scripts/build.py && docker save` commands
3. Upload tar files to server
4. Follow "Server Deployment Checklist" above

## Notes

- Deployment guide now includes essential troubleshooting
- `docker-compose.upload.yaml` is production-ready and requires no build context
- Environment variables are all configurable for different server configurations (IP, domain, etc.)
- Volume persistence tested and working correctly
