#!/usr/bin/env python3
"""
Build script with integrated health checks.
Runs linting, tests, and health verification for the entire project.
"""

import subprocess
import sys
import os
import platform

# Disable emoji on Windows
USE_EMOJI = platform.system() != "Windows"
def emoji(e, fallback):
    return e if USE_EMOJI else fallback

def run_command(cmd, cwd=None, description=""):
    """Execute a command and return True if successful."""
    if description:
        print(f"\n{emoji('🔧', '>')} {description}")
    print(f"  > {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)  # Go up one level from scripts/
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    print("=" * 60)
    print(f"{emoji('🚀', '>')} BUILD & HEALTH CHECK")
    print("=" * 60)
    
    # ==================== BACKEND ====================
    print(f"\n{emoji('📦', '>')} BACKEND")
    print("-" * 60)
    
    if not run_command(
        "pip install -r requirements.txt -q",
        cwd=backend_dir,
        description="Installing backend dependencies"
    ):
        print(f"{emoji('❌', 'X')} Failed to install backend dependencies")
        return False
    
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    if not run_command(
        "python -m pytest tests/ -v --tb=short",
        cwd=backend_dir,
        description="Running backend tests"
    ):
        print(f"{emoji('❌', 'X')} Backend tests failed")
        return False
    
    # ==================== FRONTEND ====================
    print(f"\n{emoji('📦', '>')} FRONTEND")
    print("-" * 60)
    
    if not run_command(
        "npm install --prefer-offline",
        cwd=frontend_dir,
        description="Installing frontend dependencies"
    ):
        print(f"{emoji('❌', 'X')} Failed to install frontend dependencies")
        return False
    
    if not run_command(
        "npm run lint -- --max-warnings=0",
        cwd=frontend_dir,
        description="Linting frontend code"
    ):
        print(f"{emoji('⚠️', '!')} Frontend linting found issues")
        return False
    
    if not run_command(
        "npx tsc --noEmit",
        cwd=frontend_dir,
        description="Type checking frontend code"
    ):
        print(f"{emoji('❌', 'X')} Frontend type check failed")
        return False
    
    if not run_command(
        "npm run build",
        cwd=frontend_dir,
        description="Building frontend"
    ):
        print(f"{emoji('❌', 'X')} Frontend build failed")
        return False
    
    # ==================== DOCKER COMPOSE ====================
    print(f"\n{emoji('🐳', '>')} DOCKER COMPOSE BUILD")
    print("-" * 60)
    
    if not run_command(
        "docker compose build",
        cwd=root_dir,
        description="Building Docker images"
    ):
        print(f"{emoji('❌', 'X')} Docker build failed")
        return False
    
    # ==================== SUCCESS ====================
    print("\n" + "=" * 60)
    print(f"{emoji('✅', 'OK')} BUILD SUCCESSFUL")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start services:")
    print("     docker compose up")
    print("  2. Access the application:")
    print("     - Frontend: http://localhost:5173")
    print("     - Backend API: http://localhost:8000")
    print("     - API Docs: http://localhost:8000/docs")
    print("\n  Or run full health check:")
    print("     python health_check.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{emoji('❌', 'X')} Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{emoji('❌', 'X')} Build failed with error: {e}")
        sys.exit(1)
