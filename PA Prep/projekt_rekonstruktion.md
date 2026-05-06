# Projekt-Rekonstruktion: Framework 2D Optimization (Master-Doku)

Dieses Dokument bietet eine lückenlose Rekonstruktion der Entstehung, Architektur und Funktionsweise des "Framework 2D Optimization". Es dient als zentrale Wissensbasis für die Projektarbeit.

## 1. Vision & Pädagogisches Konzept
Das Framework löst das Problem, abstrakte Optimierungstheorie (wie Genetische Algorithmen) greifbar zu machen.
- **Problem:** Optimierung findet oft in "Black Boxes" statt. Studenten verstehen die Dynamik von Exploration vs. Exploitation oft nur theoretisch.
- **Lösung:** Ein interaktives Kompetenz-Spiel.
    - **Phase A (Manuell):** Studenten "erfühlen" die Topographie durch Klicks. Sie entwickeln intuitiv Strategien (z.B. erst grobes Raster, dann lokale Suche).
    - **Phase B (Automatisiert):** Überführung der Intuition in Code (Python-Bots).
- **Zielgruppe:** Studierende der Informatik / KI im Rahmen der Vorlesung "Evolutionäre Algorithmen".

---

## 2. Detaillierter Entwicklungsverlauf & Meilensteine

### Meilenstein 1: Der synchrone Prototyp (MVP)
*   **Technik:** FastAPI (Sync), SQLite, React (Vite).
*   **Kern-Feature:** `POST /evaluate` – Ein Request pro Klick.
*   **Limitierung:** Bei >20 Teilnehmern traten Datenbank-Locks (SQLite) und hohe Latenzen auf. Das Polling der Bestenliste belastete die CPU.

### Meilenstein 2: Architektur-Shift auf High-Performance
*   **Entscheidung:** Migration auf ein voll-asynchrones System.
*   **PostgreSQL:** Einführung für sichere parallele Schreibzugriffe via `asyncpg`.
*   **Redis-Integration:** 
    *   **Caching:** Hochfrequente Daten (Leaderboard, Teilnehmerzahl) erhielten einen 1s-TTL Cache.
    *   **Snapshots:** Große Datenmengen wurden für 5s gecacht.
*   **WebSockets:** Implementierung von Real-Time Events (`click_added`, `session_ended`) via Redis Pub/Sub, was horizontales Skalieren der Backend-Instanzen ermöglicht.

### Meilenstein 3: Das "Local Evaluation" Paradigma (Phase 2)
*   **Herausforderung:** Automatisierte Bots mit Tausenden Iterationen fluteten die API.
*   **Innovation:** 
    *   **RPN Bytecode:** Das Backend übersetzt mathematische Funktionen in Reverse Polish Notation (z.B. `x 3.7 - 2 ^ y 2.1 + 2 ^ +`).
    *   **Vorteil:** Der Bot erhält die Logik verschleiert, kann aber lokal mit 0ms Latenz evaluieren.
    *   **Batch-Sync:** Einführung von `POST /sync_trajectory` für gesammelte Ergebnis-Übermittlung (bis zu 500.000 Punkte pro Session).

### Meilenstein 4: Teacher UX & Anti-Cheat
*   **Live-Monitoring:** Der Dozent kann Pfade einzelner Studenten im "Inspector" Schritt für Schritt (Slider) nachvollziehen.
*   **Server-Side Downsampling:** Um das Frontend bei massiven Bot-Daten nicht zu überlasten, sendet der Server nur repräsentative Stichproben der Pfade.
*   **Verifizierung:** Das Backend rechnet stichprobenartig Punkte aus Batch-Syncs nach, um Manipulationen der lokalen Ergebnisse zu verhindern.

---

## 3. Tiefe Technische Architektur

### Backend (Python 3.14+ / FastAPI)
- **Core-Logic:** Trennung von Routern (`api/`) und Geschäftslogik (`core/`).
- **Evaluator:** Robuste Implementierung von Benchmark-Funktionen (Sphere, Rosenbrock, Rastrigin, etc.) inkl. Bild-Generierung für den "Reveal".
- **Datenbank:** SQLAlchemy 2.0 (Async) mit PostgreSQL.
- **Sicherheit:** Dozenten-Bereich durch PIN geschützt; Funktions-Formeln verlassen den Server nur als Bytecode.

### Frontend (React / TypeScript)
- **Visualisierung:** Plotly.js für 2D-Kontur-Plots (Heatmaps) und 3D-Oberflächen.
- **Echtzeit:** Hybrides Modell aus WebSockets (Primär) und Polling (Fallback).
- **UX:** Getrennte Dashboards für Dozenten (Steuerung/Analyse) und Studenten (Interaktion).

### Infrastruktur & Qualitätssicherung
- **Docker-Orchestrierung:** `docker-compose.yaml` für reproduzierbare Umgebungen (DB, Redis, API, UI).
- **CI/CD-Skripte:** 
    - `build.py`: Vollständige Pipeline (Unit-Tests, Linting, Type-Check, Docker-Build).
    - `health_check.py`: Validierung der Service-Kette (API -> DB -> Redis).
- **Stresstests:** `stress_test.py` zur Simulation von 200+ Bots.

---

## 4. Aktueller Funktionskatalog
| Feature | Beschreibung |
| :--- | :--- |
| **Session Control** | Erstellen, Starten, Stoppen und "Revealen" durch Dozenten. |
| **Blackbox API** | REST-Endpunkte für manuelle Evaluierung und Bot-Sync. |
| **RPN Interpreter** | Lokale Berechnung der Funktionswerte auf Client-Seite. |
| **Leaderboard** | Live-Ranking nach bestem Z-Wert und benötigten Schritten. |
| **Path Inspector** | Rekonstruktion des Suchpfads jedes Teilnehmers für Analyse. |
| **Reveal-Mode** | Überlagerung der Teilnehmerpunkte mit der echten 3D-Landschaft nach Abschluss. |

---

## 5. Fazit für die Projektarbeit
Das Framework demonstriert erfolgreich den Übergang von einem einfachen Bildungs-Tool zu einer skalierbaren, industrienahen Architektur. Besonders die Lösung des Latenz-Problems bei gleichzeitiger Geheimhaltung der Zielfunktion (RPN-Ansatz) stellt eine signifikante technische Eigenleistung dar.
