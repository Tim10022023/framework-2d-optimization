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

Restart (wichtig bei Codeänderungen/DB-Umstellung):
```powershell
docker compose restart backend
```

Stop:
```powershell
# im laufenden Terminal: CTRL+C
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

- Backend nutzt jetzt SQLite + SQLAlchemy (`app.db`)
- Sessions/Teilnehmer/Klicks/Leaderboard/Export sind persistent (bleiben nach Restart erhalten)

Persistenz-Check:
1) Session erstellen + join + evaluate
2) `docker compose restart backend`
3) Session/Leaderboard/Export erneut abrufen → Daten sollten noch da sein

---

## Frontend starten (Vite)

> Hinweis: npm install/create kann im VPN blockiert sein → ggf. ohne VPN ausführen.

```powershell
# Repo-Root (nur einmal)
npm create vite@latest frontend -- --template react-ts

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
```

Nach Änderung an `.env`: Vite neu starten (`CTRL+C`, dann `npm run dev`).

Frontend Features:
- Dozentenbereich: Session erstellen/beenden, Join-Link + QR-Code, Export/Reveal
- Teilnehmerbereich: Join, Canvas-Plot (Bounds dynamisch), Pfad + Cursor-Koordinaten, Klickliste, Stats
- Leaderboard live (Polling)
- localStorage: Name + letzter Session-Code gespeichert

---

## API-Endpunkte (MVP)

- `GET  /health`
- `GET  /functions` (inkl. bounds)
- `POST /sessions` → liefert `session_code` + `admin_token`
- `GET  /sessions/{code}` → inkl. `status`
- `POST /sessions/{code}/join`
- `POST /sessions/{code}/evaluate` → gesperrt wenn `status=ended`
- `GET  /sessions/{code}/leaderboard`
- `POST /sessions/{code}/end` (Header: `X-Admin-Token`)
- `GET  /sessions/{code}/export` (Header: `X-Admin-Token`, nur wenn ended)

Verfügbare Funktionen (aktuell):
- sphere
- himmelblau
- rastrigin
- ackley
- rosenbrock

---

## Backend API testen (PowerShell)

### Session erstellen
```powershell
$s = Invoke-RestMethod -Method Post http://localhost:8000/sessions -ContentType "application/json" -Body '{"function_id":"rosenbrock","goal":"min"}'
$code = $s.session_code
$adminToken = $s.admin_token
$code
$adminToken
```

### Join + Evaluate
```powershell
$p = Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/join" -ContentType "application/json" -Body '{"name":"Alice"}'
$participantIdA = $p.participant_id

Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/evaluate" -ContentType "application/json" -Body "{`"participant_id`":`"$participantIdA`",`"x`":1.0,`"y`":1.0}"
```

### Leaderboard
```powershell
Invoke-RestMethod "http://localhost:8000/sessions/$code/leaderboard"
```

### End (Dozent)
```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/end" -Headers @{ "X-Admin-Token" = $adminToken }
```

### Export/Reveal (nach End)
```powershell
Invoke-RestMethod "http://localhost:8000/sessions/$code/export" -Headers @{ "X-Admin-Token" = $adminToken }
```

### Persistenz-Test nach Restart
```powershell
docker compose restart backend
Invoke-RestMethod "http://localhost:8000/sessions/$code"
Invoke-RestMethod "http://localhost:8000/sessions/$code/leaderboard"
Invoke-RestMethod "http://localhost:8000/sessions/$code/export" -Headers @{ "X-Admin-Token" = $adminToken }
```

---

## Frontend Test Flow

1) Backend läuft: `http://localhost:8000/docs`
2) Frontend läuft: `http://localhost:5173`
3) Dozentenbereich: Session erstellen → Join-Link/QR sichtbar
4) Teilnehmerbereich: Code+Name → Join
5) Klicks im Canvas → evaluate → Pfad/Klickliste/Stats aktualisieren sich
6) Leaderboard aktualisiert live
7) Dozent: Session beenden → Export/Reveal anzeigen
