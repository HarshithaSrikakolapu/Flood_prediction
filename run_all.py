import subprocess
import os
import sys
import time
import signal

def run_services():
    print("🚀 Starting PFEWS - Predictive Flood Early Warning System...")
    
    # 1. Start Backend
    print("📡 Starting FastAPI Backend on http://localhost:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for backend to be ready
    time.sleep(2)
    
    # 2. Start Frontend
    print("🖥️ Starting Streamlit Frontend on http://localhost:8501...")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print("\n✅ Both services are running!")
    print("  - Backend API: http://localhost:8000")
    print("  - Frontend UI: http://localhost:8501")
    print("Press Ctrl+C to stop both services.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("👋 Goodbye!")

if __name__ == "__main__":
    run_services()
