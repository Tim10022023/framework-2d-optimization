# Dev Log (aktueller Stand)

## Projektstatus

### Aktueller Funktionsumfang
- FastAPI-Backend mit SQLite-Persistenz
- Sessions erstellen / joinen / evaluieren / beenden / exportieren
- Leaderboard
- Snapshot-/Pfadansicht
- Dozentenbereich und Teilnehmerbereich
- QR-Code / Beamer Mode
- interne Bots:
  - Random Search
  - Hill Climb
- lokaler Python-Student-Bot:
  - `bot/blackbox_client.py`
  - `bot/student_bot_template.py`
- Reveal nach Session-Ende mit Funktionsbild / Plot
- finaler Funktionskatalog aus dem Notebook übernommen
- Schritt-für-Schritt-Debugging von Teilnehmer- und Bot-Pfaden
- tab-lokale Rollen-/Sessionzustände per `sessionStorage`
- Frontend und Backend containerisiert

---

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

## Frontend starten

### Lokal mit Vite
```powershell
cd frontend
npm install
npm run dev
```

Frontend:
- `http://localhost:5173`

### Per Docker / Compose
Frontend läuft im Container über nginx und ist über Compose unter `http://localhost:5173` erreichbar.

---

## Frontend Env

### `frontend/.env`
Für lokalen Dev-Betrieb:
```env
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=11335577
```

### `frontend/.env.production`
Für Production-Build / Docker:
```env
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=11335577
```

Wichtig:
- `.env` wird für `npm run dev` genutzt
- `.env.production` wird für den Production-Build im Frontend-Container genutzt

---

## Persistenz (DB)

- Backend nutzt SQLite + SQLAlchemy (`app.db`)
- Sessions / Teilnehmer / Klicks / Leaderboard / Export bleiben nach Restart erhalten
- `max_steps` ist pro Session konfigurierbar

Aktuelle Persistenz im Compose:
- `./backend/app.db:/app/backend/app.db`

Wichtig:
- bei Schemaänderungen an SQLite aktuell ggf. `app.db` löschen und Backend neu starten
- langfristig wären Migrationen (z.B. Alembic) sinnvoll

---

## Docker / Deployment-Stand

### Compose
Aktuell laufen:
- Backend-Container
- Frontend-Container

### Einschätzung
Der Stack ist jetzt grundsätzlich:
- Docker-ready
- Full-stack per Compose startbar
- gut vorbereitbar für Portainer

### Nächste Deployment-Schritte
- Full-stack Compose nochmals bewusst testen
- Deployment-/Hosting-Notizen ergänzen
- Portainer-Deployment vorbereiten / durchdenken

---

## Frontend Stand

### Dozent
- Session konfigurieren (einklappbar)
- Dozenten-PIN zum Erstellen
- Aktive Session Panel
- Join-Link + QR-Code
- Beamer Mode
- interne Bots starten
- Session beenden + Export laden
- Leaderboard + Teilnehmer-/Bot-Pfad-Inspector
- Schritt-für-Schritt-Pfadansicht per Slider

### Teilnehmer
- Join per Code
- Canvas-Plot
- eigene Klicks / Stats / Klickliste
- optional Bot-Pfade anzeigen
- keine Funktionsdetails im UI sichtbar

### Rollen / Tab-Verhalten
- `adminToken` liegt in `sessionStorage`
- Teilnehmer-Session (`participantId`) liegt in `sessionStorage`
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

## Verfügbare Funktionen

Aktueller finaler Funktionssatz:
- Sphere (verschoben)
- Booth
- Himmelblau
- Rosenbrock
- Eggholder
- Rastrigin (verschoben)
- Schwefel
- Levy
- Griewank (negiert / verschoben, Maximierung)
- Easom

Reveal-Bilder liegen unter:
- `backend/app/static/function_images/`

---

## Backend API testen (PowerShell)

### Session erstellen
```powershell
$s = Invoke-RestMethod -Method Post http://localhost:8000/sessions -ContentType "application/json" -Body '{"function_id":"himmelblau","goal":"min","max_steps":30}'
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

### Snapshot
```powershell
Invoke-RestMethod "http://localhost:8000/sessions/$code/snapshot" | ConvertTo-Json -Depth 6
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

## Lokaler Python-Bot

### Dateien
- `bot/blackbox_client.py`
- `bot/student_bot_template.py`

### Abhängigkeit
```powershell
pip install requests
```

### Start
```powershell
python bot\student_bot_template.py
```

Der Bot:
- liest öffentliche Session-Infos
- joint als Bot die Session
- evaluiert Punkte blind
- erscheint im Leaderboard und im Dozenten-Inspector

---

## Stresstest / Skalierbarkeit

### Test-Setup
Datei:
- `bot/stress_test.py`

Getestet wurden parallele lokale Bots gegen dieselbe Session.

### Ergebnisse

#### 5 Bots, 10 Steps, 0.05s Delay
- 50 Schritte
- 0 Fehler
- Gesamtlaufzeit: 2.35s
- Ø Request-Zeit: 145.67 ms
- Median: 145.72 ms
- Max: 222.75 ms

#### 10 Bots, 20 Steps, kein Delay
- 200 Schritte
- 0 Fehler
- Gesamtlaufzeit: 18.70s
- Ø Request-Zeit: 861.58 ms
- Median: 876.11 ms
- Max: 1575.09 ms

#### 20 Bots, 20 Steps, kein Delay
- 400 Schritte
- 0 Fehler
- Gesamtlaufzeit: 68.85s
- Ø Request-Zeit: 3079.77 ms
- Median: 2914.76 ms
- Max: 8140.07 ms

#### 50 Bots, 20 Steps, kein Delay
- 49 Bots erfolgreich gejoint
- 322 Schritte
- 36 Fehler / Timeouts
- Gesamtlaufzeit: 114.20s
- Ø Request-Zeit: 5138.75 ms
- Median: 4672.73 ms
- Max: 10021.67 ms

### Technische Einordnung
- Für kleine bis mittlere Gruppen / Vorlesungsszenarien ist das System gut nutzbar.
- 5 bis 10 parallele Bots laufen stabil.
- 20 parallele Bots funktionieren noch, aber mit deutlich erhöhter Latenz.
- 50 aggressive parallele Bots überschreiten die robuste Grenze des aktuellen Setups.

### Wahrscheinliche Bottlenecks
- SQLite bei vielen gleichzeitigen Schreibzugriffen
- ein HTTP-Request pro Evaluierung
- synchrone Verarbeitung
- Polling-Last im Frontend zusätzlich

### Fazit
Das System ist für den geplanten Vorlesungseinsatz wahrscheinlich ausreichend, solange nicht sehr viele Bots ohne Delay gleichzeitig feuern.
Für höhere Last wären später sinnvoll:
- andere DB
- weniger Polling / effizientere Updates
- entkoppelte Bot-Ausführung / Queue / Worker

---

## Doku / Guides

Im Ordner `docs/`:
- `participant_guide.md`
- `teacher_guide.md`
- `student_bot_guide.md`

Zusätzlich:
- `README.md`
- `dev_log.md`

---

## Offene nächste Schritte

### Fast fertig / noch sauber machen
- Leaderboard-/Polling-Verhalten einmal bewusst im Full-Stack testen
- kleine UI-/Layout-Kanten glätten
- Status-Bar final leicht polishen
- README / Docs final im Repo einordnen
- Ordnerstruktur final aufräumen

### Nächste Pflichtpunkte
- Stresstest-Ergebnisse sauber dokumentieren
- Einschätzung der aktuellen Skalierbarkeit dokumentieren
- Full-stack Docker-Setup final testen
- Deployment-/Hosting-Notizen ergänzen
- Portainer-Deployment vorbereiten

### Danach / Phase 2
- OpenStreetMap / topographische Karten
- Funktionsbilder direkt in Dozentenansicht ein-/ausblendbar
- weiteres Visual-Polish
- optional Routing / getrennte URLs
- robustere Persistenz / Architektur für höhere Last
