# Built-in imports
from pathlib import Path
from datetime import datetime
from typing import List

# Third-party imports
from streamsnapper import Snapper, StreamBaseError

# Local imports
from utils.config import Config
from utils.general import (
    ColoredTerminalText as Color,
    CustomBracket as Bracket,
    init_colorama,
    set_terminal_title,
    add_directory_to_system_path,
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
from utils.functions import download_file, update_media_metadata


def main() -> None:
    # Initialize Colorama for colored terminal output
    init_colorama(autoreset=True)

    # Set the terminal title
    set_terminal_title(Config, Config.fancy_name + ' ' + Config.version + ' - by gh@Henrique-Coder')

    # Check if the app version is up-to-date
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking if the application is up-to-date...')
    latest_app_version = get_latest_app_version()
    clear_terminal(Config)

    if latest_app_version is not None:
        if Config.version != latest_app_version:
            input(
                f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}The local version of the application is out of date, the latest version available is {Color.green}{latest_app_version}'
                f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}Download it at {Color.blue}https://github.com/Henrique-Coder/syncgroove/releases/tag/{latest_app_version} {Color.yellow}or press ENTER to continue and use it anyway (not recommended)'
            )
    else:
        input(f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}Failed to check the latest version of the application, restart the application to try again or press ENTER to continue and use it anyway (not recommended)')

    # Create the required directories
    make_dirs(Config.temporary_path)
    make_dirs(Config.main_path)
    make_dirs(Config.main_resources_path)
    make_dirs(Config.media_path)
    make_dirs(Config.default_downloaded_musics_path)
    make_dirs(Config.tools_path, ['ffmpeg'])

    # Add required directories to the system PATH
    add_directory_to_system_path(Path(Config.tools_path, 'ffmpeg'))

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

    # Check if FFmpeg binary file exists, if not, download it
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking and downloading the latest FFmpeg binary files (if necessary)...')
    download_latest_ffmpeg(Config)
    clear_terminal(Config)

    # Ask the user if they want to load the queries from a file or write them manually
    print(
        f'{Bracket('+', Color.yellow, 1)} {Color.yellow}You can load your queries from a {Color.cyan}local file {Color.yellow}or simply {Color.cyan}write them manually{Color.yellow}.'
        f'\n\n{Bracket('-', Color.white)} {Color.white}To choose a local file, leave the input below blank and press ENTER.'
        f'\n{Bracket('-', Color.white)} {Color.white}To write the queries, type in the song name or song link and press ENTER.'
        f'\n\n{Bracket('#', Color.red)} {Color.red}The list of links/queries must have one item per line; if the last line is empty, the download will start'
    )

    user_input = input(f'{Color.light_white} ›{Color.blue} ').strip()

    class InputQueries:
        _queries: List[str] = []
        _urls: List[str] = []

        class SortedURLs:
            pass

    # Load queries from a file
    if not user_input:
        clear_terminal(Config, 1)
        print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Loading queries from a file...')

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
            validation_value = is_valid_url(query, online_check=True)

            if validation_value:
                InputQueries._urls.append(query)
            elif validation_value is False:
                InputQueries._queries.append(query)

    # Write queries manually
    else:
        validation_value = is_valid_url(user_input, online_check=True)

        if validation_value:
            InputQueries._urls.append(user_input)
        elif validation_value is False:
            InputQueries._queries.append(user_input)

        while True:
            query = input(f'{Color.light_white} ›{Color.blue} ').strip()

            if not query:
                break

            validation_value = is_valid_url(query, online_check=True)

            if validation_value:
                InputQueries._urls.append(query)
            elif validation_value is False:
                InputQueries._queries.append(query)

    clear_terminal(Config)
    print(f'{Bracket('info', Color.blue, 1)} {Color.blue}The queries/URLs are being processed. This can take a while...')

    # Sort the URLs by their type
    InputQueries = sort_urls_by_type_and_domain(InputQueries)

    # Download the media files
    clear_terminal(Config)

    # Initialize the Snapper object
    snapper = Snapper(enable_ytdlp_log=False)

    for url in InputQueries.SortedURLs.youtube.single_urls:
        try:
            snapper.run(url)
        except Exception as e:
            print(f'{Bracket('error', Color.red, 1)} {Color.red}An error occurred while processing the URL {Color.cyan}{url}{Color.red}: {e}')

        snapper.analyze_media_info()
        snapper.analyze_audio_streams(preferred_language='auto')

        media_info = snapper.media_info
        stream_info = snapper.best_audio_stream

        print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Downloading {Color.cyan}{stream_info['size']} bytes {Color.blue}from {Color.cyan}{media_info['title']}{Color.blue} by {Color.cyan}{media_info['channelName']}')
        media_path = Path(Config.default_downloaded_musics_path, f'{media_info['cleanTitle']}.{stream_info['extension']}').resolve()
        # cover_image_path = Path(Config.temporary_path, f'.tmp_{media_info['id']}_cover.jpg').resolve()

        # download_file(url=media_info['thumbnails'][0], output_path=cover_image_path, max_connections=1, enable_progress_bar=False)
        download_file(url=stream_info['url'], output_path=media_path, max_connections=4)

        # update_media_metadata(path=media_path, title=media_info['title'], artist=media_info['channelName'], year=datetime.fromtimestamp(media_info['uploadTimestamp']).year, language=stream_info['language'], cover_image_path=cover_image_path)

    input(f'{Bracket('info', Color.green, 1)} {Color.green}All media files have been downloaded successfully!')
