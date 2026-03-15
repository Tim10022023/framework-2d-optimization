from __future__ import annotations

import random
import time
from typing import TypedDict

from blackbox_client import BlackBoxClient


API_URL = "http://localhost:8000"
SESSION_CODE = "2B4910"
BOT_NAME = "Bot-Student-Template-NAME"


class HistoryItem(TypedDict):
    x: float
    y: float
    z: float
    step: int


def propose_point(step: int, history: list[HistoryItem], best_z: float | None) -> tuple[float, float]:
    """
    Hier implementieren Studierende ihren eigenen Algorithmus.

    Inputs:
    - step: aktueller Schritt (0-basiert)
    - history: bisherige Evaluierungen
    - best_z: bestes bisher gesehenes z (oder None)

    Output:
    - (x, y)
    """

    # Beispiel: einfache Random Search
    x = random.uniform(-5, 5)
    y = random.uniform(-5, 5)
    return x, y


def main():
    client = BlackBoxClient(API_URL, SESSION_CODE)

    info = client.get_public_info()
    print("Public session info:", info)

    if info.status != "running":
        print(f"Session ist nicht aktiv (status={info.status}). Bot wird nicht gestartet.")
        return

    participant_id = client.join(BOT_NAME, is_bot=True)
    print("Joined as:", participant_id)

    history: list[HistoryItem] = []
    best_z: float | None = None

    for step in range(info.max_steps):
        x, y = propose_point(step, history, best_z)

        try:
            result = client.evaluate(x, y)
        except Exception as e:
            print(f"Bot gestoppt in Schritt {step + 1}: {e}")
            break

        z = float(result["z"])
        history.append(
            {
                "x": float(x),
                "y": float(y),
                "z": z,
                "step": int(result["step"]),
            }
        )

        if best_z is None or z < best_z:
            best_z = z

        print(
            f"step={result['step']:02d} "
            f"x={x:.3f} y={y:.3f} z={z:.6f} best_z={best_z:.6f}"
        )

        time.sleep(0.2)


if __name__ == "__main__":
    main()