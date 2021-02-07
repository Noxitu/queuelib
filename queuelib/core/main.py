import sys

from .job import job
from .runner import Spawner
from .utils import message


def _main(args):
    message()

    job.verify()

    if '--run' in args:
        if '--window' in args:
            with Spawner():
                job.run()
        else:
            job.run()


def main(args=None):
    try:
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, set):
            args = set(args)

        _main(args)

    except KeyboardInterrupt:
        message('\n\nKeyboardInterrupt\n')
