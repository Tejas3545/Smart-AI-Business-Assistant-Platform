"""Run the backend from the repo root with a correct PYTHONPATH.

Usage:
    python run_backend.py

This makes `app` importable for the `backend/app` package when running from the repository root.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from uvicorn import run

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run(app, host="0.0.0.0", port=port)
