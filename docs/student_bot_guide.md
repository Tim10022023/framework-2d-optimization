# Student Bot Guide

## Ziel
Mit einem lokalen Python-Bot an einer laufenden Session teilnehmen und eine eigene Optimierungsstrategie testen.

Der Bot kennt die Funktion **nicht**.  
Er kann nur:
- der Session beitreten
- Punkte `(x, y)` evaluieren
- die erhaltenen `z`-Werte nutzen

## Welche Dateien brauchst du?
Für Studierende reichen diese Dateien:
- `bot/student_bot_template.py`
- `bot/blackbox_client.py`

Zusätzlich:
- Python installiert
- Paket `requests` installiert

Installation:
```powershell
pip install requests
```

## Session-Code eintragen
In `student_bot_template.py`:

```python
SESSION_CODE = "HIER_SESSION_CODE_EINTRAGEN"
```

Optional kann auch der Bot-Name angepasst werden:

```python
BOT_NAME = "Bot-Student-Template"
```

## Bot starten
Im Projektordner:

```powershell
python bot\student_bot_template.py
```

Der Bot:
1. liest öffentliche Session-Infos
2. joint als Bot die Session
3. evaluiert Punkte
4. erscheint im Leaderboard und im Dozenten-Inspector

## Wo der eigene Algorithmus eingebaut wird
In `student_bot_template.py` gibt es die Funktion:

```python
def propose_point(step, history, best_z):
    ...
```

Dort wird die eigene Optimierungslogik implementiert.

### Eingaben
- `step`: aktueller Schritt
- `history`: bisherige Evaluierungen
- `best_z`: bester bisher gefundener Wert

### Ausgabe
Die Funktion muss zurückgeben:

```python
(x, y)
```

## Einfaches Beispiel
```python
def propose_point(step, history, best_z):
    x = random.uniform(-5, 5)
    y = random.uniform(-5, 5)
    return x, y
```

## Typischer Ablauf
1. Session-Code vom Dozenten erhalten
2. `SESSION_CODE` eintragen
3. eigenen Algorithmus in `propose_point(...)` umsetzen
4. Bot starten
5. Verlauf im Leaderboard / Inspector beobachten

## Typische Fehler

### `ModuleNotFoundError: No module named 'requests'`
Lösung:
```powershell
pip install requests
```

### `session not found`
- Session-Code prüfen
- prüfen, ob das Backend läuft
- prüfen, ob die Session noch aktiv ist

### Backend nicht erreichbar
Prüfen:
- läuft das Backend unter `http://localhost:8000`?
- stimmt `API_URL` in der Bot-Datei?

### Klicklimit erreicht
Der Bot stoppt, wenn das Session-Limit erreicht ist.

## Was du Studierenden geben solltest
Für die Nutzung des lokalen Bots genügen:
- dieser Guide
- `bot/student_bot_template.py`
- `bot/blackbox_client.py`

Mehr brauchen Studierende dafür nicht.
