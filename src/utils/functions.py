from subprocess import run as subprocess_run, CalledProcessError, PIPE
from re import match as re_match
from os import PathLike
from pathlib import Path
from typing import *

from pysmartdl2 import SmartDL


def sort_urls_by_type_and_domain(input_queries_obj: type, extract_playlist_items: bool = True) -> type:
    """
    Sort URLs by type (single or playlist) and domain.
    :param input_queries_obj: The InputQueries object.
    :param extract_playlist_items: Whether to extract items from the playlists.
    :return: The updated InputQueries object.
    """

    def classify_urls(url: str, obj: Dict[str, Any]) -> None:
        if re_match(obj['regexes']['playlist'], url):
            obj['mixedURLs']['playlist'].append(url)
        elif re_match(obj['regexes']['single'], url):
            obj['mixedURLs']['single'].append(url)

    youtube_obj = {
        'fancyName': 'YouTube',
        'mixedURLs': {'single': [], 'playlist': []},
        'singleURLs': [],
        'regexes': {
            'single': r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+(&[^\s]*)?$',
            'playlist': r'(https?://)?(www\.)?youtube\.com/(watch\?v=[\w-]+&list=|playlist\?list=)[\w-]+'
        }
    }

    youtube_music_obj = {
        'fancyName': 'YouTube Music',
        'mixedURLs': {'single': [], 'playlist': []},
        'singleURLs': [],
        'regexes': {
            'single': r'(https?://)?(www\.)?music\.youtube\.com/watch\?v=[\w-]+(&[^\s]*)?$',
            'playlist': r'(https?://)?(www\.)?music\.youtube\.com/playlist\?list=[\w-]+'
        }
    }

    for url in input_queries_obj._urls:
        classify_urls(url, youtube_obj)  # YouTube
        classify_urls(url, youtube_music_obj)  # YouTube Music

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

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_command = ['ffmpeg', '-i', Path(video_path).resolve().as_posix(), '-i', Path(audio_path).resolve().as_posix(), '-c', 'copy', '-y', '-hide_banner', '-loglevel', 'error', output_path.as_posix()]

    try:
        subprocess_run(ffmpeg_command, shell=False, check=True, stderr=PIPE)
    except CalledProcessError as e:
        raise Exception(f'An error occurred while merging the files: {e.stderr.decode()}')
