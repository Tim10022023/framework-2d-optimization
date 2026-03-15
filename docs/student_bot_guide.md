# Student Bot Guide

Diese Kurzanleitung erklärt, wie ein eigener lokaler Python-Bot gegen das Framework **2D Optimization** ausgeführt werden kann.

## Zweck

Der Student-Bot arbeitet gegen die **öffentliche Blackbox-Schnittstelle** einer laufenden Session.  
Er kennt nicht die interne Funktionsdefinition, sondern nutzt nur die erlaubten Session- und Evaluierungsinformationen.

## Relevante Dateien

- `bot/blackbox_client.py`
- `bot/student_bot_template.py`

## Voraussetzungen

Python ist lokal installiert.

Benötigte Bibliothek:

```powershell
pip install requests
```

## Session vorbereiten

Voraussetzung:
- es gibt bereits eine laufende Session
- der Session-Status ist `running`

Den Session-Code trägst du im Bot-Template ein.

## Bot starten

```powershell
python bot\student_bot_template.py
```

## Was der Bot macht

Der Bot sendet Punkte an die laufende Session und erhält dafür die jeweiligen Funktionswerte zurück.  
Die Logik, wie neue Punkte vorgeschlagen werden, implementierst du selbst.

Typischer Einstieg:
- Session-Code eintragen
- `propose_point(...)` anpassen
- Bot starten
- Verlauf im Frontend beobachten

## API / Verbindung

Der Client nutzt die öffentliche Session-/Blackbox-Schnittstelle.

Wichtig:
- lokal ist die API typischerweise unter `http://localhost:8000` erreichbar
- wenn Frontend/Backend anders gehostet sind, muss die API-URL entsprechend angepasst werden

## Hinweise zur Implementierung

Sinnvolle einfache Strategien:
- Random Search
- lokales Ausprobieren um gute Punkte herum
- Hill-Climbing-artige Verfahren
- Restart-Strategien

Wichtig:
- der Bot soll mit der Blackbox arbeiten, nicht mit internem Direktzugriff auf die Zielfunktion
- das Template ist bewusst einfach gehalten und kann erweitert werden

## Typische Fehlerquellen

- falscher Session-Code
- Session noch nicht gestartet oder schon beendet
- API-URL nicht passend gesetzt
- zu aggressive Request-Frequenz bei vielen parallelen Bots

## Einordnung

Der Student-Bot eignet sich gut für:
- Vergleich von Suchstrategien
- didaktische Experimente
- kleine Bot-Wettbewerbe innerhalb einer Lehrveranstaltung
