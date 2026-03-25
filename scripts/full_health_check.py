#!/usr/bin/env python3
"""
Full health check - starts Docker Compose and verifies all services.
Runs the complete build pipeline including Docker services.
"""

import subprocess
import time
import requests
import sys
import os
import platform

# Disable emoji on Windows
USE_EMOJI = platform.system() != "Windows"
def emoji(e, fallback):
    return e if USE_EMOJI else fallback

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def run_shell(cmd, cwd=None):
    """Executes a shell command and returns True if successful."""
    print(f"\n> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def wait_for_service(url, timeout=30):
    """Wait for a service to become available at the given URL."""
    print(f"Waiting for {url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"{emoji('✅', 'OK')} Service at {url} is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    print(f"{emoji('❌', 'X')} Timeout: Service at {url} did not respond within {timeout}s.")
    return False

def check_backend_api():
    """Verify backend API health and basic functionality."""
    print(f"\n{emoji('📡', '>')} Verifying Backend API")
    print("-" * 40)
    try:
        # 1. Health Endpoint
        res = requests.get(f"{BACKEND_URL}/health")
        if res.status_code != 200:
            print(f"{emoji('❌', 'X')} Backend health check failed.")
            return False
        print(f"{emoji('✅', 'OK')} Backend health check passed.")

        # 2. List Functions
        res = requests.get(f"{BACKEND_URL}/functions")
        if res.status_code != 200:
            print(f"{emoji('❌', 'X')} Failed to list functions.")
            return False
        functions = res.json().get("functions", [])
        print(f"{emoji('✅', 'OK')} Function list retrieved ({len(functions)} available).")
        
        # 3. Create Session (Functional Test)
        res = requests.post(f"{BACKEND_URL}/sessions", json={
            "function_id": functions[0]["id"] if functions else "sphere_shifted", 
            "goal": "min", 
            "max_steps": 10
        })
        if res.status_code != 200:
            print(f"{emoji('❌', 'X')} Failed to create session: {res.text}")
            return False
        session_data = res.json()
        print(f"{emoji('✅', 'OK')} Session created: {session_data['session_code']}")
        
        return True
    except Exception as e:
        print(f"{emoji('❌', 'X')} Backend check failed with error: {e}")
        return False

def check_frontend():
    """Verify frontend service is reachable."""
    print(f"\n{emoji('🌐', '>')} Verifying Frontend")
    print("-" * 40)
    try:
        res = requests.get(FRONTEND_URL)
        if res.status_code == 200:
            print(f"{emoji('✅', 'OK')} Frontend is reachable at {FRONTEND_URL}")
            return True
        else:
            print(f"{emoji('❌', 'X')} Frontend returned status {res.status_code}")
            return False
    except Exception as e:
        print(f"{emoji('❌', 'X')} Frontend check failed: {e}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docker_compose_file = os.path.join(script_dir, "docker-compose.yaml")
    
    print("=" * 60)
    print(f"{emoji('🚀', '>')} Starting Full Health Test")
    print("=" * 60)
    
    # 1. Docker Build & Up
    if not run_shell(f"docker compose -f {docker_compose_file} up --build -d"):
        print(f"{emoji('❌', 'X')} Failed to start Docker containers.")
        sys.exit(1)

    try:
        # 2. Wait for services to be ready
        if not wait_for_service(f"{BACKEND_URL}/health"):
            sys.exit(1)
            
        # 3. Run Checks
        api_ok = check_backend_api()
        frontend_ok = check_frontend()

        if api_ok and frontend_ok:
            print("\n" + "=" * 60)
            print(f"{emoji('🎉', '!')} ALL SYSTEMS GO: Workspace is healthy!")
            print("=" * 60)
        else:
            print("\n" + "!" * 60)
            print(f"{emoji('⚠️', '!')} HEALTH CHECK FAILED: Some systems are down.")
            print("!" * 60)
            sys.exit(1)

    finally:
        # Optional: Ask user if they want to keep the containers running
        print("\nNote: Docker containers are still running in the background.")
        print(f"Use 'docker compose -f {docker_compose_file} down' to stop them.")

if __name__ == "__main__":
    main()
