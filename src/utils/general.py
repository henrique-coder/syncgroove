# Built-in imports
from ctypes import windll, WinError
from os import PathLike, remove as remove_file
from pathlib import Path
from shutil import rmtree, move
from subprocess import run as subprocess_run, PIPE as subprocess_PIPE, SubprocessError, CalledProcessError
from tkinter import Tk, filedialog as tk_filedialog
from typing import *

# Third-party imports
from httpx import get, head, HTTPError
from remotezip import RemoteZip
from validators import url as is_url, ValidationError
from colorama import init as colorama_init, Fore as ColoramaFore

# Local imports
from .config import Config


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

def set_terminal_title(title: AnyStr) -> None:
    """
    Set the terminal title on Windows and Linux.
    :param title: The title to set.
    """

    try:
        if Config.is_windows:
            windll.kernel32.SetConsoleTitleW(title)
        elif Config.is_linux:
            subprocess_run(['echo', '-ne', f'\033]0;{title}\007'], shell=True)
    except (OSError, WinError, SubprocessError, CalledProcessError):
        raise Exception('Failed to set terminal title.')

def is_valid_url(url: AnyStr, online_check: bool = False) -> bool:
    """
    Check if a URL is valid and reachable online.
    :param url: The URL to check.
    :param online_check: If True, check if the URL is reachable online.
    :return: True if the URL is valid and reachable online, False otherwise.
    """

    try:
        bool_value = bool(is_url(str(url)))
        if not bool_value:
            return False
    except ValidationError:
        return False

    if online_check:
        try:
            response = head(url, follow_redirects=True, timeout=10)
            return True if response.is_success or response.is_redirect else False
        except HTTPError:
            return False

    return bool_value

def clear_terminal(jump_lines: int = 0) -> None:
    """
    Clear the terminal screen on Windows and Linux.
    :param jump_lines: The number of lines to jump after clearing the terminal.
    """

    try:
        if Config.is_windows:
            subprocess_run(['cls'], shell=True)
        elif Config.is_linux:
            subprocess_run(['clear'], shell=True)
    except (OSError, SubprocessError):
        raise Exception('Failed to clear terminal.')

    if jump_lines > 0:
        print('\n' * (jump_lines - 1))

def make_dirs(base_path: Union[AnyStr, Path, PathLike], path_list: List[Union[AnyStr, Path, PathLike]] = None) -> None:
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

def download_latest_ffmpeg(path: Union[AnyStr, Path, PathLike]) -> None:
    """
    Download the binary of the latest FFmpeg build from the gh@GyanD/codexffmpeg repository.
    :param path: The output path + filename of the FFmpeg binary.
    """

    if Config.is_windows:
        gh_repo_owner = 'GyanD'
        gh_repo_name = 'codexffmpeg'

        api_url = f'https://api.github.com/repos/{gh_repo_owner}/{gh_repo_name}/releases/latest'
        try: response = get(api_url)
        except HTTPError: raise Exception('Failed to fetch the latest release data.')

        if not response.is_success:
            raise Exception('Failed to fetch the latest release data.')

        response_data = response.json()

        github_repository = f'https://github.com/{gh_repo_owner}/{gh_repo_name}'
        build_name = f'ffmpeg-{response_data['tag_name']}-essentials_build'
        temporary_ffmpeg_path = Path(Config.temporary_path + '.downloaded_ffmpeg')

        try:
            with RemoteZip(f'{github_repository}/releases/latest/download/{build_name}.zip') as r_zip:
                r_zip.extract(f'{build_name}/bin/ffmpeg.exe', temporary_ffmpeg_path)

                if Path(path).exists:
                    remove_file(path)

                move(Path(temporary_ffmpeg_path, f'{build_name}/bin/ffmpeg.exe'), Path(path).resolve())
                rmtree(temporary_ffmpeg_path)
        except Exception:
            raise Exception('Failed to download the latest FFmpeg build.')
    else:
        raise Exception('FFmpeg download is only supported on Windows. (for now)')

def is_valid_ffmpeg_binary(path: Union[AnyStr, Path, PathLike]) -> bool:
    """
    Check if the FFmpeg binary is valid by running the '-version' command.
    :param path: The path to the FFmpeg binary.
    :return: True if the FFmpeg binary is valid, False otherwise
    """

    try:
        subprocess_run([Path(path).as_posix(), '-version'], stdout=subprocess_PIPE, stderr=subprocess_PIPE)
        return True
    except (OSError, SubprocessError, CalledProcessError):
        return False

def open_windows_filedialog_selector(title: str, allowed_filetypes: List[Tuple[str, str]] = [('All files', '*.*')], icon_filepath: Union[AnyStr, Path, PathLike] = None) -> Optional[str]:
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
    url = 'https://cdn.jsdelivr.net/gh/Henrique-Coder/syncgroove@main/version.json'

    try:
        response = get(url, follow_redirects=False, timeout=10)

        if response.is_success:
            return str(response.json()['current'])
    except HTTPError:
        return None

    return None
