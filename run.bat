@echo off
REM =============================================================================
REM MarketingAI - Executar sistema (backend + frontend) em desenvolvimento local
REM Atualizado a cada fase concluida.
REM =============================================================================
REM Fases: 1 Estrutura | 2 Backend | 3 Frontend | 4 Webscraping | 5 Pipeline IA
REM        6 Output | 7 Agenda | 8 Deploy | 9 Credentials | 10 Imagens preview
REM       11 Lembretes | 12 Export ZIP | 13 Testes | 14 Migrações | 15 Dashboard
REM       16 Rate limiting + paginação API | 17 Paginação no Dashboard | 18 Filtros e busca | 19 Página Credenciais | 20 Página 404 | 21 Itens por página | 22 Testes frontend | 23 Toasts | 24 Duplicar campanha | 25 Página Sobre | 26 Modo escuro | 27 Toasts no modo escuro | 28 Persistência URL e polimento final | 29 Ícone-only toggle e parsing robusto | 30 Correção dev server + varredura final dark | 31 UI responsiva + geração por URL + biblioteca de mídia | 32 Filtros de mídia + histórico de gerações | 33 Exportação ZIP da galeria filtrada | 34 Seleção manual de ativos | 35 Filtro por período de geração
REM =============================================================================
REM Uso: duplo-clique em run.bat ou: cd MarketingAI && run.bat
REM Backend: http://localhost:8000  |  Frontend: http://localhost:5173
REM Docs API: http://localhost:8000/docs
REM =============================================================================

set ROOT=%~dp0
if "%ROOT:~-1%"=="\" set ROOT=%ROOT:~0,-1%

echo MarketingAI - Iniciando backend e frontend...
echo.
echo Janela 1: Backend (FastAPI) - porta 8000
echo Janela 2: Frontend (Vite)   - porta 5173
echo.
echo Acesse: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Feche as janelas para encerrar o sistema.
echo.

start "MarketingAI - Backend" cmd /k "cd /d "%ROOT%\backend" && (py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000)"
timeout /t 2 /nobreak >nul
start "MarketingAI - Frontend" cmd /k "cd /d "%ROOT%\frontend" && (npm run dev)"
timeout /t 4 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo Backend e frontend iniciados. Navegador aberto em http://localhost:5173
pause
