# Built-in imports
from sys import exit
from typing import *

# Third-party imports
from httpx import get, head, HTTPError
from validators import url as is_url, ValidationError

# Local imports
from utils.config import Config as MainConfig
from utils.initialization import set_terminal_title


set_terminal_title(MainConfig.fancy_name, MainConfig.os_name)


def is_valid_url(url: AnyStr, online_check: bool = False) -> bool:
    """
    Check if the URL is valid and reachable online.
    :param url: The URL to check.
    :param online_check: If True, check if the URL is reachable online.
    :return: True if the URL is valid and reachable online, False otherwise.
    """

    try:
        bool_value = bool(is_url(str(url)))
        if not bool_value: return False
    except ValidationError:
        return False

    if online_check:
        try:
            response = head(url, follow_redirects=True, timeout=10)
            return True if response.is_success or response.is_redirect else False
        except HTTPError:
            return False

    return bool_value


def get_youtube_video_data_from_query(query: str) -> Dict[str, Any]:
    """
    Get the YouTube video data from a query.
    :param query: The query to search for the video.
    :return: The YouTube video data from the query.
    :raises Exception: If the server is down or if the request fails.
    """

    try:
        response = get(url='https://everytoolsapi-henrique-coder.koyeb.app/api/v2/get-youtube-video-url-from-search', params={'query': query}, timeout=30)
    except HTTPError:
        raise Exception('Failed to get the YouTube video URL from the query. The server is down.')

    if not response.is_success:
        raise Exception(f'Failed to get the YouTube video URL from the query. Status code: {response.status_code} - Response: {response.text}')

    return dict(response.json().get('response', dict()).get('foundUrlData', dict()))


def get_youtube_video_data_from_url(url: str) -> Dict[str, Any]:
    """
    Get the YouTube video data from a URL.
    :param url: The URL of the video.
    :return: The YouTube video data from the URL.
    :raises Exception: If the server is down or if the request fails.
    """

    pass


if __name__ == '__main__':
    exit()
