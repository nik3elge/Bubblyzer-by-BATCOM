@echo off
title Bubblyzer by BATCOM
cd /d "%~dp0\.."
echo ======================================================
echo           Starting Bubblyzer by BATCOM...
echo ======================================================
python src\main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Could not start Bubblyzer. Check if Python is in PATH.
    pause
)
