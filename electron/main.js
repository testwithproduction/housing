const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const findFreePort = require('find-free-port');

let mainWindow;
let streamlitProcess;
let streamlitPort = 8501;

// Keep a global reference of the window object
function createWindow() {
  // Create the browser window with enhanced security
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true,
      allowRunningInsecureContent: false,
      experimentalFeatures: false,
      preload: path.join(__dirname, 'preload.js'),
      sandbox: false, // Keep false for Streamlit compatibility
      spellcheck: false,
      devTools: isDev // Only allow DevTools in development
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    title: 'Housing Dashboard',
    show: false, // Don't show until ready
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    autoHideMenuBar: false, // Keep menu bar visible for security
    fullscreenable: true,
    maximizable: true
  });

  // Create application menu
  createMenu();

  // Handle window ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on the window
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Start Streamlit and load the app
  startStreamlitApp();
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.reload();
            }
          }
        },
        {
          label: 'Toggle Developer Tools',
          accelerator: 'F12',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Zoom In',
          accelerator: 'CmdOrCtrl+Plus',
          click: () => {
            if (mainWindow) {
              const currentZoom = mainWindow.webContents.getZoomLevel();
              mainWindow.webContents.setZoomLevel(currentZoom + 1);
            }
          }
        },
        {
          label: 'Zoom Out',
          accelerator: 'CmdOrCtrl+-',
          click: () => {
            if (mainWindow) {
              const currentZoom = mainWindow.webContents.getZoomLevel();
              mainWindow.webContents.setZoomLevel(currentZoom - 1);
            }
          }
        },
        {
          label: 'Reset Zoom',
          accelerator: 'CmdOrCtrl+0',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.setZoomLevel(0);
            }
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Housing Dashboard',
              message: 'Housing Dashboard v1.0.0',
              detail: 'A desktop application for visualizing housing market data built with Streamlit and Electron.'
            });
          }
        }
      ]
    }
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideothers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });

    // Window menu
    template.push({
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

async function findAvailablePort() {
  try {
    const ports = await findFreePort(8501, 8600);
    return ports[0];
  } catch (error) {
    console.log('Using default port 8501');
    return 8501;
  }
}

async function startStreamlitApp() {
  try {
    // Find an available port
    streamlitPort = await findAvailablePort();
    
    // Path to Python and Streamlit app
    const pythonPath = isDev ? 'python' : path.join(process.resourcesPath, 'python-dist', 'python');
    const appPath = isDev ? 'streamlit_app.py' : path.join(process.resourcesPath, 'streamlit_app.py');
    
    // Start Streamlit process using launcher script
    const launcherPath = isDev ? 'launcher.py' : path.join(process.resourcesPath, 'launcher.py');
    const streamlitArgs = [
      launcherPath,
      '--server.port', streamlitPort.toString()
    ];

    console.log('Starting Streamlit with:', pythonPath, streamlitArgs);
    
    streamlitProcess = spawn(pythonPath, streamlitArgs, {
      stdio: isDev ? 'inherit' : 'pipe'
    });

    streamlitProcess.on('error', (error) => {
      console.error('Failed to start Streamlit:', error);
      showErrorDialog('Failed to start the application. Please check if Python and required dependencies are installed.');
    });

    streamlitProcess.on('exit', (code) => {
      console.log(`Streamlit process exited with code ${code}`);
      if (code !== 0 && mainWindow) {
        showErrorDialog('The application stopped unexpectedly.');
      }
    });

    // Wait for Streamlit to start, then load the page
    setTimeout(() => {
      const url = `http://localhost:${streamlitPort}`;
      console.log('Loading Streamlit app at:', url);
      mainWindow.loadURL(url).catch(err => {
        console.log('Retrying connection in 2 seconds...');
        setTimeout(() => {
          mainWindow.loadURL(url);
        }, 2000);
      });
    }, 4000);

  } catch (error) {
    console.error('Error starting Streamlit:', error);
    showErrorDialog('Failed to start the application.');
  }
}

function showErrorDialog(message) {
  if (mainWindow) {
    dialog.showErrorBox('Application Error', message);
  }
}

function stopStreamlitApp() {
  if (streamlitProcess) {
    streamlitProcess.kill();
    streamlitProcess = null;
  }
}

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  stopStreamlitApp();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopStreamlitApp();
});

// Enhanced Security: Prevent new window creation and navigation
app.on('web-contents-created', (event, contents) => {
  // Prevent new window creation
  contents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Block navigation to external URLs
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    
    if (parsedUrl.origin !== `http://localhost:${streamlitPort}`) {
      event.preventDefault();
      shell.openExternal(navigationUrl);
    }
  });

  // Block downloads except from trusted sources
  contents.session.on('will-download', (event, item, webContents) => {
    // Allow downloads only from localhost (our Streamlit app)
    const url = item.getURL();
    if (!url.startsWith(`http://localhost:${streamlitPort}`)) {
      event.preventDefault();
    }
  });
});

// Prevent protocol handler abuse
app.on('web-contents-created', (event, contents) => {
  contents.on('will-redirect', (event, url) => {
    if (!url.startsWith(`http://localhost:${streamlitPort}`)) {
      event.preventDefault();
    }
  });
});