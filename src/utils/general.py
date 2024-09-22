# Built-in imports
from ctypes import windll, WinError
from os import PathLike, remove as remove_file, environ, pathsep
from pathlib import Path
from shutil import rmtree, move
from subprocess import run as subprocess_run, CalledProcessError
from tkinter import Tk, filedialog as tk_filedialog
from datetime import datetime
from typing import *

# Third-party imports
from colorama import init as colorama_init, Fore as ColoramaFore
from faker import Faker
from httpx import get, head, HTTPError
from validators import url as is_url, ValidationError
from orjson import loads as orjson_loads, dumps as orjson_dumps, OPT_INDENT_2, OPT_SORT_KEYS, JSONDecodeError
from PIL import Image
from unzip_http import RemoteZipFile


# Constants
fake = Faker()


class ColoredTerminalText:
    """
    A class to represent colored text.
    """

    black = ColoramaFore.BLACK
    red = ColoramaFore.RED
    white = ColoramaFore.WHITE
    green = ColoramaFore.GREEN
    blue = ColoramaFore.BLUE
    yellow = ColoramaFore.YELLOW
    cyan = ColoramaFore.CYAN
    magenta = ColoramaFore.MAGENTA

    light_black = ColoramaFore.LIGHTBLACK_EX
    light_red = ColoramaFore.LIGHTRED_EX
    light_white = ColoramaFore.LIGHTWHITE_EX
    light_green = ColoramaFore.LIGHTGREEN_EX
    light_blue = ColoramaFore.LIGHTBLUE_EX
    light_yellow = ColoramaFore.LIGHTYELLOW_EX
    light_cyan = ColoramaFore.LIGHTCYAN_EX
    light_magenta = ColoramaFore.LIGHTMAGENTA_EX

class CustomBracket(ColoredTerminalText):
    """
    Custom terminal brackets
    """

    def __init__(self, text: str, color: ColoredTerminalText, skip_lines: int = 0) -> None:
        """
        Initialize the CustomBracket class.
        :param text: The text to display inside the brackets.
        :param color: The color of the text.
        :param skip_lines: The number of lines to jump before displaying the brackets.
        """

        self.color = color
        self.text = text
        self.skip_lines = skip_lines

    def __str__(self) -> str:
        """
        Get the string representation of the CustomBracket class.
        :return: The string representation of the CustomBracket class.
        """

        return '\n' * self.skip_lines + f'{ColoredTerminalText.white}[{self.color}{self.text}{ColoredTerminalText.white}]'

def init_colorama(autoreset: bool = False) -> None:
    """
    Initialize the colorama module.
    """

    colorama_init(autoreset=autoreset)

def set_terminal_title(config_obj: type, title: str) -> None:
    """
    Set the terminal title on Windows and Linux.
    :param config_obj: The configuration object.
    :param title: The title to set.
    """

    try:
        if config_obj.is_windows:
            windll.kernel32.SetConsoleTitleW(title)
        elif config_obj.is_linux:
            subprocess_run(['echo', '-ne', f'\033]0;{title}\007'], shell=True)
    except (OSError, WinError, CalledProcessError, Exception) as e:
        raise Exception(f'Failed to set terminal title: {e}')

def add_directory_to_system_path(path: Union[str, PathLike]) -> None:
    """
    Add a directory to the system PATH.
    :param path: The directory to add to the system PATH.
    """

    environ['PATH'] += pathsep + Path(path).resolve().as_posix()

def is_valid_url(url: str, online_check: bool = False) -> Optional[bool]:
    """
    Check if a URL is valid and reachable online.
    :param url: The URL to check.
    :param online_check: If True, check if the URL is reachable online.
    :return: True if the URL is valid, False if the URL is invalid, and None if the URL is unreachable online.
    """

    try:
        bool_value = bool(is_url(url))

        if not bool_value:
            return False
    except ValidationError:
        return False

    if online_check:
        try:
            response = head(url, headers={'X-Forwarded-For': fake.ipv4_public()}, follow_redirects=True, timeout=5)
            return True if response.is_success or response.is_redirect else None
        except HTTPError:
            return None

    return bool_value

def clear_terminal(config_obj: type, jump_lines: int = 0) -> None:
    """
    Clear the terminal screen on Windows and Linux.
    :param config_obj: The configuration object.
    :param jump_lines: The number of lines to jump after clearing the terminal.
    """

    try:
        if config_obj.is_windows:
            subprocess_run(['cls'], shell=True)
        elif config_obj.is_linux:
            subprocess_run(['clear'], shell=True)
        else:
            raise Exception('The current operating system is not supported.')
    except (OSError, CalledProcessError, Exception) as e:
        raise Exception(f'Failed to clear terminal: {e}')

    if jump_lines > 0:
        print('\n' * (jump_lines - 1))

def make_dirs(base_path: Union[str, PathLike], path_list: List[Union[str, PathLike]] = None) -> None:
    """
    Create directories in the specified path or create a single directory.
    :param base_path: The base path to create the directories in.
    :param path_list: The list of directories to create.
    """

    try:
        if path_list is None:
            Path(base_path).mkdir(exist_ok=True)
        else:
            for directory in path_list:
                Path(base_path, directory).mkdir(parents=True, exist_ok=True)
    except (FileExistsError, FileNotFoundError):
        raise Exception('Failed to create directories.')

def download_latest_ffmpeg(config_obj: type) -> None:
    """
    Download the binary of the latest FFmpeg build from the gh@GyanD/codexffmpeg repository.
    :param config_obj: The configuration object.
    """

    gh_repo_owner = 'BtbN'
    gh_repo_name = 'FFmpeg-Builds'

    api_url = f'https://api.github.com/repos/{gh_repo_owner}/{gh_repo_name}/releases/latest'

    try:
        r = get(api_url, follow_redirects=False, timeout=10)
    except HTTPError:
        raise Exception('Failed to fetch the latest release data.')

    if not r.is_success:
        raise Exception('Server returned an error while fetching the latest release data.')

    r_data = orjson_loads(r.content)

    ffmpeg_base_path = Path(config_obj.tools_path, 'ffmpeg')
    ffmpeg_base_tmp_path = Path(ffmpeg_base_path, '.tmp')
    local_build_publish_timestamp_path = Path(ffmpeg_base_path, 'version.json').resolve()
    latest_build_publish_timestamp = int(datetime.strptime(r_data['published_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp())

    if not local_build_publish_timestamp_path.exists():
        local_build_publish_timestamp = 0
        Path(local_build_publish_timestamp_path).write_bytes(orjson_dumps({'publishTimestamp': local_build_publish_timestamp}, option=OPT_INDENT_2 + OPT_SORT_KEYS))
    else:
        try:
            local_build_publish_timestamp = int(orjson_loads(local_build_publish_timestamp_path.read_bytes())['publishTimestamp'])
        except (JSONDecodeError, ValueError):
            local_build_publish_timestamp = 0

    if local_build_publish_timestamp == latest_build_publish_timestamp:
        return None
    else:
        class AvailableFFmpegBuilds:
            win64 = 'ffmpeg-master-latest-win64-gpl.zip'
            linux64 = 'ffmpeg-master-latest-linux64-gpl.tar.xz'

        if config_obj.is_windows:
            for item in ffmpeg_base_path.iterdir():
                if item.is_dir():
                    rmtree(item)
                elif item.is_file() and item.name != 'version.json':
                    remove_file(item)

            download_url = f'https://github.com/{gh_repo_owner}/{gh_repo_name}/releases/download/latest/{AvailableFFmpegBuilds.win64}'
            output_filename = Path(AvailableFFmpegBuilds.win64)

            try:
                rzf = RemoteZipFile(download_url)
                source_binary_folder = f'{output_filename.stem}/bin/'
                files = [item[0] for item in rzf.files.items() if item[0].startswith(source_binary_folder) and item[0] != source_binary_folder]
                rzf.extractall(ffmpeg_base_tmp_path, members=files)

                for item in Path(ffmpeg_base_tmp_path, source_binary_folder).resolve().iterdir():
                    move(item, ffmpeg_base_path)

                rmtree(ffmpeg_base_tmp_path)
            except Exception as e:
                raise Exception(f'Failed to download the latest FFmpeg build. Error: {e}')

            Path(local_build_publish_timestamp_path).write_bytes(orjson_dumps({'publishTimestamp': latest_build_publish_timestamp}, option=OPT_INDENT_2 + OPT_SORT_KEYS))
        elif config_obj.is_linux:
            # raise Exception(f'The Linux operating system is not yet fully supported. Please manually download the latest build of FFmpeg from https://github.com/BtbN/FFmpeg-Builds/releases/latest and extract the binary files to the "syncgroove-{config_obj.version}/tools/ffmpeg" directory.')
            raise Exception(f'The Linux operating system is not yet fully supported. Please wait for the next version of SyncGroove to be released.')
        else:
            raise Exception('The current operating system is not supported.')

def open_windows_filedialog_selector(title: str, allowed_filetypes: List[Tuple[str, str]] = [('All files', '*.*')], icon_filepath: Union[str, PathLike] = None) -> Optional[str]:
    """
    Open a Windows file dialog to select a file.
    :param title: The title of the file dialog.
    :param allowed_filetypes: The allowed filetypes to select.
    :param icon_filepath: The path to the icon file.
    :return: The selected file path or None if no file was selected.
    """

    tk = Tk()
    tk.withdraw()
    tk.attributes('-topmost', True)
    tk.iconbitmap(Path(icon_filepath).resolve().as_posix()) if icon_filepath else None
    tk.update()

    input_filepath = tk_filedialog.askopenfilename(title=title, filetypes=allowed_filetypes)

    tk.destroy()

    return Path(input_filepath).resolve().as_posix() if input_filepath else None

def get_latest_app_version() -> Optional[str]:
    """
    Get the latest version of the application from the repository.
    :return: The latest version of the application or None if the version cannot be fetched.
    """


    url = 'https://raw.githubusercontent.com/Henrique-Coder/syncgroove/main/version.json'

    try:
        response = get(url, follow_redirects=False, timeout=10)

        if response.is_success:
            return str(orjson_loads(response.content)['latest'])
    except (HTTPError, JSONDecodeError):
        return None

    return None

def extract_lines_from_file(path: Union[str, PathLike], fix_lines: bool = False) -> Optional[List[str]]:
    """
    Extract lines from a file.
    :param path: The path to the file.
    :param fix_lines: If True, strip whitespace, remove empty lines, and remove duplicate lines. If False, include all lines as they are in the file.
    :return: The extracted lines from the file or None if the file does not exist or cannot be read.
    """

    try:
        extracted_lines = Path(path).read_text('utf-8').splitlines()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None

    if fix_lines:
        return list(set([line.strip() for line in extracted_lines if line.strip()]))
    else:
        return list(extracted_lines)

def download_app_icon(path: Union[str, PathLike]) -> None:
    """
    Download the application icon from the repository.
    :param path: The output path + filename of the app icon.
    """

    icon_url = 'https://cdn.jsdelivr.net/gh/Henrique-Coder/syncgroove/icon.ico'

    try:
        response = get(icon_url, follow_redirects=False, timeout=30)

        if response.is_success:
            Path(path).write_bytes(response.content)
        else:
            raise Exception('Failed to download the app icon.')
    except (HTTPError, PermissionError, FileNotFoundError):
        raise Exception('Failed to download the app icon.')

def is_image_corrupted(path: Union[str, PathLike]) -> bool:
    """
    Check if an image is corrupted.
    :param path: The path to the image.
    :return: True if the image is corrupted, False otherwise.
    """

    try:
        with Image.open(path) as img:
            img.verify()

        return False
    except (IOError, SyntaxError):
        return True
