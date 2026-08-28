@echo off
title Build Bubblyzer by BATCOM
cd /d "%~dp0"
echo ========================================================
echo       Building Standalone Bubblyzer.exe with PyInstaller
echo ========================================================

echo.
echo [1/3] Checking model file...
if not exist "comic-speech-bubble-detector.onnx" (
    echo Model comic-speech-bubble-detector.onnx not found!
    echo Running export_onnx.py first...
    python export_onnx.py
)

echo.
echo [2/3] Running PyInstaller...
pyinstaller --clean bubblyzer.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check PyInstaller output above.
    pause
    exit /b 1
)

echo.
echo [3/3] Build Complete!
echo The standalone executable is located in: dist\Bubblyzer.exe
echo ========================================================
pause
