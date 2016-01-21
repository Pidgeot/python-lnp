#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility management.

There are now two seperate metadata systems:
 - the manifest system, which applies to each dir with a manifest (and subdirs)
 - the global system, which applies to everything else

Utilities are uniformly and uniquely identified by the relative path
from `LNP/Utilities/` to the executable file.

Metadata for each is found by looking back up the pach for a manifest, and
in the global metadata if one is not found.

Utilities are found by walking down from the base dir.

For each dir, if a manifest is found it and all it's subdirs are only analysed
by the manifest system.  TODO: details here.
Otherwise, each file (and on osx, dir) is matched against standard patterns
and user include patterns.  Any matches that do not also match a user exclude
pattern are added to the list of identified utilities.

"""
from __future__ import print_function, unicode_literals, absolute_import

import glob
import os
import re
from fnmatch import fnmatch
# pylint:disable=redefined-builtin
from io import open

from . import log, manifest, paths
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

def manifest_for(path):
    """Returns the JsonConfiguration from manifest for the given utility,
    or None if no manifest exists."""
    while path:
        path = os.path.dirname(path)
        if os.path.isfile(os.path.join(
                paths.get('utilities'), path, 'manifest.json')):
            return manifest.get_cfg('utilities', path)

def get_title(path):
    """
    Returns a title for the given utility. If an non-blank override exists, it
    will be used; otherwise, the filename will be manipulated according to
    PyLNP.json settings."""
    manifest = manifest_for(path)
    if manifest is not None:
        return manifest.get_string('title')
    metadata = read_metadata()
    if os.path.basename(path) in metadata:
        if metadata[os.path.basename(path)]['title']:
            return metadata[os.path.basename(path)]['title']
    result = path
    if lnp.config.get_bool('hideUtilityPath'):
        result = os.path.basename(result)
    if lnp.config.get_bool('hideUtilityExt'):
        result = os.path.splitext(result)[0]
    return result

def get_tooltip(path):
    """Returns the tooltip for the given utility, or an empty string."""
    manifest = manifest_for(path)
    if manifest is not None:
        return manifest.get_string('tooltip')
    return read_metadata().get(os.path.basename(path), {}).get('tooltip', '')

def read_utility_lists(path):
    """
    Reads a list of filenames/tags from a utility list (e.g. include.txt).

    :param path: The file to read.
    """
    result = []
    try:
        with open(path, encoding='utf-8') as util_file:
            for line in util_file:
                for match in re.findall(r'\[(.+?)\]', line):
                    result.append(match)
    except IOError:
        pass
    return result

def scan_manifest_dir(root):
    """Yields the configured utility (or utilities) from root and subdirs."""
    m_path = os.path.relpath(root, paths.get('utilities'))
    config = manifest.get_cfg('utilities', m_path)
    pattern = config.get_string('exe_include_' + lnp.os)
    exclude = config.get_string('exe_exclude_patterns')

    utils = [u for u in glob.glob(pattern)
             if not any(fnmatch(u, p) for p in exclude)]
    if len(utils) < 1:
        log.w(m_path + ' manifest include/exclude matched no utilities!')
    if len(utils) > 1:
        log.w('Multiple paths matched by include/exclude patterns in {}: {}'
              .format(m_path, utils))
    yield from utils

def any_match(filename, include, exclude):
    """Return True if at least one pattern matches the filename, or False."""
    return any(fnmatch(filename, p) for p in include) and \
        not any(fnmatch(filename, p) for p in exclude)

def scan_normal_dir(root, dirnames, filenames):
    """Yields candidate utilities in the given root directory.

    Allow for an include list of filenames that will be treated as valid
    utilities. Useful for e.g. Linux, where executables rarely have
    extensions.  Also accepts glob patterns for filename (not path).
    """
    metadata = read_metadata()
    patterns = ['*.jar', '*.sh']
    if lnp.os == 'win':
        patterns = ['*.jar', '*.exe', '*.bat']
    exclude = read_utility_lists(paths.get('utilities', 'exclude.txt'))
    exclude += [u for u in metadata if metadata[u]['title'] == 'EXCLUDE']
    include = read_utility_lists(paths.get('utilities', 'include.txt'))
    include += [u for u in metadata if metadata[u]['title'] != 'EXCLUDE']
    if lnp.os == 'osx':
        # OS X application bundles are really directories, and always end .app
        for dirname in dirnames:
            if any_match(dirname, ['*.app'], exclude):
                yield os.path.relpath(os.path.join(root, dirname),
                                      paths.get('utilities'))
    for filename in filenames:
        if any_match(filename, patterns + include, exclude):
            yield os.path.relpath(os.path.join(root, filename),
                                  paths.get('utilities'))

def read_utilities():
    """Returns a sorted list of utility programs."""
    utilities = []
    for root, dirs, files in os.walk(paths.get('utilities')):
        if 'manifest.json' in files:
            utilities.extend(scan_manifest_dir(root))
            dirs[:] = []  # Don't run normal scan in subdirs
        else:
            utilities.extend(scan_normal_dir(root, dirs, files))
    return sorted(utilities, key=lambda u: get_title(u))

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
