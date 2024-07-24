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

    try:
        response = get(url='https://private-b9a5ee-everytoolsapi.apiary-mock.com/api/v2/get-youtube-video-url-from-search', params={'query': query}, timeout=30)
    except HTTPError:
        raise Exception('Failed to get the YouTube video URL from the query. The server is down.')

    if not response.is_success:
        raise Exception(f'Failed to get the YouTube video URL from the query. Status code: {response.status_code} - Response: {response.text}')

    return dict(response.json()['response']['foundUrlData'])


def get_youtube_video_data_from_url(url: str) -> Dict[str, Any]:
    """
    Get the YouTube video data from a URL.
    :param url: The URL of the video.
    :return: The YouTube video data from the URL.
    :raises Exception: If the server is down or if the request fails.
    """

    pass
