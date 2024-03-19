const {
    app,
    BrowserWindow,
    ipcMain,
    shell
} = require('electron');
const axios = require('axios');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 700,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });

    mainWindow.loadFile('src/index.html');
    mainWindow.removeMenu();
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

function extractVideoId(url) {
    const regex = /(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

ipcMain.on('getVideoInfo', async (event, url) => {
    const videoId = extractVideoId(url);

    if (!videoId) {
        console.error('Invalid video URL');
        event.reply('videoInfo', {
            error: 'Invalid video URL'
        });
        return;
    }

    try {
        const response = await axios.get(`http://node1.mindwired.com.br:8452/api/scraper/v1/video-youtube.com?id=${videoId}`);
        event.reply('videoInfo', response.data);
    } catch (error) {
        console.error(`Error fetching video information: ${error.message}`);
        event.reply('videoInfo', {
            error: `Error fetching video information: ${error.message}`
        });
    }
});

ipcMain.on('openExternalLink', (event, link) => {
    shell.openExternal(link);
});
