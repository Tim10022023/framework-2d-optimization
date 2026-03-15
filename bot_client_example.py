# Legacy demo script – prefer using student_bot_template.py + blackbox_client.py
import random
import time
import requests
from typing import List, Dict, Tuple

API_URL = "http://localhost:8000"
SESSION_CODE = "HIER_CODE_EINTRAGEN"
BOT_NAME = "Bot-Local-Random"


def get_public_info(code: str) -> dict:
    r = requests.get(f"{API_URL}/sessions/{code}/public", timeout=10)
    r.raise_for_status()
    return r.json()


def join_session(code: str, name: str, is_bot: bool = True) -> str:
    r = requests.post(
        f"{API_URL}/sessions/{code}/join",
        json={"name": name, "is_bot": is_bot},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["participant_id"]


def evaluate(code: str, participant_id: str, x: float, y: float) -> dict:
    r = requests.post(
        f"{API_URL}/sessions/{code}/evaluate",
        json={"participant_id": participant_id, "x": x, "y": y},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def propose_point(
    step: int,
    history: List[Dict[str, float]],
    best_z: float | None,
) -> Tuple[float, float]:
    """
    Hier können Studierende ihren eigenen Algorithmus implementieren.

    Inputs:
    - step: aktueller Schritt (0-basiert)
    - history: Liste bisheriger Evaluierungen, z.B.
      [{"x": ..., "y": ..., "z": ..., "step": ...}, ...]
    - best_z: bestes bisher gesehenes z oder None

    Output:
    - (x, y)
    """

    # Beispiel: rein zufällige Suche
    x = random.uniform(-5, 5)
    y = random.uniform(-5, 5)
    return x, y


def run_bot():
    info = get_public_info(SESSION_CODE)
    print("Public session info:", info)

    participant_id = join_session(SESSION_CODE, BOT_NAME, is_bot=True)
    print("Joined as:", participant_id)

    max_steps = info["max_steps"]
    history: List[Dict[str, float]] = []
    best_z: float | None = None

    for step in range(max_steps):
        x, y = propose_point(step, history, best_z)

        try:
            result = evaluate(SESSION_CODE, participant_id, x, y)
        except requests.HTTPError as e:
            print("Stopped:", e)
            break

        z = float(result["z"])
        history.append(
            {
                "x": float(x),
                "y": float(y),
                "z": z,
                "step": float(result["step"]),
            }
        )

        if best_z is None or z < best_z:
            best_z = z

        print(
            f"step={int(result['step']):02d} "
            f"x={x:.3f} y={y:.3f} z={z:.6f} best_z={best_z:.6f}"
        )

        time.sleep(0.2)


if __name__ == "__main__":
    run_bot()