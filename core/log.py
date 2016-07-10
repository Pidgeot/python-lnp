#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Logging module."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, traceback

_log = None

# Logging levels
VERBOSE = 0
DEBUG = 1
INFO = 2
WARNING = 3
ERROR = 4

class Log(object):
    """Logging class."""
    def __init__(self):
        """Constructor for Log. Sets the maximum logging level to WARNING."""
        self.max_level = WARNING
        self.output_err = False
        self.output_out = False
        self.level_stack = []
        self.lines = []
        self.prefixes = []

    def push_level(self, level):
        """Temporarily changes the logging level to <level>. Call pop_level to
        restore the previous level."""
        self.level_stack.append(level)
        self.set_level(level)

    def pop_level(self):
        """Restores the previous logging level, if the level stack is not
        empty."""
        try:
            self.max_level = self.level_stack.pop()
        except IndexError:
            self.e('Tried to pop logging level, but stack empty', stack=True)

    def set_level(self, level):
        """Sets the maximum logging level to <level>."""
        self.max_level = level

    def push_prefix(self, prefix):
        """Adds a prefix to future log messages. Old prefixes will appear before
        new prefixes."""
        self.prefixes.append(prefix)

    def pop_prefix(self):
        """Removes the most recently added prefix from future log messages."""
        try:
            self.prefixes.pop()
        except IndexError:
            self.e('Tried to pop logging prefix, but stack empty', stack=True)

    def __get_prefixes(self):
        """Returns a string containing the prefixes for this log message."""
        if not self.prefixes:
            return ''
        return ': '.join(self.prefixes+[''])

    def log(self, log_level, message, *args, **kwargs):
        """Logs a message if the current logging level includes messages at
        level <log_level>.

        Params:
            log_level
                The level to log the message at. If less than the current
                logging level, nothing will happen.
            message
                The message to log.
            Additional arguments
                Used to format the message with the % operator.

        Keyword arguments:
            stack
                If True, logs a stack trace. If sys.excinfo contains an
                exception, this will be formatted and logged instead."""
        if log_level < self.max_level:
            return
        p = self.__get_level_string(log_level) + self.__get_prefixes()
        self.__write(p + str(message) % args + "\n")
        if kwargs.get('stack', False):
            ex = sys.exc_info()
            if ex[2]:
                for l in traceback.format_exception(*ex):
                    self.__write(l)
            else:
                for l in traceback.format_stack():
                    self.__write(l)

    @staticmethod
    def __get_level_string(level):
        """Returns a prefix corresponding to the given logging level."""
        return ["VERBOSE", "DEBUG", "INFO", "WARNING", "ERROR"][level] + ": "

    def d(self, message, *args, **kwargs):
        """Writes a DEBUG message to the log. See Log.log for details."""
        return self.log(DEBUG, message, *args, **kwargs)

    def e(self, message, *args, **kwargs):
        """Writes an ERROR message to the log. See Log.log for details."""
        return self.log(ERROR, message, *args, **kwargs)

    def i(self, message, *args, **kwargs):
        """Writes a INFO message to the log. See Log.log for details."""
        return self.log(INFO, message, *args, **kwargs)

    def v(self, message, *args, **kwargs):
        """Writes a VERBOSE message to the log. See Log.log for details."""
        return self.log(VERBOSE, message, *args, **kwargs)

    def w(self, message, *args, **kwargs):
        """Writes a WARNING message to the log. See Log.log for details."""
        return self.log(WARNING, message, *args, **kwargs)

    def get_lines(self):
        """Returns all logged lines."""
        return self.lines

    def __write(self, text):
        """Writes a line of text to the log."""
        if self.output_err:
            sys.stderr.write(text)
        if self.output_out:
            sys.stdout.write(text)
        self.lines.append(text)


def get():
    """Returns the default Log instance."""
    return _log

# prepare the default instance
_log = Log()
# Output to error log on the default instance
_log.output_err = True

# expose the methods targeting the default instance on the module itself
push_level = _log.push_level
pop_level = _log.pop_level
set_level = _log.set_level
log = _log.log
debug = d = _log.d
error = e = _log.e
info = i = _log.i
verbose = v = _log.v
warning = w = _log.w
get_lines = _log.get_lines
push_prefix = _log.push_prefix
pop_prefix = _log.pop_prefix
