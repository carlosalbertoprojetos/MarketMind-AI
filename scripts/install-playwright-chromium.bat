@echo off
REM Instala o binário Chromium usado pelo pipeline (mesmo interpretador que roda o backend).
REM Uso: duplo-clique ou: cd MarketingAI\scripts && install-playwright-chromium.bat

set ROOT=%~dp0..
cd /d "%ROOT%"

echo.
echo === Playwright: install chromium ===

if exist "%ROOT%\backend\venv\Scripts\python.exe" (
  echo Usando backend\venv
  "%ROOT%\backend\venv\Scripts\python.exe" -m pip install -q -r "%ROOT%\ia_pipeline\requirements.txt" 2>nul
  "%ROOT%\backend\venv\Scripts\python.exe" -m playwright install chromium
) else (
  echo venv nao encontrado em backend\venv — usando py (Python do sistema^)
  py -m pip install -q -r "%ROOT%\ia_pipeline\requirements.txt" 2>nul
  py -m playwright install chromium
)

if errorlevel 1 (
  echo Falhou. Ative o venv do backend e rode: python -m playwright install chromium
  pause
  exit /b 1
)

echo Chromium pronto.
pause
