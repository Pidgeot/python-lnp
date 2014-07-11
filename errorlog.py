#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

class CaptureStream:
  """ Redirects output to a file-like object to an internal list as well as a file. """
  def __init__(self, name, tee=True):
    """
    Redirects named stream from sys.

    :param name: The name of the sys stream to capture (e.g. 'stdout' for sys.stdout)
    :param tee: If True, forward writing to the original stream after capturing. If False, the redirected stream is not used.
    """
    self.softspace = 0
    self.lines = []
    self.name = name
    self.tee = tee
    self.stream = getattr(sys, name)
    self.f = open(name+'.txt', 'w')
    self.hook()

  def write(self, string):
    self.lines.append(string)
    self.f.write(string)
    if self.tee:
      return self.stream.write(string)

  def flush(self):
    self.f.flush()

  def hook(self):
    setattr(sys, self.name, self)

  def unhook(self):
    setattr(sys, self.name, self.stream)

out = CaptureStream('stdout', not hasattr(sys, 'frozen'))
err = CaptureStream('stderr', not hasattr(sys, 'frozen'))

# vim:expandtab
