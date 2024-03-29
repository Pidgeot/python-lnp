#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manages content manifests for graphics, mods, and utilities."""

import os

from . import json_config, paths
from .lnp import lnp


def get_cfg(content_type, item):
    """Returns a JSONConfiguration object for the given item.

    **Manifest format:**

    The manifest is a dictionary of values, which can be saved as manifest.json
    in the top level of the content folder.  Content is as below, except
    that True or False should not be capitalised.  Whitespace is irrelevant.
    Unused lines can be left out of the file.

    'title' and 'tooltip' control presentation in the list for that kind of
    content.  Both should be strings.  Title is the name in the list; tooltip
    is the hovertext - linebreaks are inserted with ``\\n``, since it must be
    one ine in the manifest file.

    'folder_prefix' controls what the name of the graphics pack's folder must
    begin with.

    'author' and 'version' are strings for the author and version of the
    content.  Both are for information only at this stage.

    'df_min_version', 'df_max_version', and 'df_incompatible_versions' allow
    you to specify versions of DF with which the content is incompatible.
    Versions are strings of numbers, of the format '0.40.24'.  Min and max are
    the lowest and highest compatible versions; anything outside that range has
    the content hidden.  If they are not set, they assume all earlier or later
    versions are compatible.  incompatible_versions is a list of specific
    versions which are incompatible, for when the range alone is insufficient.

    'needs_dfhack' is a boolean value, and should only be True if the content
    does not function *at all* without DFHack.  Partial requirements can be
    explained to the user with the 'tooltip' field.

    Args:
        content_type: 'graphics', 'mods', or 'utilities'
        item: content identifier path segment, such that
            the full path is ``'LNP/content_type/item/*'``

    Returns:
        core.json_config.JSONConfiguration: manifest object
    """
    default_config = {
        'author': '',
        'content_version': '',
        'df_min_version': '',
        'df_max_version': '',
        'df_incompatible_versions': [],
        'needs_dfhack': False,
        'title': '',
        'folder_prefix': '',
        'tooltip': ''
    }
    if content_type == 'utilities':
        default_config.update({
            'win_exe': '',
            'osx_exe': '',
            'linux_exe': '',
            'launch_with_terminal': False,
            'readme': '',
        })
    manifest = paths.get(content_type, item, 'manifest.json')
    return json_config.JSONConfiguration(manifest, default_config, warn=False)


def exists(content_type, item):
    """Returns a bool, that the given item has a manifest.
    Used before calling get_cfg if logging a warning isn't required."""
    return os.path.isfile(paths.get(content_type, item, 'manifest.json'))


def is_compatible(content_type, item, ver=''):
    """Boolean compatibility rating; True unless explicitly incompatible."""
    if not exists(content_type, item):
        return True
    if not ver:
        ver = lnp.df_info.version
    cfg = get_cfg(content_type, item)
    df_min_version = cfg.get_string('df_min_version')
    df_max_version = cfg.get_string('df_max_version')
    return not any([
        ver < df_min_version,
        (ver > df_max_version and df_max_version),
        ver in cfg.get_list('incompatible_df_versions'),
        cfg.get_bool('needs_dfhack') and 'dfhack' not in lnp.df_info.variations
    ])
