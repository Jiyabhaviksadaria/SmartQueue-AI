@echo off
echo ========================================
echo SmartQueue AI - Starting Application
echo ========================================
echo.

echo [1/2] Starting Backend Server...
start "SmartQueue Backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
start "SmartQueue Frontend" cmd /k "cd \"al smart queue frontend\" && python -m http.server 3000"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo SmartQueue AI is now running!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:3000
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:3000

echo.
echo To stop the servers, close the terminal windows.
echo.
