# Portainer Deployment

Diese Notiz beschreibt nur die Schritte, um das Projekt über **Portainer** auf dem Server in Betrieb zu nehmen.

## Voraussetzungen

Vor dem Deployment muss im Projekt bereits Folgendes umgesetzt sein:

- Backend-CORS ist per `BACKEND_CORS_ORIGINS` konfigurierbar
- Frontend-Build bekommt `VITE_API_URL`, `VITE_PUBLIC_APP_URL` und `VITE_TEACHER_PIN` per Build-Args
- SQLite wird über ein Docker-Volume persistiert
- `docker-compose.yaml` ist auf dem finalen Stand

## 1. Stack in Portainer anlegen

1. In Portainer anmelden
2. Links auf **Stacks**
3. **Add stack**
4. Stack-Namen vergeben, z. B. `framework-2d-optimization`
5. Die finale `docker-compose.yaml` einfügen oder aus dem Repo laden

## 2. Environment-Variablen setzen

In Portainer im Stack diese Variablen setzen:

```env
VITE_API_URL=http://SERVER-IP:8000
VITE_PUBLIC_APP_URL=http://SERVER-IP:5173
VITE_TEACHER_PIN=DEIN_PIN
BACKEND_CORS_ORIGINS=http://SERVER-IP:5173
```

Falls eine Domain verwendet wird, statt `SERVER-IP` die Domain einsetzen.

Beispiel:

```env
VITE_API_URL=https://api.example.com
VITE_PUBLIC_APP_URL=https://app.example.com
VITE_TEACHER_PIN=DEIN_PIN
BACKEND_CORS_ORIGINS=https://app.example.com
```

## 3. Stack deployen

Nach dem Setzen der Variablen:

1. **Deploy the stack**
2. warten, bis beide Container laufen:
   - `opt2d-backend`
   - `opt2d-frontend`

## 4. Nach dem Deploy testen

Im Browser prüfen:

- Frontend erreichbar
- Dozentenansicht lädt
- Session erstellen funktioniert
- Teilnehmer-Join funktioniert
- Klicks/Evaluierungen funktionieren
- interner Random-Bot funktioniert
- interner Hill-Climb-Bot funktioniert
- Session beenden funktioniert
- Reveal / Export funktioniert

Zusätzlich prüfen:

- Backend-Health: `http://SERVER-IP:8000/health`
- Swagger: `http://SERVER-IP:8000/docs`

## 5. Persistenz prüfen

Die Datenbank wird über das Docker-Volume `opt2d_data` gespeichert.

Zum Test:

1. Session erstellen
2. Container/Stack neu starten
3. prüfen, ob Daten weiterhin vorhanden sind

Wenn ja, ist die Persistenz korrekt.

## 6. Typische Fehler

### Frontend lädt, aber API funktioniert nicht
Wahrscheinliche Ursache:
- `VITE_API_URL` zeigt noch auf `localhost`

### CORS-Fehler im Browser
Wahrscheinliche Ursache:
- `BACKEND_CORS_ORIGINS` ist falsch gesetzt

### Nach Neustart sind Daten weg
Wahrscheinliche Ursache:
- Volume ist nicht korrekt eingebunden

### Interne Bots starten nicht
Wahrscheinliche Ursache:
- Teacher-Kontext / Admin-Token fehlt
- Session ist bereits beendet

## 7. Update später einspielen

Bei Änderungen:

1. aktuellen Repo-Stand / neue Compose-Version bereitstellen
2. Stack in Portainer aktualisieren
3. neu deployen
4. kurz durchtesten

## Ergebnis

Wenn Frontend, Backend, Persistenz, Bots und Session-Ende funktionieren, ist das Projekt auf dem Server betriebsbereit.
