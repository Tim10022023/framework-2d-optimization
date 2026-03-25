# Scripts Directory

This folder contains utility scripts for building, testing, and validating the project.

## Quick Reference

| Script | Purpose | When to Use |
|--------|---------|------------|
| `build.py` | Full CI/CD pipeline | Before Docker build or deployment |
| `health_check.py` | Service verification | After starting Docker Compose |
| `full_health_check.py` | Integration test | Complete validation workflow |
| `verify_workspace.py` | Workspace check | After cloning or setup |

## Usage

### Option 1: Run from root directory
```powershell
python scripts/build.py
python scripts/health_check.py
```

### Option 2: Run from scripts directory
```powershell
cd scripts
python build.py
python health_check.py
```

## What Each Script Does

### `build.py`
Comprehensive build pipeline:
1. Backend: pip install → pytest
2. Frontend: npm install → npm lint → tsc --noEmit → npm build
3. Docker: Build images for backend and frontend

**Use when**: Preparing for deployment or before Docker builds

### `health_check.py`
Quick health verification:
- Checks if backend API is responding
- Checks if frontend is accessible
- Verifies Docker containers are healthy

**Use when**: Services are already running, want to verify they work

### `full_health_check.py`
Complete integration test:
1. Starts Docker Compose
2. Waits for services to be healthy
3. Runs health checks
4. Reports overall status

**Use when**: Need complete validation from scratch

### `verify_workspace.py`
Checks project setup:
- Verifies directory structure
- Checks required files exist
- Validates configuration

**Use when**: First clone, setup verification

## Integration with CI/CD

These scripts are designed to work in automated CI/CD pipelines:

```bash
# Development
python scripts/build.py
docker compose up

# Testing
python scripts/health_check.py

# Full integration test
python scripts/full_health_check.py
```

## Environment

Scripts work on:
- ✅ Windows (PowerShell)
- ✅ macOS (bash/zsh)
- ✅ Linux (bash/sh)

Emoji output automatically disabled on Windows for compatibility.

## Troubleshooting

**ImportError when running scripts?**
- Ensure you have Python 3.9+ installed
- Run from project root: `python scripts/build.py`

**Docker not found?**
- Install Docker Desktop or Docker CLI
- Scripts will report which dependency is missing

**Port conflicts?**
- Backend uses 8000, Frontend uses 5173
- Check if ports are already in use: `netstat -an`
