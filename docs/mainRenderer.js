const { ipcRenderer, shell } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
    toggleSection('GeneralInformation');
});

function getVideoInfo() {
    const urlInput = document.getElementById('urlInput').value;
    ipcRenderer.send('getVideoInfo', urlInput);
}

ipcRenderer.on('videoInfo', (event, result) => {
    document.getElementById('result').innerHTML = formatResult(result);
});

ipcRenderer.on('openExternalLink', (event, link) => {
    shell.openExternal(link);
});

function formatResult(result) {
    if (result.error) {
        return `<p>Error: ${result.error}</p>`;
    }

    let formattedResult = '<div class="category" onclick="toggleSection(\'GeneralInformation\')">General Information</div>';
    formattedResult += '<ul id="GeneralInformation" class="section">';
    
    const generalInfoKeys = ['URL', 'ID', 'Title', 'Channel', 'Duration', 'Views count', 'Likes count', 'Comments count', 'Tags', 'Categories', 'Age restricted', 'Upload date'];

    for (const key of generalInfoKeys) {
        if (result.output.data.info[key.toLowerCase()] !== undefined) {
            const niceKey = key.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            const value = key === 'Duration' ? formatDuration(result.output.data.info[key.toLowerCase()]) : result.output.data.info[key.toLowerCase()] || 'None';
            formattedResult += `<li><strong>${niceKey}:</strong> ${value}</li>`;
        }
    }

    formattedResult += '</ul>';

    if (result.output.data.media.video && result.output.data.media.video.length > 0) {
        formattedResult += '<div class="category" onclick="toggleSection(\'VideoDirectURLs\')">Video Direct URLs</div>';
        formattedResult += '<ul id="VideoDirectURLs" class="section" style="display:none;">';

        result.output.data.media.video.sort((a, b) => compareQualities(a.quality, b.quality)).reverse().forEach((video) => {
            const videoInfo = `${video.quality} - ${video.bitrate} kbps - ${video.codec} - ${formatBytes(video.size)}`;
            formattedResult += `<li><a href="#" onclick="openLink('${video.url}')">${videoInfo}</a></li>`;
        });

        formattedResult += '</ul>';
    }

    if (result.output.data.media.audio && result.output.data.media.audio.length > 0) {
        formattedResult += '<div class="category" onclick="toggleSection(\'AudioDirectURLs\')">Audio Direct URLs</div>';
        formattedResult += '<ul id="AudioDirectURLs" class="section" style="display:none;">';

        result.output.data.media.audio.sort((a, b) => b.bitrate - a.bitrate).forEach((audio) => {
            const audioInfo = `${audio.bitrate} kbps - ${audio.codec} - ${formatBytes(audio.size)}`;
            formattedResult += `<li><a href="#" onclick="openLink('${audio.url}')">${audioInfo}</a></li>`;
        });

        formattedResult += '</ul>';
    }

    if (result.output.data.media.subtitles && result.output.data.media.subtitles.length > 0) {
        formattedResult += '<div class="category" onclick="toggleSection(\'SubtitleDirectURLs\')">Subtitle Direct URLs</div>';
        formattedResult += '<ul id="SubtitleDirectURLs" class="section" style="display:none;">';

        result.output.data.media.subtitles.sort((a, b) => a.lang.localeCompare(b.lang)).forEach((subtitle) => {
            const subtitleInfo = `${subtitle.lang} - ${subtitle.ext}`;
            formattedResult += `<li><a href="#" onclick="openLink('${subtitle.url}')">${subtitleInfo}</a></li>`;
        });

        formattedResult += '</ul>';
    }

    return formattedResult;
}

function formatBytes(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Byte';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}

function compareQualities(qualityA, qualityB) {
    const order = ['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'];
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
