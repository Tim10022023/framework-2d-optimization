# Student Bot Guide

Diese Kurzanleitung erklärt, wie ein eigener lokaler Python-Bot gegen das Framework **2D Optimization** ausgeführt werden kann.

## Was bereitgestellt werden muss

Für Studierende sollten mindestens diese Dateien bereitgestellt werden:

- `bot/student_bot_template.py`
- `bot/blackbox_client.py`

Zusätzlich nötig:

- eine laufende Session
- der **Session-Code**
- die **API-URL** des Backends
- lokal installiertes Python
- Python-Paket `requests`

Optional sinnvoll:
- `bot/requirements.txt` mit `requests`

## Zweck

Der Student-Bot arbeitet gegen die **öffentliche Blackbox-Schnittstelle** einer laufenden Session.  
Er kennt nicht die interne Funktionsdefinition, sondern nutzt nur die erlaubten Session- und Evaluierungsinformationen.

## Voraussetzungen

Benötigte Bibliothek:

```powershell
pip install requests
```

## Session vorbereiten

Voraussetzung:

- es gibt bereits eine laufende Session
- der Session-Status ist `running`

Im Bot-Template werden typischerweise eingetragen:

- API-URL
- Session-Code
- Bot-/Teilnehmername

## Bot starten

```powershell
python bot\student_bot_template.py
```

## Was der Bot macht

Der Bot joint normal als Teilnehmer/Bot und sendet Punkte an die laufende Session.  
Für jeden Punkt erhält er den zugehörigen Funktionswert zurück.

Die Suchstrategie implementierst du selbst.

Typischer Einstieg:

- Session-Code eintragen
- API-URL prüfen
- `propose_point(...)` anpassen
- Bot starten
- Verlauf im Frontend beobachten

## Wichtige Hinweise

- der Bot soll mit der **Blackbox-Schnittstelle** arbeiten, nicht mit internem Direktzugriff auf die Zielfunktion
- nach Session-Ende sind normale Evaluierungen nicht mehr möglich
- zu aggressive Request-Frequenz kann das System bei vielen parallelen Bots belasten
