# Deployment Guide

Complete workflow for deploying the 2D Optimization Framework to a production server.

## 🏗 Deployment Architecture

The framework uses a 4-container architecture for high performance and scalability:

1.  **Backend (Custom):** FastAPI application (needs build & export).
2.  **Frontend (Custom):** React application (needs build & export).
3.  **Database (Official):** PostgreSQL 17 (pulled automatically by server).
4.  **Cache (Official):** Redis 7 (pulled automatically by server).

---

## 🛠 Step-by-Step Deployment

### 1. Build & Export (On Build Machine)
Run the full build pipeline and export the custom images:
```powershell
python scripts/build.py
docker save -o opt2d-backend-latest.tar opt2d-backend:latest
docker save -o opt2d-frontend-latest.tar opt2d-frontend:latest
```

### 2. Prepare Server
Ensure the production server has internet access (to pull official Postgres/Redis images) and has Docker/Portainer installed.

### 3. Upload & Import Custom Images (Portainer)
1. Upload the two `.tar` files to the server.
2. In Portainer, go to **Images** → **Load image**.
3. Import both `opt2d-backend-latest.tar` and `opt2d-frontend-latest.tar`.

### 4. Create Stack (Portainer)
1. Go to **Stacks** → **+ Add stack**.
2. Name it `opt2d`.
3. Paste the contents of `docker-compose.upload.yaml` into the editor.
4. Portainer will automatically pull `postgres:17-alpine` and `redis:7-alpine`.

### 5. Set Environment Variables
In the **Environment** section, set these variables:

| Variable | Scope | Purpose | Example |
|----------|-------|---------|---------|
| `BACKEND_CORS_ORIGINS` | Backend | Allow frontend calls | `http://SERVER-IP:5173` |
| `VITE_API_URL` | Frontend | API endpoint for UI | `http://SERVER-IP:8000` |
| `VITE_PUBLIC_APP_URL` | Frontend | Public app URL | `http://SERVER-IP:5173` |
| `VITE_TEACHER_PIN` | Frontend | Teacher access PIN | `MY_SECURE_PIN` |

---

## 🧪 Post-Deployment Verification

Perform these functional tests on the server:
1. **Full Stack Check:** Verify all 4 containers (`db`, `redis`, `backend`, `frontend`) are **Healthy** in Portainer.
2. **Teacher Login:** Can you log in to the Teacher view with your PIN?
3. **Session Creation:** Can you create a new session?
4. **Participant Join:** Can a student join via the session code?
5. **Evaluation:** Does clicking a point return a Z value?
6. **Leaderboard:** Does the leaderboard update in real-time?
7. **Bots:** Can you start an internal bot from the Teacher panel?
8. **Persistence:** Stop/Start the stack; is the session data still there?

---

## 🔧 Troubleshooting

### Database/Redis Connection
- **Symptoms:** Backend logs show "Connection refused" to `db` or `redis`.
- **Check:** Ensure all 4 containers are in the same Docker network (Portainer stack handles this automatically). Check health status of `db` and `redis`.

### API Connection Issues
- **Symptoms:** Frontend loads but shows "API Error".
- **Check:** Is `VITE_API_URL` correct? Does `http://SERVER-IP:8000/health` respond?
- **CORS:** Ensure `BACKEND_CORS_ORIGINS` matches the frontend URL exactly.

### Data Loss
- **Symptoms:** Sessions disappear after restart.
- **Check:** Ensure the Docker volume `opt2d_db_data` is correctly defined and mounted in `docker-compose.upload.yaml`.
