# Built-in imports
from sys import exit
from typing import *

# Local imports
from utils.config import Config as MainConfig
from utils.functions import get_youtube_video_data_from_query, get_youtube_video_data_from_url
from utils.general import set_terminal_title, is_valid_url, clear_terminal


set_terminal_title(MainConfig.fancy_name + ' ' + MainConfig.version, MainConfig.os_name)
print(MainConfig.temporary_path)


if __name__ == '__main__':
    print(get_youtube_video_data_from_query('never gonna give you up'))
    clear_terminal(MainConfig.os_name)
    exit()
