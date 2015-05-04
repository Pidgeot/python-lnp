#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manages content manifests for graphics, mods, and utilities."""
from __future__ import print_function, unicode_literals, absolute_import

import os

from . import paths, json_config
from .lnp import lnp

def get_cfg(content_type, item):
    """Returns a JSONConfiguration object for the given item.

    Params:
        content_type
            'graphics' or 'mods'
        item
            content identifier path segment, such that
            the full path is 'LNP/content_type/item/*'

    Manifest format:
    The manifest is a dictionary of values, which can be saved as manifest.json
    in the top level of the content folder.  Content is as below, except
    that True or False should not be capitalised.  Whitespace is irrelevant.
    Unused lines can be left out of the file.

    'title' and 'tooltip' control presentation in the list for that kind of
    content.  Both should be strings.  Title is the name in the list; tooltip
    is the hovertext - linebreaks are inserted with "\n", since it must be one
    line in the manifest file.

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
    """
    default_config = {
        'author': '',
        'content_version': '',
        'df_min_version': '',
        'df_max_version': '',
        'df_incompatible_versions': [],
        'needs_dfhack': False,
        'title': '',
        'tooltip': ''
        }
    manifest = paths.get(content_type, item, 'manifest.json')
    return json_config.JSONConfiguration(manifest, default_config, warn=False)

def exists(content_type, item):
    """Returns a bool, that the given item has a manifest.
    Used before calling get_cfg if logging a warning isn't required."""
    if os.path.isfile(paths.get(content_type, item, 'manifest.json')):
        return True
    return False

def is_compatible(content_type, item):
    """Boolean compatibility rating; True unless explicitly incompatible."""
    if not exists(content_type, item):
        return True
    cfg = get_cfg(content_type, item)
    if any([lnp.df_info.version < cfg.get_string('df_min_version'),
            (lnp.df_info.version > cfg.get_string('df_max_version')
             and cfg.get_string('df_max_version')),
            lnp.df_info.version in cfg.get_list('incompatible_df_versions'),
            (cfg.get_bool('needs_dfhack') and
             'dfhack' not in lnp.df_info.variations)]):
        return False
    return True

