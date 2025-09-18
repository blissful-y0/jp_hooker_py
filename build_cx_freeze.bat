@echo off
echo ========================================
echo Japanese Text Hooker - cx_Freeze Builder
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
echo [1/3] Installing required packages...
pip install --upgrade pip
pip install cx_Freeze
pip install -r requirements.txt

REM Build with cx_Freeze
echo.
echo [2/3] Building executables with cx_Freeze...
python setup.py build

REM Organize output
echo.
echo [3/3] Organizing output files...
if not exist "release_cx" mkdir release_cx
if exist "build" (
    xcopy /E /Y "build\*" "release_cx\"
    echo Build files copied to release_cx folder
)

echo.
echo ========================================
echo Build completed!
echo Executables are in the 'release_cx' folder
echo ========================================
pause