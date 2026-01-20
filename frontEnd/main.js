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
    mainWindow.loadFile("frontEnd/templates/temp.html");
}



app.whenReady().then(() => {
    createWindow()
})