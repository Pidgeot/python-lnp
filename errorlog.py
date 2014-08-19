#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Framework for logging errors."""
from __future__ import print_function, unicode_literals
import sys

class CaptureStream(object):
    """ Redirects output to a file-like object to an internal list as well as a
    file."""
    def __init__(self, name, tee=True):
        """
        Redirects named stream from sys.

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
        self.outfile = open(name+'.txt', 'w')
        self.hook()

    def write(self, string):
        """
        Writes a string to the captured stream.

        Params:
            string
                The string to write.
        """
        self.lines.append(string)
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

out = CaptureStream('stdout', not hasattr(sys, 'frozen'))
err = CaptureStream('stderr', not hasattr(sys, 'frozen'))

# vim:expandtab
