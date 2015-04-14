#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Framework for logging errors."""
from __future__ import print_function, unicode_literals, absolute_import
import sys
# pylint:disable=redefined-builtin
from io import open

from . import paths

class CaptureStream(object):
    """ Redirects output to a file-like object to an internal list as well as a
    file."""
    def __init__(self, name, tee=True):
        """
        Constructor for CaptureStream. Call redirect() to start redirection.

        Params:
            name
                The name of the sys stream to capture (e.g. 'stdout' for
                sys.stdout)
            tee
                If True, forward writing to the original stream after
                capturing. If False, the redirected stream is not used.
        """
        self.softspace = 0
        self.lines = []
        self.name = name
        self.tee = tee
        self.stream = getattr(sys, name)
        self.outfile = None

    def write(self, string):
        """
        Writes a string to the captured stream.

        Params:
            string
                The string to write.
        """
        self.lines.append(string)
        if sys.version_info[0] == 2:
            # For Python3: pylint:disable=undefined-variable
            self.outfile.write(unicode(string))
        else:
            self.outfile.write(string)
        if self.tee:
            return self.stream.write(string)

    def flush(self):
        """Flushes the output file."""
        self.outfile.flush()

    def hook(self):
        """Replaces the named stream with the redirected stream."""
        setattr(sys, self.name, self)

    def unhook(self):
        """Restores the original stream object."""
        setattr(sys, self.name, self.stream)

    def redirect(self):
        """Sets up the initial redirection."""
        self.outfile = open(
            paths.get('root', self.name+'.txt'), 'w',
            encoding='utf-8')
        self.hook()

def start():
    """Starts redirection of stdout and stderr."""
    out.redirect()
    err.redirect()

out = CaptureStream('stdout', not hasattr(sys, 'frozen'))
err = CaptureStream('stderr', not hasattr(sys, 'frozen'))

# vim:expandtab
