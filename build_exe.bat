@echo off
REM Build script for Lung-ASP standalone executable (Windows)

echo ========================================
echo Lung-ASP Executable Build Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv_build" (
    echo Creating virtual environment...
    python -m venv venv_build
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_build\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
echo This may take a while (especially PyTorch)...
pip install -r requirements_exe.txt

REM Install the package
echo Installing lung_asp package...
pip install -e .

REM Information about models
echo.
echo Note: Pre-trained models should be downloaded separately
echo   - TotalSegmentor: Run 'totalsegmentor --download_models'
echo   - nnU-Net: Place models in appropriate directory
echo.

REM Build with PyInstaller
echo Building executable with PyInstaller...
pyinstaller lung_asp.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\lung_asp" (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable location: dist\lung_asp\
    echo Main executable: dist\lung_asp\lung_asp.exe
    echo.
    echo To run:
    echo   dist\lung_asp\lung_asp.exe --help
    echo.
    echo To package for distribution:
    echo   - Use 7-Zip or WinRAR to create an archive
    echo   - Or use: tar -czf lung_asp_v1.0.0_windows.zip dist\lung_asp\
    echo.
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
    echo Check the output above for errors.
    exit /b 1
)

echo.
echo Done!
pause
