@echo off
chcp 65001 > nul
title Harness Eng AI Agent - 서버 시작

echo ==============================================
echo  Harness Eng AI Agent - 서버 시작
echo ==============================================
echo.

:: ── 기존 프로세스 정리 ──────────────────────────
echo [1/3] 기존 프로세스 종료 중...
taskkill /F /IM node.exe    2>nul
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe  2>nul
timeout /t 2 /nobreak > nul

:: ── 백엔드 (FastAPI + src/) ──────────────────────
echo [2/3] FastAPI 백엔드 시작 (port 8010)...
set PYTHONPATH=%~dp0src
set HARNESS_SKIP_LLM=1
start "Backend - FastAPI" /D "%~dp0" cmd /k "set PYTHONPATH=%~dp0src && set HARNESS_SKIP_LLM=1 && python -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload --app-dir src"
timeout /t 4 /nobreak > nul

:: ── 프론트엔드 (Vite React) ─────────────────────
echo [3/3] Vite 프론트엔드 시작 (port 5173)...
start "Frontend - Vite" /D "%~dp0frontend" cmd /k "npm run dev"

timeout /t 3 /nobreak > nul

echo.
echo ==============================================
echo  Frontend : http://localhost:5173
echo  Backend  : http://localhost:8010
echo  API Docs : http://localhost:8010/docs
echo ==============================================
echo.
echo  Login: demo@example.com / demo1234
echo.
echo 종료: kill.bat
pause
