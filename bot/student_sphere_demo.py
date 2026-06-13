import random
import time
import sys
import os

# Add current directory to path to import BlackBoxClient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blackbox_client import BlackBoxClient

def run_demo_bot(api_url="http://localhost:8000", session_code=None):
    if not session_code:
        print("Error: No session code provided.")
        return

    client = BlackBoxClient(api_url, session_code)
    
    print(f"--- Sphere Optimization Demo Bot ---")
    print(f"Joining session: {session_code}")
    
    try:
        join_data = client.join("SphereDemoBot", is_bot=True)
        print(f"Joined successfully. Participant ID: {client.participant_id}")
    except Exception as e:
        print(f"Failed to join: {e}")
        return

    # GA / ES Parameters
    POP_SIZE = 20
    GENERATIONS = 50
    MUTATION_SIGMA = 0.5
    SYNC_EVERY = 5 # Sync every 5 generations
    
    # Initialize population randomly within [-5, 5]
    population = []
    for _ in range(POP_SIZE):
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        z = client.evaluate_local(x, y)
        population.append({"x": x, "y": y, "z": z})

    trajectory = []
    best_overall = min(population, key=lambda p: p["z"])
    
    print(f"Initial Best Z: {best_overall['z']:.6f} at ({best_overall['x']:.2f}, {best_overall['y']:.2f})")
    print("-" * 40)

    for gen in range(1, GENERATIONS + 1):
        # Sort population by fitness (z-value, assuming minimization)
        population.sort(key=lambda p: p["z"])
        
        # Simple (1+lambda) style: Keep the best, create new ones by mutating the best
        best = population[0]
        new_population = [best]
        
        # Track for syncing
        trajectory.append({"x": best["x"], "y": best["y"], "z": best["z"], "step": (gen-1) * POP_SIZE})

        # Decay mutation sigma to show convergence
        current_sigma = MUTATION_SIGMA * (1.0 - gen / GENERATIONS)
        if current_sigma < 0.01: current_sigma = 0.01

        for _ in range(POP_SIZE - 1):
            # Mutate best
            child_x = best["x"] + random.gauss(0, current_sigma)
            child_y = best["y"] + random.gauss(0, current_sigma)
            
            # Bound check
            child_x = max(-5, min(5, child_x))
            child_y = max(-5, min(5, child_y))
            
            child_z = client.evaluate_local(child_x, child_y)
            new_population.append({"x": child_x, "y": child_y, "z": child_z})
            
            # Record child for trajectory
            trajectory.append({"x": child_x, "y": child_y, "z": child_z, "step": gen * POP_SIZE})

        population = new_population
        best_in_gen = population[0]
        
        if gen % 5 == 0 or gen == 1:
            print(f"Gen {gen:02d}: Best Z = {best_in_gen['z']:.8f} | Sigma = {current_sigma:.4f}")

        # Periodically sync to server so the teacher can see progress
        if gen % SYNC_EVERY == 0:
            try:
                client.sync_trajectory(trajectory)
                trajectory = [] # Clear synced points
            except Exception as e:
                print(f"Sync error: {e}")

    # Final Sync
    if trajectory:
        client.sync_trajectory(trajectory)

    print("-" * 40)
    print(f"Optimization finished.")
    print(f"Final Best Z: {population[0]['z']:.10f}")
    print(f"Coordinates:  x={population[0]['x']:.6f}, y={population[0]['y']:.6f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--session", required=True)
    args = parser.parse_args()
    
    run_demo_bot(args.url, args.session)
