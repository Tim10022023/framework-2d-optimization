# Student Bot Guide

Diese Kurzanleitung erklärt, wie ein eigener lokaler Python-Bot gegen das Framework **2D Optimization** ausgeführt werden kann.

## Was bereitgestellt werden muss

Für Studierende sollten mindestens diese Dateien bereitgestellt werden:

- `bot/student_bot_template.py`
- `bot/blackbox_client.py`

Zusätzlich werden benötigt:

- die **Backend-API-URL**
- ein **Session-Code**
- lokal installiertes **Python**
- das Paket **requests**

Optional sinnvoll:
- `bot/requirements.txt`

## Installation

```powershell
pip install requests
```

## Zweck

Der Student-Bot arbeitet gegen die **öffentliche Blackbox-Schnittstelle** einer laufenden Session.  
Er kennt die interne Zielfunktion nicht, sondern nutzt nur Join und Evaluate.

## Vorbereitung

Voraussetzung:

- es gibt bereits eine laufende Session
- der Status ist `running`

Im Bot-Template trägst du typischerweise ein:

- API-URL
- Session-Code
- Bot-/Teilnehmername

## Start

```powershell
python bot\student_bot_template.py
```

## Was der Bot macht

Der Bot joint der Session und sendet Punkte `(x, y)` an die öffentliche Evaluierungsschnittstelle.  
Als Antwort erhält er die jeweiligen Funktionswerte zurück.

Die Suchstrategie implementierst du selbst, z. B.:

- Random Search
- lokales Suchen um gute Punkte
- einfache Hill-Climbing-Strategien

## Wichtige Hinweise

- der Bot soll nur die **Blackbox-Schnittstelle** nutzen
- nach Session-Ende sind normale Evaluierungen nicht mehr möglich
- zu aggressive Request-Frequenz kann das System bei vielen parallelen Bots belasten
