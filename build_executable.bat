@echo off
REM ============================================================================
REM Build Executable Script for Lung ASP GUI (Windows)
REM ============================================================================
REM This script creates a standalone executable with all dependencies
REM including TotalSegmentator and nnU-Net
REM ============================================================================

echo.
echo ============================================================================
echo   Lung ASP - Executable Build Script for Windows
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv_build" (
    echo [2/6] Creating virtual environment...
    python -m venv venv_build
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/6] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv_build\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install dependencies
echo [4/6] Installing dependencies (this may take 10-20 minutes)...
echo This includes: numpy, scipy, scikit-image, TotalSegmentator, nnU-Net, PyInstaller
pip install --upgrade pip
pip install -r requirements-full.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Build executable with PyInstaller
echo [5/6] Building executable with PyInstaller...
echo This may take 5-10 minutes depending on your system...
pyinstaller --clean --noconfirm lung_asp_gui.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)
echo.

REM Verify build
echo [6/6] Verifying build...
if exist "dist\LungASP\LungASP.exe" (
    echo.
    echo ============================================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================================
    echo.
    echo Executable location: %CD%\dist\LungASP\
    echo Main executable: %CD%\dist\LungASP\LungASP.exe
    echo.
    echo The entire 'dist\LungASP' folder contains the standalone application.
    echo Copy this entire folder to any Windows computer to run the application.
    echo.
    echo IMPORTANT NOTES:
    echo - First run may be slow as TotalSegmentator downloads models
    echo - Ensure you have adequate disk space for models (several GB)
    echo - The application requires an internet connection on first run for models
    echo.
    echo ============================================================================
) else (
    echo.
    echo ERROR: Executable was not created successfully
    echo Please check the build output for errors
    pause
    exit /b 1
)

echo.
echo Press any key to exit...
pause >nul
