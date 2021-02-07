import subprocess

from .utils import measure_time, message
from .runner import run_with_dots


class CommandFailed(Exception):
    def __init__(self, *, returncode, cmd):
        super().__init__(f'Non-zero exit code: {returncode}')
        self.returncode = returncode
        self.cmd = cmd


def format_cmd(cmd):
    return '  '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)


class CMD:
    def __init__(self):
        self._cmd = self.cmd

    def __call__(self, *args, **kwargs):
        # Decorator - substitute internal _cmd
        if len(args) == 1 and callable(args[0]):
            self._cmd = args[0]
            return

        # Call - call internal _cmd and store default during call
        try:
            _cmd, self._cmd = self._cmd, self.cmd
            return _cmd(*args, **kwargs)

        finally:
            self._cmd = _cmd

    def cmd(self, *args):
        message('    $', format_cmd(args))

        duration = measure_time()
        returncode = run_with_dots(args, stderr=subprocess.STDOUT)

        message('      duration =', duration.smart_round())

        if returncode != 0:
            raise CommandFailed(
                cmd=args,
                returncode=returncode
            )

cmd = CMD()
