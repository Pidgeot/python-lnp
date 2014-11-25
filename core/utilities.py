#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys
import os
import re
import fnmatch
from io import open

from . import paths
from .launcher import open_folder
from .lnp import lnp

def open_utils():
    """Opens the utilities folder."""
    open_folder(paths.get('utilities'))


metadata = {}
def read_metadata():
    """Read metadata from the utilities directory."""
    metadata.clear()
    entries = read_utility_lists(
        os.path.join(paths.get('utilities'), 'utilities.txt'))
    for e in entries:
        data = e.split(':', 2)
        if len(data) < 3:
            data.extend(['', ''])
        metadata[data[0]] = {'title': data[1]}
        metadata[data[0]]['tooltip'] = data[2]

def get_title(path):
    """
    Returns a title for the given utility. If an non-blank override exists, it
    will be used; otherwise, the filename will be manipulated according to
    PyLNP.json settings."""
    if os.path.basename(path) in metadata:
        if metadata[os.path.basename(path)]['title'] != '':
            return metadata[os.path.basename(path)]['title']
    result = os.path.join(
        os.path.basename(os.path.dirname(path)), os.path.basename(path))
    if lnp.config.get_bool('hideUtilityPath'):
        result = os.path.basename(result)
    if lnp.config.get_bool('hideUtilityExt'):
        result = os.path.splitext(result)[0]
    return result

def get_tooltip(path):
    """Returns the tooltip for the given utility, or an empty string."""
    try:
        return metadata[os.path.basename(path)]['tooltip']
    except KeyError:
        return ''

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

def read_utilities():
    """Returns a list of utility programs."""
    read_metadata()
    exclusions = read_utility_lists(os.path.join(
        paths.get('utilities'), 'exclude.txt'))
    exclusions.extend(
        [u for u in metadata.keys() if metadata[u]['title'] == 'EXCLUDE'])
    # Allow for an include list of filenames that will be treated as valid
    # utilities. Useful for e.g. Linux, where executables rarely have
    # extensions.
    inclusions = read_utility_lists(os.path.join(
        paths.get('utilities'), 'include.txt'))
    inclusions.extend(
        [u for u in metadata.keys() if metadata[u]['title'] != 'EXCLUDE'])
    progs = []
    patterns = ['*.jar']  # Java applications
    if sys.platform in ['windows', 'win32']:
        patterns.append('*.exe')  # Windows executables
        patterns.append('*.bat')  # Batch files
    else:
        patterns.append('*.sh')  # Shell scripts for Linux and OS X
    for root, dirnames, filenames in os.walk(paths.get('utilities')):
        if sys.platform == 'darwin':
            for dirname in dirnames:
                if (fnmatch.fnmatch(dirname, '*.app') and
                        dirname not in exclusions):
                    # OS X application bundles are really directories
                    progs.append(os.path.relpath(
                        os.path.join(root, dirname),
                        os.path.join(paths.get('utilities'))))
        for filename in filenames:
            if ((
                    any(fnmatch.fnmatch(filename, p) for p in patterns) or
                    filename in inclusions) and
                    filename not in exclusions):
                progs.append(os.path.relpath(
                    os.path.join(root, filename),
                    os.path.join(paths.get('utilities'))))

    return progs

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
        for line in open(
                os.path.join(paths.get('utilities'), 'autorun.txt'),
                encoding='utf-8'):
            if line.endswith('\n'):
                line = line[:-1]
            lnp.autorun.append(line)
    except IOError:
        pass

def save_autorun():
    """Saves autorun settings."""
    autofile = open(os.path.join(paths.get('utilities'), 'autorun.txt'), 'w')
    autofile.write("\n".join(lnp.autorun))
    autofile.close()
