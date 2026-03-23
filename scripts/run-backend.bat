@echo off
setlocal
cd /d "%~dp0..\backend"
set "PYTHONPATH=%CD%"
set "MARKETINGAI_LOCAL_CONTROL=1"
py -3 -m uvicorn --app-dir "%CD%" marketingai_asgi:app --host 127.0.0.1 --port 8003
endlocal
