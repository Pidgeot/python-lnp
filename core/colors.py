#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Color scheme management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, shutil
from . import helpers, paths
from .lnp import lnp
from .dfraw import DFRaw

_df_colors = (
    'BLACK', 'BLUE', 'GREEN', 'CYAN',
    'RED', 'MAGENTA', 'BROWN', 'LGRAY',
    'DGRAY', 'LBLUE', 'LGREEN', 'LCYAN',
    'LRED', 'LMAGENTA', 'YELLOW', 'WHITE'
)

def read_colors():
    """Returns a list of color schemes."""
    return tuple([
        os.path.splitext(os.path.basename(p))[0] for p in
        helpers.get_text_files(paths.get('colors'))])

def get_colors(colorscheme=None):
    """
    Returns RGB tuples for all 16 colors in <colorscheme>.txt, or
    data/init/colors.txt if no scheme is provided. On errors, returns an empty
    list."""
    # pylint:disable=bare-except
    try:
        if colorscheme is not None:
            f = colorscheme
            if not f.endswith('.txt'):
                f = f + '.txt'
            if os.path.dirname(f) == '':
                f = os.path.join(paths.get('colors'), f)
        else:
            if lnp.df_info.version <= '0.31.03':
                f = os.path.join(paths.get('init'), 'init.txt')
            else:
                f = os.path.join(paths.get('init'), 'colors.txt')
        color_fields = [(c+'_R', c+'_G', c+'_B') for c in _df_colors]
        result = DFRaw(f).get_values(*color_fields)
        return [tuple(map(int, t)) for t in result]
    except:
        return []

def load_colors(filename):
    """
    Replaces the current DF color scheme.

    Params:
        filename
        The name of the new colorscheme to install (extension optional).
        If no path is specified, file is assumed to be in LNP/Colors.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    if os.path.dirname(filename) == '':
        filename = os.path.join(paths.get('colors'), filename)
    if lnp.df_info.version <= '0.31.03':
        colors = ([c+'_R' for c in _df_colors] + [c+'_G' for c in _df_colors] +
                  [c+'_B' for c in _df_colors])
        lnp.settings.read_file(filename, colors, False)
        lnp.settings.write_settings()
    else:
        shutil.copyfile(filename, os.path.join(paths.get('init'), 'colors.txt'))

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
    if lnp.df_info.version <= '0.31.03':
        print(
            "Exporting colors is only supported for DF 0.31.04 and later",
            file=sys.stderr)
        colors = ([c+'_R' for c in _df_colors] + [c+'_G' for c in _df_colors] +
                  [c+'_B' for c in _df_colors])
        lnp.settings.create_file(filename, colors)
    else:
        shutil.copyfile(os.path.join(paths.get('init'), 'colors.txt'), filename)

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

def get_installed_file():
    """Returns the name of the currently installed color scheme."""
    files = helpers.get_text_files(paths.get('colors'))
    current_scheme = get_colors()
    for scheme in files:
        if get_colors(scheme) == current_scheme:
            return os.path.splitext(os.path.basename(scheme))[0]
    return None
