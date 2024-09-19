# Built-in imports
from typing import Any, Dict

# Third-party imports
from httpx import get, HTTPError


def get_youtube_video_data_from_query(query: str) -> Dict[str, Any]:
    """
    Get the YouTube video data from a query.
    :param query: The query to search for the video.
    :return: The YouTube video data from the query.
    :raises Exception: If the server is down or if the request fails.
    """

    pass


def get_youtube_video_data_from_url(url: str) -> Dict[str, Any]:
    """
    Get the YouTube video data from a URL.
    :param url: The URL of the video.
    :return: The YouTube video data from the URL.
    :raises Exception: If the server is down or if the request fails.
    """

    pass
