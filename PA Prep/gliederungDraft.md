# Gliederungsentwurf: Projektarbeit (Bachelor-Niveau)

**Thema:** Entwicklung eines skalierbaren Frameworks zur interaktiven Vermittlung von 2D-Optimierungsalgorithmen durch Black-Box-Simulation
**Umfang:** Ziel ca. 40-50 Seiten
**Fokus:** Skalierbarkeit, lokale Evaluierung (RPN), pädagogisches Konzept

---

## 1. Einleitung
### 1.1 Motivation und Relevanz des Themas
*   Bedeutung von Optimierungsalgorithmen in der modernen Informatik.
*   Herausforderungen in der Lehre (Abstraktion vs. Intuition).
### 1.2 Problemstellung und Zielsetzung
*   Defizite herkömmlicher Lehrmethoden.
*   Anforderungskatalog an ein interaktives Framework.
### 1.3 Aufbau der Arbeit

## 2. Theoretische Grundlagen
### 2.1 Mathematische Optimierung
*   Grundlagen der 2D-Optimierung (Extrema, Sattelpunkte).
*   Benchmark-Funktionen (Sphere, Rosenbrock, Rastrigin).
### 2.2 Evolutionäre Algorithmen
*   Prinzipien (Selektion, Mutation, Rekombination).
*   Exploration vs. Exploitation.
### 2.3 Web-Technologien und Skalierbarkeit
*   Synchrones vs. Asynchrones I/O (FastAPI, Python Async).
*   Caching-Strategien und In-Memory-Datenbanken (Redis).
*   Real-Time Kommunikation via WebSockets.

## 3. Analyse und Anforderungsdefinition
### 3.1 Ist-Analyse bestehender Tools
*   Vergleich mit Standard-Simulatoren.
### 3.2 Fachliche Anforderungen
*   Multi-User Fähigkeit (Dozent vs. Student).
*   Black-Box Prinzip zur Wahrung der Suchintegrität.
### 3.3 Technische Anforderungen
*   Unterstützung für bis zu 60-100 parallele Teilnehmer.
*   Minimierung der Netzwerklatenz für automatisierte Bots.

## 4. Konzeption und Architektur
### 4.1 Systemarchitektur (High-Level)
*   Microservice-ähnlicher Aufbau mit Docker-Orchestrierung.
### 4.2 Datenmodell und Persistenz
*   Migration von SQLite zu PostgreSQL für Concurrent Writes.
### 4.3 Skalierungskonzept
*   Redis-Caching-Layer für hochfrequente Polling-Endpunkte.
*   WebSocket-Broadcasting via Redis Pub/Sub.
### 4.4 Innovation: Lokale Black-Box-Evaluierung
*   Konzept der Reverse Polish Notation (RPN) zur Funktionsverschleierung.
*   Entkopplung von Rechenlast und Netzwerktraffic.

## 5. Implementierung
### 5.1 Backend-Entwicklung (FastAPI)
*   Asynchrone Datenbankanbindung.
*   Implementierung des RPN-Generators.
### 5.2 Frontend-Entwicklung (React & TypeScript)
*   Echtzeit-Visualisierung mit Plotly.js.
*   Dozenten-Dashboard: Path Inspector und Reveal-Logik.
### 5.3 Bot-Framework und Client-Bibliothek
*   Entwicklung des RPN-Interpreters im BlackBox-Client.
*   Anti-Cheat Mechanismen (Server-side Verification).

## 6. Evaluation und Qualitätssicherung
### 6.1 Performance-Analyse und Stresstests
*   Vergleich der Latenz: Phase 1 (Sync) vs. Phase 2 (RPN/Batch).
*   Auswertung der Stresstests mit 200+ Bots.
### 6.2 Pädagogische Evaluation (Reflexion)
*   Einsatz in der Vorlesung: Beobachtungen zum Lernverhalten.
### 6.3 Code-Qualität und Maintenance
*   Automatisierung via Build-Skripte und Health Checks.

## 7. Zusammenfassung und Ausblick
### 7.1 Zusammenfassung der Ergebnisse
### 7.2 Kritische Würdigung
### 7.3 Zukünftige Erweiterungsmöglichkeiten (z.B. Multi-Dimensionale Optimierung)

---

## Anhang
*   Abbildungsverzeichnis
*   Tabellenverzeichnis
*   Quellcode-Auszüge (RPN-Interpreter, WebSocket-Manager)
*   Literaturverzeichnis
