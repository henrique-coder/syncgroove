# Built-in imports
from tempfile import gettempdir
from pathlib import Path
from platform import system as system_name


class Config:
    os_name = system_name().lower() or '?'
    is_windows = bool(os_name == 'windows')
    is_linux = bool(os_name == 'linux')
    is_macos = bool(os_name == 'darwin')
    is_java = bool(os_name == 'java')
    version = '0.0.1'
    name = 'syncgroove'
    fancy_name = 'SyncGroove'
    temporary_path = Path((gettempdir() or 'tmp'), f'{name}-{version}').resolve().as_posix()
    main_path = Path(Path.cwd(), f'{name}-{version}').resolve().as_posix()
    default_downloaded_musics_path = Path(main_path, 'downloaded-musics').resolve().as_posix()
    main_utils_path = Path(main_path, '.utils').resolve().as_posix()
    media_path = Path(main_utils_path, 'media').resolve().as_posix()
    tools_path = Path(main_utils_path, 'tools').resolve().as_posix()
