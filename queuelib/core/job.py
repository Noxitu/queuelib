import sys
import os

from .cmd import CommandFailed, format_cmd
from .utils import message
from .terminal_control_codes import Color
from .display_job import display_job


class JobScheduled(Exception):
    pass


class PathData:
    def __init__(self, path):
        self.path = path
        self.title = f'"{path}"'

    def verify(self):
        return self.path.startswith('dataset') or self.path == 'result-xyz-2'


STEP_SCHEDULING = 'scheduling' 
STEP_RUNNING = 'running'

ANALYSE_DONE = 'done'
ANALYSE_RUN = 'run'
ANALYSE_ERROR = 'error'
ANALYSE_AVAILABLE = 'available'
ANALYSE_PLANNED = 'planned'


def _analyse_job(job, generated_outputs):
    inputs = {}
    outputs = {}

    for input in job['inputs']:
        if input.path in inputs:
            inputs[input.path] = (ANALYSE_ERROR, 'Input is duplicated.')
        elif input.verify():
            inputs[input.path] = (ANALYSE_AVAILABLE, '')
        elif input.path in generated_outputs:
            inputs[input.path] = (ANALYSE_PLANNED, '')
        else:
            inputs[input.path] = (ANALYSE_ERROR, 'Input is not available.')

    for output in job['outputs']:
        if output.path in generated_outputs or output.path in outputs:
            outputs[output.path] = (ANALYSE_ERROR, 'Result is duplicated.')
        elif output.verify():
            outputs[output.path] = (ANALYSE_DONE, 'Result already computed.')
        else:
            outputs[output.path] = (ANALYSE_RUN, '')

    statuses = {status for status, _ in inputs.values()} | {status for status, _ in outputs.values()}

    if ANALYSE_ERROR in statuses:
        status = ANALYSE_ERROR
    elif ANALYSE_DONE in statuses and ANALYSE_RUN in statuses:
        status = ANALYSE_ERROR
    elif ANALYSE_DONE in statuses:
        status = ANALYSE_DONE
    elif ANALYSE_RUN in statuses:
        status = ANALYSE_RUN
    else:
        status = ANALYSE_ERROR

    return status, inputs, outputs


class Job:
    def __init__(self):
        self._jobs = []
        self._step = STEP_SCHEDULING

    def __enter__(self):
        if self._step == STEP_SCHEDULING:
            raise JobScheduled()

    def __exit__(self, *_):
        pass
    
    def __call__(self, func):
        def job_wrapper(*args, **kwargs):
            try:
                self._scheduled_job = {
                    'call': (func, args, kwargs),
                    'name': func.__name__,
                    'inputs': [],
                    'outputs': []
                }

                func(*args, **kwargs)

            except JobScheduled:
                self._jobs.append(self._scheduled_job)
                self._scheduled_job = None
                pass

        return job_wrapper

    def input(self, type, *args):
        item = type(*args) if callable(type) else PathData(type)

        if self._step == STEP_SCHEDULING:
            self._scheduled_job['inputs'].append(item)

        return item if callable(type) else item.path

    def output(self, type, *args):
        item = type(*args) if callable(type) else PathData(type)

        if self._step == STEP_SCHEDULING:
            self._scheduled_job['outputs'].append(item)

        return item if callable(type) else item.path

    def name(self, name):
        if self._step == STEP_SCHEDULING:
            self._scheduled_job['name'] = name

    def verify(self):
        self._step = 'analysing'
        success = True

        generated_outputs = set()

        for job in self._jobs:
            status, inputs, outputs = _analyse_job(job, generated_outputs)
            display_job(job, status, inputs, outputs)

            if status == ANALYSE_RUN:
                generated_outputs |= set(outputs)

            if status == ANALYSE_ERROR:
                success = False

        message()

        if not success:
            raise Exception('Jobs have errors. Aborting.')

    def run(self):
        self._step = STEP_RUNNING
        skipped_count = 0
        not_run_count = 0
        failed_count = 0

        for idx, job in enumerate(self._jobs):
            result, _, _ = _analyse_job(job, set())

            if result == ANALYSE_DONE:
                skipped_count += 1
                message(f'Skipping #{idx} ', Color.GREEN, job['name'], Color.RESET, sep='')
                message()
                continue

            message(f'Running #{idx} ', Color.BLUE, job['name'], Color.RESET, sep='')

            if result == ANALYSE_ERROR:
                not_run_count += 1
                message(Color.RED, 'Failure.', Color.RESET, ' Job was predicted to fail if run.', sep='')
                message()
                continue

            try:
                call, args, kwargs = job['call']
                call(*args, **kwargs)

            except CommandFailed as exc:
                failed_count += 1
                message(Color.RED, 'Failed.', Color.RESET, ' Job command failed.', sep='')
                message('    ', 'Exit code = ', exc.returncode, sep='')
                message('    ', 'Command   = ', format_cmd(exc.cmd), sep='')
                message()
                continue

            outputs = [(output, output.verify()) for output in job['outputs']]

            if any(not verified for _, verified in outputs):
                failed_count += 1
                message(Color.RED, 'Failed.', Color.RESET, ' Job did not produce all outputs', sep='')
                for output, verified in outputs:
                    message('    ',
                            Color.GREEN if verified else Color.RED,
                            output.title,
                            Color.RESET,
                            '  ok' if verified else '  missing',
                            sep='')
                message()
                continue

            message(Color.GREEN, 'Success.', Color.RESET, sep='')
            message()

        message('Finished running', len(self._jobs), 'jobs.')

        if skipped_count > 0:
            message('    ', skipped_count, Color.BLUE, ' skipped', Color.RESET, sep='')

        if not_run_count > 0:
            message('    ', not_run_count, Color.RED, ' not run', Color.RESET, ' as predicted to fail', sep='')

        if failed_count > 0:
            message('    ', failed_count, Color.RED, ' failed', Color.RESET, sep='')

        if not_run_count+failed_count == 0:
            message(Color.GREEN, 'Success.', Color.RESET, sep='')

        message()

job = Job()
