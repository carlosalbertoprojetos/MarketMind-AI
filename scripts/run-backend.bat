@echo off
cd /d "%~dp0..\backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
