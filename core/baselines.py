#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced raw and data folder management, for mods or graphics packs."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil, filecmp, sys, glob, tempfile, re, zipfile
import distutils.dir_util as dir_util

from . import paths
from . import update
from .lnp import lnp

def find_vanilla_raws(version=None):
    """Finds vanilla raws for the requested version.
    If required, unzip a DF release to create the folder in LNP/Baselines/.

    Params:
        version
            String indicating version in format 'df_40_15'
            None returns the latest available raws.

    Returns:
        The path to the requested vanilla 'raw' folder
            eg: 'LNP/Baselines/df_40_15/raw'
        If requested version unavailable, path to latest version
        None if no version was available.
    """
    # TODO: handle other DF versions; esp. small pack and non-SDL releases
    zipped = glob.glob(os.path.join(paths.get('baselines'), 'df_??_?*.zip'))
    for item in zipped:
        version = os.path.basename(item)[0:8]
        file = os.path.join(paths.get('baselines'), version)
        if not os.path.isdir(file):
            zipfile.ZipFile(item).extractall(file)
            simplify_pack(version, 'baselines')
        os.remove(item)

    available = [os.path.basename(item) for item in glob.glob(os.path.join(
                paths.get('baselines'), 'df_??_?*')) if os.path.isdir(item)]
    if version == None:
        version = 'df_' + str(lnp.df_info.version)[2:].replace('.', '_')
        if lnp.df_info.source == "init detection":
            # WARNING: likley to be much too early in this case
            # User should restore 'release notes.txt'
            pass
    if version not in available:
        update.download_df_version_to_baselines(version)
        version = available[-1]

    return os.path.join(paths.get('baselines'), version, 'raw')

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

        if not folder=='mods':
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
    for root, dirs, files in os.walk(raw_folder):
        for file in files:
            file = os.path.join(root, file)
            # silently clean up so empty dirs can be removed
            silently_kill = ('Thumbs.db', 'installed_mods.txt')
            if any(file.endswith(k) for k in silently_kill):
                os.remove(file)
                continue
            file = os.path.relpath(file, raw_folder)
            # if there's an identical vanilla file, remove the mod file
            if os.path.isfile(os.path.join(vanilla_raw_folder, file)):
                if filecmp.cmp(os.path.join(vanilla_raw_folder, file),
                               os.path.join(raw_folder, file)):
                    os.remove(os.path.join(raw_folder, file))

def remove_empty_dirs(pack, folder):
    """Removes empty subdirs in a mods or graphics pack.

    Params:
        pack
            The pack to simplify.
        folder
            The parent folder of the pack (either 'mods' or 'graphics')
    """
    pack = os.path.join(paths.get(folder), pack)
    for n in range(3):
        # only catches the lowest level each iteration
        for root, dirs, files in os.walk(pack):
            if not dirs and not files:
                os.rmdir(root)
