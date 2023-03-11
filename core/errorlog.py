#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Framework for logging errors."""

import sys

from . import paths


class CaptureStream(object):
    """ Redirects output to a file-like object to an internal list as well as a
    file."""
    def __init__(self, name, add_header=False, tee=True):
        """
        Constructor for CaptureStream. Call redirect() to start redirection.

        Args:
            name: the name of the sys stream to capture (e.g. 'stdout' for
                sys.stdout)
            add_header: if True, extra information will be printed to the file
                when it is initially written to. The text contains the PyLNP
                version number, the OS it's running on, and whether it's a
                compiled executable.
            tee: if True, forward writing to the original stream after
                capturing. If False, the redirected stream is not used.
        """
        self.softspace = 0
        self.lines = []
        self.name = name
        self.add_header = add_header
        self.tee = tee
        self.stream = getattr(sys, name)
        self.outfile = None

    def write(self, string):
        """
        Writes a string to the captured stream.

        Args:
            string: The string to write.
        """
        self.lines.append(string)
        if not self.outfile:
            # TODO: See if it's possible to use a with statment here
            # pylint: disable=consider-using-with
            self.outfile = open(
                paths.get('root', self.name + '.txt'), 'w', encoding='utf-8')
            # pylint: enable=consider-using-with
            if self.add_header:
                from .lnp import VERSION, lnp
                self.outfile.write(
                    "Running PyLNP {} (OS: {}, Compiled: {})\n".format(
                        VERSION, lnp.os, lnp.os == lnp.bundle))
        self.outfile.write(string)
        self.flush()
        if self.tee:
            return self.stream.write(string)
        return None

    def flush(self):
        """Flushes the output file."""
        if self.outfile is not None:
            self.outfile.flush()

    def hook(self):
        """Replaces the named stream with the redirected stream."""
        setattr(sys, self.name, self)

    def unhook(self):
        """Restores the original stream object."""
        setattr(sys, self.name, self.stream)

def start():
    """Starts redirection of stdout and stderr."""
    out.hook()
    err.hook()

def stop():
    """Stops redirection of stdout and stderr."""
    out.unhook()
    err.unhook()


out = CaptureStream('stdout')
err = CaptureStream('stderr', True)

# vim:expandtab
