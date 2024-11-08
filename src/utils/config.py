# Built-in imports
from tempfile import gettempdir
from pathlib import Path
from platform import system as system_name

# Third-party imports
from platformdirs import user_music_dir, user_downloads_dir


class Config:
    os_name: str = system_name().lower() or '?'
    is_windows: bool = bool(os_name == 'windows')
    is_linux: bool = bool(os_name == 'linux')
    version: str = '0.0.4'
    name: str = 'syncgroove'
    fancy_name: str = 'SyncGroove'
    temporary_path: str = Path((gettempdir() or 'tmp'), f'{name}-{version}').resolve().as_posix()
    main_path: str = Path(Path.cwd(), f'{name}-{version}').resolve().as_posix()
    default_downloaded_musics_path: str = user_music_dir() or user_downloads_dir()
    main_resources_path: str = Path(main_path, 'resources').resolve().as_posix()
    media_path: str = Path(main_resources_path, 'media').resolve().as_posix()
    tools_path: str = Path(main_resources_path, 'tools').resolve().as_posix()
