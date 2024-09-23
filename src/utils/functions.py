from subprocess import run as subprocess_run, CalledProcessError, PIPE
from os import PathLike
from pathlib import Path
from shutil import move
from random import choices
from string import ascii_letters, digits
from typing import Union, List

from pysmartdl2 import SmartDL


def generate_random_string(length: int) -> str:
    """
    Generate a random string.
    :param length: The length of the string.
    :return: The random string.
    """

    return ''.join(choices(ascii_letters + digits, k=length))

def generate_temporary_file_path(path: Union[str, PathLike], length: int = 32) -> Path:
    """
    Generate an unused temporary file path based on the original path.
    :param path: The original file path.
    :param length: The length of the random file name.
    :return: The temporary file path
    """

    path = Path(path).resolve()

    if not path.is_file():
        raise ValueError(f'The path "{path}" is not a file.')

    original_extension = path.suffix
    directory = path.parent
    new_name = generate_random_string(length) + original_extension
    new_path = Path(directory, '.tmp_' + new_name)

    while new_path.exists():
        new_name = generate_random_string(length) + original_extension
        new_path = Path(directory, new_name)

    return new_path.resolve()

def update_media_metadata(path: Union[str, PathLike], strip_metadata: bool = True, title: str = None, artist: str = None, year: int = None, language: str = None, cover_image_path: Union[str, PathLike] = None, output_path: Union[str, PathLike] = None) -> None:
    """
    Update the metadata of a media file.
    :param path: The path of the media file.
    :param strip_metadata: Whether to strip the old metadata.
    :param title: The title of the media file.
    :param artist: The artist of the media file.
    :param year: The year of the media file.
    :param language: The language of the media file.
    :param cover_image_path: The path of the cover image.
    :param output_path: The path where the new file will be saved. If None, the original file will be updated.
    """

    path = Path(path).resolve()
    temp_output_path = generate_temporary_file_path(path)

    output_path = Path(output_path).resolve() if output_path else temp_output_path

    if output_path == path:
        output_path = temp_output_path

    cover_image_path = Path(cover_image_path).resolve() if cover_image_path else None

    command: List[str] = ['ffmpeg', '-i', path.as_posix()]

    if cover_image_path:
        command.extend(['-i', cover_image_path.as_posix(), '-map', '0', '-map', '1', '-metadata:s:v', 'title=Cover', '-metadata:s:v', 'comment=Cover (front)', '-c:v', 'copy', '-c:a', 'copy'])
    if strip_metadata:
        command.extend(['-map_metadata', '-1'])
    if title:
        command.extend(['-metadata', f'title={title}'])
    if artist:
        command.extend(['-metadata', f'artist={artist}'])
    if year:
        command.extend(['-metadata', f'date={year}'])
    if language:
        command.extend(['-metadata', f'language={language}'])

    command.extend(['-y', output_path.as_posix()])

    try:
        subprocess_run(command, stdout=PIPE, stderr=PIPE, check=True)
    except CalledProcessError as e:
        raise ValueError(f'Failed to update metadata for "{path}". Error: {e.stderr.decode()}')

    if temp_output_path.exists():
        move(temp_output_path, path)

def download_file(url: str, output_path: Union[str, PathLike], max_connections: int = 1, enable_progress_bar: bool = True, timeout: int = 120) -> None:
    """
    Download a file from the internet.
    :param url: The URL of the file.
    :param output_path: The file path where the file will be saved.
    :param max_connections: The maximum number of connections to use.
    :param enable_progress_bar: Whether to enable the progress bar.
    :param timeout: The timeout for the download.
    """

    download_obj = SmartDL(urls=url, dest=Path(output_path).resolve().as_posix(), threads=max_connections, progress_bar=enable_progress_bar, timeout=timeout)
    download_obj.start()
