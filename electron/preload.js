// Preload script for security and context isolation
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any secure API methods here if needed in the future
  platform: process.platform,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  }
});

// Prevent context menu (optional - for cleaner desktop app experience)
window.addEventListener('contextmenu', (e) => {
  e.preventDefault();
});

// Prevent drag and drop of files (security)
window.addEventListener('dragover', (e) => {
  e.preventDefault();
});

window.addEventListener('drop', (e) => {
  e.preventDefault();
});