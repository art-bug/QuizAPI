'''
    The module contains the Loguru logger settings.
'''

from collections import defaultdict
from random import choice
import sys

from loguru import logger

colors = ["blue", "cyan", "green", "magenta", "red", "yellow"]
color_choice = defaultdict(lambda: choice(colors))


def formatter(record):
    '''
        Formats logger output line and colorizes different parts of it
        with random colors.
    '''

    time_color_tag = color_choice[record["time"]]
    message_color_tag = color_choice[record["message"]]

    colored_time = f"<{time_color_tag}>{{time}}</>"
    colored_message = f"<{message_color_tag}><bold>{{message}}</></>"

    return f"{colored_time} {{level}} {colored_message}\n{{exception}}"


logger.remove(0)
logger.add(sys.stderr, format=formatter)
