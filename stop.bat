@echo off
setlocal

echo MarketingAI - Encerrando processos locais...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop-local.ps1" -RootPath "%~dp0"
echo Processos locais encerrados.
endlocal
