# Framework 2D Optimization - Projektkontext und Architektur

Dieses Dokument bietet einen umfassenden und detaillierten Überblick über das Projekt "Framework 2D Optimization". Es dient als zentrale theoretische und technische Referenz für die Projektarbeit und beschreibt die vollständige Projektstruktur von der ursprünglichen Idee über die fachliche Architektur bis hin zur konkreten Implementierung und Skalierung.

---

## 1. Projektidee und pädagogisches Konzept

Das Framework entstand aus der Motivation heraus, die oft sehr abstrakten theoretischen Konzepte der mathematischen Optimierung und der evolutionären Algorithmen (Bio-inspired AI) für Studierende greifbarer zu machen. 

### Das Problem
In Vorlesungen (wie *Evolutionary Computing*) werden Optimierungsverfahren oft als "Black Boxes" betrachtet. Studierende verstehen die Dynamik zwischen *Exploration* (weitläufige Suche im Suchraum) und *Exploitation* (lokale Ausbeutung vielversprechender Bereiche) in der Theorie, können jedoch nur schwer eine echte Intuition dafür entwickeln.

### Die Lösung: Ein interaktives Kompetenz-Spiel
Das Projekt löst dieses Problem durch eine webbasierte, interaktive Black-Box-Simulation, die in zwei Phasen unterteilt ist:
1. **Phase A (Manuelle Intuitionsbildung):** Studierende erhalten ein 2D-Koordinatensystem in einer Weboberfläche, ohne die zugrundeliegende topographische Funktion (z.B. Sphere, Rosenbrock) zu kennen. Durch das Klicken auf Punkte (X, Y) erhalten sie die zugehörige Höhe (Z-Wert). Ziel ist es, den globalen Hoch-/Tiefpunkt zu finden. Die Studierenden entwickeln dabei intuitiv Strategien (z.B. zuerst grobes Rastern des Suchraums, gefolgt von einer lokalen Suche).
2. **Phase B (Automatisierung):** Im Anschluss überführen die Studierenden ihre entwickelte Intuition in Python-Code. Sie schreiben Bots, die mittels Suchalgorithmen automatisiert gegen die Schnittstelle optimieren. 

---

## 2. Eingereichte Themenstellung

Die formelle Zielsetzung der Studienarbeit lautete wie folgt:

> **Titel:** Framework zur Optimierung von zweidimensionalen Funktionen
> 
> **Kurzbeschreibung:** In dieser Studienarbeit soll ein docker-basierter Webservice entwickelt werden, der die Visualisierung und Optimierung von zweidimensionalen Funktionen erlaubt. Dabei soll in einer Weboberfläche ein 2D-Koordinatensystem dargestellt werden. Hinterlegt, jedoch für den Nutzer nicht sichtbar, ist eine zweidimensionale Funktion oder topographische Karte. Nutzer haben dann die Aufgabe blind auf diesem Koordinatensystem Hoch-/Tiefpunkte zu finden. Hierfür sollen sie beliebige Punkte auswählen und erhalten eine Information über dessen Höhe. Dadurch sollen Nutzer eine Strategie entwickeln, wie Funktionen optimiert werden können.
>
> Für den Organisator dieser Optimierungsaufgabe soll es möglich sein die Funktion bzw. topographische Karte zu definieren, eine Optimierungssession zu starten und zu beenden. Die Nutzer können, während sie Punkte setzen um den Hochpunkt zu finden, eine globale Rangliste mit den anderen Teilnehmern dieser Session sehen.
> Die Architektur der Anwendung soll so gestaltet sein, dass später auch Optimierungsalgorithmen durch Übermittlung von Punkt-Koordinaten visualisiert werden können. Als Programmiersprache soll Python genutzt werden. Die Anwendung soll mittels Docker [...] aufgesetzt werden.

---

## 3. Architektur und Technische Umsetzung

Das System ist als hochperformante, asynchrone Microservice-Architektur konzipiert, die auch unter Last (Simulation von hunderten automatisierten Bots) stabile Echtzeit-Aktualisierungen für Dozenten und Studierende garantiert.

### 3.1 Backend (Python / FastAPI)
*   **Technologie-Stack:** Python 3.14+, FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL, Redis.
*   **Asynchrones Design:** Das gesamte Backend arbeitet nicht blockierend. Durch die Nutzung von `asyncpg` und asynchronen Datenbank-Sessions können hunderte Requests pro Sekunde ohne Thread-Locking verarbeitet werden. (Dies ist eine Weiterentwicklung aus *Phase 1*, in der das System noch synchron mit SQLite lief und unter Last blockierte).
*   **Redis Caching-Layer:** Um die PostgreSQL-Datenbank zu entlasten, werden hochfrequente Daten zwischengespeichert:
    *   1s TTL (Time-To-Live) für das Live-Leaderboard und Teilnehmerzahlen.
    *   5s TTL für rechenintensive Session-Snapshots.
    *   Gezielte Invalidierung bei Statusänderungen oder neuen Punkt-Eingaben.

### 3.2 Frontend (React / TypeScript)
*   **Technologie-Stack:** React, TypeScript, Vite, Plotly.js.
*   **State Management:** Um die Komplexität gering zu halten, wird auf globale State-Container wie Redux verzichtet; stattdessen kommen standardisierte React-Hooks (`useState`, `useMemo`, `useEffect`) zum Einsatz.
*   **Visualisierung:** Komplexe Datenpfade und Zielfunktionen werden über Plotly.js dargestellt:
    *   *2D-Heatmaps* (Contour Plots) für die Suche.
    *   *3D-Surface Plots* für den abschließenden "Reveal"-Modus (wenn der Dozent die Funktion aufdeckt).
*   **Hybrides Kommunikationsmodell:** Das Frontend nutzt primär WebSockets für serverseitige Events (via Redis Pub/Sub), um sofort auf Ereignisse wie `click_added` oder `session_ended` zu reagieren. Für Batch-Daten oder als Fallback wird klassisches REST-Polling verwendet.

---

## 4. Innovation: Lokale Evaluierung & Anti-Cheat Mechanismen

Eine der größten architektonischen Herausforderungen war der Übergang zur automatisierten Nutzung durch Bots (Phase 2). Ein einziger lokaler Bot kann theoretisch tausende Requests pro Sekunde generieren. Bei 50 Studierenden würde das Netzwerk durch simples REST-Polling kollabieren.

### Das RPN / Batching Paradigma
Um dieses Problem zu lösen, wurde die Rechenlast vom Server auf die Clients verlagert, **ohne** dabei die zu optimierende Funktion ("Black-Box") offenzulegen:
1.  **Obfuskation mittels RPN:** Der Server übersetzt die komplexe mathematische Topographie-Funktion in eine verschleierte **Reverse Polish Notation** (z.B. `x 3.7 - 2 ^ y 2.1 + 2 ^ +`).
2.  **Lokaler Interpreter:** Die Python-Client-Library (`blackbox_client.py`) für die Studierenden beinhaltet einen extrem leichtgewichtigen Interpreter, der diesen RPN-Code parst.
3.  **Zero-Latency Evaluierung:** Bots können Millionen von Punkten in Millisekunden berechnen, ohne einen einzigen Netzwerk-Request abzufeuern.
4.  **Batch-Syncing:** Am Ende eines Bot-Laufs oder periodisch sendet der Bot gesammelt eine große Trajektorie (Liste von Tausenden Punkten) über den Endpunkt `POST /sync_trajectory` an den Server.

### Anti-Cheat und Frontend-Schutz
*   **Server-Side Verification (Random Sampling):** Da die Bots die Z-Werte theoretisch fälschen könnten (da sie lokal rechnen), rechnet das Backend beim Empfang von Batch-Trajektorien stichprobenartig Kontrollpunkte nach. Stimmen die übermittelten Ergebnisse nicht mit der wahren Formel überein, wird der Teilnehmer disqualifiziert.
*   **Server-Side Downsampling:** Um den Web-Browser des Dozenten bei der Live-Visualisierung nicht mit Millionen von Punkten zum Absturz zu bringen, aggregiert und reduziert der Server die Datenpunkte in repräsentative Stichproben, bevor sie über den WebSocket ans Frontend geschickt werden.

---

## 5. Ordner- und Projektstruktur

Das Repository spiegelt die Microservice-Architektur klar wider:

```text
framework-2d-optimization/
├── backend/                # Das Python FastAPI Backend
│   ├── app/
│   │   ├── api/            # Controller: REST-Routen & WebSocket-Handler
│   │   ├── core/           # Business Logic: Evaluators, Caching, RPN-Generatoren
│   │   ├── db/             # ORM-Modelle für PostgreSQL und Datenbank-Setup
│   │   └── static/         # Statische Ressourcen (z.B. Bilder der aufgedeckten Funktionen)
│   ├── tests/              # Umfassende Pytest-Suite für Unit- und Integrationstests
│   └── requirements.txt    # Backend Abhängigkeiten
├── frontend/               # Das React / TypeScript UI
│   ├── src/
│   │   ├── components/     # Modulare UI-Komponenten (Panels, Inspector, 3D Canvas)
│   │   ├── api.ts          # API-Client und WebSocket-Management-Logik
│   │   └── types.ts        # Zentrale Typdefinitionen für Backend-Frontend Synchronität
│   └── package.json        # Frontend Abhängigkeiten und Scripts
├── bot/                    # Client-Bibliotheken und Entwicklungs-Tools
│   ├── blackbox_client.py  # Der offizielle Client inklusive RPN-Interpreter
│   ├── student_bot_template.py # Vorlage für die Algorithmen der Studenten
│   ├── genetic_algorithm_template.py # Weiterführendes Template (Vorlesungsbezug)
│   └── stress_test.py      # Simulator zur Erzeugung massiver Last (200+ parallele Bots)
├── docs/                   # Vertiefende Markdown-Dokumentationen (Guides, Architektur)
├── scripts/                # CI/CD, Build-Scripte und Health-Checks (`build.py`, `health_check.py`)
├── PA Prep/                # Verzeichnis für Entwürfe, Gliederungen und Exzerpte für die Projektarbeit
└── docker-compose.yaml     # Orchestrierung der Services (API, DB, Redis, UI)
```

---

## 6. Benutzeroberfläche und Funktionen (UI)

Die Anwendung bietet rollenspezifische Dashboards:

1.  **Teacher Dashboard:** Erlaubt das Erstellen von Sessions, die Auswahl der versteckten Zielfunktion und die Live-Überwachung.
2.  **Teacher Inspector (Live-Map):** Ein spezieller Modus für Dozenten. Mit einem Slider können die Suchpfade einzelner Studierender Schritt-für-Schritt rekonstruiert werden, um algorithmische Tendenzen oder Fehler mit der Klasse zu besprechen.
3.  **Student / Participant Panel:** Die interaktive Klick-Oberfläche zur manuellen Suche.
4.  **Global Leaderboard:** Eine Live-Tabelle, sortiert nach dem besten gefundenen Optimum und (als Tie-Breaker) der geringsten Anzahl an benötigten Schritten.
5.  **Reveal Mode:** Die dramaturgische Auflösung am Ende der Session: Die Heatmap weicht einer 3D-Ansicht (Plotly.js Surface Plot), auf der die echten Konturen der Topographie sichtbar werden und die Versuchspunkte farbig markiert übereinanderliegen.

*(Hinweis: Aussagekräftige Screenshots der jeweiligen Dashboards, des 3D Reveal-Modus und des Path-Inspectors werden im finalen Dokument hier eingefügt.)*

---

## 7. Qualitätssicherung und Betrieb

*   **Docker Orchestrierung:** Der gesamte Stack (Postgres, Redis, FastAPI, Vite) lässt sich mit einem einzigen Kommando (`docker compose up --build`) plattformunabhängig hochfahren.
*   **CI/CD Pipeline (`scripts/build.py`):** Ein Python-Skript orchestriert die Qualitätssicherung lokal vor jedem Commit: Es führt Pytest aus, linted das React-Frontend, prüft Types und testet den Production-Build.
*   **Health Checks (`scripts/health_check.py`):** Prüft die Runtime-Gesundheit, insbesondere die Erreichbarkeit und Synchronität zwischen Redis-Broker und PostgreSQL-Datenbank.
*   **Stress Testing (`bot/stress_test.py`):** Ein dediziertes Skript erzeugt massive Parallel-Last (200 simulierte Bots), um die asynchrone Skalierbarkeit unter realen Bedingungen zu demonstrieren.