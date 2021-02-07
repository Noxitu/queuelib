import os


def _enable_control_codes():
    from ctypes import byref, windll
    from ctypes.wintypes import DWORD

    kernel32 = windll.kernel32

    handle = kernel32.GetStdHandle(-11)

    mode = DWORD()
    kernel32.GetConsoleMode(handle, byref(mode))

    kernel32.SetConsoleMode(handle, mode.value | 0x4)


if os.name == 'nt':
    _enable_control_codes()


class Color:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[36m'
    RESET = '\033[m'


HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'