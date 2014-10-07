#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Color scheme management."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil
from . import helpers, paths
from .lnp import lnp

def read_colors():
    """Returns a list of color schemes."""
    return tuple([
        os.path.splitext(os.path.basename(p))[0] for p in
        helpers.get_text_files(paths.get('colors'))])

def get_colors(colorscheme=None):
    """
    Returns RGB tuples for all 16 colors in <colorscheme>.txt, or
    data/init/colors.txt if no scheme is provided."""
    result = []
    f = os.path.join(paths.get('init'), 'colors.txt')
    if colorscheme is not None:
        f = os.path.join(paths.get('colors'), colorscheme+'.txt')
    for c in [
            'BLACK', 'BLUE', 'GREEN', 'CYAN', 'RED', 'MAGENTA', 'BROWN',
            'LGRAY', 'DGRAY', 'LBLUE', 'LGREEN', 'LCYAN', 'LRED',
            'LMAGENTA', 'YELLOW', 'WHITE']:
        result.append((
            int(lnp.settings.read_value(f, c+'_R')),
            int(lnp.settings.read_value(f, c+'_G')),
            int(lnp.settings.read_value(f, c+'_B'))))
    return result

def load_colors(filename):
    """
    Replaces the current DF color scheme.

    Params:
        filename
        The name of the new colorscheme to install (filename without
        extension).
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    shutil.copyfile(
        os.path.join(paths.get('colors'), filename),
        os.path.join(paths.get('init'), 'colors.txt'))

def save_colors(filename):
    """
    Save current keybindings to a file.

    Params:
        filename
            The name of the new keybindings file.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    filename = os.path.join(paths.get('colors'), filename)
    shutil.copyfile(os.path.join(paths.get('init'), 'colors.txt'), filename)
    read_colors()

def color_exists(filename):
    """
    Returns whether or not a color scheme already exists.

    Params:
        filename
            The filename to check.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    return os.access(os.path.join(paths.get('colors'), filename), os.F_OK)

def delete_colors(filename):
    """
    Deletes a color scheme file.

    Params:
        filename
            The filename to delete.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    os.remove(os.path.join(paths.get('colors'), filename))


