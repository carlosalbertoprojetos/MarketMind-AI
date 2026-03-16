@echo off
setlocal

cd /d "%~dp0\.."

if not exist ".local" mkdir ".local"

rem Start backend
start "marketmind-backend" /D "%cd%\backend" py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

rem Start frontend
start "marketmind-frontend" /D "%cd%\frontend" cmd /c npm run dev -- --hostname 127.0.0.1 --port 3000

echo Backend: http://127.0.0.1:8000/api/v1/health
echo Frontend: http://127.0.0.1:3000
