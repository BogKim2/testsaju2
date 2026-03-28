@echo off
chcp 65001 >nul
setlocal

REM saju-gstack: backend (8030) + frontend (5175) in separate windows
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

echo [saju-gstack] Starting backend: http://127.0.0.1:8030
start "saju-gstack-backend" cmd /k "cd /d ""%ROOT%\backend"" && python -m uvicorn main:app --host 127.0.0.1 --port 8030 --reload"

REM delay ~2s (works in non-interactive sessions; timeout.exe can fail there)
ping -n 3 127.0.0.1 >nul

echo [saju-gstack] Starting frontend: http://localhost:5175
start "saju-gstack-frontend" cmd /k "cd /d ""%ROOT%\frontend"" && npm run dev"

echo [saju-gstack] Two windows opened. Close them to stop servers, or run kill.bat to free ports.
endlocal
