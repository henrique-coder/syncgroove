# Built-in imports
from ctypes import windll, WinError
from subprocess import run, SubprocessError
from typing import AnyStr, Literal


# allowed: windows, linux
def set_terminal_title(title: AnyStr, os_name: Literal['windows', 'linux']) -> bool:
    """
    Set the terminal title. This function is used to set the terminal title on Windows and Linux. (returns True if successful, False otherwise)
    :param title: The title to set.
    :param os_name: The name of the operating system.
    """

    try:
        if os_name == 'windows':
            windll.kernel32.SetConsoleTitleW(title)
        elif os_name == 'linux':
            run(['echo', '-ne', f'\033]0;{title}\007'], shell=True)
        else:
            return False

        return True
    except (OSError, WinError, SubprocessError):
        return False
