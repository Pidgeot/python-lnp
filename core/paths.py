#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Path management."""
from __future__ import print_function, unicode_literals, absolute_import

import os

__paths = {}

def _identify_folder_name(base, name):
    """
    Allows folder names to be lowercase on case-sensitive systems.
    Returns "base/name" where name is lowercase if the lower case version
    exists and the standard case version does not.

    Params:
        base
            The path containing the desired folder.
        name
            The standard case name of the desired folder.
    """
    normal = os.path.join(base, name)
    lower = os.path.join(base, name.lower())
    if os.path.isdir(lower) and not os.path.isdir(normal):
        return lower
    return normal


def register(name, *path_elms, **kwargs):
    """Registers a path constructed by <path_elms> under <name>.
    If multiple path elements are given, the last
    element will undergo case correction (see _identify_folder_name).
    kwargs:
        allow_create
            If True, the registered path will be created if it does not already
            exist. Defaults to True."""
    if len(path_elms) > 1:
        __paths[name] = _identify_folder_name(os.path.join(
            *path_elms[:-1]), path_elms[-1])
    else:
        __paths[name] = path_elms[0]
    if kwargs.get('allow_create', True) and not os.path.exists(__paths[name]):
        os.makedirs(__paths[name])


def get(name, *paths):
    """Returns the path registered under <name>, or an empty string if <name>
    is not known."""
    try:
        base = __paths[name]
    except KeyError:
        base = ''
    return os.path.join(base, *paths)


def clear():
    """Clears the path cache."""
    __paths.clear()
