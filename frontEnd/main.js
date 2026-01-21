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

  mainWindow.loadFile(path.join(__dirname, "templates", "login.html"));
  mainWindow.webContents.openDevTools();
}

app.whenReady().then(createWindow);
