# Student Bot Guide (Phase 2 - Scalable Optimization)

Diese Anleitung erklärt, wie du einen leistungsstarken Python-Bot entwickelst, der bis zu **500.000 Evaluationen** pro Session durchführen kann.

## Was bereitgestellt werden muss

Für Studierende sollten mindestens diese Dateien bereitgestellt werden:

- `bot/blackbox_client.py` (Der API-Client mit RPN-Support)
- `bot/student_bot_template.py` (Einfaches Beispiel für RPN-Nutzung)
- `bot/genetic_algorithm_template.py` (Fortgeschrittenes Beispiel: Genetischer Algorithmus)
- `bot/requirements.txt` (Abhängigkeiten)

## Installation

```powershell
pip install -r bot/requirements.txt
```

## Funktionsweise (Phase 2)

Im Gegensatz zur einfachen Phase 1 (einzelne HTTP-Requests pro Punkt) nutzt Phase 2 ein **Hybrid-Modell**:

1.  **Join:** Dein Bot tritt der Session bei.
2.  **Bytecode-Download:** Der Bot erhält eine verschleierte mathematische Formel (RPN-Bytecode).
3.  **Lokale Evaluation:** Mit `client.evaluate_local(x, y)` berechnet dein Bot den Funktionswert `z` direkt auf deinem Computer (extrem schnell, kein Netzwerk-Delay).
4.  **Batch-Sync:** Dein Bot sammelt seine Suchschritte (Trajektorie) und schickt sie in Paketen (z. B. alle 25.000 Schritte) mit `client.sync_trajectory(points)` an den Server.

## Strategien

Dank der lokalen Evaluation sind nun komplexe Algorithmen möglich:

- **Genetische Algorithmen (GA):** Populationen, Selektion, Mutation und Crossover.
- **Partikelschwarmoptimierung (PSO):** Schwärme, die den besten Punkt suchen.
- **Differential Evolution:** Fortgeschrittene evolutionäre Suche.

## Wichtige API-Funktionen (`blackbox_client.py`)

- `client.join_session(name, is_bot=True)`: Tritt bei und lädt automatisch den Bytecode.
- `client.evaluate_local(x, y)`: Berechnet `z` sofort lokal.
- `client.sync_trajectory(points)`: Synchronisiert eine Liste von `(x, y, z, step)`-Tupeln mit dem Server.
- `client.get_best_so_far()`: Gibt den bisher besten gefundenen Punkt deines Bots zurück.

## Performance-Tipp

Das Backend speichert serverseitig nur eine repräsentative Stichprobe deiner Trajektorie (Downsampling), um die Datenbank zu schonen. Dein gesamter Fortschritt (Klick-Counter und Bestwert) wird jedoch exakt getrackt.

**Viel Erfolg bei der Suche nach dem globalen Minimum!**
