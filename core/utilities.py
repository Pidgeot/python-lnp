#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys
import os
import re
from fnmatch import fnmatch
# pylint:disable=redefined-builtin
from io import open

from . import paths
from .launcher import open_folder
from .lnp import lnp

def open_utils():
    """Opens the utilities folder."""
    open_folder(paths.get('utilities'))

def read_metadata():
    """Read metadata from the utilities directory."""
    metadata = {}
    for e in read_utility_lists(paths.get('utilities', 'utilities.txt')):
        fname, title, tooltip, *_ = e.split(':', 2) + ['', '']
        metadata[fname] = {'title': title, 'tooltip': tooltip}
    return metadata

def get_title(path):
    """
    Returns a title for the given utility. If an non-blank override exists, it
    will be used; otherwise, the filename will be manipulated according to
    PyLNP.json settings."""
    metadata = read_metadata()
    if os.path.basename(path) in metadata:
        if metadata[os.path.basename(path)]['title'] != '':
            return metadata[os.path.basename(path)]['title']
    result = path
    if lnp.config.get_bool('hideUtilityPath'):
        result = os.path.basename(result)
    if lnp.config.get_bool('hideUtilityExt'):
        result = os.path.splitext(result)[0]
    return result

def get_tooltip(path):
    """Returns the tooltip for the given utility, or an empty string."""
    return read_metadata().get(os.path.basename(path), {}).get('tooltip', '')

def read_utility_lists(path):
    """
    Reads a list of filenames/tags from a utility list (e.g. include.txt).

    :param path: The file to read.
    """
    result = []
    try:
        util_file = open(path, encoding='utf-8')
        for line in util_file:
            for match in re.findall(r'\[(.+?)\]', line):
                result.append(match)
    except IOError:
        pass
    return result

def find_executables(include=None):
    """Yield a sequence of (potential) utilities.

    The unique identifier is a relative path from the `LNP/Utilities/` dir.
    This sequence is *before* any items are excluded.
    """
    if include is None:
        # User include patterns, useful eg on Linux without set file extensions
        include = []
    patterns = ['*.jar', '*.sh']
    if lnp.os == 'win':
        patterns = ['*.jar', '*.exe', '*.bat']
    for root, dirnames, filenames in os.walk(paths.get('utilities')):
        if lnp.os == 'osx':
            for dirname in dirnames:
                if any(fnmatch(dirname, p) for p in ['*.app'] + include):
                    # OS X application bundles are really directories
                    yield os.path.relpath(os.path.join(root, dirname),
                                          paths.get('utilities'))
        for filename in filenames:
            if any(fnmatch(filename, p) for p in patterns + include):
                yield os.path.relpath(os.path.join(root, filename),
                                      paths.get('utilities'))

def read_utilities():
    """Returns a list of utility programs."""
    metadata = read_metadata()
    exclusions = read_utility_lists(paths.get('utilities', 'exclude.txt'))
    exclusions.extend(
        [u for u in metadata.keys() if metadata[u]['title'] == 'EXCLUDE'])
    # Allow for an include list of filenames that will be treated as valid
    # utilities. Useful for e.g. Linux, where executables rarely have
    # extensions.  Also accepts glob patterns for filename (not path).
    inclusions = read_utility_lists(paths.get('utilities', 'include.txt'))
    inclusions.extend(
        [u for u in metadata.keys() if metadata[u]['title'] != 'EXCLUDE'])
    return sorted(util for util in find_executables(inclusions)
                  if not any(fnmatch(util, ex) for ex in exclusions))

def toggle_autorun(item):
    """
    Toggles autorun for the specified item.

    Params:
        item
            The item to toggle autorun for.
    """
    if item in lnp.autorun:
        lnp.autorun.remove(item)
    else:
        lnp.autorun.append(item)
    save_autorun()

def load_autorun():
    """Loads autorun settings."""
    lnp.autorun = []
    try:
        with open(paths.get('utilities', 'autorun.txt'),
                  encoding='utf-8') as file:
            for line in file:
                lnp.autorun.append(line.rstrip('\n'))
    except IOError:
        pass

def save_autorun():
    """Saves autorun settings."""
    with open(paths.get('utilities', 'autorun.txt'), 'w') as autofile:
        autofile.write("\n".join(lnp.autorun))
