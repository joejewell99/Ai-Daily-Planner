import subprocess
import os

# Path to your virtual environment
venv_path = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")

def run_backend():
    return subprocess.Popen([venv_path, "backend.py"])

def run_frontend():
    return subprocess.Popen([venv_path, "frontend.py"])

def run_app():
    backend_process = run_backend()
    frontend_process = run_frontend()

    # Wait for the frontend process to terminate
    frontend_process.wait()

    # Once frontend is closed, terminate the backend process
    backend_process.terminate()
    backend_process.wait()

if __name__ == '__main__':
    run_app()
