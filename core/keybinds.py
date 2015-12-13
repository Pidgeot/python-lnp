#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Keybinding management."""
from __future__ import print_function, unicode_literals, absolute_import

import collections
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
            if ('[BIND:' in f.read(20)) != ('legacy' in lnp.df_info.variations):
                files.append(fname)
    return sorted(tuple(os.path.basename(o) for o in files))

def _sdl_keybinds_serialiser(lines):
    """Turn lines into an ordered dict, to preserve structure of file.

    Allows keybindings to be stored as files with only the non-vanilla
    bindings, improving readability and compatibility across DF versions.
    Only compatible with SDL versions however.
    """
    od, lastkey = collections.OrderedDict(), None
    for line in (l.strip() for l in lines if l.strip()):
        if line.startswith('[BIND:'):
            od[line], lastkey = [], line
        elif lastkey is not None:
            od[lastkey].append(line)
    return od

def _sdl_get_binds(filename):
    """Return serialised keybindings for vanilla and for the given file."""
    try:
        vanfile = os.path.join(
            baselines.find_vanilla(), 'data', 'init', 'interface.txt')
    except TypeError:
        log.w("Can't load or change keybinds with missing baseline!")
        return None, None
    with open(vanfile, encoding='cp437') as f:
        van = _sdl_keybinds_serialiser(f.readlines())
    with open(filename, encoding='cp437') as f:
        return van, _sdl_keybinds_serialiser(f.readlines())

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
        van, cfg = _sdl_get_binds(filename)
        if not van:
            return
        van.update(cfg)
        lines = ['']
        for bind, vals in van.items():
            lines.append(bind)
            lines.extend(vals)
        with open(target, 'w', encoding='cp437') as f:
            f.write('\n'.join(lines))

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
    filename = _keybind_fname(filename)
    log.i('Saving current keybinds as ' + filename)
    if 'legacy' in lnp.df_info.variations:
        shutil.copyfile(paths.get('init', 'interface.txt'), filename)
    else:
        van, cfg = _sdl_get_binds(filename)
        if not van:
            return
        with open(filename, 'w', encoding='cp437') as f:
            for bind, vals in cfg.items():
                if vals != van.get(bind):
                    f.write(bind)
                    for line in van.get(bind):
                        f.write('    ' + line)

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
    files = helpers.get_text_files(paths.get('keybinds'))
    current = paths.get('init', 'interface.txt')
    result = helpers.detect_installed_file(current, files)
    return os.path.basename(result)
