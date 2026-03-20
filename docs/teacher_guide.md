# Teacher Guide

Diese Kurzanleitung richtet sich an Dozierende bzw. die administrierende Rolle im Framework **2D Optimization**.

## Was benötigt wird

- die **Frontend-URL** des Tools
- der **Dozenten-PIN**

Optional hilfreich:
- Backend-Health / Swagger für technische Prüfung

## Ziel

Als Dozent erstellst du Sessions, steuerst den Ablauf und beobachtest Teilnehmer und Bots in der Dozentenansicht.

## Session starten

1. Frontend öffnen
2. in die **Dozentenansicht** wechseln
3. Funktion, Ziel und maximale Klickzahl wählen
4. **Dozenten-PIN** eingeben
5. **Session erstellen**

Danach erhältst du einen **Session-Code**.

## Teilnehmerzugang

Teilnehmende können über:

- den **Session-Code**
- oder den **QR-Code / Beamer Mode**

der Session beitreten.

## Während der Session

In der Dozentenansicht kannst du:

- das **Leaderboard** beobachten
- Teilnehmer und Bots unterscheiden
- Pfade im Inspector ansehen
- per **Slider** Schritt für Schritt durch den Verlauf gehen
- **Random Search** und **Hill Climb** als interne Bots starten
- bei Bedarf **Reveal-Plots** einblenden

## Session-Ende und Reveal

Die Steuerung ist getrennt:

- **Session beenden**: beendet die aktive Teilnehmerphase
- **Reveal anzeigen / ausblenden**: blendet die Analyse in der Dozentenansicht ein oder aus

Wichtig:
- nach Session-Ende können Teilnehmer nicht mehr normal evaluieren
- interne Teacher-Bots können weiterhin gestartet werden
- Reveal ist nur für die Dozentenansicht gedacht

## Hinweise

- Teilnehmende sehen während der Session keine Funktionsdetails
- den **Dozenten-PIN** nicht an Studierende weitergeben
- das Tool ist für Demo-, Lehr- und kleine bis mittlere Gruppenszenarien gedacht
