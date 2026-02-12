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

REM Step 1: Check Python version
echo Step 1: Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8-3.11
    pause
    exit /b 1
)
echo.

REM Step 2: Check dependencies
echo Step 2: Checking installed dependencies...
python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul || echo ✗ PyTorch not found
python -c "import totalsegmentor; print('✓ TotalSegmentor: OK')" 2>nul || echo ✗ TotalSegmentor not found
python -c "import nnunetv2; print('✓ nnU-Net: OK')" 2>nul || echo ✗ nnU-Net not found
python -c "import numpy; print('✓ NumPy: OK')" 2>nul || echo ✗ NumPy not found
python -c "import PyInstaller; print('✓ PyInstaller: OK')" 2>nul || echo ✗ PyInstaller not found
echo.

pause
echo.

REM Step 3: Install lung_asp package
echo Step 3: Installing lung_asp package...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)
echo ✓ Package installed
echo.

REM Step 4: Test CLI
echo Step 4: Testing CLI functionality...
python lung_asp_cli.py --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: CLI test failed
    pause
    exit /b 1
)
echo ✓ CLI test passed
echo.

REM Step 5: Clean previous builds
echo Step 5: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✓ Cleaned
echo.

REM Step 6: Build with PyInstaller
echo Step 6: Building executable with PyInstaller...
echo This may take 5-15 minutes...
echo.

pyinstaller lung_asp.spec --clean --noconfirm

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

REM Step 7: Verify build
echo Step 7: Verifying build...

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

REM Step 8: Summary
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
