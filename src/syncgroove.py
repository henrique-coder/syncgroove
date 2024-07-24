# Built-in imports
from pathlib import Path
from time import sleep
from typing import *

# Local imports
from utils.config import Config
from utils.functions import (
    get_youtube_video_data_from_query, get_youtube_video_data_from_url
)
from utils.general import (
    ColoredTerminalText as Color,
    CustomBracket as Bracket,
    init_colorama,
    set_terminal_title,
    is_valid_url,
    clear_terminal,
    make_dirs,
    download_latest_ffmpeg,
    is_valid_ffmpeg_binary,
    open_windows_filedialog_selector,
    get_latest_app_version,
    extract_lines_from_file
)


def main() -> None:
    # Set the terminal title
    set_terminal_title(Config.fancy_name + ' ' + Config.version + ' - by gh@Henrique Coder')

    # Initialize Colorama for colored terminal output
    init_colorama(autoreset=True)

    # # Check if the app version is up-to-date
    # print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking if the application is up-to-date...')
    # latest_app_version = get_latest_app_version()
    # clear_terminal()
    #
    # if latest_app_version is not None:
    #     if Config.version != latest_app_version:
    #         input(
    #             f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}The local version of the application is out of date, the latest version available is {Color.green}{latest_app_version}'
    #             f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}Download it at {Color.blue}https://github.com/Henrique-Coder/syncgroove/releases/tag/{latest_app_version} {Color.yellow}or press ENTER to continue and use it anyway (not recommended)'
    #         )
    # else:
    #     input(f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}Failed to check the latest version of the application, restart the application to try again or press ENTER to continue and use it anyway (not recommended)')

    # Create the required directories
    make_dirs(Config.temporary_path)
    make_dirs(Config.main_path)
    make_dirs(Config.main_utils_path)
    make_dirs(Config.media_path)
    make_dirs(Config.tools_path)

    # Check if application icon file exists, if not, download it
    # ...

    # # Check if FFmpeg binary file exists, if not, download it
    # print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Checking if the FFmpeg binary file exists...')
    # ffmpeg_tool_path = Path(Config.tools_path, 'ffmpeg.exe' if Config.is_windows else 'ffmpeg')
    #
    # if not ffmpeg_tool_path.exists():
    #     clear_terminal()
    #     print(f'{Bracket('warning', Color.yellow, 1)} {Color.yellow}The FFmpeg binary file does not exist, downloading it...')
    #     download_latest_ffmpeg(ffmpeg_tool_path)
    # else:
    #     while True:
    #         if is_valid_ffmpeg_binary(ffmpeg_tool_path):
    #             clear_terminal()
    #             print(f'{Bracket('success', Color.green, 1)} {Color.green}The FFmpeg binary file exists and is working properly')
    #             break
    #         else:
    #             clear_terminal()
    #             print(f'{Bracket('error', Color.red, 1)} {Color.red}The FFmpeg binary file exists but is not working properly, re-downloading it...')
    #             download_latest_ffmpeg(ffmpeg_tool_path)

    # Ask the user if they want to load the queries from a file or write them manually
    print(
        f'{Bracket('+', Color.yellow, 1)} {Color.yellow}You can load your queries from a {Color.cyan}local file {Color.yellow}or simply {Color.cyan}write them manually{Color.yellow}.'
        f'\n\n{Bracket('-', Color.white)} {Color.white}To choose a local file, leave the input below blank and press ENTER.'
        f'\n{Bracket('-', Color.white)} {Color.white}To write the queries, type in the song name or song link and press ENTER.'
        f'\n\n{Bracket('#', Color.red)} {Color.red}The list of links/queries must have one item per line; if the last line is empty, the download will start'
    )

    user_input = input(f'{Color.light_white} ›{Color.blue} ').strip()

    query_list = list()

    # Load queries from a file
    if not user_input:
        clear_terminal(1)
        print(f'{Bracket('info', Color.blue, 1)} {Color.blue}Loading queries from a file...')

        queries_filepath = open_windows_filedialog_selector('Select a file with the URLs/Queries (one by line)', [('Text files', '*.txt'), ('All files', '*.*')])

        if not queries_filepath:
            clear_terminal(1)
            print(f'{Bracket('error', Color.red, 1)} {Color.red}No file selected, exiting...')
            exit(1)

        extracted_queries = extract_lines_from_file(queries_filepath)

        if not extracted_queries:
            clear_terminal(1)
            print(f'{Bracket('error', Color.red, 1)} {Color.red}The file is empty or cannot be read, exiting...')
            exit(1)

        query_list.extend(extracted_queries)

    # Write queries manually
    else:
        query_list.append(user_input)

        while True:
            query = input(f'{Color.light_white} ›{Color.blue} ').strip()

            if not query:
                break

            query_list.append(query)
            sleep(0.1)


if __name__ == '__main__':
    main()
