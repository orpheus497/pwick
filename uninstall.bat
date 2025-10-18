@echo off
REM Uninstallation script for pwick on Windows

echo ======================================
echo   pwick Uninstallation Script
echo ======================================
echo.

REM Check if pwick is installed
python -m pip show pwick >nul 2>&1
if errorlevel 1 (
    echo pwick is not installed.
    pause
    exit /b 0
)

echo This will uninstall pwick from your system.
set /p confirm="Are you sure? [y/N]: "

if /i "%confirm%"=="y" (
    echo.
    echo Uninstalling pwick...
    python -m pip uninstall -y pwick
    
    echo.
    echo ======================================
    echo   pwick has been uninstalled.
    echo ======================================
    echo.
    echo Note: Your vault files are NOT deleted.
    echo They remain at their saved locations.
    echo.
) else (
    echo Uninstallation cancelled.
)

pause
