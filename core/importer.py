#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import user content from an old DF or Starter Pack install.


Provides three modes:
    - detect if no saves are present
    - choose what (if anything) to import from an old install (ie validation)
    - safely import the selected content



"""
from __future__ import print_function, unicode_literals, absolute_import

import os

from . import log, paths


def saves_exist():
    """Return True if the pack has been used, based on $df/data/save/"""
    return os.path.isdir(paths.get('save')) and os.listdir(paths.get('save'))


def choose_imports(basedir):
    """Return a list of suggested (src, dest) files and directories to copy
    from the old pack to the new pack. The list may be empty.

    This function is where the fun / tricky stuff lives...
    """
    # TODO:  add {tag: path} map in pylnp.json, allowing cross-pack imports
    # TODO:  (eventually)  support wildcards, error reporting, etc.
    # TODO:  (maybe)  allow runtime user input to resolve ambiguity

    # edit df.py to return stuff, instead of just mutating lnp.X
    # find DF dir in basedir
    # implement basic / vanilla version (saves, gamelog, etc.)
    return []


def do_imports(path_pairs):
    """For (src, dest) in path_pairs, copy from old pack to new.
    Return True/False for sucess/failure."""
    imports = tuple((os.path.normpath(src), os.path.normpath(dest))
                    for src, dest in path_pairs)

    src_prefix = os.path.commonpath(src for src, _ in imports)
    if not src_prefix:
        # TODO:  check that src_prefix is safe and sane - eg has DF dir inside
        log.w('Can only import content from single basedir')
        return False

    dest_prefix = os.path.commonpath(dest for _, dest in imports)
    if not dest_prefix or not paths.get('base').startswith(dest_prefix):
        log.w('Can only import content to destinations below current basedir')
        return False

    for src, dest in path_pairs:
        # TODO:  Validate that src exists and dest does not or is empty
        # TODO:  Copy data from src to dest
        pass
    return True



