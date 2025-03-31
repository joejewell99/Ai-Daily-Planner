import subprocess
import os

# Path to your virtual environment
venv_path = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")

def run_backend():
    subprocess.Popen([venv_path, "backend.py"])

def run_frontend():
    subprocess.Popen([venv_path, "frontend.py"])

if __name__ == '__main__':
    run_backend()
    run_frontend()
