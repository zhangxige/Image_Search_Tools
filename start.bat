@echo off
echo Starting backend...
start "backend" cmd /c "cd /d %~dp0backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo Starting frontend...
start "frontend" cmd /c "cd /d %~dp0frontend && npm run dev"
echo Both servers started. Close the windows to stop.
pause
