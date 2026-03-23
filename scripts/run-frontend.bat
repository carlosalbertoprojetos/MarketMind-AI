@echo off
setlocal
cd /d "%~dp0..\frontend"
set "VITE_MARKETINGAI_LOCAL_CONTROL=1"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
endlocal
