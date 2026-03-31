# Deployment Guide

Complete workflow for deploying the 2D Optimization Framework to a production server using Portainer.

## 🏗 Deployment Architecture

The framework uses a 4-container architecture for high performance and scalability:

1.  **Backend (Custom):** FastAPI application (needs build & export). Runs on port **8001** (internal 8000).
2.  **Frontend (Custom):** React application (needs build & export). Runs on port **5173** (internal 80).
3.  **Database (Official):** PostgreSQL 16 (pulled automatically).
4.  **Cache (Official):** Redis 7 (pulled automatically).

---

## 🛠 Step-by-Step Deployment

### 1. Build & Export (On Build Machine)
Run the build command providing the production server's IP and your desired Teacher PIN. These are baked into the frontend image at build-time.

```powershell
# 1. Build locally with production arguments
# Replace <SERVER_IP> with your Portainer host IP/domain
docker compose build `
  --build-arg VITE_API_URL=http://<SERVER_IP>:8001 `
  --build-arg VITE_TEACHER_PIN=9999

# 2. Save the custom images to compressed tar files
docker save framework-2d-optimization-backend:latest | gzip > backend.tar.gz
docker save framework-2d-optimization-frontend:latest | gzip > frontend.tar.gz
```

### 2. Prepare Server
Ensure the production server has internet access (to pull official Postgres/Redis images) and has Docker/Portainer installed.

### 3. Upload & Import Custom Images (Portainer)
1. In Portainer, go to **Images** → **Import**.
2. Upload `backend.tar.gz`. Wait for completion.
3. Upload `frontend.tar.gz`. Wait for completion.

### 4. Create Stack (Portainer)
1. Go to **Stacks** → **Add stack**.
2. Name it `opt2d`.
3. Build method: **Upload**.
4. Upload your `docker-compose.upload.yaml` file.

### 5. Set Environment Variables
In the **Environment variables** section of the stack creation page, you **must** add these variables:

| Variable | Recommended Value | Purpose |
|----------|-------------------|---------|
| `POSTGRES_USER` | `opt2d_admin` | Database username |
| `POSTGRES_PASSWORD` | `choose_a_password` | Database password |
| `POSTGRES_DB` | `opt2d_prod` | Database name |
| `VITE_TEACHER_PIN` | `9999` | (Backend check) Match your build PIN |
| `BACKEND_CORS_ORIGINS` | `*` | Allow frontend calls |

---

## 🧪 Post-Deployment Verification

Perform these functional tests on the server:
1. **Full Stack Check:** Verify all 4 containers (`opt2d-db`, `opt2d-redis`, `opt2d-backend`, `opt2d-frontend`) are **Healthy** or **Running**.
2. **Frontend:** Access `http://<SERVER_IP>:5173`.
3. **Teacher Login:** Can you log in to the Teacher view with your PIN?
4. **Backend Health:** Access `http://<SERVER_IP>:8001/health`.
5. **Session Creation:** Can you create a new session?
6. **Persistence:** Stop/Start the stack; is the session data still there?

---

## 🔧 Troubleshooting

### "Invalid Stack Config"
- **Error:** `depends_on source data must be an array or slice`.
- **Fix:** Ensure you are using the simplified `depends_on` list in `docker-compose.upload.yaml`.

### Port 8000 Already Allocated
- **Fix:** We use port **8001** for the backend in `docker-compose.upload.yaml` to avoid conflicts with other services. Ensure your frontend build-arg matches this.

### PIN is "CHANGE_ME"
- **Cause:** You set the PIN in Portainer but didn't rebuild the frontend image.
- **Fix:** Re-run Step 1 with the `--build-arg VITE_TEACHER_PIN=...` and re-upload the frontend image.
