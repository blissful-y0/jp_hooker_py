@echo off
echo ========================================
echo Japanese Text Hooker - EXE Builder
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

REM Build basic version
echo.
echo [2/4] Building basic text hooker...
pyinstaller text_hooker.spec --clean --noconfirm

REM Build advanced version
echo.
echo [3/4] Building advanced text hooker...
pyinstaller advanced_hooker.spec --clean --noconfirm

REM Create output folder
echo.
echo [4/4] Organizing output files...
if not exist "release" mkdir release
if exist "dist\JapaneseTextHooker.exe" (
    move "dist\JapaneseTextHooker.exe" "release\JapaneseTextHooker.exe"
    echo Basic version: release\JapaneseTextHooker.exe
)
if exist "dist\AdvancedTextHooker.exe" (
    move "dist\AdvancedTextHooker.exe" "release\AdvancedTextHooker.exe"
    echo Advanced version: release\AdvancedTextHooker.exe
)

REM Cleanup
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
if exist "*.pyc" del /q *.pyc

echo.
echo ========================================
echo Build completed successfully!
echo EXE files are in the 'release' folder
echo ========================================
pause