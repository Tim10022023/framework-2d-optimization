# Frontend Analysis: Framework 2D Optimization

This report provides a detailed analysis of the frontend implementation of the Framework 2D Optimization platform, intended for inclusion in a scientific thesis chapter.

---

## 1. Frontend technology stack

- **Framework and language:** React 19 (TypeScript). The implementation leverages modern React features such as functional components and hooks (`useState`, `useEffect`, `useMemo`, `useRef`).
- **Build tool:** Vite, ensuring fast development cycles and optimized production builds.
- **Main libraries used:**
    - **Plotly.js (`react-plotly.js`):** Used for sophisticated 2D contour and 3D surface visualizations during the reveal phase.
    - **Vanilla Canvas API:** Used for the high-performance "Black-Box" interaction area (`PlotCanvas.tsx`).
- **Styling/UI approach:** Primarily Vanilla CSS using inline styles for component-level layouts and a global `index.css`/`App.css` for base styles. This approach maintains simplicity and zero-dependency styling.
- **State management approach:** Managed locally via React standard hooks. Persistent state (session context, admin tokens, user roles) is stored in `sessionStorage` and `localStorage`. No external state libraries (Redux/Zustand) are used.
- **API/WebSocket communication approach:** 
    - **REST (Fetch API):** Used for session lifecycle (create, join, end), fetching snapshots, and exporting data.
    - **WebSockets:** Used for real-time broadcasting of click events, participant counts, and leaderboard updates, enabling a synchronized multi-user experience.

---

## 2. Frontend folder and module structure

```text
frontend/src/
├── api.ts              # Central API client (REST & WebSocket management)
├── App.tsx             # Main application entry point, role routing, and global state
├── types.ts            # Shared TypeScript definitions (Models, Responses, DTOs)
├── components/         # UI Components
│   ├── PlotCanvas.tsx             # Interactive 2D search space (Canvas-based)
│   ├── TeacherCreatePanel.tsx      # Configuration for session setup
│   ├── TeacherActiveSessionPanel.tsx # Control center for running sessions
│   ├── TeacherInspectPanel.tsx     # Step-by-step analysis and Reveal view
│   ├── LeaderboardPanel.tsx        # Live-updating ranking list
│   ├── FunctionContourPlot.tsx     # Plotly 2D heatmap visualization
│   ├── FunctionSurfacePlot.tsx     # Plotly 3D landscape visualization
│   ├── StatsPanel.tsx              # Individual progress metrics
│   ├── PointsListPanel.tsx         # Tabular history of evaluated points
│   └── StatusBar.tsx               # Context-aware session status indicator
└── lib/
    └── benchmarkFunctions.ts       # Frontend mirror of optimization functions for visualization
```

---

## 3. Main user roles and UI flows

### Teacher/Session Creator
1. **Session Creation:** Selects a function (e.g., Sphere, Rosenbrock), optimization goal (Min/Max), and click limit. Protects creation with a teacher PIN.
2. **Active Management:** Monitors live participants, adds bot-participants (Random or Hill-Climb), and ends the session.
3. **Analysis:** Inspects individual participant trajectories step-by-step using a timeline slider and toggles the "Reveal" mode to compare search paths with the actual function landscape.

### Student/Participant
1. **Session Joining:** Joins via a code (or URL) and enters a nickname.
2. **Search Phase:** Clicks on the `PlotCanvas` to evaluate points. Receives immediate feedback on the `z` value and proximity to the goal.
3. **Observation:** Monitors their own stats and observes bot trajectories (if enabled) to reflect on different search strategies in real-time.

---

## 4. Important React components/pages

| Component Name | Purpose | Key Props/State | Backend/WS Connection | Req. ID |
| :--- | :--- | :--- | :--- | :--- |
| `App` | Orchestrates roles and global state. | `activeView`, `points`, `leaderboard` | Multiple REST + WebSocket | F1, F2 |
| `PlotCanvas` | Interactive search area. | `bounds`, `points`, `onEvaluate` | `POST /evaluate` | F3 |
| `TeacherInspectPanel` | Post-session analysis & Reveal. | `snapshot`, `visibleStep`, `revealed` | `GET /snapshot` | F7, F8 |
| `LeaderboardPanel` | Live participant ranking. | `leaderboard`, `hoveredPid` | WS `leaderboard_updated` | F4 |
| `TeacherCreatePanel` | Configuration of new sessions. | `functions`, `maxSteps`, `pin` | `POST /sessions` | F1 |
| `FunctionSurfacePlot`| 3D landscape visualization. | `functionId`, `points` | Local computation (lib) | F7 |

---

## 5. API communication

| Frontend Action | Method/Event | Purpose | Data Sent | Req. ID |
| :--- | :--- | :--- | :--- | :--- |
| Create Session | `POST /sessions` | Initialize a game. | `function_id`, `goal`, `max_steps` | F1 |
| Join Session | `POST /.../join` | Participate in session. | `name` | F2 |
| Evaluate Point | `POST /.../evaluate` | Get `z` for `(x,y)`. | `x`, `y`, `participant_id` | F3 |
| Get Snapshot | `GET /.../snapshot` | Fetch all session data. | Admin Token | F8 |
| Receive Click | WS `click_added` | Real-time path update. | `x`, `y`, `z`, `step`, `p_id` | NF2 |
| Update Leaderboard| WS `leaderboard_updated` | Update live ranking. | `leaderboard` array | F4 |

---

## 6. Visualization and interaction with the 2D search space

- **Display:** The search space is rendered as an abstract 2D coordinate system using the HTML5 Canvas API. Grid lines and axes provide orientation without revealing the underlying function.
- **Interaction:** Clicks on the canvas are mapped from pixel coordinates to search space coordinates (e.g., [-5, 5]) based on the session's `bounds`.
- **Evaluation:** Points are rendered as circles. The current point is highlighted, and past points are connected by lines to show the search path (trajectory).
- **Black-Box Principle:** During the active phase, the landscape is entirely hidden. Only evaluated points are visible. The UI enforces "Black-Box" by only rendering what has been explicitly explored.
- **Data Reveal:** After the session ends, the teacher can trigger the "Reveal" mode, which overlays the canvas data onto a Plotly heatmap or 3D surface plot.

---

## 7. Teacher view

The teacher view is designed for **didactic control**:
- **Configuration:** Allows setting pedagogical constraints (e.g., limited steps to force efficient searching).
- **Bot Orchestration:** Teachers can inject different bot types (Random vs. Hill-Climb) to demonstrate various optimization behaviors to students.
- **Live Monitoring:** The `LeaderboardPanel` and `TeacherInspectPanel` provide a "God view" of the room's progress without interfering with the students' search.

---

## 8. Student view

The student view focuses on **exploration and immediate feedback**:
- **Minimalist Interface:** Prevents information overload; focus is on the 2D plane.
- **Immediate Feedback:** Evaluation results appear instantly (via REST) and are synced (via WS) to ensure the UI reflects the true server state.
- **Bot Trails:** Students can optionally toggle "Bot-Pfade" to see how automated algorithms explore the space, fostering social and algorithmic learning.

---

## 9. Reveal / analysis mode

The Reveal mode is the "Aha!" moment of the educational flow:
- **Trajectory Analysis:** A range slider allows "replaying" a student's search. This supports reflection: "Why did I get stuck here?\" or \"How did I miss that peak?\".
- **Side-by-Side Visualization:** The 2D Canvas is shown next to 2D Contour and 3D Surface plots. This bridges the gap between the abstract search and the mathematical reality.
- **Reflection:** Teachers can use the path of a successful student versus a bot to discuss the trade-off between exploration and exploitation.

---

## 10. Error handling and UX

- **Graceful Failures:** The `api.ts` maps backend error codes to human-readable German messages (e.g., \"Klick-Limit erreicht\", \"Session nicht gefunden\").
- **Persistence:** `sessionStorage` allows users to refresh the page without losing their session or progress.
- **WebSocket Resilience:** Includes an automatic reconnection logic (3-second delay) if the socket drops.
- **UX Safeguards:** The `TeacherCreatePanel` requires a PIN to prevent accidental session creation by students. Buttons are disabled during pending async operations (`isJoining`, `isCreatingSession`).

---

## 11. Screenshots recommended for the thesis

1. **Teacher Creation Panel:**
    - **What it shows:** The configuration options (Function selection, bounds, max steps).
    - **Placement:** Section 5.2.1 (Initialization).
    - **Goal:** Demonstrates the didactic flexibility and session setup.
    - **Caption:** \"Interface for session configuration and parameterization.\"
2. **Active Student Dashboard:**
    - **What it shows:** The `PlotCanvas` with a trajectory and the `StatsPanel`.
    - **Placement:** Section 5.2.2 (Execution).
    - **Goal:** Visualizes the Black-Box search interaction.
    - **Caption:** \"Participant view during the optimization phase.\"
3. **Teacher Reveal Mode:**
    - **What it shows:** Side-by-side view of the Canvas path and the Plotly 3D Surface plot.
    - **Placement:** Section 5.2.3 (Reflection).
    - **Goal:** Highlights the educational \"reveal\" of the landscape.
    - **Caption:** \"Comparison of search trajectory and the actual function landscape in Reveal Mode.\"
4. **Live Leaderboard:**
    - **What it shows:** The ranking of participants with their best `z` values.
    - **Placement:** Section 5.2.2 (Execution).
    - **Goal:** Demonstrates real-time multi-user feedback.
    - **Caption:** \"Live Leaderboard showing real-time participant progress.\"

---

## 12. Thesis-relevant interpretation

The frontend implementation effectively realizes the \"Black-Box\" educational concept by **strictly separating state and visualization**. During the active phase, the UI acts as a filter, only showing point-wise data. The transition to the Reveal phase using Plotly.js transforms the \"game\" into a \"mathematical analysis tool.\" The use of WebSockets is critical for the \"live classroom\" feel, ensuring that the leaderboard and bot trajectories act as immediate social anchors for the students' own exploration strategies. This architecture supports the didactic goal of **experiential learning** followed by **guided reflection**.
