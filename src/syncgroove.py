# Built-in imports
from typing import *

# Local imports
from utils.config import Config
from utils.functions import (
    get_youtube_video_data_from_query,
    get_youtube_video_data_from_url
)
from utils.general import (
    init_colorama,
    ColoredTerminalText as Color,
    CustomBracket as Bracket,
    set_terminal_title,
    is_valid_url,
    clear_terminal,
    make_dirs,
    download_latest_ffmpeg,
    open_windows_filedialog_selector
)


def main() -> None:
    """
    The main function of the program.
    """

    # print(open_windows_filedialog_selector('Select a file with the URLs/Queries (one by line)', [('Text files', '*.txt'), ('All files', '*.*')]))

    # Set the terminal title
    set_terminal_title(Config.fancy_name + ' ' + Config.version)

    # Create the required directories
    make_dirs(Config.temporary_path)
    make_dirs(Config.main_path)
    make_dirs(Config.default_downloaded_musics_path)
    make_dirs(Config.main_utils_path)
    make_dirs(Config.media_path)
    make_dirs(Config.tools_path)

    # Initialize Colorama for colored terminal output
    clear_terminal()
    init_colorama()


if __name__ == '__main__':
    main()
