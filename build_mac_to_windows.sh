#!/bin/bash

echo "========================================="
echo "Building Windows EXE on Mac"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "Method 1: Using Docker (Recommended)"
echo "-------------------------------------"

# Build Docker image
echo "Building Docker image..."
docker build -t text-hooker-builder -f Dockerfile.windows .

# Build EXE files using Docker
echo "Building Windows executables..."

# Create output directory
mkdir -p release

# Build basic version
docker run --rm -v "$(pwd):/src" text-hooker-builder \
    pyinstaller --onefile --noconsole --name "JapaneseTextHooker" \
    --hidden-import win32api \
    --hidden-import win32con \
    --hidden-import win32gui \
    --hidden-import win32process \
    --hidden-import psutil \
    --hidden-import pyperclip \
    text_hooker.py

# Build overlay version
docker run --rm -v "$(pwd):/src" text-hooker-builder \
    pyinstaller --onefile --noconsole --name "TextHookerOverlay" \
    --hidden-import win32api \
    --hidden-import win32con \
    --hidden-import win32gui \
    --hidden-import win32process \
    --hidden-import psutil \
    --hidden-import google.generativeai \
    --add-data "settings.json:." \
    overlay_hooker.py

# Move built files
if [ -f "dist/JapaneseTextHooker.exe" ]; then
    mv dist/JapaneseTextHooker.exe release/
    echo "✓ Built: release/JapaneseTextHooker.exe"
fi

if [ -f "dist/TextHookerOverlay.exe" ]; then
    mv dist/TextHookerOverlay.exe release/
    echo "✓ Built: release/TextHookerOverlay.exe"
fi

# Clean up
rm -rf build dist __pycache__ *.spec

echo ""
echo "========================================="
echo "Build completed!"
echo "EXE files are in the 'release' folder"
echo "========================================="