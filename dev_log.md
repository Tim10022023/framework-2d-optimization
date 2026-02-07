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
```
Nach Änderung an `.env`: Vite neu starten (`CTRL+C`, dann `npm run dev`).

---

## API-Endpunkte (MVP)

- `GET  /health`
- `GET  /functions`
- `POST /sessions`  → liefert `session_code` + `admin_token`
- `GET  /sessions/{code}`
- `POST /sessions/{code}/join`
- `POST /sessions/{code}/evaluate`  → gesperrt wenn `status=ended`
- `GET  /sessions/{code}/leaderboard`
- `POST /sessions/{code}/end`  (Header: `X-Admin-Token`)
- `GET  /sessions/{code}/export` (Header: `X-Admin-Token`, nur wenn ended)

---

## Backend API testen (PowerShell)

### Session erstellen
```powershell
$s = Invoke-RestMethod -Method Post http://localhost:8000/sessions -ContentType "application/json" -Body '{"function_id":"sphere","goal":"min"}'
$code = $s.session_code
$adminToken = $s.admin_token
$code
$adminToken
```

### Join + Evaluate
```powershell
$p = Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/join" -ContentType "application/json" -Body '{"name":"Alice"}'
$participantIdA = $p.participant_id

Invoke-RestMethod -Method Post "http://localhost:8000/sessions/$code/evaluate" -ContentType "application/json" -Body "{`"participant_id`":`"$participantIdA`",`"x`":0.2,`"y`":0.2}"
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

---

## Frontend Test Flow

1) Backend läuft: `http://localhost:8000/docs`
2) Session erstellen (`POST /sessions`) → `session_code` kopieren
3) Frontend: `http://localhost:5173` → Code + Name → Join
4) Klick ins Feld → `evaluate` → z/steps werden angezeigt
5) Leaderboard panel pollt `GET /leaderboard` automatisch
