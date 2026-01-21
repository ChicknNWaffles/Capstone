const { app, BrowserWindow, Menu } = require("electron")

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1500,
        hight: 500,
        maximizable: true,
        minimizable: true
    });
    mainWindow.maximize();
    mainWindow.setMenu(null);
    //mainWindow.loadFile("frontEnd/templates/editor.html");
    mainWindow.loadURL("http://127.0.0.1:5000");

    mainWindow.webContents.openDevTools();
}



app.whenReady().then(() => {
    createWindow()
})