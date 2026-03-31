from __future__ import annotations

import random
import time
import math
from typing import List, Tuple, Dict

from blackbox_client import BlackBoxClient

# --- Konfiguration ---
API_URL = "http://localhost:8000/"
SESSION_CODE = "FFB378"  # Bitte durch aktuellen Code ersetzen
BOT_NAME = f"GA-Heavy-{random.randint(100, 999)}"

# --- Heavy GA Parameter ---
POPULATION_SIZE = 100
GENERATIONS = 200 # Total 20,000 evaluations
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.8
ELITISM_COUNT = 5

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
    """
    def __init__(self, api_url: str, session_code: str, bot_name: str):
        self.client = BlackBoxClient(api_url, session_code)
        self.bot_name = bot_name
        self.bounds = {"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5}
        self.goal = "min"
        self.full_trajectory = [] 

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
        
        # 2. Startpopulation initialisieren
        population = self.init_population(POPULATION_SIZE)
        
        # Mutation-Stärke basierend auf Suchraum-Breite (10%)
        self.mut_strength_x = (self.bounds["xmax"] - self.bounds["xmin"]) * 0.1
        self.mut_strength_y = (self.bounds["ymax"] - self.bounds["ymin"]) * 0.1

        for gen in range(GENERATIONS):
            # 3. Fitness evaluieren (Lokal!)
            self.evaluate_population(population)
            
            # Bestes Individuum der Generation finden
            if self.goal == "min":
                best = min(population, key=lambda ind: ind.fitness)
            else:
                best = max(population, key=lambda ind: ind.fitness)
                
            print(f"Generation {gen:03d}: Best Fitness = {best.fitness:12.6f} at ({best.x:8.3f}, {best.y:8.3f})")
            
            # 4. Sync zum Server (alle 10 Generationen bei Heavy GA)
            if gen % 10 == 0:
                self.sync_progress()

            # Abbruchbedingungen prüfen
            if len(self.full_trajectory) >= info.max_steps:
                print("Maximales Schrittlimit erreicht!")
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
        print("Optimierung beendet.")

    def init_population(self, size: int) -> List[Individual]:
        pop = []
        for _ in range(size):
            x = random.uniform(self.bounds["xmin"], self.bounds["xmax"])
            y = random.uniform(self.bounds["ymin"], self.bounds["ymax"])
            pop.append(Individual(x, y))
        return pop

    def evaluate_population(self, population: List[Individual]):
        for ind in population:
            if ind.fitness is None:
                # Lokale Evaluierung
                try:
                    ind.fitness = self.client.evaluate_local(ind.x, ind.y)
                    # Merken für den Server
                    self.full_trajectory.append({"x": ind.x, "y": ind.y, "z": ind.fitness})
                except Exception as e:
                    # Manchmal knallt math.sqrt oder math.log bei ungültigen Werten
                    ind.fitness = float('inf') if self.goal == "min" else float('-inf')

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
            self.client.sync_trajectory(self.full_trajectory)
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
