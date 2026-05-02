import asyncio
import httpx
import time
import random
import multiprocessing
import requests
from blackbox_client import BlackBoxClient

# Configuration
API_URL = "http://localhost:8000"
SESSION_CODE = "0F6D02" 
BOT_COUNT = 50
EVALS_PER_BOT = 10000  
SYNC_INTERVAL = 1000   
GA_POPULATION = 50

async def run_ga_bot(bot_index, session_code):
    client = BlackBoxClient(API_URL, session_code)
    name = f"GA-StressBot-{bot_index:03d}"
    
    try:
        # 1. Join
        client.join(name)
        participant_id = client.participant_id
        
        # 2. Simulate GA locally using the RPN payload
        trajectory = []
        best_z = float('inf')
        
        for step in range(1, EVALS_PER_BOT + 1):
            x = random.uniform(-5, 5)
            y = random.uniform(-5, 5)
            
            # Use real local evaluation from the client
            z = client.evaluate_local(x, y)
            best_z = min(best_z, z)
            
            trajectory.append({"x": x, "y": y, "z": z, "step": step})
            
            if step % SYNC_INTERVAL == 0:
                # Use the client's built-in sync method
                client.sync_trajectory(trajectory)
                trajectory = [] 
                
        if trajectory:
            client.sync_trajectory(trajectory)
            
        print(f"[{name}] FINISHED {EVALS_PER_BOT} evals. Best Z: {best_z:.4f}")
        return True

    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        return False

def bot_process_wrapper(bot_index, session_code):
    asyncio.run(run_ga_bot(bot_index, session_code))

async def main():
    print(f"--- Starting GA Stress Test with {BOT_COUNT} Bots ---")
    print(f"Target: {API_URL} | Session: {SESSION_CODE}")
    
    # We use multiprocessing to simulate real concurrent load
    processes = []
    for i in range(BOT_COUNT):
        p = multiprocessing.Process(target=bot_process_wrapper, args=(i, SESSION_CODE))
        p.start()
        processes.append(p)
        
        # Small stagger to avoid thundering herd on Join
        if i % 10 == 0:
            await asyncio.sleep(0.1)

    for p in processes:
        p.join()

    print("--- Stress Test Completed ---")

if __name__ == "__main__":
    asyncio.run(main())
