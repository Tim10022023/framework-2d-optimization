from __future__ import annotations

import random
import statistics
import threading
import time
from dataclasses import dataclass, field

from blackbox_client import BlackBoxClient


API_URL = "http://localhost:8000"
SESSION_CODE = "3DF6A7"

NUM_BOTS = 50
STEPS_PER_BOT = 20
SLEEP_BETWEEN_STEPS = 0.0


@dataclass
class BotStats:
    name: str
    joined: bool = False
    steps_done: int = 0
    errors: list[str] = field(default_factory=list)
    step_durations_ms: list[float] = field(default_factory=list)


def run_single_bot(bot_idx: int, results: list[BotStats]):
    bot_name = f"StressBot-{bot_idx:02d}"
    stats = BotStats(name=bot_name)
    results.append(stats)

    client = BlackBoxClient(API_URL, SESSION_CODE)

    try:
        info = client.get_public_info()
        client.join(bot_name, is_bot=True)
        stats.joined = True
    except Exception as e:
        stats.errors.append(f"join failed: {e}")
        return

    # bewusst simple Random Search
    for step in range(min(STEPS_PER_BOT, info.max_steps)):
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)

        t0 = time.perf_counter()
        try:
            client.evaluate(x, y)
        except Exception as e:
            stats.errors.append(f"step {step + 1}: {e}")
            break
        t1 = time.perf_counter()

        stats.steps_done += 1
        stats.step_durations_ms.append((t1 - t0) * 1000.0)

        if SLEEP_BETWEEN_STEPS > 0:
            time.sleep(SLEEP_BETWEEN_STEPS)


def main():
    print("=== Stress Test ===")
    print(f"API_URL={API_URL}")
    print(f"SESSION_CODE={SESSION_CODE}")
    print(f"NUM_BOTS={NUM_BOTS}")
    print(f"STEPS_PER_BOT={STEPS_PER_BOT}")
    print(f"SLEEP_BETWEEN_STEPS={SLEEP_BETWEEN_STEPS}")
    print()

    threads: list[threading.Thread] = []
    results: list[BotStats] = []

    t0 = time.perf_counter()

    for i in range(NUM_BOTS):
        th = threading.Thread(target=run_single_bot, args=(i + 1, results))
        threads.append(th)
        th.start()

    for th in threads:
        th.join()

    t1 = time.perf_counter()
    total_runtime = t1 - t0

    joined_count = sum(1 for r in results if r.joined)
    total_steps = sum(r.steps_done for r in results)
    total_errors = sum(len(r.errors) for r in results)

    all_step_times = [ms for r in results for ms in r.step_durations_ms]

    print("=== Ergebnis ===")
    print(f"Bots gestartet: {NUM_BOTS}")
    print(f"Erfolgreich gejoint: {joined_count}")
    print(f"Gesamte Schritte: {total_steps}")
    print(f"Gesamte Fehler: {total_errors}")
    print(f"Gesamtlaufzeit: {total_runtime:.2f}s")

    if all_step_times:
        print(f"Ø Request-Zeit: {statistics.mean(all_step_times):.2f} ms")
        print(f"Median Request-Zeit: {statistics.median(all_step_times):.2f} ms")
        print(f"Max Request-Zeit: {max(all_step_times):.2f} ms")

    print()
    print("=== Details ===")
    for r in sorted(results, key=lambda x: x.name):
        print(
            f"{r.name}: joined={r.joined}, "
            f"steps={r.steps_done}, errors={len(r.errors)}"
        )
        for err in r.errors:
            print(f"  - {err}")


if __name__ == "__main__":
    main()