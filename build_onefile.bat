@echo off
echo ========================================
echo Japanese Text Hooker - Single EXE Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install required packages
echo [1/4] Installing required packages...
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt

REM Build basic version (single file)
echo.
echo [2/4] Building basic text hooker (single exe)...
pyinstaller --onefile --noconsole --name "JapaneseTextHooker" ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import win32gui ^
    --hidden-import win32process ^
    --hidden-import psutil ^
    --hidden-import pyperclip ^
    text_hooker.py

REM Build advanced version (single file)
echo.
echo [3/4] Building advanced text hooker (single exe)...
pyinstaller --onefile --noconsole --name "AdvancedTextHooker" ^
    --uac-admin ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import win32gui ^
    --hidden-import win32process ^
    --hidden-import win32clipboard ^
    --hidden-import psutil ^
    advanced_hooker.py

REM Create output folder
echo.
echo [4/4] Organizing output files...
if not exist "release" mkdir release
if exist "dist\JapaneseTextHooker.exe" (
    move "dist\JapaneseTextHooker.exe" "release\JapaneseTextHooker_portable.exe"
    echo Basic version: release\JapaneseTextHooker_portable.exe
)
if exist "dist\AdvancedTextHooker.exe" (
    move "dist\AdvancedTextHooker.exe" "release\AdvancedTextHooker_portable.exe"
    echo Advanced version: release\AdvancedTextHooker_portable.exe
)

REM Cleanup
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
if exist "*.pyc" del /q *.pyc
if exist "*.spec" del /q *.spec

echo.
echo ========================================
echo Build completed successfully!
echo Portable EXE files are in the 'release' folder
echo ========================================
pause