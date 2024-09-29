# Built-in imports
from os import PathLike, remove
from pathlib import Path
from typing import Union

# Third-party imports
from pysmartdl2 import SmartDL
from pydub import AudioSegment
from music_tag import load_file as mt_load_file


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

def transcode_and_edit_metadata(path: Union[str, PathLike], output_path: Union[str, PathLike], bitrate: int, title: str = None, artist: str = None, year: str = None, cover_image: Union[str, PathLike] = None) -> None:
    audio = AudioSegment.from_file(file=path)
    audio.export(output_path, format='opus', codec='libopus', bitrate=f'{bitrate}k')

    remove(path)

    audio = mt_load_file(output_path)
    audio['tracktitle'] = title
    audio['artist'] = artist
    audio['year'] = year
    audio['artwork'] = Path(cover_image).read_bytes()
    audio.save()
