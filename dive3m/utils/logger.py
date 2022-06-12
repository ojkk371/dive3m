import os
import atexit
import json
import time
import sys
import logging

# fmt: off
_ATTRIBUTES = {
    'bold': 1, 'dark': 2, 'underline': 4,
    'blink': 5, 'reverse': 7, 'concealed': 8,
}
# fmt: off
_FG_COLORS = {
    'gray': 30, 'red': 31, 'green': 32, 'yellow': 33,
    'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37,
}
# fmt: off
_BG_COLORS = {
    'gray': 40, 'red': 41, 'green': 42, 'yellow': 43,
    'blue': 44, 'magenta': 45, 'cyan': 46, 'white': 47,
}


def colorize_text(text, fg_color=None, bg_color=None, attrs=None):
    format_str = lambda text, color: f'\033[{color}m{text}'
    if fg_color is not None:
        text = format_str(text, _FG_COLORS[fg_color])
    if bg_color is not None:
        text = format_str(text, _BG_COLORS[bg_color])
    if attrs is not None:
        if isinstance(attrs, str):
            attrs = [attrs]
        for attr in attrs:
            text = format_str(text, _ATTRIBUTES[attr])
    return text + '\033[0m'


class HumanReadableFormatter(logging.Formatter):

    def format(self, record):
        log = super(HumanReadableFormatter, self).format(record)
        if record.exc_text:
            log = log.replace(record.exc_text, colorize_text(record.exc_text, 'gray'))
        log = log.splitlines(True)

        levelname = f'{record.levelname:>7}'
        if record.levelno == logging.DEBUG:
            levelname = colorize_text(levelname, fg_color='green')
        elif record.levelno == logging.INFO:
            levelname = colorize_text(levelname, fg_color='green')
        elif record.levelno == logging.WARNING:
            levelname = colorize_text(levelname, fg_color='yellow', attrs='blink')
        elif record.levelno == logging.ERROR:
            levelname = colorize_text(levelname, fg_color='red', attrs='blink')

        name = colorize_text(record.name, fg_color='white', attrs='bold')
        timestamp = colorize_text(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            fg_color='cyan',
        )
        location = colorize_text(
            f'in {record.filename} (line:{record.lineno})',
            fg_color='magenta',
        )
        first_line = [' '.join((levelname, name, location, timestamp)) + '\n']
        log = (' ' * 8).join(first_line + log)
        return log


class MachineReadableFormatter(logging.Formatter):
    def format(self, record):
        out = {}
        out['log'] = super(MachineReadableFormatter, self).format(record)
        out['name'] = record.name
        out['level'] = record.levelname
        out['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        out['location'] = f'{record.filename} (line:{record.lineno})'
        out = json.dumps(out, indent=2, separators=(',', ':')) + ','
        return out


def get_logger(name, level, stdout=False, out_dir=None):
    logger = logging.getLogger(name=name)
    level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }[level]
    logger.setLevel(level)

    if stdout:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(HumanReadableFormatter())
        logger.addHandler(handler)

    if out_dir is not None:
        os.makedirs(out_dir, exist_ok=True)
        filename = os.path.join(
            out_dir,
            time.strftime('%Y_%m_%d-%H_%M_%S', time.localtime()) + '.json',
        )
        io = open(filename, 'w')
        handler = logging.StreamHandler(stream=io)
        handler.setFormatter(MachineReadableFormatter())
        logger.addHandler(handler)
        atexit.register(lambda: finalize_logfile(io, filename))
    return logger


def finalize_logfile(io, filename):
    io.close()
    with open(filename, 'r') as f:
        log = f.read()
    log = f'[\n{log[:-2]}\n]'
    with open(filename, 'w') as f:
        f.write(log)


Logger = get_logger('main', 'debug', stdout=True, out_dir='logs')
