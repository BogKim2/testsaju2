# saju_gstack 전용 FastAPI 진입점
# 실행: cd backend && uvicorn main:app --host 0.0.0.0 --port 8030 --reload

from saju.api_app import app  # noqa: F401
