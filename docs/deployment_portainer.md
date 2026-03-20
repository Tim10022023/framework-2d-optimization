# Portainer Deployment

Diese Notiz beschreibt Schritt für Schritt, wie das Projekt über **Portainer** auf dem Server aktiviert wird.

## Vorbereitungen

Vor dem Deployment sollten bereitliegen:

- die finale `docker-compose.yaml`
- die Server-IP oder Domain
- der gewünschte **Dozenten-PIN**
- Portainer-Zugang
- ein funktionierender Docker-/Portainer-Host

Außerdem muss im Projekt bereits korrekt umgesetzt sein:

- Backend-CORS ist per `BACKEND_CORS_ORIGINS` konfigurierbar
- Frontend-Build bekommt `VITE_API_URL`, `VITE_PUBLIC_APP_URL` und `VITE_TEACHER_PIN`
- SQLite wird über ein Docker-Volume persistiert

## Schritt 1: Stack in Portainer anlegen

1. In Portainer anmelden
2. Links **Stacks** öffnen
3. **Add stack** auswählen
4. Einen Stack-Namen vergeben, z. B. `framework-2d-optimization`
5. Die finale `docker-compose.yaml` einfügen oder aus dem Repo laden

## Schritt 2: Environment-Variablen setzen

Im Stack diese Variablen setzen:

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

## Schritt 3: Stack deployen

1. Prüfen, ob Compose-Datei und Variablen korrekt sind
2. **Deploy the stack** ausführen
3. warten, bis beide Container laufen:
   - `opt2d-backend`
   - `opt2d-frontend`

## Schritt 4: Erreichbarkeit prüfen

Im Browser testen:

- Frontend: `http://SERVER-IP:5173`
- Backend-Health: `http://SERVER-IP:8000/health`
- Swagger: `http://SERVER-IP:8000/docs`

Wenn eine Domain verwendet wird, entsprechend die Domain nutzen.

## Schritt 5: Funktionstest nach Deployment

Nach erfolgreichem Deploy einmal kurz komplett testen:

1. Dozentenansicht öffnen
2. Session mit PIN erstellen
3. Teilnehmer-Join testen
4. Evaluierung testen
5. internen Random-Bot testen
6. internen Hill-Climb-Bot testen
7. Reveal testen
8. Session-Ende testen

## Schritt 6: Persistenz prüfen

Die Datenbank wird über das Docker-Volume `opt2d_data` gespeichert.

Kurztest:

1. Session erstellen
2. Stack oder Container neu starten
3. prüfen, ob die Daten weiterhin vorhanden sind

## Schritt 7: Typische Fehler

### Frontend lädt, aber API funktioniert nicht
Wahrscheinliche Ursache:
- `VITE_API_URL` zeigt noch auf `localhost`

### CORS-Fehler im Browser
Wahrscheinliche Ursache:
- `BACKEND_CORS_ORIGINS` ist falsch gesetzt

### Nach Neustart sind Daten weg
Wahrscheinliche Ursache:
- Volume ist nicht korrekt eingebunden

### Session-Erstellung funktioniert nicht
Wahrscheinliche Ursache:
- `VITE_TEACHER_PIN` wurde falsch gesetzt oder das Frontend wurde nicht mit den korrekten Build-Args gebaut

### Interne Bots starten nicht
Wahrscheinliche Ursache:
- administrativer Kontext fehlt
- Session-Code oder Teacher-Kontext ist falsch

## Schritt 8: Updates später einspielen

Bei Änderungen:

1. neuen Repo-Stand oder neue Compose-Datei bereitstellen
2. Stack in Portainer aktualisieren
3. neu deployen
4. denselben kurzen Funktionstest erneut durchführen

## Ergebnis

Wenn Frontend, Backend, Persistenz, Session-Erstellung, Reveal und Bots funktionieren, ist das Projekt auf dem Server betriebsbereit.
