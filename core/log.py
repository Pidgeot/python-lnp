#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Logging module."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, traceback

_log = None

# Error levels
VERBOSE = 0
DEBUG = 1
INFO = 2
WARNING = 3
ERROR = 4

class Log(object):
    """Logging class."""
    def __init__(self):
        """Constructor for Log. Sets the maximum logging level to WARNING."""
        #pylint: disable=global-statement
        global _log
        if not _log:
            _log = self
        self.max_level = WARNING
        self.output_err = False
        self.output_out = False
        self.level_stack = []
        self.lines = []

    @staticmethod
    def get():
        """Returns the active Log instance."""
        return _log

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
            self.w('Tried to pop logging level, but stack empty', stack=True)

    def set_level(self, level):
        """Sets the maximum logging level to <level>."""
        self.max_level = level

    def log(self, log_level, message, **kwargs):
        """Logs a message if the current logging level includes messages at
        level <log_level>.

        Params:
            log_level
                The level to log the message at. If less than the current
                logging level, nothing will happen.
            message
                The message to log.

        Keyword arguments:
            stack
                If True, logs a stack trace."""
        if log_level < self.max_level:
            return
        p = self.__get_level_string(log_level)
        self.__write(p + str(message) + "\n")
        if kwargs.get('stack', False):
            for l in traceback.format_stack():
                self.__write(l)

    @staticmethod
    def __get_level_string(level):
        """Returns a prefix corresponding to the given logging level."""
        return ["VERBOSE", "DEBUG", "INFO", "WARNING", "ERROR"][level] + ": "

    def d(self, message, **kwargs):
        """Writes a DEBUG message to the log. See Log.log for details."""
        return self.log(DEBUG, message, **kwargs)

    def e(self, message, **kwargs):
        """Writes an ERROR message to the log. See Log.log for details."""
        return self.log(ERROR, message, **kwargs)

    def i(self, message, **kwargs):
        """Writes a INFO message to the log. See Log.log for details."""
        return self.log(INFO, message, **kwargs)

    def v(self, message, **kwargs):
        """Writes a VERBOSE message to the log. See Log.log for details."""
        return self.log(VERBOSE, message, **kwargs)

    def w(self, message, **kwargs):
        """Writes a WARNING message to the log. See Log.log for details."""
        return self.log(WARNING, message, **kwargs)

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


# prepare the default instance
Log()
# Output to error log on the default instance
Log.get().output_err = True

# expose the methods targeting the default instance on the module itself
push_level = Log.get().push_level
pop_level = Log.get().pop_level
set_level = Log.get().set_level
log = Log.get().log
d = Log.get().d
e = Log.get().e
i = Log.get().i
v = Log.get().v
w = Log.get().w
get_lines = Log.get().get_lines
