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

  //mainWindow.loadURL("http://127.0.0.1:5000");
  mainWindow.loadURL("http://127.0.0.1:5000/login");
  //mainWindow.loadURL("http://127.0.0.1:5000/signup");
  mainWindow.webContents.openDevTools();
}

app.whenReady().then(createWindow);
