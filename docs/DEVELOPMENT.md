# Development Notes & Technical Decisions

This document tracks implementation details, scaling analysis, and technical decisions made during development.

## Project Status

The framework is **functionally complete** for educational classroom use:

- ✅ FastAPI backend with SQLite persistence
- ✅ Full session lifecycle (create, join, evaluate, end, export)
- ✅ Leaderboard with real-time updates
- ✅ Step-by-step path inspection with snapshots
- ✅ Teacher and participant interfaces
- ✅ QR code / session code access
- ✅ Internal comparison bots (Random Search, Hill Climb)
- ✅ Python student bot template (blackbox_client.py)
- ✅ Full-stack Docker containerization
- ✅ Reveal with function visualization
- ✅ Session export (JSON)

## Database

- **SQLite** + SQLAlchemy ORM
- Database file: `backend/app.db`
- Persisted via Docker volume
- Tables: sessions, participants, evaluations, snapshots
- No migrations tool (manual schema via models)

## API Endpoints

Core endpoints:
- `GET /health` - Health check
- `GET /functions` - List available optimization functions
- `POST /sessions` - Create new session
- `GET /sessions/{code}` - Get session details
- `GET /sessions/{code}/public` - Public session info (for bots)
- `POST /sessions/{code}/join` - Join session as participant
- `POST /sessions/{code}/evaluate` - Submit point evaluation
- `GET /sessions/{code}/leaderboard` - Get rankings
- `GET /sessions/{code}/snapshot` - Get step-by-step path
- `POST /sessions/{code}/end` - End session (admin)
- `GET /sessions/{code}/export` - Export full session (admin)

Bot endpoints:
- `POST /sessions/{code}/bots/random_search` - Start random search bot
- `POST /sessions/{code}/bots/hill_climb` - Start hill climb bot

## Available Optimization Functions

1. **Sphere** (shifted) - Unimodal, smooth
2. **Booth** - Multi-modal, bounded
3. **Himmelblau** - Multi-modal (4 local minima)
4. **Rosenbrock** - Valley-shaped, difficult
5. **Eggholder** - Highly multi-modal, irregular
6. **Rastrigin** (shifted) - Multi-modal with many local optima
7. **Schwefel** - Deceptive, highly multi-modal
8. **Levy** - Multi-modal with narrow valleys
9. **Griewank** (negated/shifted) - Maximization variant
10. **Easom** - Highly multi-modal, single global minimum

Reveal images stored in `backend/app/static/function_images/`

## Python Bot System

### Components

- **`bot/blackbox_client.py`** - HTTP client library for API access
- **`bot/student_bot_template.py`** - Template for students to implement algorithms
- **`bot/stress_test.py`** - Utility for load testing

### Student Workflow

Students edit `student_bot_template.py`:
```python
def propose_point(step, history, best_z):
    # Implement your optimization algorithm
    # Input: current step, history of previous (x,y,z), best z seen
    # Output: (x, y) for next evaluation
    return x, y
```

Then run:
```powershell
pip install requests
python student_bot_template.py
```

## Stress Testing & Scaling Analysis

### Historical Results (Old Test)

From original `bot/stress_test.py`:
- 5 bots, 10 steps: ✅ Stable
- 10 bots, 20 steps: ✅ Good
- 20 bots, 20 steps: ⚠️ Slower but works
- 50 bots, 20 steps: ❌ Timeouts / limit reached

**Old conclusion**: "50 aggressive parallel bots exceed robust limits"

### Current Test Results (March 2026)

**Bot Template Stress Tests** (concurrent bots making rapid requests):
- 20 bots: ✅ 400 evaluations, 0 errors, 2.89s, 138 steps/sec
- 50 bots: ✅ 1000 evaluations, 0 errors, 7.02s, 142 steps/sec
- 100 bots: ✅ 2000 evaluations, 0 errors, 15.09s, 132 steps/sec
- 200 bots: ✅ 4000 evaluations, 0 errors, 30.84s, 129 steps/sec

**Key Finding**: System is far more capable than old estimate. All tests showed:
- 0% error rate
- 100% join success
- 100% completion rate
- Stable throughput regardless of load

**UI Load Tests** (realistic user interaction with clicks + leaderboard polling):
- 25 users: ✅ 375 clicks, 0 errors, avg 106ms/click
- 50 users: ✅ 750 clicks, 0 errors, avg 500ms/click

### Performance Characteristics

**Request Timing by Load**:
| Load | Avg Response | Status |
|------|---|---|
| 20 bots | 133ms | Snappy |
| 50 bots | 326ms | Good |
| 100 bots | 700ms | Acceptable |
| 200 bots | 1400ms | Slow but stable |
| 25 UI users | 106ms | Excellent |
| 50 UI users | 500ms | Acceptable |

**Throughput**: Consistent 130-140 steps/sec across all bot load levels (shows healthy linear scaling)

### Why Old Estimate Was Conservative

1. **Different test conditions** - May have used different parameters, timing, or test setup
2. **Test harness differences** - Old code vs. current bot template
3. **Conservative safety margin** - Old estimate included safety buffer
4. **Actual usage patterns** - Bots are synchronized worst-case; real UI users stagger requests

### Bottlenecks (Current Architecture)

1. **SQLite sequential writes** - Can't handle many simultaneous writers
2. **Synchronous evaluation** - One HTTP request at a time, no parallelism
3. **No caching** - Every evaluation hits database
4. **Frontend polling** - Multiple clients refreshing leaderboard adds overhead

### Suitable For

✅ **Classrooms**: 5-30 students (perfect experience)
✅ **Larger lectures**: 30-50 students (acceptable, slight delays)
⚠️ **Very large**: 50-100 students (works but noticeable slowdown)
❌ **Extreme**: 100+ students (would need optimization)

### Phase 2 Improvements (If Needed)

To support 100+ concurrent users:
1. **Database**: Upgrade SQLite → PostgreSQL (handles concurrent writes)
2. **Async backend**: Add async/await to evaluation handler
3. **Caching**: Cache function evaluations to reduce database hits
4. **WebSockets**: Replace HTTP polling with push updates
5. **Load balancing**: Run multiple backend instances

## Architecture Decisions

### Why SQLite?

- Simple file-based database (no server setup)
- Sufficient for classroom scale
- Good for quick iteration during development
- Easily upgrade to PostgreSQL later if needed

### Why FastAPI?

- Fast async-capable framework
- Automatic API documentation (Swagger)
- Type hints with Pydantic
- Easy to test
- Good for this project scale

### Why React + Vite?

- Fast development with HMR
- Component-based UI
- TypeScript for safety
- No build complexity (Vite abstracts webpack)

### Why No Backend Templating?

API-only backend allows:
- Frontend to be deployed independently
- Easy to build mobile apps later
- Clear separation of concerns
- Easier testing

### Why No State Library (Redux/Zustand)?

For this project scale:
- sessionStorage sufficient for session ID + role
- Few components needing shared state
- Simpler codebase, easier to understand
- Could add later if complexity grows

## Current Limitations

1. **No user authentication** - Relies on teacher PIN for admin operations
2. **No persistent sessions** - Sessions data lost if Docker container dies (mitigated by volume mount)
3. **Single database** - No replication or backup
4. **No async evaluation** - Evaluations processed sequentially
5. **No caching** - All function evaluations hit database
6. **Single backend instance** - No horizontal scaling
7. **SQLite scalability** - Limited concurrent writes

## Files Organization

### Backend
```
backend/
├── app/
│   ├── api/             # Route handlers
│   │   ├── functions.py # Function list endpoint
│   │   └── sessions.py  # Session lifecycle
│   ├── core/            # Core logic
│   │   ├── functions.py # Function evaluators
│   │   └── store.py     # Session/participant store
│   ├── db/              # Database
│   │   ├── models.py    # SQLAlchemy models
│   │   └── session.py   # DB session setup
│   ├── static/          # Reveal images
│   ├── main.py          # FastAPI app
│   └── app.db           # SQLite database (volume mounted)
└── tests/               # pytest test suite
```

### Frontend
```
frontend/
├── src/
│   ├── components/      # React components
│   ├── api.ts           # HTTP client
│   ├── types.ts         # TypeScript types
│   ├── App.tsx          # Main component
│   └── index.css        # Global styles
├── public/
├── index.html
└── package.json
```

### Bot
```
bot/
├── blackbox_client.py       # HTTP client library
├── student_bot_template.py  # Student algorithm template
├── stress_test.py           # Load testing utility
└── requirements.txt         # Dependencies
```

## Deployment

### Local Development
```powershell
docker compose up --build
```

### Production (Tar-based)
```powershell
# Export images
docker image save opt2d-backend:latest -o backend.tar
docker image save opt2d-frontend:latest -o frontend.tar

# On server, load and run
docker image load -i backend.tar
docker image load -i frontend.tar
docker compose -f docker-compose.upload.yaml up
```

See `deployment_portainer.md` for detailed server setup.

## Next Steps / Future Considerations

### Short Term
- Monitor real-world classroom usage
- Gather feedback from students and instructors
- Document any edge cases discovered

### Medium Term
- Add optional authentication (if multi-classroom scenario)
- Improve error messages and user feedback
- Consider WebSocket for real-time updates

### Long Term
- PostgreSQL upgrade for larger deployments
- Async evaluation optimization
- Horizontal scaling capability
- Mobile app companion
