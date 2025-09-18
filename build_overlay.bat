@echo off
echo ========================================
echo Japanese Text Hooker with Overlay Builder
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    pause
    exit /b 1
)

REM Install packages
echo Installing required packages...
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt

REM Build overlay version
echo.
echo Building overlay version...
pyinstaller --onefile --noconsole --name "TextHookerOverlay" ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import win32gui ^
    --hidden-import win32process ^
    --hidden-import psutil ^
    --hidden-import google.generativeai ^
    --hidden-import aiohttp ^
    --add-data "settings.json;." ^
    overlay_hooker.py

REM Organize output
echo.
echo Organizing files...
if not exist "release" mkdir release
if exist "dist\TextHookerOverlay.exe" (
    move "dist\TextHookerOverlay.exe" "release\TextHookerOverlay.exe"
    echo Success: release\TextHookerOverlay.exe
)

REM Cleanup
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__

echo.
echo ========================================
echo Build completed!
echo ========================================
pause