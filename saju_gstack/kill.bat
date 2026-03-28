@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM Stop dev servers: FastAPI 8030, Vite 5175
echo [saju-gstack] Stopping listeners on ports 8030 and 5175 ...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='SilentlyContinue'; " ^
  "$ports = @(8030, 5175); " ^
  "foreach ($port in $ports) { " ^
  "  $pids = Get-NetTCPConnection -LocalPort $port -State Listen | Select-Object -ExpandProperty OwningProcess -Unique; " ^
  "  foreach ($procId in $pids) { if ($procId -gt 0) { Write-Host ('  Killing PID ' + $procId + ' (port ' + $port + ')'); Stop-Process -Id $procId -Force } } " ^
  "}"

echo [saju-gstack] Done.
endlocal
