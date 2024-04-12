const {
    ipcRenderer,
    shell
} = require('electron');

document.addEventListener('DOMContentLoaded', () => {
    toggleSection('GeneralInformation');
});

const loader = document.createElement('div');
loader.classList.add('loader');

function getVideoInfo() {
    const urlInput = document.getElementById('urlInput').value;
    const resultContainer = document.getElementById('result');
    resultContainer.innerHTML = '';
    resultContainer.appendChild(loader);
    ipcRenderer.send('getVideoInfo', urlInput);
}

ipcRenderer.on('videoInfo', (event, result) => {
    const resultContainer = document.getElementById('result');
    resultContainer.innerHTML = formatResult(result.response.info, result.response.media);
});

ipcRenderer.on('openExternalLink', (event, link) => {
    shell.openExternal(link);
});

function formatResult(info, media) {
    let formattedResult = '<div class="category" onclick="toggleSection(\'GeneralInformation\')">General Information</div>';
    formattedResult += '<ul id="GeneralInformation" class="section">';

    const generalInfoKeys = {
        'URL': info.short_url,
        'ID': info.id,
        'Title': info.title,
        'Channel': info.channel_name,
        'Duration': formatDuration(info.duration),
        'Views count': info.views,
        'Likes count': info.likes,
        'Comments count': info.comments,
        'Tags': info.tags.join(', '),
        'Categories': info.categories.join(', '),
        'Age restricted': info.is_age_restricted ? 'Yes' : 'No',
        'Upload date': new Date(info.upload_date * 1000).toLocaleDateString()
    };

    for (const [key, value] of Object.entries(generalInfoKeys)) {
        formattedResult += `<li><strong>${key}:</strong> ${value || 'None'}</li>`;
    }

    formattedResult += '</ul>';

    if (media.video && media.video.length > 0) {
        const sortedVideoUrls = media.video.sort((a, b) => {
            if (a.quality !== b.quality) {
                return compareQualities(a.quality, b.quality);
            } else {
                return b.bitrate - a.bitrate;
            }
        });

        formattedResult += '<div class="category" onclick="toggleSection(\'VideoDirectURLs\')">Video Direct URLs</div>';
        formattedResult += '<ul id="VideoDirectURLs" class="section" style="display:none;">';

        sortedVideoUrls.forEach((video) => {
            const videoInfo = `${video.quality} - ${video.bitrate} kbps - ${video.codec} - ${formatBytes(video.size)}`;
            formattedResult += `<li><a href="#" onclick="openLink('${video.url}')">${videoInfo}</a></li>`;
        });

        formattedResult += '</ul>';
    }

    if (media.audio && media.audio.length > 0) {
        formattedResult += '<div class="category" onclick="toggleSection(\'AudioDirectURLs\')">Audio Direct URLs</div>';
        formattedResult += '<ul id="AudioDirectURLs" class="section" style="display:none;">';

        media.audio.sort((a, b) => b.bitrate - a.bitrate).forEach((audio) => {
            const audioInfo = `${audio.bitrate} kbps - ${audio.codec} - ${formatBytes(audio.size)}`;
            formattedResult += `<li><a href="#" onclick="openLink('${audio.url}')">${audioInfo}</a></li>`;
        });

        formattedResult += '</ul>';
    }

    return formattedResult;
}

function formatBytes(bytes) {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Byte';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}

function compareQualities(qualityA, qualityB) {
    const order = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p'];
    return order.indexOf(qualityB) - order.indexOf(qualityA);
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${pad(hours)}:${pad(minutes)}:${pad(remainingSeconds)}`;
}

function pad(value) {
    return value < 10 ? `0${value}` : value;
}

function toggleSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach((section) => {
        section.style.display = 'none';
    });

    const section = document.getElementById(sectionId);
    section.style.display = 'block';
}

function openLink(link) {
    ipcRenderer.send('openExternalLink', link);
}
