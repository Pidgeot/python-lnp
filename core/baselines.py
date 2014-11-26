#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced raw and data folder management, for mods or graphics packs."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil, filecmp, sys, glob, tempfile, zipfile
import distutils.dir_util as dir_util

from . import paths, update
from .lnp import lnp

def find_vanilla_raws():
    """Finds vanilla raws for the current version.
    Starts by unzipping any DF releases in baselines and preprocessing them.

    Returns:
        Path to the vanilla 'raw' folder, eg 'LNP/Baselines/df_40_15/raw'
        False if baseline not available (and start download)
        None if version detection is not accurate
    """
    if lnp.df_info.source == "init detection":
        # WARNING: probably the wrong version!  Restore 'release notes.txt'.
        return None
    prepare_baselines()
    version = 'df_' + str(lnp.df_info.version)[2:].replace('.', '_')
    if os.path.isdir(os.path.join(paths.get('baselines'), version, 'raw')):
        return os.path.join(paths.get('baselines'), version, 'raw')
    update.download_df_baseline()
    return False

def prepare_baselines():
    """Unzip any DF releases found, and discard non-universial files."""
    zipped = glob.glob(os.path.join(paths.get('baselines'), 'df_??_?*.zip'))
    for item in zipped:
        version = os.path.basename(item)
        for s in ['_win', '_legacy', '_s', '.zip']:
            version = version.replace(s, '')
        f = os.path.join(paths.get('baselines'), version)
        if not os.path.isdir(f):
            zipfile.ZipFile(item).extractall(f)
            simplify_pack(version, 'baselines')
        os.remove(item)

def simplify_pack(pack, folder):
    """Removes unnecessary files from LNP/<folder>/<pack>.
    Necessary files means:
      * 'raw/objects/' and 'raw/graphics/'
      * 'data/art/' for graphics, and specific files in 'data/init/'
      * readme.txt and manifest.json for mods

    Params:
        pack
            The pack to simplify.
        folder
            The parent folder of the pack (either 'mods' or 'graphics')

    Returns:
        The number of files removed if successful
        False if an exception occurred
        None if folder is empty
    """
    valid_dirs = ('graphics', 'mods', 'baselines')
    if not folder in valid_dirs:
        return False
    pack = os.path.join(paths.get(folder), pack)
    files_before = sum(len(f) for (_, _, f) in os.walk(pack))
    if files_before == 0:
        return None
    tmp = tempfile.mkdtemp()
    try:
        dir_util.copy_tree(pack, tmp)
        if os.path.isdir(pack):
            dir_util.remove_tree(pack)

        os.makedirs(pack)
        os.makedirs(os.path.join(pack, 'raw', 'graphics'))
        os.makedirs(os.path.join(pack, 'raw', 'objects'))

        if os.path.exists(os.path.join(tmp, 'raw', 'graphics')):
            dir_util.copy_tree(
                os.path.join(tmp, 'raw', 'graphics'),
                os.path.join(pack, 'raw', 'graphics'))
        if os.path.exists(os.path.join(tmp, 'raw', 'objects')):
            dir_util.copy_tree(
                os.path.join(tmp, 'raw', 'objects'),
                os.path.join(pack, 'raw', 'objects'))

        if not folder == 'mods':
            os.makedirs(os.path.join(pack, 'data', 'init'))
            os.makedirs(os.path.join(pack, 'data', 'art'))
            if os.path.exists(os.path.join(tmp, 'data', 'art')):
                dir_util.copy_tree(
                    os.path.join(tmp, 'data', 'art'),
                    os.path.join(pack, 'data', 'art'))
            for filename in ('colors.txt', 'init.txt',
                             'd_init.txt', 'overrides.txt'):
                if os.path.isfile(os.path.join(tmp, 'data', 'init', filename)):
                    shutil.copyfile(
                        os.path.join(tmp, 'data', 'init', filename),
                        os.path.join(pack, 'data', 'init', filename))

    except IOError:
        sys.excepthook(*sys.exc_info())
        retval = False
    else:
        files_after = sum(len(f) for (_, _, f) in os.walk(pack))
        retval = files_after - files_before
    if os.path.isdir(tmp):
        dir_util.remove_tree(tmp)
    return retval

def remove_vanilla_raws_from_pack(pack, folder):
    """Remove files identical to vanilla raws, return files removed

    Params:
        pack
            The pack to simplify.
        folder
            The parent folder of the pack (either 'mods' or 'graphics')
    """
    raw_folder = os.path.join(paths.get(folder), pack, 'raw')
    vanilla_raw_folder = find_vanilla_raws()
    for root, _, files in os.walk(raw_folder):
        for f in files:
            f = os.path.join(root, f)
            # silently clean up so empty dirs can be removed
            silently_kill = ('Thumbs.db', 'installed_mods.txt')
            if any(f.endswith(k) for k in silently_kill):
                os.remove(f)
                continue
            f = os.path.relpath(f, raw_folder)
            # if there's an identical vanilla file, remove the mod file
            if os.path.isfile(os.path.join(vanilla_raw_folder, f)):
                if filecmp.cmp(os.path.join(vanilla_raw_folder, f),
                               os.path.join(raw_folder, f)):
                    os.remove(os.path.join(raw_folder, f))

def remove_empty_dirs(pack, folder):
    """Removes empty subdirs in a mods or graphics pack.

    Params:
        pack
            The pack to simplify.
        folder
            The parent folder of the pack (either 'mods' or 'graphics')
    """
    pack = os.path.join(paths.get(folder), pack)
    for _ in range(3):
        # only catches the lowest level each iteration
        for root, dirs, files in os.walk(pack):
            if not dirs and not files:
                os.rmdir(root)
