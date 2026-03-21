@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
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

echo MarketingAI - Iniciando backend e frontend...
echo.
echo Backend:  %BACKEND_URL%
echo Frontend: %FRONTEND_URL%
echo.

start "MarketingAI - Backend" /D "%BACKEND_DIR%" cmd /k py -3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8003
if errorlevel 1 (
  echo Falha ao iniciar a janela do backend.
  pause
  exit /b 1
)

timeout /t 3 /nobreak >nul

start "MarketingAI - Frontend" /D "%FRONTEND_DIR%" cmd /k npm run dev -- --host 127.0.0.1 --port 5173
if errorlevel 1 (
  echo Falha ao iniciar a janela do frontend.
  pause
  exit /b 1
)

timeout /t 5 /nobreak >nul
start "" "%FRONTEND_URL%"

echo.
echo Janelas iniciadas:
echo - Backend em %BACKEND_URL%
echo - Frontend em %FRONTEND_URL%
echo.
echo Se o navegador abrir antes do frontend responder, aguarde alguns segundos e recarregue.
pause
endlocal
