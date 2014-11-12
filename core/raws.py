#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced raw and data folder management, for mods or graphics packs."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil, filecmp, sys, glob, tempfile
import distutils.dir_util as dir_util

from . import paths, update

paths.register('baselines', 'LNP', 'baselines')

def find_vanilla_raws(version=None):
    # override for testing:
    return os.path.join('LNP', 'Baselines', 'df_40_11_win', 'raw')
    """Finds vanilla raws for the requested version.
    If required, unzip a DF release to create the folder in LNP/Baselines/.

    Params:
        version
            String indicating version in format 'df_40_15'
            None returns the latest available raws.

    Returns:
        The path to the requested vanilla 'raw' folder
        If requested version unavailable, path to latest version
        None if no version was available.
    """
    # TODO: handle other DF versions; esp. small pack and non-SDL releases
    # and non-zip files?  Folder size minimisation?
    available = [os.path.basename(item) for item in glob.glob(
                 os.path.join(paths.get('baselines'), 'df_??_?*'))]
    if version == None:
        version = available[-1][0:8]
    version_dir = os.path.join(paths.get('baselines'), version)
    version_dir_win = os.path.join(paths.get('baselines'), version + '_win')

    if os.path.isdir(version_dir):
        return os.path.join(version_dir, 'raw')
    elif os.path.isdir(version_dir_win):
        return os.path.join(version_dir, 'raw')
    elif os.path.isfile(version_dir + '.zip'):
        file = zipfile.ZipFile(version_dir + '_win.zip')
        file.extractall(version_dir)
        return os.path.join(version_dir, 'raw')
    else:
        update.download_df_version_to_baselines(version)
        return None

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
    if not (folder=='graphics' or folder=='mods'):
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

        if folder=='mods'and os.path.exists(os.path.join(tmp, 'manifest.json')):
            shutil.copyfile(
                os.path.join(tmp, 'manifest.json'),
                os.path.join(pack, 'manifest.json'))
        if folder=='mods'and os.path.exists(os.path.join(tmp, 'readme.txt')):
            shutil.copyfile(
                os.path.join(tmp, 'readme.txt'),
                os.path.join(pack, 'readme.txt'))
        if folder=='mods'and os.path.exists(os.path.join(tmp, 'installed_mods.txt')):
            shutil.copyfile(
                os.path.join(tmp, 'raw', 'installed_mods.txt'),
                os.path.join(pack, 'raw', 'installed_mods.txt'))

        if folder=='graphics':
            os.makedirs(os.path.join(pack, 'data', 'init'))
            os.makedirs(os.path.join(pack, 'data', 'art'))
            dir_util.copy_tree(
                os.path.join(tmp, 'data', 'art'),
                os.path.join(pack, 'data', 'art'))
            for filename in ('colors.txt', 'init.txt',
                             'd_init.txt'): #, 'overrides.txt'
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
