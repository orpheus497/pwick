@echo off
REM Uninstallation script for pwick on Windows

echo ======================================
echo   pwick Uninstallation Script
echo ======================================
echo.

echo This will remove the local pwick environment (the 'venv' directory and launcher script).
set /p confirm="Are you sure? [y/N]: "

if /i "%confirm%"=="y" (
    echo.
    echo Removing local environment...
    rd /s /q venv
    del run_pwick.bat
    
    echo.
    echo ======================================
echo   pwick local environment has been removed.
    echo ======================================
echo.
    echo Note: Your vault files are NOT deleted.
    echo They remain at their saved locations.
    echo.
) else (
    echo Uninstallation cancelled.
)

pause