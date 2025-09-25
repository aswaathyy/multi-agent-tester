import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Change to backend directory
os.chdir(backend_path)

if __name__ == "__main__":
    import uvicorn

    print("Starting Multi-Agent Game Tester POC...")
    print("Backend running at: http://localhost:8000")
    print("Frontend available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")

    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped!")