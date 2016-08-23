#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Keybinding management."""
from __future__ import print_function, unicode_literals, absolute_import

import collections
from functools import lru_cache
# pylint:disable=redefined-builtin
from io import open
import os
import shutil

from . import baselines, helpers, paths, log
from .lnp import lnp


def _keybind_fname(filename):
    """Turn a string into a valid filename for storing keybindings."""
    filename = os.path.basename(filename)
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    return paths.get('keybinds', filename)

def read_keybinds():
    """Returns a list of keybinding files."""
    files = []
    for fname in helpers.get_text_files(paths.get('keybinds')):
        with open(fname, encoding='cp437') as f:
            if ('[DISPLAY_STRING:' in f.read()) == \
                    ('legacy' in lnp.df_info.variations):
                files.append(fname)
    return tuple(sorted(os.path.basename(o) for o in files))

def _sdl_get_binds(filename, compressed=True):
    """Return serialised keybindings for the given file.
    Returns a compressed version, without vanilla entries, unless disabled.

    Allows keybindings to be stored as files with only the non-vanilla
    bindings, improving readability and compatibility across DF versions.
    Only compatible with SDL versions however.
    """
    with open(filename, encoding='cp437') as f:
        lines = f.readlines()
    od, lastkey = collections.OrderedDict(), None
    for line in (l.strip() for l in lines if l.strip()):
        if line.startswith('[BIND:'):
            od[line], lastkey = [], line
        elif lastkey is not None:
            od[lastkey].append(line)
    if not compressed:
        return od
    van = _get_vanilla_binds()
    if van is not None:
        return collections.OrderedDict(
            (k, v) for k, v in od.items()
            # only keep items with a vanilla counterpart, which is different
            if van.get(k) and set(van.get(k)) != set(v))

def _sdl_write_binds(filename, binds_od, expanded=False):
    """Write keybindings to the given file, optionally expanding them."""
    if expanded:
        van = _get_vanilla_binds()
        if van is not None:
            binds_od = collections.OrderedDict(
                (k, binds_od.get(k) or v) for k, v in van.items())
    lines = ['']
    for bind, vals in binds_od.items():
        lines.append(bind)
        # no indent allowed in interface.txt; otherwise makes reading easier
        lines.extend(vals if expanded else ['    ' + v for v in vals])
    text = '\n'.join(lines) + '\n'
    if filename is None:
        return text
    with open(filename, 'w', encoding='cp437') as f:
        f.write(text)

def _get_vanilla_binds():
    """Return the vanilla keybindings for use in compression or expansion."""
    try:
        vanfile = os.path.join(
            baselines.find_vanilla(False), 'data', 'init', 'interface.txt')
        return _sdl_get_binds(vanfile, compressed=False)
    except TypeError:
        log.w("Can't load or change keybinds with missing baseline!")

def load_keybinds(filename):
    """
    Overwrites Dwarf Fortress keybindings from a file.

    Params:
        filename
            The keybindings file to use.
    """
    target = paths.get('init', 'interface.txt')
    filename = _keybind_fname(filename)
    log.i('Loading keybinds:  ' + filename)
    if 'legacy' in lnp.df_info.variations:
        shutil.copyfile(filename, target)
    else:
        _sdl_write_binds(target, _sdl_get_binds(filename), expanded=True)

def keybind_exists(filename):
    """
    Returns whether or not a keybindings file already exists.

    Params:
        filename
            The filename to check.
    """
    return os.access(_keybind_fname(filename), os.F_OK)

def save_keybinds(filename):
    """
    Save current keybindings to a file.

    Params:
        filename
            The name of the new keybindings file.
    """
    installed = paths.get('init', 'interface.txt')
    filename = _keybind_fname(filename)
    log.i('Saving current keybinds as ' + filename)
    if 'legacy' in lnp.df_info.variations:
        shutil.copyfile(installed, filename)
    else:
        _sdl_write_binds(filename, _sdl_get_binds(installed))

def delete_keybinds(filename):
    """
    Deletes a keybindings file.

    Params:
        filename
            The filename to delete.
    """
    log.i('Deleting ' + filename + 'keybinds')
    os.remove(_keybind_fname(filename))

def get_installed_file():
    """Returns the name of the currently installed keybindings."""
    @lru_cache()
    def unordered(fname):
        """An order-independent representation of keybindings from a file."""
        return {k: set(v) for k, v in _sdl_get_binds(fname).items()}

    try:
        installed = paths.get('df', 'data', 'init', 'interface.txt')
        for fname in helpers.get_text_files(paths.get('keybinds')):
            if unordered(installed) == unordered(fname):
                return os.path.basename(fname)
    except: #pylint: disable=bare-except
        # Baseline missing, or interface.txt is missing from baseline - use
        # plain file comparsion
        pass

    files = helpers.get_text_files(paths.get('keybinds'))
    current = paths.get('init', 'interface.txt')
    result = helpers.detect_installed_file(current, files)
    return os.path.basename(result)
