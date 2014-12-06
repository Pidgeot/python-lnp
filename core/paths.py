#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Path management."""
from __future__ import print_function, unicode_literals, absolute_import

import os
from . import helpers

__paths = {}


def register(name, *path_elms):
    """Registers a path constructed by <path_elms> under <name>.
    If multiple path elements are given, the last
    element will undergo case correction (see helpers.identify_folder_name)."""
    if len(path_elms) > 1:
        __paths[name] = helpers.identify_folder_name(os.path.join(
            *path_elms[:-1]), path_elms[-1])
    else:
        __paths[name] = path_elms[0]


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
