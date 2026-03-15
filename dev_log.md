# Dev Log (aktueller Stand)

Dieses Dev-Log dokumentiert den technischen Entwicklungsstand, die Abschlussphase und die wichtigsten Einordnungen zu Funktionalität, Skalierbarkeit und verbleibenden Abschlussarbeiten.

## Projektstatus

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
- Heatmap-Overlay im Inspector als Bonus
- Frontend und Backend containerisiert
- Full Stack läuft gemeinsam per Docker Compose

## Backend starten

### Docker

```powershell
docker compose up --build
```

### Lokal

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Frontend starten

### Lokal mit Vite

```powershell
cd frontend
npm install
npm run dev
```

### Per Docker / Compose

Frontend läuft im Container über nginx und ist per Compose unter `http://localhost:5173` erreichbar.

## Persistenz (DB)

- Backend nutzt SQLite + SQLAlchemy (`app.db`)
- Sessions / Teilnehmer / Klicks / Leaderboard / Export bleiben nach Restart erhalten
- `max_steps` ist pro Session konfigurierbar

Compose-Mount:
- `./backend/app.db:/app/backend/app.db`

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

Reveal-Bilder liegen unter:
- `backend/app/static/function_images/`

## Lokaler Python-Bot

Dateien:
- `bot/blackbox_client.py`
- `bot/student_bot_template.py`

Abhängigkeit:
```powershell
pip install requests
```

Start:
```powershell
python bot\student_bot_template.py
```

## Stresstest / Skalierbarkeit

Datei:
- `bot/stress_test.py`

Ergebnisse:
- 5 Bots, 10 Steps, 0.05s Delay: stabil
- 10 Bots, 20 Steps, kein Delay: gut nutzbar
- 20 Bots, 20 Steps, kein Delay: deutlich langsamer, aber ohne Fehler
- 50 Bots, 20 Steps, kein Delay: Timeouts / Grenze des aktuellen Setups

Einordnung:
- Für kleine bis mittlere Gruppen / Vorlesungsszenarien gut nutzbar
- 50 aggressive parallele Bots überschreiten die robuste Grenze des aktuellen Setups

Wahrscheinliche Bottlenecks:
- SQLite bei vielen gleichzeitigen Schreibzugriffen
- ein HTTP-Request pro Evaluierung
- synchrone Verarbeitung
- Polling-Last im Frontend zusätzlich

## Aktuelle Restagenda

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

## Abschlussfazit

Das Kernsystem ist funktional weitgehend abgeschlossen und für Demo-, Lehr- und kleinere bis mittlere Vorlesungsszenarien gut geeignet. Der Fokus liegt jetzt nicht mehr auf neuen Kernfeatures, sondern auf Abschlussarbeiten: Doku aktualisieren, Repo sauber finalisieren, Full-Stack-Test absichern und Deployment-/Hosting-Notizen ergänzen.
