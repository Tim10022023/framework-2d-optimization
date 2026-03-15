# Framework 2D Optimization

Interaktives Lehr- und Demonstrationstool für 2D-Optimierungsprobleme mit Dozenten- und Teilnehmeransicht, Vergleichsbots, Reveal nach Session-Ende und lokalem Python-Bot-Template für Studierende.

---

## Projektidee

Studierende optimieren eine unbekannte 2D-Funktion als **Blackbox**.  
Sie sehen während der Session **nicht** die eigentliche Funktion, sondern nur ihre eigenen Abfragen `(x, y)` und die zugehörigen Funktionswerte `z`.

Der Dozent kann:
- Sessions konfigurieren
- QR / Session-Code freigeben
- Teilnehmer und Bots beobachten
- Pfade Schritt für Schritt analysieren
- nach Session-Ende den Reveal anzeigen

Zusätzlich können Studierende einen **lokalen Python-Bot** gegen die laufende Session ausführen.

---

## Features

### Backend
- FastAPI REST API
- SQLite-Persistenz
- Sessions erstellen / joinen / evaluieren / beenden / exportieren
- Leaderboard
- Snapshot für Pfad-Ansichten
- max. Klickanzahl pro Session
- interne Vergleichsbots:
  - Random Search
  - Hill Climb
- Public Session Endpoint für Blackbox-Bots

### Frontend
- Dozentenbereich
- Teilnehmerbereich
- Join per Code
- QR-Code / Beamer Mode
- Live-Leaderboard
- Teilnehmer-Pfad-Inspector
- Schritt-für-Schritt-Debugging per Slider
- Reveal / Export nach Session-Ende
- Bot-Pfade optional im Teilnehmer-UI
- tab-lokale Rollen-/Sessionzustände per `sessionStorage`

### Blackbox / Bot
- `blackbox_client.py` als einfache Python-API
- `student_bot_template.py` als Template für eigene lokale Optimierungsalgorithmen

---

## Projektstruktur

```text
framework-2d-optimization/
├─ backend/
│  ├─ app/
│  ├─ requirements.txt
│  └─ ...
├─ frontend/
│  ├─ src/
│  └─ ...
├─ docs/
│  ├─ participant_guide.md
│  ├─ teacher_guide.md
│  └─ student_bot_guide.md
├─ bot/
│  ├─ blackbox_client.py
│  └─ student_bot_template.py
├─ docker-compose.yaml
├─ Dockerfile
├─ dev_log.md
└─ README.md
```

---

## Backend starten

### Docker
```powershell
docker compose up --build
```

Backend:
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Logs:
```powershell
docker compose logs -f backend
```

Restart:
```powershell
docker compose restart backend
```

### Lokal
```powershell
.\backend\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

---

## Frontend starten

```powershell
cd frontend
npm install
npm run dev
```

Frontend:
- `http://localhost:5173`

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=11335577
```

---

## Lokalen Student-Bot starten

Benötigte Dateien:
- `bot/student_bot_template.py`
- `bot/blackbox_client.py`

Abhängigkeit:
```powershell
pip install requests
```

Session-Code in `student_bot_template.py` eintragen und dann starten:

```powershell
python bot\student_bot_template.py
```

Der Bot:
- joint als Bot die Session
- evaluiert Punkte blind
- erscheint im Leaderboard und im Dozenten-Inspector

---

## Verfügbare Funktionen

Aktueller finaler Katalog:
- Sphere (verschoben)
- Booth
- Himmelblau
- Rosenbrock
- Eggholder
- Rastrigin (verschoben)
- Schwefel
- Levy
- Griewank (negiert, verschoben)
- Easom

---

## Typischer Ablauf

### Dozent
1. Session konfigurieren
2. QR / Code freigeben
3. Teilnehmer und Bots beobachten
4. Session beenden
5. Reveal anzeigen

### Teilnehmer
1. Code eingeben
2. Join
3. Punkte klicken
4. Statistik beobachten

### Student-Bot
1. Session-Code eintragen
2. `propose_point(...)` implementieren
3. Bot starten
4. Verlauf beobachten

---

## Guides

Im Ordner `docs/`:
- `participant_guide.md`
- `teacher_guide.md`
- `student_bot_guide.md`

---

## Deployment-Hinweis

Aktueller Stand:
- Backend ist Docker-ready
- Frontend läuft aktuell als Vite-Frontend
- nächster sinnvoller Deployment-Schritt: Frontend ebenfalls containerisieren

Für späteren Betrieb über Portainer empfiehlt sich:
- fertige Docker-Container/Images
- saubere Compose-/Stack-Konfiguration
- optional getrennte Produktionskonfiguration für Backend + Frontend

---

## Technische Einordnung

Der aktuelle Stand ist gut geeignet für:
- Vorlesungen
- kleine bis mittlere Gruppen
- Vergleich von Menschen und Bots
- Demonstrationen von Optimierungsstrategien

Für größere Lasttests wären später sinnvoll:
- systematischere Stress-Tests
- ggf. weniger Polling / effizientere Updates
- ggf. robustere Persistenz als SQLite bei hoher Parallelität

---

## Status

Der Projektstand umfasst bereits:
- Sessions
- Persistenz
- Dozenten-/Teilnehmer-UI
- Reveal
- Bots
- lokalen Python-Bot
- Schritt-für-Schritt-Pfadinspektion

Offene nächste Themen:
- Doku finalisieren
- Stress-Tests
- Frontend-Container
- Portainer-Deployment
- weitere UI-Politur
