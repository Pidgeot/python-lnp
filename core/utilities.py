#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility management.

There are now two separate metadata systems:

- the manifest system, which applies to each dir with a manifest (and subdirs)
- the global system, which applies to everything else

Utilities are uniformly and uniquely identified by the relative path
from ``LNP/Utilities/`` to the executable file.

Metadata for each is found by looking back up the path for a manifest, and
in the global metadata if one is not found.

Utilities are found by walking down from the base dir.

For each dir, if a manifest is found it and all it's subdirs are only analysed
by the manifest system.  See the README for how this works, and note that it
is more structured as well as more powerful, slightly decreasing flexibility -
for example mandating only one executable per platform, but specifying
requirements for DFHack or a terminal.

Otherwise, each file (and on OSX, dir) is matched against standard patterns
and user include patterns.  Any matches that do not also match a user exclude
pattern are added to the list of identified utilities.  This global config is
found in some combination of include.txt, exclude.txt, and utilities.txt.
"""

import os
import re
from fnmatch import fnmatch

from . import log, manifest, paths
from .launcher import open_file
from .lnp import lnp


def open_utils():
    """Opens the utilities folder."""
    open_file(paths.get('utilities'))


def read_metadata():
    """Read metadata from the utilities directory."""
    metadata = {}
    for e in read_utility_lists(paths.get('utilities', 'utilities.txt')):
        fname, title, tooltip = (e.split(':', 2) + ['', ''])[:3]
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
    return None


def get_title(path):
    """
    Returns a title for the given utility. If a non-blank override exists, it
    will be used; otherwise, the filename will be manipulated according to
    PyLNP.json settings."""
    config = manifest_for(path)
    if config is not None:
        if config.get_string('title'):
            return config.get_string('title')
    else:
        metadata = read_metadata()
        if os.path.basename(path) in metadata:
            if metadata[os.path.basename(path)]['title']:
                return metadata[os.path.basename(path)]['title']
    head, result = os.path.split(path)
    if not lnp.config.get_bool('hideUtilityPath'):
        result = os.path.join(os.path.basename(head), result)
    if lnp.config.get_bool('hideUtilityExt'):
        result = os.path.splitext(result)[0]
    return result


def get_tooltip(path):
    """Returns the tooltip for the given utility, or an empty string."""
    config = manifest_for(path)
    if config is not None:
        return config.get_string('tooltip')
    return read_metadata().get(os.path.basename(path), {}).get('tooltip', '')


def read_utility_lists(path):
    """
    Reads a list of filenames/tags from a utility list (e.g. include.txt).

    Args:
        path: The file to read.
    """
    result = []
    try:
        with open(path, encoding='utf-8') as util_file:
            for line in util_file:
                for match in re.findall(r'\[(.+?)]', line):
                    result.append(match)
    except IOError:
        pass
    return result


def scan_manifest_dir(root):
    """Yields the configured utility (or utilities) from root and subdirs."""
    m_path = os.path.relpath(root, paths.get('utilities'))
    util = manifest.get_cfg('utilities', m_path).get_string(lnp.os + '_exe')
    if manifest.is_compatible('utilities', m_path):
        if os.path.isfile(os.path.join(root, util)):
            return os.path.join(m_path, util)
        log.w('Utility not found:  {}'.format(os.path.join(m_path, util)))
    return None


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
    # pylint: disable=consider-using-dict-items
    exclude += [u for u in metadata if metadata[u]['title'] == 'EXCLUDE']
    include = read_utility_lists(paths.get('utilities', 'include.txt'))
    include += [u for u in metadata if metadata[u]['title'] != 'EXCLUDE']
    # pylint: enable=consider-using-dict-items
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
            util = scan_manifest_dir(root)
            if util is not None:
                utilities.append(util)
            dirs[:] = []  # Don't run normal scan in subdirs
        else:
            utilities.extend(scan_normal_dir(root, dirs, files))
    return sorted(utilities, key=get_title)


def toggle_autorun(item):
    """
    Toggles autorun for the specified item.

    Args:
        item: the item to toggle autorun for.
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
    filepath = paths.get('utilities', 'autorun.txt')
    with open(filepath, 'w', encoding="utf-8") as autofile:
        autofile.write("\n".join(lnp.autorun))


def open_readme(path):
    """
    Opens the readme associated with the utility <path>, if one exists.
    Returns False if no readme was found; otherwise True.
    """
    readme = None
    log.d('Finding readme for ' + path)
    m = manifest_for(path)
    path = paths.get('utilities', os.path.dirname(path))
    if m:
        readme = m.get('readme', None)
    if not readme:
        dir_contents = os.listdir(path)
        for s in sorted(dir_contents):
            if re.match('read[ _]?me', s, re.IGNORECASE):
                readme = s
                break
        else:
            log.d('No readme found')
            return False
    readme = os.path.join(path, readme)
    log.d('Found readme at ' + readme)
    open_file(readme)
    return True
