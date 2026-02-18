@echo off
title SmartQueue Frontend Server
color 0B
echo ========================================
echo   SmartQueue AI - Frontend Server
echo ========================================
echo.
echo Starting frontend on http://localhost:3000
echo.
echo Open in browser:
echo   Main App: http://localhost:3000/index%%20(2).html
echo   Test Page: http://localhost:3000/test-connection.html
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

cd "al smart queue frontend"
python -m http.server 3000

pause
