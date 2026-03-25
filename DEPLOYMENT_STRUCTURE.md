# Deployment Structure Guide

This document explains the **refactored deployment architecture** separating build artifacts from deployment configuration.

## Problem Statement

Previously, a single `docker-compose.yaml` was used for both:
- **Local development** (building images from source)
- **Server deployment** (running pre-built images)

This created friction for the deployment workflow:
1. Developer builds images locally
2. Developer exports images as tar files
3. Server needs to import images into Docker
4. But the compose file expected build context (source code)

## Solution: Deployment Separation

### Two Compose Files

#### 1. `docker-compose.yaml` - Local Development
**Purpose:** Building images from source for local development/testing

```yaml
services:
  backend:
    build:                    # ← Builds from source
      context: .
      dockerfile: Dockerfile
    # ... other config
    
  frontend:
    build:                    # ← Builds from source
      context: ./frontend
      dockerfile: Dockerfile
      args:                   # ← Build arguments
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
        VITE_TEACHER_PIN: ${VITE_TEACHER_PIN:-CHANGE_ME}
    # ... other config
```

**Used by:** Developer (running `docker compose build` and `docker compose up`)

**Workflow:**
```powershell
python scripts/build.py          # Runs tests, then: docker compose build
docker compose up                # Start services locally
```

#### 2. `docker-compose.upload.yaml` - Server Deployment
**Purpose:** Running pre-built images (no build context needed)

```yaml
services:
  backend:
    image: opt2d-backend:latest   # ← Pre-built image (tar → import)
    # ... environment vars only
    
  frontend:
    image: opt2d-frontend:latest  # ← Pre-built image (tar → import)
    # ... environment vars only
```

**Used by:** Server Administrator (via Portainer or CLI)

**Workflow:**
```
1. Developer: docker save -o opt2d-backend-latest.tar opt2d-backend:latest
2. Admin: Upload tar to server
3. Admin: docker load -i opt2d-backend-latest.tar (or import via Portainer)
4. Admin: docker-compose -f docker-compose.upload.yaml up
```

## File Organization

```
framework-2d-optimization/
│
├─ docker-compose.yaml               # ← Local dev (builds from source)
├─ docker-compose.upload.yaml        # ← Server prod (pre-built images)
│
├─ Dockerfile                         # Backend image build
├─ frontend/Dockerfile               # Frontend image build
│
├─ backend/
│  └─ requirements.txt               # Python dependencies
│
├─ frontend/
│  ├─ package.json
│  └─ package-lock.json              # Node dependencies
│
├─ scripts/
│  ├─ build.py                       # Local build orchestrator
│  ├─ health_check.py                # Service verification
│  └─ full_health_check.py           # Extended verification
│
└─ docs/
   ├─ deployment_portainer.md        # ← Updated with tar workflow
   ├─ BUILD_AND_HEALTH_CHECK.md
   ├─ ARCHITECTURE.md
   └─ updates/
      ├─ 2026-03-25_deployment_refactor.md  # ← This refactor
      └─ ... (other session logs)
```

## Build vs Deployment Configuration

### Build Configuration (docker-compose.yaml)

```yaml
build:
  args:
    VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    VITE_PUBLIC_APP_URL: ${VITE_PUBLIC_APP_URL:-http://localhost:5173}
    VITE_TEACHER_PIN: ${VITE_TEACHER_PIN:-CHANGE_ME}
```

**When:** Compiled into image at build time (locked into tar file)
**Can Change After Deployment:** NO (would need new image)

### Deployment Configuration (docker-compose.upload.yaml)

```yaml
environment:
  BACKEND_CORS_ORIGINS: ${BACKEND_CORS_ORIGINS}
  VITE_API_URL: http://server:8000
  # (etc)
```

**When:** Applied at runtime (containers can restart with different values)
**Can Change After Deployment:** YES (just redeploy compose)

## Typical Workflows

### Scenario 1: Local Development

**Goal:** Build and test locally

```powershell
# Build everything
cd framework-2d-optimization
python scripts/build.py        # Tests + builds images

# Start locally
docker compose up              # Uses docker-compose.yaml

# Access at http://localhost:5173
```

### Scenario 2: Export to Server (Tar Files)

**Goal:** Get images ready for server deployment

```powershell
# Build and export
python scripts/build.py                                    # Build
docker save -o opt2d-backend-latest.tar opt2d-backend:latest
docker save -o opt2d-frontend-latest.tar opt2d-frontend:latest

# Upload tar files to server
# (Manual step or SCP)
```

### Scenario 3: Deploy on Server (Portainer)

**Goal:** Run pre-built images on server

```
Portainer UI:
  1. Images → Load → upload tar files
  2. Stacks → Add Stack
  3. Paste docker-compose.upload.yaml
  4. Set environment variables:
     - BACKEND_CORS_ORIGINS=http://SERVER-IP:5173
     - VITE_API_URL=http://SERVER-IP:8000
     - VITE_TEACHER_PIN=SECURE_PIN
  5. Deploy
```

### Scenario 4: Update Server Deployment

**Goal:** Deploy new version of code

```powershell
# On build machine
git pull
python scripts/build.py
docker save -o opt2d-backend-latest.tar opt2d-backend:latest
docker save -o opt2d-frontend-latest.tar opt2d-frontend:latest
# Upload tar files

# On server (Portainer)
# 1. Stop stack
# 2. Delete old images
# 3. Load new tar files
# 4. Restart stack (uses new images)
```

## Why This Structure?

### Advantages

1. **Clear Separation:** Build logic separate from deployment
2. **Security:** Source code never goes to production server
3. **Efficiency:** Images built once, deployed multiple times
4. **Flexibility:** Can deploy same images to multiple servers
5. **Automation:** Deployments don't require rebuilding
6. **Scaling:** Add more servers without rebuilding

### Key Principles

- **Build machine** has source code, builds images
- **Server machine** only needs images (tar files), no source code
- **Build config** (ARGs) locked into tar files at build time
- **Deploy config** (ENV) flexible, can change without rebuild
- **Volumes** persist data across container restarts

## Environment Variable Mapping

### Build-Time (Frontend Only)

| Variable | Scope | When Set | File |
|----------|-------|----------|------|
| `VITE_API_URL` | Frontend | Build (docker-compose.yaml) | Locked in image |
| `VITE_PUBLIC_APP_URL` | Frontend | Build (docker-compose.yaml) | Locked in image |
| `VITE_TEACHER_PIN` | Frontend | Build (docker-compose.yaml) | Locked in image |

### Runtime (Both)

| Variable | Scope | When Set | File |
|----------|-------|----------|------|
| `BACKEND_CORS_ORIGINS` | Backend | Deployment (docker-compose.upload.yaml) | Environment |
| `DATABASE_URL` | Backend | Deployment (docker-compose.upload.yaml) | Environment |

### Why This Split?

- **Frontend is static:** Must know API URL at build time (compiled into HTML/JS)
- **Backend is dynamic:** Can be configured at runtime without rebuilding

## Checklist: Before First Server Deployment

- [ ] Both compose files exist: `docker-compose.yaml` and `docker-compose.upload.yaml`
- [ ] Dockerfile and frontend/Dockerfile build correctly
- [ ] `python scripts/build.py` passes all tests
- [ ] Images exported to tar: `opt2d-backend-latest.tar`, `opt2d-frontend-latest.tar`
- [ ] Deployment guide updated: `docs/deployment_portainer.md`
- [ ] Environment variables documented in deployment guide
- [ ] Troubleshooting section covers common issues
- [ ] Local `docker compose up` works without errors
- [ ] Services healthy check passes
- [ ] README.md references deployment guide

## Checklist: Before Each Server Update

- [ ] Code changes merged to main branch
- [ ] All tests passing (`python scripts/build.py`)
- [ ] Images re-built and exported
- [ ] Update log created in `docs/updates/`
- [ ] Deployment guide updated if env vars changed
- [ ] New tar files ready to upload to server

## References

- See `docs/deployment_portainer.md` for step-by-step server deployment
- See `docs/BUILD_AND_HEALTH_CHECK.md` for build pipeline details
- See `docs/ARCHITECTURE.md` for technical architecture
