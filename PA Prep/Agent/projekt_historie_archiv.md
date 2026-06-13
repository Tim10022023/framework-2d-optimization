# Archiv: Projekt-Historie & Kickoff-Notizen

Dieses Dokument archiviert die ursprünglichen Planungsunterlagen und Notizen aus der Startphase des Projekts.

## 1. Ursprüngliche Projektausschreibung (einreichung.txt)
*   **Titel:** Framework zur Optimierung von zweidimensionalen Funktionen.
*   **Konzept:** Docker-basierter Webservice zur Visualisierung und Optimierung. "Blindes" Suchen von Extrempunkten auf einer topographischen Karte/Funktion.
*   **Ziel:** Nutzer entwickeln Strategien; Rangliste vergleicht Teilnehmer.
*   **Erweiterbarkeit:** Spätere Visualisierung von Optimierungsalgorithmen durch Koordinatenübermittlung.
*   **Technik:** Python, Docker, AI-Server MGH.

## 2. Kickoff-Notizen (notes.txt)
*   **Inspiration:** Besuch einer Konferenz; Online-Spielesimulator (Punkte wählen, höchsten Punkt finden).
*   **Ideen für das Backend:** Mathematische Landkarten oder Topographische Karten (Open Street Map Integration - *Hinweis: Fokus lag später primär auf math. Funktionen*).
*   **Anforderungen:** Session-Code, Rangliste (Tie-Breaker: Zeit), Dozenten-Dashboard zur Steuerung.
*   **Dokumentation:** Entwicklerguide soll Teil der 60-80 seitigen Studienarbeit sein.
*   **Gitlab-Referenz:** AI-Lehre Mosbach (Gitlab).

### Zwischenstands-Notizen:
*   Refactoring der Panels (Trennung Dozenten-Erstellung vs. aktive Session).
*   Teilnehmer dürfen die Funktion nicht kennen; sehen nur eigene Punkte und ggf. Bot-Pfade.
*   Bots mit Delay (z.B. 0,5s) zur Entlastung der API und besseren Verfolgbarkeit.
*   Farbliche Markierung der Punkte (Bester Punkt = Grün).
*   Stresstests mit vielen Bots.

## 3. Ursprünglicher Projektplan (plan.txt)
*   **Ziele:** Intuitive Vermittlung, Vergleich Mensch vs. Algorithmus, Einsatz in Live-Vorlesungen.
*   **Rollen:** Dozent (Konfiguration, Start/Ende), Student (Teilnahme via Code).
*   **Spielprinzip:** Auswahl (x, y) -> Rückgabe z = f(x, y). Bewertung nach Klicks/Schritten.
*   **Geplante Algorithmen:** Random Search, Hill Climbing (später erweitert um GA).
*   **Erweiterungsideen:** Heatmaps der Klickverteilung, Export von Session-Daten.

## 4. Abschluss-Agenda (agendatemp.txt)
*   Checkliste vor Abgabe: Full-Stack-Endtest (Docker Compose), Hosting-Block (Portainer), Stresstest-Dokumentation, UI-Polish (Status-Bar, Bot-Bereich), Repo-Aufräumarbeiten.
