# Teacher Guide

Diese Kurzanleitung richtet sich an Dozierende bzw. die administrierende Rolle im Framework **2D Optimization**.

## Was bereitgestellt werden muss

Für den Dozentenbetrieb werden benötigt:

- Zugriff auf die laufende Frontend-URL
- der **Dozenten-PIN** zum Erstellen von Sessions

Optional hilfreich:
- Zugriff auf die Backend-URL / Swagger-Doku für technische Prüfung

## Ziel

Als Dozent erstellst und steuerst du Sessions, beobachtest Teilnehmer und Bots und kannst Reveal/Analyse in der Dozentenansicht einblenden.

## Session starten

1. Frontend öffnen
2. in die **Dozentenansicht** wechseln
3. Funktion auswählen
4. Ziel und maximale Klickzahl festlegen
5. **Dozenten-PIN** eingeben
6. **Session erstellen**

Nach dem Start wird ein Session-Code erzeugt.

## Teilnehmerzugang

Teilnehmende können über:
- den Session-Code oder
- den QR-Code / Beamer Mode

einer Session beitreten.

## Während der Session

In der Dozentenansicht kannst du:

- Leaderboard beobachten
- Teilnehmer und Bots unterscheiden
- Teilnehmerpfade inspizieren
- Bot-Pfade inspizieren
- Schritt-für-Schritt-Debugging per Slider verwenden
- Reveal-Plots bei Bedarf einblenden

Zusätzlich stehen zur Verfügung:

- QR / Beamer Mode
- tab-lokale Rollen-/Sessionzustände
- Bot-Markierung im UI

## Reveal und Session-Ende

Die Session-Steuerung ist getrennt:

- **Session beenden**: beendet die aktive Teilnehmerphase
- **Reveal anzeigen / ausblenden**: blendet die Analyse-/Reveal-Daten in der Dozentenansicht ein oder aus

Hinweis:
- Nach Session-Ende können Teilnehmer nicht mehr normal evaluieren
- interne Teacher-Bots können weiterhin gestartet werden
- Reveal ist eine Dozentenansicht und kann separat ein- oder ausgeblendet werden

## Bots

Interne Vergleichsbots im Dozenten-UI:

- Random Search
- Hill Climb

Diese sind Dozentenfunktionen und laufen über den administrativen Kontext.

## Hinweise

- Teilnehmer sehen während der Session keine Funktionsdetails
- der Dozenten-PIN sollte nur an die administrierende Person gegeben werden
- das Tool ist vor allem für Demo-, Lehr- und kleinere bis mittlere Gruppenszenarien gedacht
