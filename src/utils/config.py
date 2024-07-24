# Built-in imports
from platform import system as system_name


class Config:
    os_name = str(system_name().lower()) or '?'
    version = '0.0.1'
    name = 'syncgroove'
    fancy_name = 'SyncGroove'
