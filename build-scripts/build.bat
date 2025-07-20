@echo off
REM Housing Dashboard Build Script for Windows
REM This script builds the desktop application for distribution

echo 🏠 Building Housing Dashboard Desktop Application...

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    exit /b 1
)

echo 📦 Installing Node.js dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    exit /b 1
)

echo 🐍 Installing Python dependencies...
call python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    exit /b 1
)

echo 🔨 Building Electron application...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Failed to build application
    exit /b 1
)

echo ✅ Build complete! Check the 'dist' folder for the application packages.
echo.
echo 📁 Distribution files:
dir dist\

pause