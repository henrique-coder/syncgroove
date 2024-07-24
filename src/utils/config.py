# Built-in imports
from tempfile import gettempdir
from pathlib import Path
from platform import system as system_name


class Config:
    os_name = str(system_name().lower()) or '?'
    version = '0.0.1'
    name = 'syncgroove'
    fancy_name = 'SyncGroove'
    temporary_path = Path((gettempdir() or '/tmp') + f'/{name}').resolve().as_posix()
