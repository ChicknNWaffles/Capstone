const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1500,
    height: 800,
    maximizable: true,
    minimizable: true,
  });

  mainWindow.maximize();
  mainWindow.setMenu(null);

  //mainWindow.loadURL("http://127.0.0.1:8000/login");
  //mainWindow.loadURL("http://127.0.0.1:8000/signup");
  //mainWindow.loadURL("http://127.0.0.1:8000/");
  mainWindow.loadURL("http://127.0.0.1:8000/editor");
  mainWindow.webContents.openDevTools();
}

app.whenReady().then(createWindow);
