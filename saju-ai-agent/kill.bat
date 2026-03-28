@echo off
chcp 65001 > nul
title Kill All - Harness Eng AI Agent

echo ==============================================
echo  Harness Eng AI Agent - 모든 서버 종료
echo ==============================================
echo.

:: node (Vite 프론트엔드)
echo [1] node.exe 종료 중...
taskkill /F /IM node.exe 2>nul
if %errorlevel%==0 (echo    → 종료 완료) else (echo    → 실행 중이 아님)

:: python / uvicorn (FastAPI 백엔드)
echo [2] python.exe / uvicorn.exe 종료 중...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe  2>nul
if %errorlevel%==0 (echo    → 종료 완료) else (echo    → 실행 중이 아님)

:: 포트 3000, 8010 점유 프로세스 강제 종료
echo [3] 포트 3000 / 8010 해제 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "  2^>nul') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8010 "  2^>nul') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo ==============================================
echo  모든 서버 종료 완료
echo ==============================================
timeout /t 2 /nobreak > nul
