import concurrent.futures
import ctypes
import multiprocessing
import threading
import subprocess

from .utils import measure_time, message
from .terminal_control_codes import HIDE_CURSOR, SHOW_CURSOR


def _spawn_process_simple(*args, **kwargs):
    future = concurrent.futures.Future()
    process = subprocess.Popen(*args, **kwargs)

    def get_return_code():
        process.wait()
        future.set_result(process.returncode)

    thread = threading.Thread(target=get_return_code)
    thread.daemon = True
    thread.start()
    return future


_spawn_process = _spawn_process_simple


class Spawner:
    def __enter__(self):
        global _spawn_process

        _spawn_process = self
        self._pipe, worker_pipe = multiprocessing.Pipe()
        self._process = multiprocessing.Process(target=self._loop, args=(worker_pipe,))
        self._process.start()
        return self

    def __exit__(self, *_):
        self._pipe.close()
        _spawn_process = _spawn_process_simple

    @staticmethod
    def _loop(worker_pipe):
        ctypes.windll.kernel32.FreeConsole()
        ctypes.windll.kernel32.AllocConsole()

        while True:
            try:
                print(':: Idle')
                args, kwargs = worker_pipe.recv()
                print(':: Starting', args, kwargs)

            except EOFError:
                break

            process = subprocess.Popen(*args, **kwargs)
            process.wait()
            worker_pipe.send(process.returncode)

    @staticmethod
    def _get_response(pipe, future):
        future.set_result(pipe.recv())

    def _create_response(self):
        future = concurrent.futures.Future()
        thread = threading.Thread(target=self._get_response, args=(self._pipe, future))
        thread.daemon = True
        thread.start()
        return future

    def __call__(self, *args, **kwargs):
        self._pipe.send((args, kwargs))
        return self._create_response()


def run(*args, **kwargs):
    process = _spawn_process(*args, **kwargs)
    return process.result()


def run_with_dots(*args, stdin=subprocess.DEVNULL, interval=1, length=5, **kwargs):
    process = _spawn_process(*args, stdin=stdin, **kwargs)

    def progress():
        lines = ['.' * dots + (length-dots) * ' ' for dots in range(1, length+1)]
        while True:
            yield from lines

    message(HIDE_CURSOR, end='', flush=True)

    for line in progress():
        try:
            message('\r', line, sep='', end='', flush=True)
            returncode = process.result(interval)
            break

        except concurrent.futures.TimeoutError:
            continue

    message(SHOW_CURSOR, end='', flush=True)
    message('\r        \r', end='', flush=True)

    return returncode
