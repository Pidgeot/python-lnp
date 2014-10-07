#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Keybinding management."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil
from . import helpers, paths

def read_keybinds():
    """Returns a list of keybinding files."""
    return tuple([
        os.path.basename(o) for o in helpers.get_text_files(
            paths.get('keybinds'))])

def load_keybinds(filename):
    """
    Overwrites Dwarf Fortress keybindings from a file.

    Params:
        filename
            The keybindings file to use.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    target = os.path.join(paths.get('init'), 'interface.txt')
    shutil.copyfile(os.path.join(paths.get('keybinds'), filename), target)

def keybind_exists(filename):
    """
    Returns whether or not a keybindings file already exists.

    Params:
        filename
            The filename to check.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    return os.access(os.path.join(paths.get('keybinds'), filename), os.F_OK)

def save_keybinds(filename):
    """
    Save current keybindings to a file.

    Params:
        filename
            The name of the new keybindings file.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    filename = os.path.join(paths.get('keybinds'), filename)
    shutil.copyfile(os.path.join(paths.get('init'), 'interface.txt'), filename)
    read_keybinds()

def delete_keybinds(filename):
    """
    Deletes a keybindings file.

    Params:
        filename
            The filename to delete.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    os.remove(os.path.join(paths.get('keybinds'), filename))

