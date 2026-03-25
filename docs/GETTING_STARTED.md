# Getting Started

## Quick Start

### Option 1: Docker (Recommended)
```powershell
# Build the project with full validation
python scripts/build.py

# Start services
docker compose up

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# API runs at http://localhost:8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

### Option 3: Python Bot (Student Template)
```powershell
cd bot
pip install requests
python student_bot_template.py
```

## What to Do Next

- **Learn the application**: See `GUIDES.md` for user guides
- **Understand the architecture**: See `ARCHITECTURE.md`
- **Deploy to server**: See `deployment_portainer.md`
- **Build & test**: See `BUILD_AND_HEALTH_CHECK.md`
