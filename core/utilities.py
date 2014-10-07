#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, re, fnmatch
from . import paths
from .lnp import lnp
from .launcher import open_folder

def open_utils():
    """Opens the utilities folder."""
    open_folder(paths.get('utilities'))

def read_utility_lists(path):
    """
    Reads a list of filenames from a utility list (e.g. include.txt).

    :param path: The file to read.
    """
    result = []
    try:
        util_file = open(path)
        for line in util_file:
            for match in re.findall(r'\[(.+)\]', line):
                result.append(match)
    except IOError:
        pass
    return result

def read_utilities():
    """Returns a list of utility programs."""
    exclusions = read_utility_lists(os.path.join(
        paths.get('utilities'), 'exclude.txt'))
    # Allow for an include list of filenames that will be treated as valid
    # utilities. Useful for e.g. Linux, where executables rarely have
    # extensions.
    inclusions = read_utility_lists(os.path.join(
        paths.get('utilities'), 'include.txt'))
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
                if fnmatch.fnmatch(dirname, '*.app'):
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
        for line in open(os.path.join(paths.get('utilities'), 'autorun.txt')):
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

