# Teacher Guide

Diese Kurzanleitung richtet sich an Dozierende bzw. die administrierende Rolle im Framework **2D Optimization**.

## Ziel

Als Dozent verwaltest du eine Session, beobachtest Teilnehmer und Bots und führst nach Session-Ende den Reveal durch.

## Session starten

1. Frontend öffnen
2. in die Dozentenansicht wechseln
3. Funktions-ID auswählen
4. Session konfigurieren
5. Session erstellen

Typische Konfigurationspunkte:
- Name / Bezeichnung
- verwendete Funktion
- maximale Schrittzahl
- optionale Bot-Nutzung

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

Je nach UI-Stand stehen zusätzlich zur Verfügung:
- QR / Beamer Mode
- tab-lokale Rollen-/Sessionzustände
- optionale Bot-Markierung
- Heatmap-Overlay im Inspector als Bonus

## Leaderboard und Verlauf

Das Leaderboard aktualisiert sich während der laufenden Session.  
Der Inspector erlaubt es, einzelne Teilnehmer oder Bots auszuwählen und deren Verlauf schrittweise nachzuvollziehen.

Damit lassen sich unter anderem analysieren:
- welche Punkte ausprobiert wurden
- wie sich der bestgefundene Wert entwickelt hat
- wie sich Mensch und Bot unterscheiden

## Session beenden

Wenn die aktive Phase abgeschlossen ist:

1. Session beenden
2. Reveal laden bzw. anzeigen
3. Export prüfen

Nach dem Session-Ende können Reveal und Export nach Refresh im Dozenten-UI erneut geladen werden.

## Reveal

Nach dem Ende der Session stehen zusätzliche Informationen zur Verfügung, zum Beispiel:
- Funktionsbild / Plot
- Exportdaten
- detailliertere Analyse des Suchverlaufs

Die Heatmap im Inspector ist dabei als Bonusfunktion zu verstehen.

## Hinweise

- Teilnehmer sehen während der Session keine Funktionsdetails
- Bots sind im UI markiert
- das Tool ist vor allem für Demo-, Lehr- und kleinere bis mittlere Gruppenszenarien gedacht
