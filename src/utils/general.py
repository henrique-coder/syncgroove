# Built-in imports
from ctypes import windll, WinError
from os import PathLike
from pathlib import Path
from shutil import rmtree, move
from subprocess import run, SubprocessError
from typing import *

# Third-party imports
from httpx import get, head, HTTPError
from remotezip import RemoteZip
from validators import url as is_url, ValidationError

# Local imports
from .config import Config as MainConfig


def set_terminal_title(title: AnyStr, os_name: str) -> None:
    """
    Set the terminal title on Windows and Linux.
    :param title: The title to set.
    :param os_name: The name of the operating system.
    """

    try:
        if os_name == 'windows':
            windll.kernel32.SetConsoleTitleW(title)
        elif os_name == 'linux':
            run(['echo', '-ne', f'\033]0;{title}\007'], shell=True)
    except (OSError, WinError, SubprocessError):
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

def clear_terminal(os_name: str) -> None:
    """
    Clear the terminal screen on Windows and Linux.
    :param os_name: The name of the operating system.
    """

    try:
        if os_name == 'windows':
            run(['cls', '>nul', '2>&1'], shell=True)
        elif os_name == 'linux':
            run(['clear'], shell=True)
    except (OSError, SubprocessError):
        raise Exception('Failed to clear terminal.')

def make_dirs(base_path: Union[AnyStr, Path, PathLike], path_list: List[Union[AnyStr, Path, PathLike]] = None) -> None:
    """
    Create directories in the specified path or create a single directory.
    :param base_path: The base path to create the directories in.
    :param path_list: The list of directories to create.
    """

    try:
        if path_list is None:
            Path(base_path).mkdir(parents=True, exist_ok=True)
        else:
            for directory in path_list:
                Path(base_path, directory).mkdir(parents=True, exist_ok=True)
    except (FileExistsError, FileNotFoundError):
        raise Exception('Failed to create directories.')

def download_latest_ffmpeg(filepath: Union[AnyStr, Path, PathLike], os_name: str) -> None:
    """
    Download the binary of the latest FFmpeg build from the gh@GyanD/codexffmpeg repository.
    :param filepath: The output path + filename of the FFmpeg binary.
    :param os_name: The name of the operating system.
    """

    if os_name == 'windows':
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
        temporary_ffmpeg_path = Path(MainConfig.temporary_path + '/.downloaded_ffmpeg')

        try:
            with RemoteZip(f'{github_repository}/releases/latest/download/{build_name}.zip') as r_zip:
                r_zip.extract(f'{build_name}/bin/ffmpeg.exe', temporary_ffmpeg_path)
                move(Path(temporary_ffmpeg_path, f'{build_name}/bin/ffmpeg.exe'), Path(filepath).resolve())
                rmtree(temporary_ffmpeg_path)
        except Exception:
            raise Exception('Failed to download the latest FFmpeg build.')
    else:
        raise Exception('FFmpeg download is only supported on Windows. (for now)')
