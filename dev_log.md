# Dev Log (aktueller Stand)

## Backend starten

### Docker (empfohlen)
```powershell
# Repo-Root
docker compose up --build
```

Test:
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

Stop:
```powershell
docker compose down
```

### Lokal (ohne Docker)
```powershell
.\backend\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

---

## Persistenz (DB)

- Backend nutzt SQLite + SQLAlchemy (`app.db`)
- Sessions / Teilnehmer / Klicks / Leaderboard / Export bleiben nach Restart erhalten
- `max_steps` ist pro Session konfigurierbar

Wichtig:
- Bei Schemaänderungen an SQLite aktuell ggf. `app.db` löschen und Backend neu starten
- Langfristig wären Migrationen (z.B. Alembic) sinnvoll

---

## Frontend starten (Vite)

```powershell
cd frontend
npm install
npm run dev
```

Frontend:
- `http://localhost:5173`

### Frontend Env
Datei `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=1234
```

Nach Änderung an `.env`: Vite neu starten.

---

## Frontend Stand

### Dozent
- Session konfigurieren (eingeklappt)
- Dozenten-PIN zum Erstellen
- Aktive Session Panel
- Join-Link + QR-Code
- Beamer Mode (großer QR / Code, ohne Leaks)
- Bots starten
- Session beenden + Export laden
- Leaderboard + Teilnehmer-Pfad-Inspector rechts

### Teilnehmer
- Join per Code
- Canvas-Plot
- eigene Klicks / Stats / Klickliste
- optional Bot-Pfade anzeigen
- keine Funktionsdetails im UI sichtbar

### Rollen / Tab-Verhalten
- `adminToken` liegt in `sessionStorage` (tab-lokal)
- Teilnehmer-Session (`participantId`) liegt in `sessionStorage` (tab-lokal)
- `activeView` liegt in `sessionStorage`
- Name + letzter Code bleiben in `localStorage`

---

## API-Endpunkte

- `GET  /health`
- `GET  /functions`
- `POST /sessions`
- `GET  /sessions/{code}`
- `GET  /sessions/{code}/public`
- `POST /sessions/{code}/join`
- `POST /sessions/{code}/evaluate`
- `GET  /sessions/{code}/leaderboard`
- `GET  /sessions/{code}/snapshot`
- `POST /sessions/{code}/end`
- `GET  /sessions/{code}/export`

### Bot-Endpunkte
- `POST /sessions/{code}/bots/random_search`
- `POST /sessions/{code}/bots/hill_climb`

---

## Verfügbare Funktionen (aktuell im Projekt)
- sphere
- himmelblau
- rastrigin
- ackley
- rosenbrock

### Geplanter finaler Funktionssatz (aus Notebook)
- Sphere (shifted)
- Booth
- Himmelblau
- Rosenbrock
- Eggholder
- Rastrigin (shifted)
- Schwefel
- Levy
- Griewank (negated / shifted, max-case)
- Easom

---

## Backend API testen (PowerShell)

### Session erstellen
```powershell
$s = Invoke-RestMethod -Method Post http://localhost:8000/sessions -ContentType "application/json" -Body '{"function_id":"rosenbrock","goal":"min","max_steps":30}'
$code = $s.session_code
$adminToken = $s.admin_token
```

### Join
```powershell
$p = Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/join" -ContentType "application/json" -Body '{"name":"Alice"}'
$participantId = $p.participant_id
```

### Evaluate
```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/evaluate" -ContentType "application/json" -Body "{`"participant_id`":`"$participantId`",`"x`":1.0,`"y`":1.0}"
```

### Leaderboard
```powershell
Invoke-RestMethod "http://localhost:8000/sessions/$code/leaderboard"
```

### Public Session Info
```powershell
Invoke-RestMethod "http://localhost:8000/sessions/$code/public"
```

### End / Export
```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/end" -Headers @{ "X-Admin-Token" = $adminToken }
Invoke-RestMethod "http://localhost:8000/sessions/$code/export" -Headers @{ "X-Admin-Token" = $adminToken }
```

---

## Lokaler Python-Bot (aktueller Stand)

Neue Datei:
- `bot_client_example.py`

Aktuell:
- nutzt `GET /sessions/{code}/public`
- joint als normaler Teilnehmer
- evaluiert blind Punkte
- taucht im Leaderboard / Inspector auf

Wichtig:
- `requests` muss in die Backend-Requirements aufgenommen werden

### Noch in `backend/requirements.txt` ergänzen
```txt
requests
```

---

## Offene Kernpunkte

### Als Nächstes wichtig
- lokaler Python-Teilnehmer-Bot sauber ausbauen
- Reveal am Ende mit Funktionsbild / Plot
- finalen Funktionskatalog aus Notebook übernehmen
- Farben für Algorithmen/Bots
- Leaderboard-/Polling-Stabilität final prüfen
- kurze Guides schreiben

### Später
- Frontend containerisieren
- Routing / getrennte URLs optional
- OSM / topographische Karten
- Stress-Tests mit vielen Bots

---

## Deployment / Hosting

### Aktueller Stand
- Backend ist containerisiert und Docker-ready
- Persistenz via SQLite vorhanden
- Frontend läuft aktuell noch als Vite Dev Server

### Nächster Schritt für Hosting
- Frontend ebenfalls containerisieren
- `docker-compose` um Frontend-Service erweitern
- später als Portainer Stack deployen

### Einschätzung
Ja, ihr seid weiterhin auf einem guten Weg, das später sauber:
- zu dockerisieren
- über Portainer zu deployen
- und auf dem Laborserver laufen zu lassen

Der größte fehlende Deployment-Schritt ist aktuell nur noch:
- Frontend als Produktions-Container
