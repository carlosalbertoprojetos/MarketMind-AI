@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "LAUNCH_SCRIPT=%ROOT%\scripts\launch-local.ps1"
set "FRONTEND_URL=http://127.0.0.1:5173"
set "BACKEND_URL=http://127.0.0.1:8003"

if not exist "%BACKEND_DIR%\app\main.py" (
  echo Backend nao encontrado em "%BACKEND_DIR%".
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
  echo Frontend nao encontrado em "%FRONTEND_DIR%".
  pause
  exit /b 1
)

if not exist "%LAUNCH_SCRIPT%" (
  echo Script de inicializacao nao encontrado em "%LAUNCH_SCRIPT%".
  pause
  exit /b 1
)

echo MarketingAI - Iniciando backend, frontend e browser local...
echo.
echo Backend:  %BACKEND_URL%
echo Frontend: %FRONTEND_URL%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCH_SCRIPT%" -RootPath "%ROOT%"
if errorlevel 1 (
  echo Falha ao iniciar o ambiente local.
  pause
  exit /b 1
)

echo.
echo Janelas iniciadas:
echo - Backend em %BACKEND_URL%
echo - Frontend em %FRONTEND_URL%
echo - Browser local dedicado, quando Edge/Chrome estiverem disponiveis
echo.
echo Se a interface nao responder de imediato, aguarde alguns segundos e recarregue.
pause
endlocal
