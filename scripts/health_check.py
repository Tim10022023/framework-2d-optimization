#!/usr/bin/env python3
"""
Health check utility for running services.
Verifies backend and frontend are responding correctly.
"""

import requests
import time
import sys
import platform

# Disable emoji on Windows
USE_EMOJI = platform.system() != "Windows"
def emoji(e, fallback):
    return e if USE_EMOJI else fallback

def check_health(url, service_name, timeout=30):
    """Check if a service is responding at the given URL."""
    print(f"\n{emoji('🔍', '>')} Checking {service_name}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"  {emoji('✅', 'OK')} {service_name} is responding")
                return True
        except requests.exceptions.RequestException:
            pass
        
        elapsed = int(time.time() - start_time)
        print(f"  {emoji('⏳', '...')} Waiting for {service_name}... ({elapsed}s/{timeout}s)", end="\r")
        time.sleep(1)
    
    print(f"  {emoji('❌', 'X')} {service_name} did not respond within {timeout}s")
    return False

def check_backend_api(base_url="http://localhost:8000"):
    """Verify backend API health and basic endpoints."""
    print(f"\n{emoji('📡', '>')} Backend API Checks")
    print("-" * 40)
    
    try:
        # Health endpoint
        res = requests.get(f"{base_url}/health")
        if res.status_code != 200 or res.json().get("status") != "ok":
            print(f"  {emoji('❌', 'X')} Health endpoint failed")
            return False
        print(f"  {emoji('✅', 'OK')} Health endpoint OK")
        
        # Functions endpoint
        res = requests.get(f"{base_url}/functions")
        if res.status_code != 200:
            print(f"  {emoji('❌', 'X')} Functions endpoint failed")
            return False
        functions = res.json().get("functions", [])
        print(f"  {emoji('✅', 'OK')} Functions endpoint OK ({len(functions)} functions available)")
        
        # Session creation (integration test)
        res = requests.post(f"{base_url}/sessions", json={
            "function_id": functions[0]["id"] if functions else "sphere_shifted",
            "goal": "min",
            "max_steps": 5
        })
        if res.status_code != 200:
            print(f"  {emoji('❌', 'X')} Session creation failed: {res.text}")
            return False
        session_code = res.json().get("session_code")
        print(f"  {emoji('✅', 'OK')} Session creation OK (code: {session_code})")
        
        return True
    except Exception as e:
        print(f"  {emoji('❌', 'X')} Backend check failed: {e}")
        return False

def check_frontend(url="http://localhost:5173"):
    """Verify frontend is reachable."""
    print(f"\n{emoji('🌐', '>')} Frontend Checks")
    print("-" * 40)
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            print(f"  {emoji('✅', 'OK')} Frontend is reachable")
            return True
        else:
            print(f"  {emoji('❌', 'X')} Frontend returned status {res.status_code}")
            return False
    except Exception as e:
        print(f"  {emoji('❌', 'X')} Frontend check failed: {e}")
        return False

def main():
    print("=" * 60)
    print(f"{emoji('🏥', '>')} HEALTH CHECK")
    print("=" * 60)
    
    backend_ok = check_health("http://localhost:8000/health", "Backend", timeout=30)
    frontend_ok = check_health("http://localhost:5173", "Frontend", timeout=30)
    
    if not (backend_ok and frontend_ok):
        print(f"\n{emoji('❌', 'X')} Services not ready. Make sure Docker Compose is running:")
        print("   docker compose up")
        return False
    
    api_ok = check_backend_api()
    frontend_responding = check_frontend()
    
    print("\n" + "=" * 60)
    if api_ok and frontend_responding:
        print(f"{emoji('✅', 'OK')} ALL SYSTEMS HEALTHY")
        print("=" * 60)
        return True
    else:
        print(f"{emoji('⚠️', '!')} SOME CHECKS FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
