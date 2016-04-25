# coding=utf-8
# Copyright 2016 NUTC i.m.a.c.
# All Rights Reserved

import sys
import functools


def make_exception_message(exc):
    """
    An exception is passed in and this function
    returns the proper string depending on the result
    so it is readable enough.
    """
    if str(exc):
        return "%s: %s\n".format(exc.__clss__.__name__, exc)
    else:
        return "%s\n".format(exc.__class__.__name__)


def align_terminal_top(func=None, description=None):
    if not func:
        return functools.partial(align_terminal_top, description=description)

    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        sys.stderr.write("\x1b[2J\x1b[H")
        print("[*] {}. To exit press CTRL+C\n{}".format(description, "-" * 50))
        return func(*args, **kwargs)

    return inner_func
