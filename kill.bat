@echo off
chcp 65001 > nul
echo 사주 분석 서버 종료 중...

:: node 프로세스 종료 (프론트엔드)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5174 "') do (
    taskkill /PID %%a /F > nul 2>&1
)

:: Python/uvicorn 프로세스 종료 (백엔드)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8020 "') do (
    taskkill /PID %%a /F > nul 2>&1
)

:: 명시적으로 제목이 있는 창 종료
taskkill /FI "WINDOWTITLE eq Saju-Backend" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq Saju-Frontend" /F > nul 2>&1

:: 추가적으로 node/uvicorn 프로세스 정리
taskkill /IM node.exe /F > nul 2>&1
taskkill /IM python.exe /F > nul 2>&1

echo 완료! 모든 서버가 종료되었습니다.
pause
