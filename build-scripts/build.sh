#!/bin/bash

# Housing Dashboard Build Script
# This script builds the desktop application for distribution

set -e  # Exit on any error

echo "🏠 Building Housing Dashboard Desktop Application..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "📦 Installing Node.js dependencies..."
npm install

echo "🐍 Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

echo "🔨 Building Electron application..."
npm run build

echo "✅ Build complete! Check the 'dist' folder for the application packages."
echo ""
echo "📁 Distribution files:"
ls -la dist/