# Built-in imports
from ctypes import windll, WinError
from os import PathLike
from pathlib import Path
from subprocess import run, SubprocessError
from typing import *
from zipfile import ZipFile
from shutil import rmtree

# Third-party imports
from httpx import get, head, HTTPError
from remotezip import RemoteZip
from validators import url as is_url, ValidationError


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

def make_dirs(base_path: Union[AnyStr, Path, PathLike], path_list: List[Union[AnyStr, Path, PathLike]]) -> None:
    """
    Create subdirectories in a base directory.
    :param base_path: The base path to create the directories in.
    :param path_list: The list of directories to create.
    """

    try:
        for directory in path_list:
            Path(base_path, directory).mkdir(parents=True, exist_ok=True)
    except (FileExistsError, FileNotFoundError):
        raise Exception('Failed to create directories.')

def download_latest_ffmpeg(filepath: Path) -> None:
    """
    Download the binary of the latest FFmpeg build from the gh@GyanD/codexffmpeg repository.
    :param filepath: The path to save the FFmpeg binary to.
    """

    gh_repo_owner = 'GyanD'
    gh_repo_name = 'codexffmpeg'

    api_url = f'https://api.github.com/repos/{gh_repo_owner}/{gh_repo_name}/releases/latest'
    gh_data = get(api_url).json()

    github_repository = f'https://github.com/{github_repository_owner}/{github_repository_name}'
    build_name = f'ffmpeg-{gh_data['tag_name']}-essentials_build'

    with RemoteZip(f'{github_repository}/releases/latest/download/{build_name}.zip') as rzip:
        rzip.extract(f'{build_name}/bin/{file_name}.exe', output_file_dir)

        Path(f'{output_file_dir}/{build_name}/bin/{file_name}.exe').rename(Path(f'{output_file_dir}/{file_name}.exe'))
        rmtree(Path(f'{output_file_dir}/{build_name}'), ignore_errors=True)
