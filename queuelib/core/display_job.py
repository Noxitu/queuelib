from .utils import message
from .terminal_control_codes import Color


JOB_STATUS_COLOR = {
    'run': Color.YELLOW,
    'done': Color.GREEN,
    'error': Color.RED
}

INPUT_STATUS_COLOR = {
    'planned': Color.YELLOW,
    'available': Color.GREEN,
    'error': Color.RED
}


def display_job(job, status, inputs, outputs):
    message('Job ', JOB_STATUS_COLOR[status], job['name'], Color.RESET, sep='')

    for input in job['inputs']:
        item_status, item_message = inputs[input.path]
        message('    Input ', INPUT_STATUS_COLOR[item_status], input.title, Color.RESET, '        ', item_message, sep='')

    
    for output in job['outputs']:
        item_status, item_message = outputs[output.path]
        message('    Output ', JOB_STATUS_COLOR[item_status], output.title, Color.RESET, '        ', item_message, sep='')
