# Housing Dashboard Desktop Application

This guide explains how to build and run the Housing Dashboard as a desktop application using Electron.

## Prerequisites

1. **Node.js** (version 16 or higher)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify installation: `node --version`

2. **Python** (version 3.8 or higher)
   - Download from [python.org](https://python.org/)
   - Verify installation: `python --version` or `python3 --version`

3. **Git** (for cloning the repository)
   - Download from [git-scm.com](https://git-scm.com/)

## Quick Start

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run in Development Mode

```bash
# Start the desktop app in development mode
npm run electron-dev
```

This will:
- Start the Streamlit app on a free port
- Open the Electron window
- Enable developer tools for debugging

### 3. Build for Distribution

#### Option A: Use Build Scripts (Recommended)

**macOS/Linux:**
```bash
./build-scripts/build.sh
```

**Windows:**
```bash
build-scripts\build.bat
```

#### Option B: Manual Build Commands

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build-win    # Windows
npm run build-mac    # macOS
npm run build-linux  # Linux
```

## File Structure

```
housing/
├── electron/
│   ├── main.js          # Main Electron process
│   ├── preload.js       # Security preload script
│   └── assets/          # App icons (add your own)
├── build-scripts/
│   ├── build.sh         # Build script for macOS/Linux
│   └── build.bat        # Build script for Windows
├── streamlit_app.py     # Your Streamlit application
├── package.json         # Node.js configuration
└── dist/               # Built applications (after build)
```

## Application Features

### Desktop Integration
- **Native Window**: Proper desktop window with title bar
- **Menu Bar**: File, View, and Help menus with keyboard shortcuts
- **System Integration**: Dock/taskbar icon, window management
- **Zoom Controls**: Ctrl/Cmd + Plus/Minus for zooming

### Security Features
- **Context Isolation**: Secure separation between main and renderer processes
- **No Node Integration**: Prevents security vulnerabilities
- **External Link Handling**: Opens external links in default browser

### Performance
- **Port Detection**: Automatically finds available ports for Streamlit
- **Process Management**: Properly starts/stops Streamlit with the app
- **Error Handling**: User-friendly error messages

## Distribution

After building, you'll find the packaged applications in the `dist/` folder:

- **Windows**: `.exe` installer and unpacked files
- **macOS**: `.dmg` disk image and `.app` bundle
- **Linux**: `.AppImage` portable executable

## Development Commands

```bash
# Install dependencies
npm install

# Run in development mode (with DevTools)
npm run electron-dev

# Run in production mode
npm run electron

# Build for all platforms
npm run build

# Build for specific platform
npm run build-win
npm run build-mac
npm run build-linux

# Create package directory without installer
npm run pack
```

## Customization

### App Icons
Place your app icons in `electron/assets/`:
- `icon.png` - Linux (512x512 PNG)
- `icon.ico` - Windows (ICO format)
- `icon.icns` - macOS (ICNS format)

### Window Settings
Edit `electron/main.js` to customize:
- Window size and minimum dimensions
- Title bar style
- Menu items
- Keyboard shortcuts

### Build Configuration
Edit `package.json` build section to customize:
- App metadata (name, description, author)
- Target platforms and architectures
- Installer options
- File inclusion/exclusion

## Troubleshooting

### Common Issues

1. **"Python not found" error**
   - Ensure Python is installed and in your PATH
   - Try using `python3` instead of `python`

2. **Port already in use**
   - The app automatically finds free ports
   - If issues persist, check for other Streamlit instances

3. **Build fails on macOS**
   - Install Xcode Command Line Tools: `xcode-select --install`
   - Ensure you have proper code signing setup for distribution

4. **Windows build issues**
   - Install Windows Build Tools: `npm install -g windows-build-tools`
   - Run PowerShell as Administrator

### Debug Mode

Run with debug output:
```bash
DEBUG=* npm run electron-dev
```

### Logs Location
- **Windows**: `%USERPROFILE%\AppData\Roaming\housing-dashboard\logs`
- **macOS**: `~/Library/Logs/housing-dashboard`
- **Linux**: `~/.cache/housing-dashboard/logs`

## Production Deployment

For production deployment:

1. **Code Signing** (recommended for distribution)
   - Windows: Use a code signing certificate
   - macOS: Use Apple Developer account
   - Linux: No signing required

2. **Auto-updater** (optional)
   - Consider implementing electron-updater for automatic updates

3. **Crash Reporting** (optional)
   - Integrate with services like Sentry for error tracking

## Support

For issues specific to the desktop app wrapper, check:
1. Electron logs in the app's log directory
2. Developer console (F12 in development mode)
3. Streamlit logs in the terminal/console