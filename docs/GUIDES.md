# Documentation Index

## Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick setup for Docker, local development, or Python bot

## User Guides
- **[teacher_guide.md](teacher_guide.md)** - How teachers create sessions, monitor progress, and analyze results
- **[participant_guide.md](participant_guide.md)** - How students join and participate in optimization sessions
- **[student_bot_guide.md](student_bot_guide.md)** - How to write your own optimization algorithm using the Python bot template

## Development & Deployment
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Project structure, API design, component overview
- **[BUILD_AND_HEALTH_CHECK.md](BUILD_AND_HEALTH_CHECK.md)** - Build pipeline, health checks, testing
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Technical notes, scaling analysis, implementation details
- **[deployment_portainer.md](deployment_portainer.md)** - How to deploy on a server using Portainer

## Performance & Scaling
- See **DEVELOPMENT.md** → "Stresstest / Skalierbarkeit" for performance metrics
- Current system stable for:
  - ✅ 25+ concurrent UI users (classroom size)
  - ✅ 200+ concurrent bot requests (stress test)
  - ⚠️ 50+ UI users with acceptable slowdown
