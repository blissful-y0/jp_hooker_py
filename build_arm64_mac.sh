#!/bin/bash

echo "========================================="
echo "Building Windows EXE on Apple Silicon Mac"
echo "========================================="
echo ""

# Detect if running on ARM64 Mac
if [[ $(uname -m) == "arm64" ]]; then
    echo "✓ Detected Apple Silicon Mac (M1/M2/M3)"
else
    echo "ℹ Running on Intel Mac - use build_mac_to_windows.sh instead"
fi

echo ""
echo "Since direct cross-compilation from ARM64 to Windows is complex,"
echo "we'll use GitHub Actions for building."
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Create a simple Python build script that can run locally
echo "Creating a local Python package..."

# Create setup script for local testing
cat > setup_local.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="japanese-text-hooker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.8",
        "pyperclip>=1.8.2",
        "google-generativeai>=0.3.2",
        "aiohttp>=3.9.1"
    ],
    entry_points={
        'console_scripts': [
            'text-hooker=text_hooker:main',
            'overlay-hooker=overlay_hooker:main',
        ],
    },
)
EOF

echo ""
echo "Option 1: Use GitHub Actions (Recommended)"
echo "==========================================="
echo "1. Create a GitHub repository"
echo "2. Push your code:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Go to GitHub Actions tab"
echo "4. Run the workflow manually or push a tag:"
echo "   git tag v1.0.0"
echo "   git push origin v1.0.0"
echo ""

echo "Option 2: Use a Windows Cloud VM"
echo "================================="
echo "1. Use GitHub Codespaces or Gitpod with Windows"
echo "2. Or use a free Windows VM from:"
echo "   - https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/"
echo "   - AWS Free Tier Windows instance"
echo ""

echo "Option 3: Use Wine with x86_64 emulation (Experimental)"
echo "========================================================"
echo "This requires Rosetta 2:"
echo ""
echo "   # Install Rosetta if not installed"
echo "   softwareupdate --install-rosetta"
echo ""
echo "   # Run Wine in x86_64 mode"
echo "   arch -x86_64 /bin/bash build_with_wine.sh"
echo ""

echo "Creating automated GitHub push script..."
cat > push_and_build.sh << 'SCRIPT'
#!/bin/bash

# Automated GitHub push and build script
echo "Pushing to GitHub and triggering build..."

# Check if remote is set
if ! git remote | grep -q origin; then
    echo "Please set up GitHub remote first:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    exit 1
fi

# Commit any changes
git add .
git commit -m "Build update $(date +%Y%m%d-%H%M%S)" || true

# Push to main
git push origin main

# Create and push a tag to trigger release
VERSION="v$(date +%Y%m%d.%H%M%S)"
git tag $VERSION
git push origin $VERSION

echo ""
echo "✓ Code pushed to GitHub"
echo "✓ Tag $VERSION created"
echo ""
echo "Now go to GitHub Actions to see the build progress:"
echo "https://github.com/YOUR_USERNAME/YOUR_REPO/actions"
echo ""
echo "The Windows EXE files will be available in:"
echo "1. Actions tab → Latest workflow run → Artifacts"
echo "2. Releases section (for tagged versions)"
SCRIPT

chmod +x push_and_build.sh

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Quick Start:"
echo "1. Set up GitHub repository"
echo "2. Run: ./push_and_build.sh"
echo "3. Download EXE from GitHub Actions"
echo ""
echo "For manual GitHub Actions trigger:"
echo "- Go to Actions tab → Run workflow"