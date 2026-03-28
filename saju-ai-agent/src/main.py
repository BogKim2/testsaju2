"""
Entry point — run: uvicorn main:app --reload

실행 예 (PowerShell, 프로젝트 루트):
  $env:PYTHONPATH = 'src'
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from harness_eng.api import app

__all__ = ["app"]
