# Built-in imports
from os import PathLike
from pathlib import Path
from typing import Optional, Union

# Third-party imports
from pydub import AudioSegment
from music_tag import load_file as mt_load_file


def transcode_and_edit_metadata(path: Union[str, PathLike], output_path: Union[str, PathLike], bitrate: int, title: Optional[str] = None, artist: Optional[str] = None, year: Optional[str] = None, cover_image: Optional[Union[str, PathLike]] = None) -> None:
    audio = AudioSegment.from_file(file=path)
    audio.export(output_path, format='opus', codec='libopus', bitrate=f'{bitrate}k')

    Path(path).unlink(missing_ok=True)

    audio = mt_load_file(output_path)
    audio['tracktitle'] = title
    audio['artist'] = artist
    audio['year'] = year
    audio['artwork'] = Path(cover_image).read_bytes() if cover_image else None
    audio.save()
