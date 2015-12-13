#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Embark profile management."""
from __future__ import print_function, unicode_literals, absolute_import

import os
from . import helpers, paths, log
from .dfraw import DFRaw

def read_embarks():
    """Returns a list of embark profiles."""
    return sorted(tuple([
        os.path.basename(o) for o in helpers.get_text_files(
            paths.get('embarks'))]))

def install_embarks(files):
    """
    Installs a list of embark profiles.

    Params:
        files
            List of files to install.
    """
    with DFRaw.open(paths.get('init', 'embark_profiles.txt'), 'wt') as out:
        log.i('Installing embark profiles: ' + str(files))
        for f in files:
            embark = DFRaw.read(paths.get('embarks', f))
            out.write(embark + "\n\n")

def get_installed_files():
    """Returns the names of the currently installed embark profiles."""
    files = helpers.get_text_files(paths.get('embarks'))
    current = paths.get('init', 'embark_profiles.txt')
    result = helpers.detect_installed_files(current, files)
    return [os.path.basename(r) for r in result]
