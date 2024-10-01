# Built-in imports
from pathlib import Path
from datetime import datetime
from logging import getLogger, CRITICAL
from typing import List
from sys import exit

# Third-party imports
from streamsnapper import Snapper, StreamBaseError

# Local imports
from utils.config import Config
from utils.general import (
    ColoredTerminalText as Color,
    CustomBracket as Bracket,
    init_colorama,
    set_terminal_title,
    # add_directory_to_system_path,
    is_valid_url,
    clear_terminal,
    make_dirs,
    download_app_icon,
    is_image_corrupted,
    download_latest_ffmpeg,
    open_windows_filedialog_selector,
    get_latest_app_version,
    extract_lines_from_file
)
from utils.classifier import sort_urls_by_type_and_domain
from utils.functions import download_file, transcode_and_edit_metadata


class InputQueriesTemplate:
    def __init__(self) -> None:
        self._queries: List[str] = []
        self._urls: List[str] = []

        class SortedURLs:
            class youtube:
                def __init__(self) -> None:
                    pass

            class youtube_music:
                def __init__(self) -> None:
                    pass

        self.SortedURLs = SortedURLs()


def main() -> None:
    # Initialize Colorama for colored terminal output
    init_colorama(autoreset=True)

    # Set the terminal title
    set_terminal_title(Config, f'{Config.fancy_name} {Config.version} - by gh@Henrique-Coder')

    # Check if the app version is up-to-date
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking if the application is up-to-date...')
    latest_app_version = get_latest_app_version()
    clear_terminal(Config)

    if latest_app_version is not None:
        if Config.version < latest_app_version:
            input(
                f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}The local version of the application is out of date, the latest version available is {Color.green}{latest_app_version}'
                f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}Download it at {Color.blue}https://github.com/Henrique-Coder/syncgroove/releases/tag/v{latest_app_version} {Color.yellow}or press ENTER to continue and use it anyway (not recommended)'
            )
    else:
        input(f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}Failed to check the latest version of the application, restart the application to try again or press ENTER to continue and use it anyway (not recommended)')

    # Create the required directories
    make_dirs(Config.temporary_path)
    make_dirs(Config.main_path)
    make_dirs(Config.main_resources_path)
    make_dirs(Config.media_path)
    make_dirs(Config.default_downloaded_musics_path)

    # Add required directories to the system PATH
    # ...

    # Check if application icon file exists, if not, download it
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking if the application icon file exists...')
    app_icon_path = Path(Config.media_path, 'icon.ico')

    if not app_icon_path.exists():
        clear_terminal(Config)
        print(f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}The application icon file does not exist, downloading it...')
        download_app_icon(app_icon_path)
    elif is_image_corrupted(app_icon_path):
        clear_terminal(Config)
        print(f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}The application icon file exists but is corrupted, re-downloading it...')
        download_app_icon(app_icon_path)
    else:
        clear_terminal(Config)
        print(f'{Bracket('success', Color.green, 1)} {Color.green}The application icon file exists and is working properly')

    # Set the logging level to CRITICAL for the FFmpeg and FFprobe classes
    getLogger('pyffmpeg.pseudo_ffprobe.FFprobe').setLevel(CRITICAL)
    getLogger('pyffmpeg.misc.Paths').setLevel(CRITICAL)

    # Check if FFmpeg binary file exists, if not, download it
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking and downloading the latest FFmpeg binary files (if necessary)...')
    download_latest_ffmpeg(Config)
    clear_terminal(Config)

    # Initialize the InputQueries object
    InputQueries = InputQueriesTemplate()

    # Ask the user if they want to load the queries from a file or write them manually
    print(
        f'{Bracket('+', Color.yellow, 1)} {Color.yellow}You can load your queries from a {Color.cyan}local file {Color.yellow}or simply {Color.cyan}write them manually{Color.yellow}.'
        f'\n\n{Bracket('-', Color.white)} {Color.white}To choose a local file, leave the first input below blank and press ENTER.'
        f'\n{Bracket('-', Color.white)} {Color.white}To write the queries, type in the song name or song link and press ENTER.'
        f'\n\n{Bracket('#', Color.red)} {Color.red}The list of links/queries must have one item per line; if the last line is empty, the download will start'
    )

    # Ask the user to choose the input method
    user_input = input(f'{Color.light_white} ›{Color.blue} ').strip()

    # Load queries from a file
    if not user_input:
        clear_terminal(Config, 1)
        print(f'{Bracket('info', Color.blue)} {Color.blue}Loading queries from a file...')

        queries_filepath = open_windows_filedialog_selector('Select a file with the URLs/Queries (one by line)', [('Text files', '*.txt'), ('All files', '*.*')])

        if not queries_filepath:
            clear_terminal(Config, 1)
            print(f'{Bracket('error', Color.red, 1)} {Color.red}No file selected, exiting...')
            exit(1)

        extracted_queries = extract_lines_from_file(queries_filepath, fix_lines=True)

        if not extracted_queries:
            clear_terminal(Config, 1)
            print(f'{Bracket('error', Color.red, 1)} {Color.red}The file is empty or cannot be read, exiting...')
            exit(1)

        for query in extracted_queries:
            validation_value = is_valid_url(query, online_check=False)

            if validation_value:
                InputQueries._urls.append(query)
            elif validation_value is False:
                InputQueries._queries.append(query)

    # Write queries manually
    else:
        validation_value = is_valid_url(user_input, online_check=False)

        if validation_value:
            InputQueries._urls.append(user_input)
        elif validation_value is False:
            InputQueries._queries.append(user_input)

        while True:
            query = input(f'{Color.light_white} ›{Color.blue} ').strip()

            if not query:
                break

            validation_value = is_valid_url(query, online_check=False)

            if validation_value:
                InputQueries._urls.append(query)
            elif validation_value is False:
                InputQueries._queries.append(query)

    clear_terminal(Config)
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}The following queries/URLs are being processed. This may take some time...')
    print(f'{Bracket('info', Color.blue)} {Color.blue}Queries ({Color.cyan}{len(InputQueries._queries)}{Color.blue} item(s): {Color.cyan}{InputQueries._queries}')
    print(f'{Bracket('info', Color.blue)} {Color.blue}URLs ({Color.cyan}{len(InputQueries._urls)}{Color.blue} item(s)): {Color.cyan}{InputQueries._urls}')

    # Sort the URLs by their type
    InputQueries = sort_urls_by_type_and_domain(InputQueries)

    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}The queries/URLs have been successfully processed and sorted by type and domain, below you will see a summary of the process carried out.')
    print(f'{Bracket('info', Color.blue)} {Color.blue}1. {Color.cyan}{InputQueries.SortedURLs.youtube.fancy_name} {Color.light_blue}[Final Single] {Color.blue}({Color.cyan}{len(InputQueries.SortedURLs.youtube.single_urls)} URL(s){Color.blue}): {Color.cyan}{InputQueries.SortedURLs.youtube.single_urls}')
    print(f'{Bracket('info', Color.blue)} {Color.blue}1.1 {Color.cyan}{InputQueries.SortedURLs.youtube.fancy_name} {Color.blue}[Single] ({Color.cyan}{len(InputQueries.SortedURLs.youtube.mixed_urls['single'])} URL(s){Color.blue}): {Color.cyan}{InputQueries.SortedURLs.youtube.mixed_urls['single']}')
    print(f'{Bracket('info', Color.blue)} {Color.blue}1.2 {Color.cyan}{InputQueries.SortedURLs.youtube.fancy_name} {Color.blue}[Playlist] ({Color.cyan}{len(InputQueries.SortedURLs.youtube.mixed_urls['playlist'])} URL(s){Color.blue}): {Color.cyan}{InputQueries.SortedURLs.youtube.mixed_urls['playlist']}')
    print(f'{Bracket('info', Color.blue)} {Color.blue}2. {Color.cyan}{InputQueries.SortedURLs.youtube_music.fancy_name} {Color.light_blue}[Final Single] {Color.blue}({Color.cyan}{len(InputQueries.SortedURLs.youtube_music.single_urls)} URL(s){Color.blue}): {Color.cyan}{InputQueries.SortedURLs.youtube_music.single_urls}')
    print(f'{Bracket('info', Color.blue)} {Color.blue}2.1 {Color.cyan}{InputQueries.SortedURLs.youtube_music.fancy_name} {Color.blue}[Single] ({Color.cyan}{len(InputQueries.SortedURLs.youtube_music.mixed_urls['single'])} URL(s){Color.blue}): {Color.cyan}{InputQueries.SortedURLs.youtube_music.mixed_urls['single']}')
    print(f'{Bracket('info', Color.blue)} {Color.blue}2.2 {Color.cyan}{InputQueries.SortedURLs.youtube_music.fancy_name} {Color.blue}[Playlist] ({Color.cyan}{len(InputQueries.SortedURLs.youtube_music.mixed_urls['playlist'])} URL(s){Color.blue}): {Color.cyan}{InputQueries.SortedURLs.youtube_music.mixed_urls['playlist']}')

    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Starting the download process...')

    # Initialize the Snapper object
    snapper = Snapper(enable_ytdlp_log=False)

    for url in InputQueries.SortedURLs.youtube.single_urls + InputQueries.SortedURLs.youtube_music.single_urls:
        print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Extracting information from the URL {Color.cyan}{url}{Color.blue}...')
        try:
            snapper.run(url)
        except Exception as e:
            print(f'{Bracket('error', Color.red, 1)} {Color.red}An error occurred while processing the URL {Color.cyan}{url}{Color.red}: {e}')
            continue

        snapper.analyze_media_info()
        snapper.analyze_audio_streams(preferred_language='auto')

        media_info = snapper.media_info
        stream_info = snapper.best_audio_stream

        cover_image_path = Path(Config.temporary_path, f'.tmp_{media_info['id']}_cover.jpg').resolve()
        audio_path = Path(Config.default_downloaded_musics_path, f'{media_info['cleanTitle']}.{stream_info['extension']}').resolve()

        print(f'{Bracket('info', Color.blue)} {Color.blue}Downloading {Color.cyan}{stream_info['size']} bytes {Color.blue}from {Color.cyan}{media_info['title']}{Color.blue} by {Color.cyan}{media_info['channelName']}{Color.blue} to {Color.cyan}{audio_path.as_posix()}')
        download_file(url=media_info['thumbnails'][0], output_path=cover_image_path, max_connections=1)
        download_file(url=stream_info['url'], output_path=audio_path, max_connections=6)

        print(f'{Bracket('info', Color.blue)} {Color.blue}Transcoding audio to {Color.cyan}OPUS {Color.blue}codec and adding metadata...')
        transcode_and_edit_metadata(path=audio_path, output_path=audio_path.with_suffix('.opus'), bitrate=int(stream_info['bitrate']), title=media_info['title'], artist=media_info['channelName'], year=datetime.fromtimestamp(media_info['uploadTimestamp']).year, cover_image=cover_image_path)
        print(f'{Bracket('success', Color.green)} {Color.green}The audio file has been downloaded and processed successfully to {Color.light_green}{audio_path.with_suffix('.opus').as_posix()}')

        # Exit the application
        total_downloaded_musics = len(InputQueries.SortedURLs.youtube.single_urls) + len(InputQueries.SortedURLs.youtube_music.single_urls)
        input(f'{Bracket('info', Color.light_green, 1)} {Color.light_green}The download process has been completed successfully, {Color.green}{total_downloaded_musics} music(s) {Color.light_green}have been downloaded and processed, press any key to exit...')
        exit(0)


if __name__ == '__main__':
    clear_terminal(Config)
    main()

# Alok, Bruno Martini feat. Zeeba - Hear Me Now (Official Music Video)
# https://www.youtube.com/watch?v=4N1iwQxiHrs
# https://www.youtube.com/playlist?list=PLRBp0Fe2GpgnymQGm0yIxcdzkQsPKwnBD
