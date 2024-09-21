from typing import *
from re import match as re_match
from os import PathLike

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

def download_file(url: str, output_path: PathLike, max_connections: int = 1, enable_progress_bar: bool = True, timeout: int = 120) -> None:
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
