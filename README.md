# 2D Optimization Framework

Interactive educational platform for teaching 2D optimization concepts through a "black box" game.

## 📋 Documentation Index

### 🚀 Getting Started & Development
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Setup, local development, build pipeline, and technical reference.
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical design, scaling, and system components.

### 🌐 Deployment
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Step-by-step guide for production deployment via Portainer.
- **[DISTRIBUTION.md](docs/DISTRIBUTION.md)** - Guide for instructors on what to provide to participants and bots.

### 📖 User Guides
- **[Teacher Guide](docs/teacher_guide.md)** - Managing sessions and monitoring progress.
- **[Participant Guide](docs/participant_guide.md)** - Using the manual click interface.
- **[Student Bot Guide](docs/student_bot_guide.md)** - Developing optimization algorithms.

---

## 🏗 High-Level Tech Stack
- **Backend:** FastAPI, PostgreSQL, Redis.
- **Frontend:** React, Vite, Plotly.js.
- **Real-time:** WebSockets with Redis Pub/Sub.
- **Orchestration:** Docker & Docker Compose.

## 🤖 Bot Support
The framework supports automated optimization bots. Students can use the provided Python client library to evaluate functions locally and sync their progress with the server.
- Library: `bot/blackbox_client.py`
- Template: `bot/student_bot_template.py`
