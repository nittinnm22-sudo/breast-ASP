@echo off
REM #######################################
REM Lung-ASP Executable Builder for Windows
REM Complete build script with all dependencies
REM Run this on your local Windows system
REM #######################################

echo ==========================================
echo    Lung-ASP Full Executable Builder
echo    With TotalSegmentor ^& nnU-Net
echo ==========================================
echo.

REM Step 1: Check Python version and environment
echo Step 1: Checking Python version and virtual environment...

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo ✓ Virtual environment detected: %VIRTUAL_ENV%
    set PYTHON_CMD=%VIRTUAL_ENV%\Scripts\python.exe
    set PIP_CMD=%VIRTUAL_ENV%\Scripts\pip.exe
    set PYINSTALLER_CMD=%VIRTUAL_ENV%\Scripts\pyinstaller.exe
) else (
    echo ╔════════════════════════════════════════════════════════╗
    echo ║  WARNING: No virtual environment detected!            ║
    echo ╚════════════════════════════════════════════════════════╝
    echo.
    echo FIRST TIME SETUP?
    echo   See SETUP_FIRST_TIME.md for complete setup instructions.
    echo.
    echo QUICK SETUP:
    echo   1. python -m venv lung_env
    echo   2. lung_env\Scripts\activate
    echo   3. pip install -e .
    echo   4. Run this script again
    echo.
    echo If you already have a virtual environment:
    echo   lung_env\Scripts\activate
    echo.
    set /p CONTINUE="Continue anyway? (NOT recommended) (y/n): "
    if /i not "%CONTINUE%"=="y" (
        echo.
        echo Setup your virtual environment first, then try again.
        echo See SETUP_FIRST_TIME.md for detailed instructions.
        pause
        exit /b 1
    )
    echo.
    echo WARNING: Continuing without virtual environment...
    echo This may cause conflicts with your system Python.
    echo.
    set PYTHON_CMD=python
    set PIP_CMD=pip
    set PYINSTALLER_CMD=pyinstaller
)

echo Using Python from: %PYTHON_CMD%
%PYTHON_CMD% --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8-3.11
    pause
    exit /b 1
)
echo.

REM Step 2: Check dependencies
echo Step 2: Checking installed dependencies...
%PYTHON_CMD% -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul || echo ✗ PyTorch not found
%PYTHON_CMD% -c "import totalsegmentor; print('✓ TotalSegmentor: OK')" 2>nul || echo ✗ TotalSegmentor not found
%PYTHON_CMD% -c "import nnunetv2; print('✓ nnU-Net: OK')" 2>nul || echo ✗ nnU-Net not found
%PYTHON_CMD% -c "import numpy; print('✓ NumPy: OK')" 2>nul || echo ✗ NumPy not found
%PYTHON_CMD% -c "import PyInstaller; print('✓ PyInstaller: OK')" 2>nul || echo ✗ PyInstaller not found
echo.

pause
echo.

REM Step 3: Check for lung_asp.spec file
echo Step 3: Checking for lung_asp.spec file...
if not exist lung_asp.spec (
    echo ERROR: lung_asp.spec file not found!
    echo.
    echo This file is required for building the executable.
    echo.
    echo Please ensure you have downloaded all files from the repository.
    echo The file should be in the root directory: %CD%
    echo.
    echo You can download it from:
    echo   https://github.com/nittinnm22-sudo/breast-ASP/blob/main/lung_asp.spec
    echo.
    pause
    exit /b 1
)
echo ✓ lung_asp.spec found
echo.

REM Step 4: Install lung_asp package
echo Step 4: Installing lung_asp package...
%PIP_CMD% install -e .
if errorlevel 1 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)
echo ✓ Package installed
echo.

REM Step 5: Test CLI
echo Step 5: Testing CLI functionality...
%PYTHON_CMD% lung_asp_cli.py --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: CLI test failed
    pause
    exit /b 1
)
echo ✓ CLI test passed
echo.

REM Step 6: Clean previous builds
echo Step 6: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✓ Cleaned
echo.

REM Step 7: Build with PyInstaller
echo Step 7: Building executable with PyInstaller...
echo This may take 5-15 minutes...
echo.

%PYINSTALLER_CMD% lung_asp.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo ✓ Build completed successfully!
echo.

REM Step 8: Verify build
echo Step 8: Verifying build...

if exist dist\lung_asp\lung_asp.exe (
    echo ✓ Executable found
    
    REM Test executable
    echo.
    echo Testing executable...
    dist\lung_asp\lung_asp.exe --help >nul 2>&1
    if errorlevel 1 (
        echo ⚠ Executable test failed ^(might still work^)
    ) else (
        echo ✓ Executable test passed
    )
) else (
    echo ERROR: Executable not found
    pause
    exit /b 1
)
echo.

REM Step 9: Summary
echo ==========================================
echo        BUILD SUCCESSFUL!
echo ==========================================
echo.
echo 📦 Executable location: dist\lung_asp\
echo 🚀 Main executable: dist\lung_asp\lung_asp.exe
echo.
echo To test:
echo   dist\lung_asp\lung_asp.exe --help
echo.
echo To package for distribution:
echo   cd dist
echo   tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
echo   cd ..
echo.

REM Optional: Create package
set /p CREATE_PKG="Create distributable ZIP package now? (y/n): "
if /i "%CREATE_PKG%"=="y" (
    echo Creating package...
    cd dist
    tar -a -c -f lung_asp_v1.0.0_windows.zip lung_asp
    if errorlevel 1 (
        echo ERROR: Failed to create ZIP
        echo You can manually zip the dist\lung_asp folder
    ) else (
        echo ✓ Package created: dist\lung_asp_v1.0.0_windows.zip
    )
    cd ..
    echo.
)

echo Done! 🎉
echo.
pause
