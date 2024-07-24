# Built-in imports
from typing import *

# Local imports
from utils.config import Config as MainConfig
from utils.functions import get_youtube_video_data_from_query, get_youtube_video_data_from_url
from utils.general import set_terminal_title, is_valid_url, clear_terminal, make_dirs, download_latest_ffmpeg, open_windows_filedialog_selector


def main() -> None:
    """
    The main function of the program.
    """
    
    # Set the terminal title
    set_terminal_title(MainConfig.fancy_name + ' ' + MainConfig.version, MainConfig.os_name)

    # Create the required directories
    make_dirs(MainConfig.temporary_app_path)
    make_dirs(MainConfig.app_path)


if __name__ == '__main__':
    main()
