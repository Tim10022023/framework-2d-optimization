from __future__ import annotations

import random
import time
from typing import TypedDict, Any

from blackbox_client import BlackBoxClient


# --- Konfiguration ---
API_URL = "http://localhost:8000/"
SESSION_CODE = "91198B"  # Bitte durch aktuellen Code ersetzen
BOT_NAME = f"Bot-Student-{random.randint(100, 999)}"


class HistoryItem(TypedDict):
    x: float
    y: float
    z: float
    step: int


class LocalSearchBot:
    """
    Beispiel-Bot, der die neue 'Local Evaluation' (Phase 2) nutzt.
    Anstatt für jeden Punkt den Server anzufragen, wird die mathematische
    Funktion lokal berechnet. Nur die Ergebnisse werden am Ende (oder periodisch)
    per 'sync_trajectory' an den Server übertragen.
    """
    def __init__(self, api_url: str, session_code: str, bot_name: str):
        self.client = BlackBoxClient(api_url, session_code)
        self.bot_name = bot_name
        self.trajectory = []
        self.best_z = None
        self.best_x = None
        self.best_y = None

    def run(self, max_local_steps: int = 100):
        # 1. Session beitreten & Blackbox-Payload erhalten
        print(f"Trete Session {self.client.session_code} bei...")
        self.client.join(self.bot_name, is_bot=True)
        
        # 2. Session-Limit abfragen
        info = self.client.get_public_info()
        print(f"Session-Limit: {info.max_steps} Schritte")
        
        # 3. Lokale Optimierung (Hill Climbing)
        # Wir starten an einem zufälligen Punkt
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        
        step_size = 0.1
        total_steps = 0
        
        print(f"Starte lokale Optimierung (Limit: {min(max_local_steps, info.max_steps)} Schritte)...")
        
        for i in range(min(max_local_steps, info.max_steps)):
            # Lokale Evaluierung (Kostet 0ms Latenz, 0 Network Traffic)
            z = self.client.evaluate_local(x, y)
            total_steps += 1
            
            self.trajectory.append({"x": x, "y": y, "z": z})
            
            if self.best_z is None or z < self.best_z:
                self.best_z = z
                self.best_x, self.best_y = x, y
            
            # Einfacher Hill Climb: Probiere Nachbarn
            found_better = False
            # Wir prüfen 4 Nachbarn -> Jeder zählt als lokaler Schritt
            for dx, dy in [(step_size, 0), (-step_size, 0), (0, step_size), (0, -step_size)]:
                if total_steps >= info.max_steps:
                    break
                
                nx, ny = x + dx, y + dy
                nz = self.client.evaluate_local(nx, ny)
                total_steps += 1
                
                if nz < z:
                    x, y = nx, ny
                    found_better = True
                    # Wir fügen den verbesserten Punkt auch zur Trajektorie hinzu
                    self.trajectory.append({"x": nx, "y": ny, "z": nz})
                    break
            
            if not found_better:
                step_size *= 0.0001
                if step_size < 1e-5:
                    break

            # Periodisches Syncing (optional, z.B. alle 50 Schritte)
            if len(self.trajectory) >= 50:
                print(f"Syncing {len(self.trajectory)} Punkte zum Server...")
                self.client.sync_trajectory(self.trajectory)
                self.trajectory = []
            
            if total_steps >= info.max_steps:
                print("Maximales Session-Limit erreicht!")
                break

        # 4. Finaler Sync
        if self.trajectory:
            print(f"Finaler Sync von {len(self.trajectory)} Punkten...")
            self.client.sync_trajectory(self.trajectory)
            self.trajectory = []

        print(f"Optimierung beendet. Bestes Z lokal: {self.best_z:.6f} bei ({self.best_x:.3f}, {self.best_y:.3f})")


def main():
    # Beispiel für den neuen Workflow (Phase 2)
    bot = LocalSearchBot(API_URL, SESSION_CODE, BOT_NAME)
    try:
        bot.run(max_local_steps=500000)
    except Exception as e:
        print(f"Fehler: {e}")
        print("Hinweis: Stelle sicher, dass der Backend-Server läuft und der SESSION_CODE korrekt ist.")


if __name__ == "__main__":
    main()
