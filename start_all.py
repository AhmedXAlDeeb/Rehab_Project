import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # We resolve the absolute paths to the virtual environment executables
    # This prevents the need to run activate scripts
    venv_python = os.path.join(root_dir, ".venv", "Scripts", "python.exe")
    venv_uvicorn = os.path.join(root_dir, ".venv", "Scripts", "uvicorn.exe")
    
    # Fallback to system-level if the expected venv is missing
    if not os.path.exists(venv_python):
        print(f"Warning: Virtual environment not found at {os.path.join(root_dir, '.venv')}")
        print("Falling back to system 'python' and 'uvicorn'")
        venv_python = "python"
        venv_uvicorn = "uvicorn"

    services = [
        {
            "name": "Classification",
            "cwd": os.path.join(root_dir, "classification_service"),
            "cmd": [venv_uvicorn, "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            "shell": False
        },
        {
            "name": "Integration",
            "cwd": os.path.join(root_dir, "integration_service"),
            "cmd": [venv_uvicorn, "integration_service:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
            "shell": False
        },
        {
            "name": "Generation",
            "cwd": os.path.join(root_dir, "generation_service"),
            "cmd": [venv_uvicorn, "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"],
            "shell": False
        },
        {
            "name": "WebSocket",
            "cwd": os.path.join(root_dir, "simulation-frontend"),
            "cmd": [venv_python, "bridge/ws_server.py"],
            "shell": False
        },
        {
            "name": "Frontend",
            "cwd": os.path.join(root_dir, "react-control-frontend"),
            "cmd": "if not exist node_modules (npm install) && npm run dev",
            "shell": True
        }
    ]

    print("Starting all services...")
    processes = []

    try:
        # Launch all services
        for svc in services:
            print(f"[{svc['name']}] Starting in {svc['cwd']}...")
            
            p = subprocess.Popen(
                svc["cmd"],
                cwd=svc["cwd"],
                shell=svc["shell"]
            )
            processes.append((svc["name"], p))

        print("\nAll services are running! Their output will stream here.")
        print("Press Ctrl+C to stop them all.\n")

        # Keep the main process alive waiting for the child processes
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping all services gracefully...")
        
        # Terminate everything on a Ctrl+C
        for name, p in processes:
            print(f"Terminating {name}...")
            # Using terminate() instead of kill() so they can exit gracefully if needed
            p.terminate()
            
        print("All processes stopped. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()