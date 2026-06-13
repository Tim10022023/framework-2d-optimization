# Gliederungsentwurf: Projektarbeit

**Thema:** Entwicklung eines skalierbaren Frameworks zur interaktiven Vermittlung von 2D-Optimierungsalgorithmen durch Black-Box-Simulation
**Umfang:** Ziel ca. 40-50 Seiten
**Fokus:** Skalierbarkeit (Redis/PostgreSQL), lokale Evaluierung (RPN), Gamification & pädagogischer Transfer

---

## 1. Einleitung

### 1.1 Motivation und Relevanz des Themas
* Bedeutung von Optimierungsalgorithmen in der modernen Informatik (Bsp. wie Routingprobleme etc.)
* Herausforderungen in der Lehre (Abstraktion vs. Intuition).
* Begriffseinordnung: Evolutionäre Algorithmen im Kontext der Künstlichen Intelligenz (Bio-inspired AI).

### 1.2 Problemstellung und Zielsetzung
* Defizite herkömmlicher Lehrmethoden.
* Anforderungskatalog an ein interaktives Framework.
* Formulierung der Hypothese: Ein interaktives Black-Box-Framework vereinfacht das Verständnis und die Intuition für abstrakte Optimierungsalgorithmen.

### 1.3 Aufbau der Arbeit

## 2. Theoretische Grundlagen

### 2.1 Mathematische Optimierung
* Grundlagen der 2D-Optimierung (Extrema, Sattelpunkte).
* Benchmark-Funktionen (Sphere, Rosenbrock, Rastrigin).

### 2.2 Evolutionäre Algorithmen
* Prinzipien (Selektion, Mutation, Rekombination).
* Exploration vs. Exploitation.
* Bezug zur Vorlesung Evolutionäry Computing.

### 2.3 Web-Technologien und Skalierbarkeit
* Synchrones vs. Asynchrones I/O (FastAPI, Python Async).
* Caching-Strategien und In-Memory-Datenbanken (Redis).
* Real-Time Kommunikation via WebSockets.

## 3. Analyse und Anforderungsdefinition

### 3.1 Ist-Analyse bestehender Tools
* Vergleich mit Standard-Simulatoren und Lehrmitteln.

### 3.2 Fachliche Anforderungen
* Multi-User Fähigkeit (Dozent vs. Student).
* Black-Box Prinzip und Wahrung der Suchintegrität (Geheimhaltung der Zielfunktion).

### 3.3 Technische Anforderungen
* Unterstützung für 100+ parallele Teilnehmer.
* Minimierung der Netzwerklatenz für automatisierte Bots.

## 4. Konzeption und Architektur

### 4.1 Systemarchitektur (High-Level)
* Microservice-orientierter Aufbau mit Docker-Orchestrierung.

### 4.2 Datenmodell und Persistenz
* Migration von SQLite zu PostgreSQL zur Bewältigung von Concurrent Writes.

### 4.3 Skalierung und hybride Kommunikation
* Redis-Caching-Layer für hochfrequente Polling-Endpunkte.
* Kombiniertes Kommunikationsmodell: WebSockets für Echtzeit-Events und REST für Batch-Datenübertragung.

### 4.4 Innovation: Lokale Black-Box-Evaluierung
* Konzept der Reverse Polish Notation (RPN) zur Funktionsverschleierung.
* Strategische Entkopplung von Rechenlast und Netzwerktraffic.

## 5. Implementierung

### 5.1 Backend-Entwicklung (FastAPI)
* Asynchrone Datenbankanbindung und Ressourcen-Management.
* Implementierung des RPN-Generators für dynamische Funktionen.

### 5.2 Frontend-Entwicklung (React & TypeScript)
* Echtzeit-Visualisierung komplexer Datenpfade mit Plotly.js.
* Dozenten-Dashboard: Path Inspector und interaktive Reveal-Logik.

### 5.3 Bot-Framework und Client-Bibliothek
* Entwicklung des RPN-Interpreters im BlackBox-Client.
* Anti-Cheat Mechanismen: Server-side Verification mittels Random Sampling.

## 6. Evaluation und Qualitätssicherung

### 6.1 Performance-Analyse und Benchmarking
* Vergleich der Architektursprünge: Phase 1 (Sync) vs. Phase 2 (RPN/Batch).
* Auswertung der Stresstests mit 200+ simulierten Bots.
* Performance im Live-Betrieb

### 6.2 Pädagogische Evaluation und Reflexion
* Methodik: Konzeption und Durchführung einer Studenten-Umfrage im Rahmen der Vorlesung.
* Auswertung des Feedbacks und Reflexion eigener Beobachtungen zum Lernverhalten.
* Validierung der aufgestellten Hypothese anhand der Evaluationsergebnisse.
* Analyse des Usability-Feedbacks.

### 6.3 Code-Qualität und Maintenance
* Automatisierung via Build-Skripte und automatisierte Health Checks.

## 7. Zusammenfassung und Ausblick

### 7.1 Zusammenfassung der Ergebnisse
* Beantwortung der Problemstellung und abschließendes Fazit zur Hypothese.

### 7.2 Kritische Reflexion

### 7.3 Zukünftige Erweiterungsmöglichkeiten (z.B. Multi-Dimensionale Optimierung)
