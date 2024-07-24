# Built-in imports
from pathlib import Path
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
    get_latest_app_version
)


def main() -> None:
    # # # print(open_windows_filedialog_selector('Select a file with the URLs/Queries (one by line)', [('Text files', '*.txt'), ('All files', '*.*')]))

    # Set the terminal title
    set_terminal_title(Config.fancy_name + ' ' + Config.version)

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


if __name__ == '__main__':
    main()
