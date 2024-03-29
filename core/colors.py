#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Color scheme management."""

import os
import shutil

from . import helpers, log, paths
from .dfraw import DFRaw
from .lnp import lnp

_df_colors = (
    'BLACK', 'BLUE', 'GREEN', 'CYAN',
    'RED', 'MAGENTA', 'BROWN', 'LGRAY',
    'DGRAY', 'LBLUE', 'LGREEN', 'LCYAN',
    'LRED', 'LMAGENTA', 'YELLOW', 'WHITE'
)


def read_colors():
    """Returns a sorted tuple of color scheme basenames, in LNP/Colors."""
    return tuple(sorted(
        [os.path.splitext(os.path.basename(p))[0] for p in
         helpers.get_text_files(paths.get('colors'))],
        key=helpers.key_from_underscore_prefixed_string))


def get_colors(colorscheme=None):
    """
    Returns RGB tuples for all 16 colors in <colorscheme>.txt, or
    data/init/colors.txt if no scheme is provided. On errors, returns an empty
    list."""
    try:
        if colorscheme is not None:
            f = colorscheme
            if not f.endswith('.txt'):
                f = f + '.txt'
            if os.path.dirname(f) == '':
                f = paths.get('colors', f)
        else:
            if lnp.df_info.version <= '0.31.03':
                f = paths.get('init', 'init.txt')
            else:
                f = paths.get('init', 'colors.txt')
        color_fields = [(c + '_R', c + '_G', c + '_B') for c in _df_colors]
        result = DFRaw(f).get_values(*color_fields)
        return [tuple(int(x) for x in t) for t in result]
    except Exception:
        if colorscheme:
            log.e('Unable to read colorscheme %s', colorscheme, stack=True)
        else:
            log.e('Unable to read current colors', stack=True)
        return []


def load_colors(filename):
    """
    Replaces the current DF color scheme.

    Args:
        filename: The name of the new colorscheme to apply (extension optional).
            If no path is specified, file is assumed to be in LNP/Colors.
    """
    log.i('Loading colorscheme ' + filename)
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    if os.path.dirname(filename) == '':
        filename = paths.get('colors', filename)
    if lnp.df_info.version <= '0.31.03':
        colors = ([c + '_R' for c in _df_colors] + [c + '_G' for c in _df_colors]
                  + [c + '_B' for c in _df_colors])
        lnp.settings.read_file(filename, colors, False)
        lnp.settings.write_settings()
    else:
        shutil.copyfile(filename, paths.get('init', 'colors.txt'))


def save_colors(filename):
    """
    Save current keybindings to a file.

    Args:
        filename: the name of the new color scheme file.
    """
    log.i('Saving colorscheme ' + filename)
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    filename = paths.get('colors', filename)
    if lnp.df_info.version <= '0.31.03':
        colors = ([c + '_R' for c in _df_colors] + [c + '_G' for c in _df_colors]
                  + [c + '_B' for c in _df_colors])
        lnp.settings.create_file(filename, colors)
    else:
        shutil.copyfile(paths.get('init', 'colors.txt'), filename)


def color_exists(filename):
    """
    Returns whether a color scheme already exists.

    Args:
        filename: the filename to check.
    """
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    return os.access(paths.get('colors', filename), os.F_OK)


def delete_colors(filename):
    """
    Deletes a color scheme file.

    Args:
        filename: the filename to delete.
    """
    log.i('Deleting colorscheme ' + filename)
    if not filename.endswith('.txt'):
        filename = filename + '.txt'
    os.remove(paths.get('colors', filename))


def get_installed_file():
    """Returns the name of the currently installed color scheme, or None."""
    files = helpers.get_text_files(paths.get('colors'))
    current_scheme = get_colors()
    for scheme in files:
        if get_colors(scheme) == current_scheme:
            return os.path.splitext(os.path.basename(scheme))[0]
    return None
