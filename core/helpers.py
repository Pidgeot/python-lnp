#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions."""
from __future__ import print_function, unicode_literals, absolute_import

import os, glob
import sys

from .dfraw import DFRaw
from . import log

def identify_folder_name(base, name):
    """
    Allows folder names to be lowercase on case-sensitive systems.
    Returns "base/name" where name is lowercase if the lower case version
    exists and the standard case version does not.

    Params:
        base
            The path containing the desired folder.
        name
            The standard case name of the desired folder.
    """
    normal = os.path.join(base, name)
    lower = os.path.join(base, name.lower())
    if os.path.isdir(lower) and not os.path.isdir(normal):
        return lower
    return normal

def get_text_files(directory):
    """
    Returns a list of .txt files in <directory>.
    Excludes all filenames beginning with "readme" (case-insensitive).

    Params:
        directory
            The directory to search.
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
            if tested[-1] == '\n':
                tested = tested[:-1]
            if tested in current:
                return f
    except IOError:
        pass
    return "Unknown"

def detect_installed_files(current_file, test_files):
    """Returns a list of files in <test_files> that are contained in
    <current_file>."""
    installed = []
    try:
        current = DFRaw.read(current_file)
        for f in test_files:
            try:
                tested = DFRaw.read(f)
                if tested[-1] == '\n':
                    tested = tested[:-1]
                if tested in current:
                    installed.append(f)
            except IOError:
                log.e('Cannot tell if {} is installed; read failed'.format(
                    f))
    except IOError:
        log.e('Cannot check installs in {}; read failed'.format(current_file))
    return installed

def get_resource(filename):
    """
    If running in a bundle, this will point to the place internal
    resources are located; if running the script directly,
    no modification takes place.
    :param str filename:
    :return str: Path for bundled filename
    """
    from .lnp import lnp
    if lnp.bundle == 'osx':
        # file is inside application bundle on OS X
        return os.path.join(os.path.dirname(sys.executable), filename)
    elif lnp.bundle in ['win', 'linux']:
        # file is inside executable on Linux and Windows
        # pylint: disable=protected-access, no-member, maybe-no-member
        return os.path.join(sys._MEIPASS, filename)
    else:
        return os.path.abspath(filename)
