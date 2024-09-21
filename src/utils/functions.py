from subprocess import run as subprocess_run, CalledProcessError
from re import match as re_match
from os import PathLike
from pathlib import Path
from typing import *

from pysmartdl2 import SmartDL


def sort_urls_by_type_and_domain(input_queries_obj: type) -> type:
    """
    Sort URLs by type (single or playlist) and domain.
    :param input_queries_obj: The InputQueries object.
    :return: The updated InputQueries object.
    """

    def classify_urls(url: str, obj: Dict[str, Any]) -> None:
        if re_match(obj['regexes']['playlist'], url):
            obj['urls']['playlist'].append(url)
        elif re_match(obj['regexes']['single'], url):
            obj['urls']['single'].append(url)

    youtube_obj = {
        'fancyName': 'YouTube',
        'urls': {'single': [], 'playlist': []},
        'regexes': {
            'single': r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+(&[^\s]*)?$',
            'playlist': r'(https?://)?(www\.)?youtube\.com/(watch\?v=[\w-]+&list=|playlist\?list=)[\w-]+'
        }
    }

    youtube_music_obj = {
        'fancyName': 'YouTube Music',
        'urls': {'single': [], 'playlist': []},
        'regexes': {
            'single': r'(https?://)?(www\.)?music\.youtube\.com/watch\?v=[\w-]+(&[^\s]*)?$',
            'playlist': r'(https?://)?(www\.)?music\.youtube\.com/playlist\?list=[\w-]+'
        }
    }

    for url in input_queries_obj._urls:
        classify_urls(url, youtube_obj)  # YouTube
        classify_urls(url, youtube_music_obj)  # YouTube Music

    # Update the InputQueries object with the sorted URLs
    input_queries_obj.SortedURLs.youtube = youtube_obj
    input_queries_obj.SortedURLs.youtube_music = youtube_music_obj

    return input_queries_obj

def download_file(url: str, output_path: Union[str, PathLike], max_connections: int = 1, enable_progress_bar: bool = True, timeout: int = 120) -> None:
    """
    Download a file from the internet.
    :param url: The URL of the file.
    :param output_path: The path where the file will be saved.
    :param max_connections: The maximum number of connections to use.
    :param enable_progress_bar: Whether to enable the progress bar.
    :param timeout: The timeout for the download.
    """

    download_obj = SmartDL(urls=url, dest=output_path, threads=max_connections, progress_bar=enable_progress_bar, timeout=timeout)
    download_obj.start()

def merge_media_files(video_path: Union[str, PathLike], audio_path: Union[str, PathLike], output_path: Union[str, PathLike]) -> None:
    """
    Merge video and audio files into a single file.
    :param video_path: The path to the video file.
    :param audio_path: The path to the audio file.
    :param output_path: The path where the merged file will be saved.
    """

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_command = f'ffmpeg -i "{Path(video_path).resolve().as_posix()}" -i "{Path(audio_path).resolve().as_posix()}" -c copy -y -hide_banner -loglevel error "{output_path}"'

    try:
        subprocess_run(ffmpeg_command, shell=True, check=True)
    except CalledProcessError as e:
        raise Exception(f'An error occurred while merging the files: {e}')
