# Portainer Deployment Guide

Server deployment workflow for the 2D Optimization Framework.

## Overview

This guide explains how to deploy the application to a production server using **Portainer** and pre-built Docker images.

### Deployment Workflow

```
Local Machine:
  1. Build & test: python scripts/build.py
  2. Export images: docker save opt2d-backend:latest, opt2d-frontend:latest
  3. Upload tar files to server

Server (Portainer):
  4. Import tar files (Docker Images → Load)
  5. Create stack (docker-compose.upload.yaml)
  6. Set environment variables
  7. Deploy and verify
```

## Prerequisites

Before deployment, ensure you have:

- ✅ **Docker images** - `opt2d-backend-latest.tar` and `opt2d-frontend-latest.tar` (exported from build machine)
- ✅ **Server details** - Server IP or domain name
- ✅ **Network access** - Portainer accessible and logged in
- ✅ **Teacher PIN** - Secure PIN for instructor access (e.g., "2024SECRET")
- ✅ **Configuration details:**
  - `BACKEND_CORS_ORIGINS` - Frontend URL (e.g., `http://SERVER-IP:5173`)
  - `VITE_API_URL` - Backend URL for frontend (e.g., `http://SERVER-IP:8000`)
  - `VITE_PUBLIC_APP_URL` - Public app URL (e.g., `http://SERVER-IP:5173`)
  - `VITE_TEACHER_PIN` - Your chosen teacher PIN


## Step 1: Import Docker Images

1. In Portainer, navigate to **Images**
2. Click **Load image** (or **Import**)
3. Upload `opt2d-backend-latest.tar`
   - Wait for import to complete
4. Upload `opt2d-frontend-latest.tar`
   - Wait for import to complete
5. Verify both images appear in Images list:
   - `opt2d-backend:latest`
   - `opt2d-frontend:latest`

## Step 2: Create Stack in Portainer

1. Navigate to **Stacks** (left sidebar)
2. Click **+ Add stack**
3. Enter stack name: `framework-2d-optimization`
4. In **Build method** section, choose **Paste** (or **Git**)
5. Paste the contents of `docker-compose.upload.yaml` into the editor:

```yaml
services:
  backend:
    image: opt2d-backend:latest
    container_name: opt2d-backend
    ports:
      - "8001:8000"
    environment:
      DATABASE_URL: sqlite:///./data/app.db
      BACKEND_CORS_ORIGINS: ${BACKEND_CORS_ORIGINS}
    volumes:
      - opt2d_data:/app/backend/data
    restart: unless-stopped

  frontend:
    image: opt2d-frontend:latest
    container_name: opt2d-frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  opt2d_data:
```

## Step 3: Set Environment Variables

In the **Environment** section of the Portainer stack editor, set these variables:

| Variable | Value | Example |
|----------|-------|---------|
| `BACKEND_CORS_ORIGINS` | Frontend URL for CORS | `http://192.168.1.100:5173` |
| `VITE_API_URL` | Backend URL (from browser perspective) | `http://192.168.1.100:8000` |
| `VITE_PUBLIC_APP_URL` | Public app URL | `http://192.168.1.100:5173` |
| `VITE_TEACHER_PIN` | Secure teacher PIN | `MY_SECURE_PIN_2024` |

### Example Configuration (for `192.168.1.100`):

```env
BACKEND_CORS_ORIGINS=http://192.168.1.100:5173
VITE_API_URL=http://192.168.1.100:8000
VITE_PUBLIC_APP_URL=http://192.168.1.100:5173
VITE_TEACHER_PIN=MY_SECURE_PIN_2024
```

### Example Configuration (for domain):

```env
BACKEND_CORS_ORIGINS=https://app.example.com
VITE_API_URL=https://api.example.com
VITE_PUBLIC_APP_URL=https://app.example.com
VITE_TEACHER_PIN=MY_SECURE_PIN_2024
```

## Step 4: Deploy Stack

1. Verify all environment variables are set correctly
2. Scroll down and click **Deploy the stack**
3. Wait for both containers to start:
   - `opt2d-backend` (should be healthy)
   - `opt2d-frontend` (should be healthy)
4. Portainer shows deployment status - wait until both are running


## Step 5: Verify Services Are Running

In Portainer, under **Containers**, verify:
- ✅ `opt2d-backend` - Status: **Running** (green), Health: **Healthy**
- ✅ `opt2d-frontend` - Status: **Running** (green), Health: **Healthy**

If either container is not healthy:
1. Click on the container name
2. Check **Logs** tab for error messages
3. See **Troubleshooting** section below

## Step 6: Test Frontend and Backend Accessibility

In your browser, test these URLs (replace `192.168.1.100` with your server IP/domain):

| Endpoint | Purpose | Expected Result |
|----------|---------|-----------------|
| `http://192.168.1.100:5173` | Frontend | You see the 2D Optimization app |
| `http://192.168.1.100:8000/health` | Backend health | Returns `{"status":"ok"}` |
| `http://192.168.1.100:8000/docs` | API documentation | Swagger UI shows all endpoints |

## Step 7: Functional Tests (Essential)

Run these tests to verify everything works:

### 1. Teacher Creates Session
1. Open frontend at `http://SERVER-IP:5173`
2. Switch to **Teacher** view
3. Enter teacher PIN (the value you set in `VITE_TEACHER_PIN`)
4. Click **Create Session**
5. Select a function and click **Create**
6. ✅ Should see session code and QR code

### 2. Participant Joins Session
1. Open new browser tab to `http://SERVER-IP:5173`
2. Select **Participant** role
3. Enter the session code from step 6
4. Click **Join**
5. ✅ Should see the 2D plot area

### 3. Evaluate Points
1. As participant, click a point on the plot
2. ✅ Should get function value and see point marked
3. Click more points to build a path

### 4. Verify Leaderboard
1. ✅ Best points should appear in leaderboard
2. Your points should be ranked

### 5. Test Internal Bots
1. As teacher, go back to teacher session view
2. Find option to enable **Random Search** or **Hill Climb** bot
3. ✅ Bots should start evaluating points automatically

### 6. End Session and Reveal
1. As teacher, click **End Session**
2. ✅ Session should show **Ended** status
3. Click **Reveal** or **Show Result**
4. ✅ Should see function contour plot with optimal point marked

### 7. Export Session Data
1. Find **Export** button in ended session
2. Click to download JSON
3. ✅ File should contain all evaluations and metadata

## Step 8: Verify Data Persistence

1. In Portainer, find the stack
2. Click **Stop** to stop all containers
3. Wait 10 seconds
4. Click **Start** to restart containers
5. Open frontend and access the same session code
6. ✅ Previous data should still be visible (database persisted)


## Step 9: Troubleshooting

### Frontend Loads But Backend Not Responding

**Symptoms:**
- Frontend page loads but you see "API error" messages
- Network tab shows failing requests to backend

**Check:**
1. Verify `VITE_API_URL` is correct (matches your server IP/domain)
2. In Portainer, click **backend** container → **Logs**
3. Look for error messages
4. Test endpoint directly: `curl http://SERVER-IP:8000/health`

**Solutions:**
- If `VITE_API_URL` was wrong, re-deploy stack with correct value
- If backend container crashed, restart it from Portainer
- Check firewall allows traffic on port 8000

### CORS Errors in Browser Console

**Symptoms:**
- Browser console shows: `"Access to XMLHttpRequest has been blocked by CORS policy"`

**Cause:**
- `BACKEND_CORS_ORIGINS` environment variable is incorrect

**Fix:**
1. In Portainer, go to **Stacks** → `framework-2d-optimization`
2. Click **Editor** (or update stack)
3. Verify `BACKEND_CORS_ORIGINS` matches your frontend URL exactly
4. Re-deploy stack

### Session Creation Fails (Teacher PIN Not Working)

**Symptoms:**
- Teacher view won't accept PIN or won't create session

**Cause:**
- Frontend built with wrong `VITE_TEACHER_PIN` environment variable

**Fix:**
1. Verify tar files were built with correct PIN
2. In Portainer, re-deploy with correct `VITE_TEACHER_PIN`
3. Note: Frontend tar must be rebuilt to reflect PIN change (requires re-export from build machine)

### Database Lost After Restart

**Symptoms:**
- Sessions disappear after stopping/restarting stack

**Cause:**
- Docker volume `opt2d_data` not mounted correctly

**Check:**
1. In Portainer, go to **Stacks** → `framework-2d-optimization`
2. Check that volume is listed in volumes section
3. Run: `docker volume ls | grep opt2d` (should show `opt2d_data`)

### Containers Won't Start

**Symptoms:**
- Containers stuck in **Exited** state or constantly restarting

**Check:**
1. Click container → **Logs** tab in Portainer
2. Look for error messages
3. Common issues:
   - Port 8000 or 5173 already in use on server (change in docker-compose.upload.yaml)
   - Volume mount permission issue
   - Environment variables missing or malformed

### Internal Bots (Random Search, Hill Climb) Not Starting

**Symptoms:**
- You can manually evaluate points but bots don't start

**Cause:**
- Backend issue or permissions problem

**Check:**
1. In Portainer, backend container → **Logs** tab
2. Look for bot-related errors
3. Re-start backend container

### Very Slow Performance

**Symptoms:**
- Page takes long to load, point evaluation is slow

**Causes:**
- Server resources low
- Network latency high

**Solutions:**
- Check Portainer dashboard for CPU/memory usage
- If <10 concurrent users, should be smooth
- If >50 concurrent users, consider scaling backend (see DEVELOPMENT.md)


## Step 10: Updates and Future Deployments

When deploying a new version:

1. **On build machine:**
   ```powershell
   git pull  # Get latest code
   python scripts/build.py  # Full build + test
   docker save -o opt2d-backend-latest.tar opt2d-backend:latest
   docker save -o opt2d-frontend-latest.tar opt2d-frontend:latest
   ```

2. **On server (Portainer):**
   - Delete old images (Docker Images → delete `opt2d-backend:latest` and `opt2d-frontend:latest`)
   - Import new tar files (step 1 above)
   - Stop current stack
   - Re-deploy stack (new images will be used)
   - Run functional tests again

## Summary: Deployment Success Criteria

✅ **Deployment is successful when:**

- [ ] Both containers running and healthy in Portainer
- [ ] Frontend accessible at `http://SERVER-IP:5173`
- [ ] Backend health check returns `{"status":"ok"}`
- [ ] Teacher can create session with correct PIN
- [ ] Participant can join session
- [ ] Point evaluation works
- [ ] Leaderboard updates
- [ ] Internal bots work (Random Search, Hill Climb)
- [ ] Session can be ended and revealed
- [ ] Session data persists after restart

**Next:** Monitor application in production using Portainer. Check logs regularly for errors.
