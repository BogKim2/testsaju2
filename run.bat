@echo off
chcp 65001 > nul
echo ============================================
echo  사주 분석 웹앱 시작
echo  Backend : http://localhost:8020
echo  Frontend: http://localhost:5174
echo  API 문서: http://localhost:8020/docs
echo ============================================

set ROOT=%~dp0

:: 백엔드 시작
echo [1/2] 백엔드 (FastAPI) 시작...
set PYTHONPATH=%ROOT%backend
start "Saju-Backend" /D "%ROOT%" cmd /k "cd /d %ROOT% && set PYTHONPATH=%ROOT%backend && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload"

:: 잠시 대기
timeout /t 3 /nobreak > nul

:: 프론트엔드 시작
echo [2/2] 프론트엔드 (Vite) 시작...
start "Saju-Frontend" /D "%ROOT%frontend" cmd /k "cd /d %ROOT%frontend && npm run dev"

echo.
echo 두 서버가 시작되었습니다!
echo 브라우저에서 http://localhost:5174 을 여세요.
echo.
echo 로그인 정보:
echo   이메일: demo@saju.com
echo   비밀번호: saju1234
echo.
pause
