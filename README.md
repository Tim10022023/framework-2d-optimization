# Framework 2D Optimization

Interactive educational tool for **2D optimization** with instructor and participant views, comparison bots, result visualization, and Python bot template for students.

## What Is This?

Students optimize an unknown 2D function as a **black box** while instructors monitor progress, analyze solution paths, and reveal the function after the session ends.

- **Students** click points in 2D space and receive function values
- **Instructors** create sessions, monitor participants, inspect paths, and enable post-session visualizations
- **Comparison bots** (Random Search, Hill Climb) provide learning benchmarks
- **Python API** allows students to submit their own optimization algorithms locally

## Quick Start

### Docker (Recommended)
```powershell
python scripts/build.py   # Validate and build
docker compose up         # Start services
```

Services available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development
```powershell
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Python Bot (separate terminal)
cd bot
pip install requests
python student_bot_template.py
```

## Documentation

Full documentation is in [`docs/`](docs/):

| Guide | Purpose |
|-------|---------|
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Quick setup and first steps |
| [GUIDES.md](docs/GUIDES.md) | Documentation index |
| [teacher_guide.md](docs/teacher_guide.md) | How instructors use the tool |
| [participant_guide.md](docs/participant_guide.md) | How students participate |
| [student_bot_guide.md](docs/student_bot_guide.md) | How to write optimization algorithms |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical design and code structure |
| [BUILD_AND_HEALTH_CHECK.md](docs/BUILD_AND_HEALTH_CHECK.md) | Build pipeline and testing |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Implementation notes and scaling analysis |
| [deployment_portainer.md](docs/deployment_portainer.md) | Server deployment guide |

## Features

### Instructor Features
- Create sessions with configurable parameters
- Monitor live participant and bot activity
- Inspect solution paths step-by-step
- Visualize function landscapes after session ends
- Export session data for analysis
- Access via QR code or session code

### Participant Features
- Join sessions via code or QR code
- Click points on 2D space (blackbox evaluation)
- View live leaderboard and rankings
- See best solution found so far
- Download session data

### Student Bot Template
- Simple Python API for algorithm submission
- Implement your optimization algorithm in one function
- Run locally against live sessions
- Get timing and performance metrics

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + SQLite + SQLAlchemy |
| Frontend | React + TypeScript + Vite |
| Visualization | Plotly.js (2D/3D plots) |
| Bot | Python + requests |
| Deployment | Docker + Docker Compose |

## Performance & Scaling

✅ **Verified stable for:**
- 25+ concurrent UI users (classroom scenario)
- 50+ concurrent bot requests
- 200+ concurrent bots (stress test)

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed performance metrics.

## Build & Test

```powershell
python scripts/build.py        # Full CI/CD pipeline
python scripts/health_check.py # Verify services
```

See [scripts/README.md](scripts/README.md) for all available scripts.

## Project Structure

```
framework-2d-optimization/
├─ backend/           # FastAPI REST API
├─ frontend/          # React web UI
├─ bot/               # Python client & student template
├─ docs/              # Documentation & guides
├─ build.py           # Build orchestrator
├─ health_check.py    # Service verification
└─ docker-compose.yaml
```

## License & Attribution

This educational framework was created for teaching optimization concepts. Use freely in educational settings.

---

**For detailed setup and usage**, start with [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
