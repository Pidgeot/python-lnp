#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import user content from an old DF or Starter Pack install.

The content to import is defined in PyLNP.json

Two import strategies are currently supported:
    copy_add: copy a file or directory contents, non-recursive, no overwriting
    text_prepend: prepend imported file content (for logfiles)

These strategies support the 'low hanging fruit' of imports.  Other content
or more advanced strategies have been identified, but are difficult to
implement without risking a 'bad import' scenario:

    init files:
        Not simply copyable. Sophisticated merging (similar to graphics
        upgrades) may lead to bad config when using settings from an older
        version of DF.  Will not be supported.
    keybinds:
        Could be imported by minimising interface.txt (and LNP/Keybinds/*)
        (see core/keybinds.py), and copying if a duplicate set is not yet
        available.  Planned for future update.
    world_gen, embark_profiles:
        Importing world gen and embark profiles may be supported eventually.
        No obvious downsides beyond tricky implementation.
    other:
        Custom settings importer - eg which graphics pack, are aquifers
        disabled, other PyLNP settings...  May be added later but no plans.

"""
from __future__ import print_function, unicode_literals, absolute_import

import os
import shutil

from . import lnp, log, paths


def saves_exist():
    """Return True if the pack has been used, based on $df/data/save/"""
    return os.path.isdir(paths.get('save')) and os.listdir(paths.get('save'))


def strat_copy_add(src, dest):
    """Copy a file or directory contents from src to dest, without overwriting.
    If a single file, an existing file may be overwritten if it only contains
    whitespace.  For directory contents, only the top level is 'filled in'.
    """
    # handle the simple case, one file
    if os.path.isfile(src):
        if os.path.isfile(dest):
            with open(dest) as f:
                if f.read().strip():
                    return
        shutil.copy2(src, dest)
        return
    # adding dir contents
    for it in os.listdir(src):
        if os.path.exists(os.path.join(dest, it)):
            continue
        if not os.path.isdir(dest):
            os.makedirs(dest)
        item = os.path.join(src, it)
        if os.path.isfile(item):
            shutil.copy2(item, dest)
        else:
            shutil.copytree(item, dest)


def strat_text_prepend(src, dest):
    """Prepend the src textfile to the dest textfile, creating it if needed."""
    if not os.path.isfile(src):
        return
    if not os.path.isfile(dest):
        shutil.copy2(src, dest)
        return
    with open(src) as f:
        srctext = f.read()
    with open(dest) as f:
        desttext = f.read()
    with open(src, 'w') as f:
        f.writelines([srctext, '\n', desttext])


def do_imports(from_df_dir):
    """Import content (defined in PyLNP.json) from the given previous df_dir,
    and associated LNP install if any.
    """
    # Get list of paths, and add dest where implicit (ie same as src)
    raw_config = [(c + [c[1]])[:3] for c in lnp.config['to_import']]
    # Turn "paths" in PyLNP into real paths
    path_pairs = [
        (st, os.path.normpath(src.replace('<df>', from_df_dir)),
         os.path.normpath(os.path.join(
            paths.get('root'), dest.replace('<df>', paths.get('df'))))
         )
        for st, src, dest in raw_config]

    # Sanity-check the provided paths...
    src_prefix = os.path.commonpath(src for _, src, _ in path_pairs)
    dest_prefix = os.path.commonpath(dest for _, _, dest in path_pairs)
    if not src_prefix:
        log.w('Can only import content from single basedir')
        return False
    if not dest_prefix or not paths.get('base').startswith(dest_prefix):
        log.w('Can only import content to destinations below current basedir')
        return False

    for strat, src, dest in path_pairs:
        if not os.path.exists(src):
            continue
        if strat == 'copy_add':
            strat_copy_add(src, dest)
        elif strat == 'text_prepend':
            strat_text_prepend(src, dest)
        else:
            log.w('Attempted to use unknown strategy')
    return True
