from __future__ import annotations

import random
import time
import math
from typing import List, Tuple, Dict

from blackbox_client import BlackBoxClient

# --- Konfiguration ---
API_URL = "http://localhost:8000/"
SESSION_CODE = "9989DB"  # Bitte durch aktuellen Code ersetzen
BOT_NAME = f"GA-Heavy-{random.randint(100, 999)}"

# --- Heavy GA Parameter ---
POPULATION_SIZE = 500
GENERATIONS = 1000 # Total 500,000 evaluations
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.8
ELITISM_COUNT = 10

class Individual:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.fitness = None

    def __repr__(self):
        return f"Ind(x={self.x:.3f}, y={self.y:.3f}, f={self.fitness})"

class GeneticAlgorithmBot:
    """
    Ein robuster evolutionärer Algorithmus.
    Lädt die Suchraum-Grenzen und das Ziel (min/max) automatisch vom Server.
    Synchronisiert den Fortschritt in 20 gleich großen Teilen zum Server.
    """
    def __init__(self, api_url: str, session_code: str, bot_name: str):
        self.client = BlackBoxClient(api_url, session_code)
        self.bot_name = bot_name
        self.bounds = {"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5}
        self.goal = "min"
        self.full_trajectory = [] 
        self.sync_interval = 1000 # Standard, wird überschrieben

    def run(self):
        # 1. Session beitreten & Suchraum-Parameter erhalten
        print(f"Trete Session {self.client.session_code} bei...")
        join_data = self.client.join(self.bot_name, is_bot=True)
        
        self.bounds = join_data["bounds"]
        self.goal = join_data["goal"]
        
        info = self.client.get_public_info()
        print(f"Ziel: {self.goal}")
        print(f"Suchraum: x=[{self.bounds['xmin']}, {self.bounds['xmax']}], y=[{self.bounds['ymin']}, {self.bounds['ymax']}]")
        print(f"Session-Limit: {info.max_steps} Schritte")
        
        # Berechnung des Sync-Intervalls (20 Teile)
        self.sync_interval = max(1, info.max_steps // 20)
        print(f"Synchronisations-Intervall: Alle {self.sync_interval} Evaluationen (1/20 der Session)")

        # 2. Startpopulation initialisieren
        population = self.init_population(POPULATION_SIZE)
        
        # Mutation-Stärke basierend auf Suchraum-Breite (10%)
        self.mut_strength_x = (self.bounds["xmax"] - self.bounds["xmin"]) * 0.1
        self.mut_strength_y = (self.bounds["ymax"] - self.bounds["ymin"]) * 0.1

        total_evals = 0
        last_sync_at = 0

        for gen in range(GENERATIONS):
            # 3. Fitness evaluieren (Lokal!)
            for ind in population:
                if ind.fitness is None:
                    try:
                        ind.fitness = self.client.evaluate_local(ind.x, ind.y)
                        self.full_trajectory.append({"x": ind.x, "y": ind.y, "z": ind.fitness})
                        total_evals += 1
                    except Exception:
                        ind.fitness = float('inf') if self.goal == "min" else float('-inf')

            # Bestes Individuum der Generation finden
            if self.goal == "min":
                best = min(population, key=lambda ind: ind.fitness)
            else:
                best = max(population, key=lambda ind: ind.fitness)
                
            if gen % 10 == 0:
                print(f"Gen {gen:04d}: Best={best.fitness:12.6f} (Total Evals: {total_evals})")
            
            # 4. Sync zum Server (wenn Intervall erreicht)
            if total_evals - last_sync_at >= self.sync_interval:
                self.sync_progress()
                last_sync_at = total_evals

            # Abbruchbedingungen prüfen
            if total_evals >= info.max_steps:
                print(f"Maximales Schrittlimit ({info.max_steps}) erreicht!")
                break

            # 5. Neue Generation erzeugen
            new_population = []
            
            # Elitismus: Die Besten kopieren
            sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=(self.goal == "max"))
            new_population.extend(sorted_pop[:ELITISM_COUNT])
            
            while len(new_population) < POPULATION_SIZE:
                # Selection
                parent1 = self.selection_tournament(population)
                parent2 = self.selection_tournament(population)
                
                # Crossover
                child1_coords, child2_coords = self.crossover(parent1, parent2)
                
                # Mutation
                c1 = Individual(*self.mutate(*child1_coords))
                c2 = Individual(*self.mutate(*child2_coords))
                
                new_population.append(c1)
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(c2)
            
            population = new_population

        # Finaler Sync
        self.sync_progress()
        print(f"Optimierung beendet. Insgesamt {total_evals} Evaluationen.")

    def init_population(self, size: int) -> List[Individual]:
        pop = []
        for _ in range(size):
            x = random.uniform(self.bounds["xmin"], self.bounds["xmax"])
            y = random.uniform(self.bounds["ymin"], self.bounds["ymax"])
            pop.append(Individual(x, y))
        return pop

    def selection_tournament(self, population: List[Individual], k=5) -> Individual:
        participants = random.sample(population, k)
        if self.goal == "min":
            return min(participants, key=lambda ind: ind.fitness)
        else:
            return max(participants, key=lambda ind: ind.fitness)

    def crossover(self, p1: Individual, p2: Individual) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        if random.random() < CROSSOVER_RATE:
            # Arithmetisches Crossover (Mittelwertbildung)
            alpha = random.random()
            child1_x = alpha * p1.x + (1 - alpha) * p2.x
            child1_y = alpha * p1.y + (1 - alpha) * p2.y
            
            child2_x = (1 - alpha) * p1.x + alpha * p2.x
            child2_y = (1 - alpha) * p1.y + alpha * p2.y
            return (child1_x, child1_y), (child2_x, child2_y)
        return (p1.x, p1.y), (p2.x, p2.y)

    def mutate(self, x: float, y: float) -> Tuple[float, float]:
        if random.random() < MUTATION_RATE:
            # Gaußsche Mutation skaliert auf den Suchraum
            x += random.normalvariate(0, self.mut_strength_x)
            y += random.normalvariate(0, self.mut_strength_y)
            
            # Bounds einhalten
            x = max(self.bounds["xmin"], min(self.bounds["xmax"], x))
            y = max(self.bounds["ymin"], min(self.bounds["ymax"], y))
        return x, y

    def sync_progress(self):
        if not self.full_trajectory:
            return
        print(f"Syncing {len(self.full_trajectory)} Punkte zum Server...")
        try:
            start_t = time.time()
            self.client.sync_trajectory(self.full_trajectory)
            duration = time.time() - start_t
            print(f"Sync erfolgreich ({duration:.2f}s)")
            self.full_trajectory = [] 
        except Exception as e:
            print(f"Sync fehlgeschlagen: {e}")


def main():
    bot = GeneticAlgorithmBot(API_URL, SESSION_CODE, BOT_NAME)
    try:
        bot.run()
    except Exception as e:
        print(f"Fehler: {e}")
        print("Hinweis: Stelle sicher, dass der Backend-Server läuft (Port 8001) und der SESSION_CODE korrekt ist.")

if __name__ == "__main__":
    main()
