from queuelib.core import cmd, main, job
import queuelib.project_name as project_name


@job
def compute(dataset, param):
    job.name(f'Running {dataset} - {param}')
    input = job.input(project_name.dataset, f'd:/datasets/{dataset}')
    output = job.output(f'd:/results/{dataset}/{param}')

    with job:
        cmd('python', '-c', 'import time; print("started"); time.sleep(1); print("Done."); time.sleep(1)')


@job
def summary(dataset, param):
    job.name(f'Generating summary {dataset} - {param}')
    result = job.input(f'd:/results/{dataset}/{param}')
    summary = job.output(project_name.summary, f'd:/results/{dataset}/{param}/summary', f'{dataset}-{param}')

    with job:
        cmd('summary', result, summary.path)


# @cmd
# def custom_cmd(*args):
#     cmd('cmd', '/c', 'start', '/wait', *args)


DATASETS = [
    'abc',
    'xyz'
]


if __name__ == '__main__':
    for dataset in DATASETS:
        for param in [1, 2, 3]:
            compute(dataset, param)

    summary('abc', 1)
    # summary('abc', 1)
    # summary('abc', 4)

    main()
