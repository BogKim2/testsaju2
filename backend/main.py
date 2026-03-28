# 백엔드 uvicorn 진입점
# 실행: uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload

from saju.api import app  # noqa: F401
