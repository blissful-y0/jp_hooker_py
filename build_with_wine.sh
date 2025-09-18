#!/bin/bash

echo "========================================="
echo "Building Windows EXE using Wine"
echo "========================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check if Wine is installed
if ! command -v wine64 &> /dev/null; then
    echo "Installing Wine..."
    brew install --cask wine-stable
fi

# Check if Python is installed in Wine
if ! wine64 python --version &> /dev/null 2>&1; then
    echo "Setting up Python in Wine..."

    # Download Python installer
    curl -o python-installer.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

    # Install Python in Wine
    wine64 python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

    # Wait for installation
    sleep 10

    # Clean up
    rm python-installer.exe
fi

echo "Installing Python packages in Wine..."
wine64 python -m pip install --upgrade pip
wine64 python -m pip install pyinstaller
wine64 python -m pip install pywin32
wine64 python -m pip install psutil
wine64 python -m pip install pyperclip
wine64 python -m pip install google-generativeai

echo "Building EXE files..."

# Create output directory
mkdir -p release

# Build basic version
echo "Building basic text hooker..."
wine64 python -m PyInstaller --onefile --noconsole \
    --name "JapaneseTextHooker" \
    --distpath release \
    text_hooker.py

# Build overlay version
echo "Building overlay version..."
wine64 python -m PyInstaller --onefile --noconsole \
    --name "TextHookerOverlay" \
    --distpath release \
    --add-data "settings.json;." \
    overlay_hooker.py

# Clean up
rm -rf build dist __pycache__ *.spec

echo ""
echo "========================================="
echo "Build completed!"
echo "EXE files are in the 'release' folder"
echo "========================================="