# Built-in imports
from os import PathLike
from pathlib import Path
from re import sub as re_sub
from typing import Any, Optional, Union, Type, AnyStr, Dict, List

# Third-party imports
from orjson import loads as orjson_loads, dumps as orjson_dumps, OPT_INDENT_2, JSONEncodeError, JSONDecodeError
from unicodedata import normalize
from yt_dlp import YoutubeDL


def format_string(query: AnyStr, max_length: int = 128) -> Optional[str]:
    """
    Format a string to be used as a filename or directory name. Remove special characters, limit length etc.
    :param query: The string to be formatted.
    :param max_length: The maximum length of the formatted string. If the string is longer, it will be truncated.
    :return: The formatted string. If the input string is empty or None, return None.
    """

    if not query or not query.strip():
        return None

    normalized_string = normalize('NFKD', str(query)).encode('ASCII', 'ignore').decode('utf-8')
    sanitized_string = re_sub(r'\s+', ' ', re_sub(r'[^a-zA-Z0-9\-_()[\]{}!$#+;,. ]', '', normalized_string)).strip()

    if len(sanitized_string) > max_length:
        cutoff = sanitized_string[:max_length].rfind(' ')
        sanitized_string = sanitized_string[:cutoff] if cutoff != -1 else sanitized_string[:max_length]

    return sanitized_string


def get_value(data: Dict[Any, Any], key: Any, fallback_key: Any = None, convert_to: Type = None, default_to: Any = None) -> Any:
    """
    Get a value from a dictionary, with optional fallback key, conversion and default value.
    :param data: The dictionary to search for the key.
    :param key: The key to search for in the dictionary.
    :param fallback_key: The fallback key to search for in the dictionary if the main key is not found.
    :param convert_to: The type to convert the value to. If the conversion fails, return the default value. If None, return the value as is.
    :param default_to: The default value to return if the key is not found.
    :return: The value from the dictionary, or the default value if the key is not found.
    """

    try:
        value = data[key]
    except KeyError:
        if fallback_key is not None:
            try:
                value = data[fallback_key]
            except KeyError:
                return default_to
        else:
            return default_to

    if convert_to is not None:
        try:
            value = convert_to(value)
        except (ValueError, TypeError):
            return default_to

    return value


class DLPHumanizer:
    """
    A class to extract and format data from YouTube videos using yt-dlp.
    """

    def __init__(self, url: str, quiet: bool = False, no_warnings: bool = True, ignore_errors: bool = True) -> None:
        """
        Initialize the DLPHumanizer class.
        :param url: The YouTube video url to extract data from.
        :param quiet: Whether to suppress console output from yt-dlp.
        :param no_warnings: Whether to suppress warnings from yt-dlp.
        :param ignore_errors: Whether to ignore errors from yt-dlp.
        """

        self._url: str = url
        self._ydl_opts: Dict[str, bool] = {'extract_flat': True, 'geo_bypass': True, 'noplaylist': True, 'age_limit': None, 'quiet': quiet, 'no_warnings': no_warnings, 'ignoreerrors': ignore_errors}
        self._raw_youtube_data: Dict[Any, Any] = {}
        self._raw_youtube_streams: List[Dict[Any, Any]] = []
        self._raw_youtube_subtitles: Dict[str, List[Dict[str, str]]] = {}

        self.media_info: Dict[str, Any] = {}

        self.best_video_streams: Optional[List[Dict[str, Any]]] = []
        self.best_video_stream: Optional[Dict[str, Any]] = {}
        self.best_video_download_url: Optional[str] = None

        self.best_audio_streams: Optional[List[Dict[str, Any]]] = []
        self.best_audio_stream: Optional[Dict[str, Any]] = {}
        self.best_audio_download_url: Optional[str] = None

        self.subtitle_streams: Dict[str, List[Dict[str, str]]] = {}

    @staticmethod
    def save_json(output_path: Union[str, PathLike], data: Union[Dict[Any, Any], List[Any]], indent_code: bool = True) -> None:
        """
        Save a dictionary/list to a JSON file.
        :param path: The path to save the JSON file to.
        :param data: The dictionary/list to save to the JSON file.
        :param indent_code: Whether to indent the JSON code. (2 spaces)
        """

        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            output_path.write_bytes(orjson_dumps(data, option=OPT_INDENT_2 if indent_code else None))
        except JSONEncodeError:
            raise JSONEncodeError(f'The data could not be encoded as JSON.')

    def extract(self, source_data: Union[Dict[Any, Any], Union[str, PathLike]] = None) -> None:
        """
        Extracts all the source data from the media using yt-dlp.
        :param source_data: The source data you extracted using yt-dlp.
        """

        if source_data:
            if isinstance(source_data, (str, PathLike)):
                source_data_path = Path(source_data).resolve()

                if not source_data_path.is_file():
                    raise FileNotFoundError(f'The input "{source_data_path.as_posix()}" is not a valid file path or does not exist.')
                if source_data_path.suffix != '.json':
                    raise ValueError(f'The file "{source_data_path.as_posix()}" is not a JSON file.')

                try:
                    source_data = orjson_loads(source_data_path.read_bytes())
                except FileNotFoundError:
                    raise FileNotFoundError(f'The file "{source_data_path.as_posix()}" could not be found.')
                except JSONDecodeError:
                    raise JSONDecodeError(f'The file "{source_data_path.as_posix()}" could not be decoded as JSON.')

            self._raw_youtube_data = source_data
            self._raw_youtube_streams = source_data.get('formats', [])
            self._raw_youtube_subtitles = source_data.get('subtitles', {})
        else:
            with YoutubeDL(self._ydl_opts) as ydl:
                self._raw_youtube_data = ydl.extract_info(self._url, download=False, process=True)

            self._raw_youtube_streams = self._raw_youtube_data.get('formats', [])
            self._raw_youtube_subtitles = self._raw_youtube_data.get('subtitles', {})

    def retrieve_media_info(self) -> None:
        """
        Extract and format relevant information from the raw yt-dlp response.
        """

        data = self._raw_youtube_data

        id_ = data.get('id')
        title = get_value(data, 'fulltitle', 'title')
        clean_title = format_string(title)
        channel_name = get_value(data, 'channel', 'uploader')
        clean_channel_name = format_string(channel_name)
        chapters = data.get('chapters', [])

        if chapters:
            chapters = [
                {
                    'title': chapter.get('title'),
                    'startTime': get_value(chapter, 'start_time', convert_to=float),
                    'endTime': get_value(chapter, 'end_time', convert_to=float)
                }
                for chapter in chapters
            ]

        media_info = {
            'fullUrl': f'https://www.youtube.com/watch?v={id_}',
            'shortUrl': f'https://youtu.be/{id_}',
            'embedUrl': f'https://www.youtube.com/embed/{id_}',
            'id': id_,
            'title': title,
            'cleanTitle': clean_title,
            'description': data.get('description'),
            'channelId': data.get('channel_id'),
            'channelUrl': get_value(data, 'uploader_url', 'channel_url'),
            'channelName': channel_name,
            'cleanChannelName': clean_channel_name,
            'isVerifiedChannel': get_value(data, 'channel_is_verified', default_to=False),
            'duration': get_value(data, 'duration'),
            'viewCount': get_value(data, 'view_count'),
            'isAgeRestricted': get_value(data, 'age_limit', convert_to=bool),
            'categories': get_value(data, 'categories', default_to=[]),
            'tags': get_value(data, 'tags', default_to=[]),
            'isStreaming': get_value(data, 'is_live'),
            'uploadTimestamp': get_value(data, 'timestamp', 'release_timestamp'),
            'availability': get_value(data, 'availability'),
            'chapters': chapters,
            'commentCount': get_value(data, 'comment_count'),
            'likeCount': get_value(data, 'like_count'),
            'followCount': get_value(data, 'channel_follower_count'),
            'language': get_value(data, 'language'),
            'thumbnails': [
                f'https://img.youtube.com/vi/{id_}/maxresdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/sddefault.jpg',
                f'https://img.youtube.com/vi/{id_}/hqdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/mqdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/default.jpg'
            ]
        }

        self.media_info = dict(sorted(media_info.items()))

    def analyze_video_streams(self) -> None:
        """
        Extract and format the best video streams from the raw yt-dlp response.
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            702: 'mp4', 571: 'mp4', 402: 'mp4', 272: 'webm',  # 7680x4320
            701: 'mp4', 401: 'mp4', 337: 'webm', 315: 'webm', 313: 'webm', 305: 'mp4', 266: 'mp4',  # 3840x2160
            700: 'mp4', 400: 'mp4', 336: 'webm', 308: 'webm', 271: 'webm', 304: 'mp4', 264: 'mp4',  # 2560x1440
            699: 'mp4', 399: 'mp4', 335: 'webm', 303: 'webm', 248: 'webm', 299: 'mp4', 137: 'mp4', 216: 'mp4', 170: 'webm',  # 1920x1080 (616: 'webm' - Premium [m3u8])
            698: 'mp4', 398: 'mp4', 334: 'webm', 302: 'webm', 612: 'webm', 247: 'webm', 298: 'mp4', 136: 'mp4', 169: 'webm',  # 1280x720
            697: 'mp4', 397: 'mp4', 333: 'webm', 244: 'webm', 135: 'mp4', 168: 'webm',  # 854x480
            696: 'mp4', 396: 'mp4', 332: 'webm', 243: 'webm', 134: 'mp4', 167: 'webm',  # 640x360
            695: 'mp4', 395: 'mp4', 331: 'webm', 242: 'webm', 133: 'mp4',  # 426x240
            694: 'mp4', 394: 'mp4', 330: 'webm', 278: 'webm', 598: 'webm', 160: 'mp4', 597: 'mp4',  # 256x144
        }

        video_streams = [
            stream for stream in data
            if stream.get('vcodec') != 'none' and int(get_value(stream, 'format_id').split('-')[0]) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            width = stream.get('width', 0)
            height = stream.get('height', 0)
            framerate = stream.get('fps', 0)
            bitrate = stream.get('tbr', 0)

            return width * height * framerate * bitrate

        sorted_video_streams = sorted(video_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Any]:
            codec = stream.get('vcodec', '')
            codec_parts = codec.split('.', 1)
            youtube_format_id = int(get_value(stream, 'format_id').split('-')[0])

            return {
                'url': stream.get('url'),
                'codec': codec_parts[0] if codec_parts else None,
                'codecVariant': codec_parts[1] if len(codec_parts) > 1 else None,
                'rawCodec': codec,
                'extension': format_id_extension_map.get(youtube_format_id, 'mp3'),
                'width': stream.get('width'),
                'height': stream.get('height'),
                'framerate': stream.get('fps'),
                'bitrate': stream.get('tbr'),
                'quality': stream.get('height'),
                'qualityNote': stream.get('format_note'),
                'size': stream.get('filesize'),
                'language': stream.get('language'),
                'youtubeFormatId': youtube_format_id
            }

        self.best_video_streams = [extract_stream_info(stream) for stream in sorted_video_streams] if sorted_video_streams else None
        self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else None
        self.best_video_download_url = self.best_video_stream['url'] if self.best_video_stream else None

    def analyze_audio_streams(self, preferred_language: str = None) -> None:
        """
        Extract and format the best audio streams from the raw yt-dlp response.
        :param preferred_language: The preferred language code of the audio stream. If "original", only the original audios will be considered. If None, all audio streams will be considered, regardless of language.
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            338: 'webm',  # Opus - (VBR) ~480 Kbps (?) - Quadraphonic (4)
            380: 'mp4',  # AC3 - 384 Kbps - Surround (5.1) - Rarely
            328: 'mp4',  # EAC3 - 384 Kbps - Surround (5.1) - Rarely
            258: 'mp4',  # AAC (LC) - 384 Kbps - Surround (5.1) - Rarely
            325: 'mp4',  # DTSE (DTS Express) - 384 Kbps - Surround (5.1) - Rarely*
            327: 'mp4',  # AAC (LC) - 256 Kbps - Surround (5.1) - ?*
            141: 'mp4',  # AAC (LC) - 256 Kbps - Stereo (2) - No, YT Music*
            774: 'webm',  # Opus - (VBR) ~256 Kbps - Stereo (2) - Some, YT Music*
            256: 'mp4',  # AAC (HE v1) - 192 Kbps - Surround (5.1) - Rarely
            251: 'webm',  # Opus - (VBR) <=160 Kbps - Stereo (2) - Yes
            140: 'mp4',  # AAC (LC) - 128 Kbps - Stereo (2) - Yes, YT Music
            250: 'webm',  # Opus - (VBR) ~70 Kbps - Stereo (2) - Yes
            249: 'webm',  # Opus - (VBR) ~50 Kbps - Stereo (2) - Yes
            139: 'mp4',  # AAC (HE v1) - 48 Kbps - Stereo (2) - Yes, YT Music
            600: 'webm',  # Opus - (VBR) ~35 Kbps - Stereo (2) - Yes
            599: 'mp4',  # AAC (HE v1) - 30 Kbps - Stereo (2) - Yes
        }

        audio_streams = [
            stream for stream in data
            if stream.get('acodec') != 'none' and int(get_value(stream, 'format_id').split('-')[0]) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            bitrate = stream.get('abr', 0)
            sample_rate = stream.get('asr', 0)

            return bitrate * 0.4 + sample_rate / 1000

        sorted_audio_streams = sorted(audio_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Any]:
            codec = stream.get('acodec', '')
            codec_parts = codec.split('.', 1)
            youtube_format_id = int(get_value(stream, 'format_id').split('-')[0])
            youtube_format_note = stream.get('format_note')

            return {
                'url': stream.get('url'),
                'codec': codec_parts[0] if codec_parts else None,
                'codecVariant': codec_parts[1] if len(codec_parts) > 1 else None,
                'rawCodec': codec,
                'extension': format_id_extension_map.get(youtube_format_id, 'mp3'),
                'bitrate': stream.get('abr'),
                'qualityNote': youtube_format_note,
                'isOriginalAudio': '(default)' in youtube_format_note,
                'size': stream.get('filesize'),
                'samplerate': stream.get('asr'),
                'channels': stream.get('audio_channels'),
                'language': stream.get('language'),
                'youtubeFormatId': youtube_format_id
            }

        self.best_audio_streams = [extract_stream_info(stream) for stream in sorted_audio_streams] if sorted_audio_streams else None
        self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else None
        self.best_audio_download_url = self.best_audio_stream['url'] if self.best_audio_stream else None

        if preferred_language:
            preferred_language = preferred_language.strip().lower()

            if preferred_language == 'original':
                self.best_audio_streams = [stream for stream in self.best_audio_streams if stream['isOriginalAudio']]
            else:
                self.best_audio_streams = [stream for stream in self.best_audio_streams if (stream['language'] or '') == preferred_language]

            self.best_audio_stream = self.best_audio_streams[0]
            self.best_audio_download_url = self.best_audio_stream['url']

    def analyze_subtitle_streams(self) -> None:
        """
        Extract and format the best subtitle streams from the raw yt-dlp response.
        """

        data = self._raw_youtube_subtitles

        subtitle_streams = {}

        for stream in data:
            subtitle_streams[stream] = [
                {
                    'extension': subtitle.get('ext'),
                    'url': subtitle.get('url'),
                    'language': subtitle.get('name')
                }
                for subtitle in data[stream]
            ]

        self.subtitle_streams = dict(sorted(subtitle_streams.items()))
