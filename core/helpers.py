#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions."""

import glob
import os
import platform
import sys

from . import log
from .dfraw import DFRaw


def get_text_files(directory):
    """
    Returns a list of .txt files in <directory>.
    Excludes all filenames beginning with "readme" (case-insensitive).

    Args:
        directory: the directory to search.
    """
    temp = glob.glob(os.path.join(directory, '*.txt'))
    result = []
    for f in temp:
        if not os.path.basename(f).lower().startswith('readme'):
            result.append(f)
    return result


def detect_installed_file(current_file, test_files):
    """Returns the file in <test_files> which is contained in
    <current_file>, or "Unknown"."""
    try:
        current = DFRaw.read(current_file)
        for f in test_files:
            tested = DFRaw.read(f)
            if tested.endswith('\n'):
                tested = tested[:-1]
            if tested in current:
                return f
    except IOError:
        pass
    return "Unknown"


def detect_installed_files(current_file, test_files):
    """Returns a list of files in <test_files> that are contained in
    <current_file>."""
    if not os.path.isfile(current_file):
        log.d('Nothing installed in nonexistent file {}'.format(current_file))
        return []
    installed = []
    try:
        current = DFRaw.read(current_file)
        for f in test_files:
            try:
                tested = DFRaw.read(f)
                if tested.endswith('\n'):
                    tested = tested[:-1]
                if tested in current:
                    installed.append(f)
            except IOError:
                log.e('Cannot tell if {} is installed; read failed'.format(f))
    except IOError:
        log.e('Cannot check installs in {}; read failed'.format(current_file))
    return installed


def get_resource(filename):
    """
    If running in a bundle, this will point to the place internal
    resources are located; if running the script directly,
    no modification takes place.

    Args:
        filename (str): the ordinary path to the resource

    Returns:
        (str): Path for bundled filename
    """
    from .lnp import lnp
    if lnp.bundle == 'osx':
        # file is inside application bundle on OS X
        return os.path.join(os.path.dirname(sys.executable), filename)
    if lnp.bundle in ['win', 'linux']:
        # file is inside executable on Linux and Windows
        # pylint: disable=protected-access, no-member
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)


def os_is_64bit():
    """Returns true if running on a 64-bit OS."""
    return platform.machine().endswith('64')


def key_from_underscore_prefixed_string(s):
    """Converts a string to a key such that strings prefixed with an underscore
    will be sorted before other strings."""
    return not s.startswith('_'), s
