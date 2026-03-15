# Framework 2D Optimization

Interaktives Lehr- und Demonstrationstool für **2D-Optimierungsprobleme** mit Dozenten- und Teilnehmeransicht, Vergleichsbots, Reveal nach Session-Ende und lokalem Python-Bot-Template für Studierende.

Das Projekt ist primär als **didaktisches Demo- und Lehrtool** gedacht: Studierende optimieren eine unbekannte 2D-Funktion als Blackbox, während Dozierende den Verlauf beobachten, analysieren und nach Session-Ende den Reveal anzeigen können.

## Projektidee

Studierende optimieren eine unbekannte 2D-Funktion als **Blackbox**. Während der Session sehen sie nicht die eigentliche Funktion, sondern nur ihre Abfragen `(x, y)` und die zugehörigen Funktionswerte `z`.

Der Dozent kann:
- Sessions konfigurieren
- QR / Session-Code freigeben
- Teilnehmer und Bots beobachten
- Pfade Schritt für Schritt analysieren
- nach Session-Ende den Reveal anzeigen

Zusätzlich können Studierende einen lokalen Python-Bot gegen die laufende Session ausführen.

## Aktueller Funktionsumfang

### Backend
- FastAPI REST API
- SQLite-Persistenz
- Sessions erstellen / joinen / evaluieren / beenden / exportieren
- Leaderboard
- Snapshot für Pfad-Ansichten
- maximale Klickanzahl pro Session
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
- Teilnehmer-/Bot-Pfad-Inspector
- Schritt-für-Schritt-Debugging per Slider
- Reveal / Export nach Session-Ende
- optionale Bot-Pfade im Teilnehmer-UI
- Heatmap-Overlay im Inspector als Bonus nach Reveal
- tab-lokale Rollen-/Sessionzustände per `sessionStorage`

### Bot / Blackbox
- `bot/blackbox_client.py` als einfache Python-API
- `bot/student_bot_template.py` als Template für eigene lokale Optimierungsalgorithmen
- `bot/stress_test.py` für parallele Lasttests

## Projektstruktur

```text
framework-2d-optimization/
├─ backend/
├─ frontend/
├─ docs/
├─ bot/
├─ docker-compose.yaml
├─ Dockerfile
├─ README.md
└─ dev_log.md
```

## Schnellstart

### Docker Compose (empfohlen)

```powershell
docker compose up --build
```

Danach erreichbar unter:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Frontend und Backend laufen gemeinsam per Docker Compose. Für den normalen Projektstart ist das der empfohlene Weg.

## Lokaler Start ohne Docker

### Backend

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Falls lokal mit virtueller Umgebung gearbeitet wird, diese vorher aktivieren.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend lokal:
- `http://localhost:5173`

## Frontend-Umgebungsvariablen

`frontend/.env`
```env
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=3736283747
```

`frontend/.env.production`
```env
VITE_API_URL=http://localhost:8000
VITE_PUBLIC_APP_URL=http://localhost:5173
VITE_TEACHER_PIN=3736283747
```

Hinweis: Für echtes Deployment sollte `VITE_API_URL` auf die produktive Backend-URL angepasst werden.

## Lokalen Student-Bot starten

Benötigte Dateien:
- `bot/student_bot_template.py`
- `bot/blackbox_client.py`

Abhängigkeit:
```powershell
pip install requests
```

Session-Code in `student_bot_template.py` eintragen und starten:

```powershell
python bot\student_bot_template.py
```

Hinweis:
Der Bot startet nur bei aktiver Session (`status=running`).

## Verfügbare Funktionen

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

## Stresstest / Skalierbarkeit

Bisherige Einordnung:
- 5 Bots: stabil
- 10 Bots: gut nutzbar
- 20 Bots: deutlich langsamer, aber ohne Fehler
- 50 aggressive Bots: Timeouts / Grenze des aktuellen Setups

Fazit:
- geeignet für Vorlesung / kleine bis mittlere Gruppen
- nicht für hohe Parallelität optimiert

Die detailliertere technische Einordnung steht in `dev_log.md`.

## Deployment-Hinweis

Aktueller Stand:
- Backend ist Docker-ready
- Frontend ist ebenfalls containerisiert
- Full Stack läuft per Docker Compose
- SQLite bleibt per `app.db` persistent

Deployment-/Hosting-Notizen und Portainer-Hinweise können als separate Betriebsdokumentation ergänzt werden.

## Weitere Dokumente

Im Ordner `docs/`:
- `participant_guide.md`
- `teacher_guide.md`
- `student_bot_guide.md`

Zusätzlich:
- `dev_log.md` für technischen Verlauf, Stresstest und Skalierungseinordnung
