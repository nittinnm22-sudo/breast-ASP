@echo off
REM Build script for Lung ASP on Windows
echo ============================================
echo Lung ASP - Full Build Script (Windows)
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo [2/4] Installing Lung ASP package...
pip install -e .
if errorlevel 1 (
    echo Error: Failed to install package
    exit /b 1
)

echo.
echo [3/4] Checking TotalSegmentator installation...
python src/download_models.py
if errorlevel 1 (
    echo Error: Failed to setup models
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo To run the GUI: python src\Lung_ASP_GUI.py
echo To run the CLI: lung-asp --help
echo.
pause
