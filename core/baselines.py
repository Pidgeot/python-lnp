#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced raw and data folder management, for mods or graphics packs."""
from __future__ import print_function, unicode_literals, absolute_import

import os, glob, zipfile, fnmatch
from io import open

from . import paths, update
from .lnp import lnp

def find_vanilla(download_missing=True):
    """Finds the vanilla baseline for the current version.

    Starts by unzipping any DF releases in baselines and preprocessing them.
    If download_missing is set to True, missing baselines will be downloaded.

    Returns:
        Path to the vanilla folder, eg 'LNP/Baselines/df_40_15'
        False if baseline not available (and start download)
        None if version detection is not accurate
    """
    if lnp.df_info.source == "init detection":
        # WARNING: probably the wrong version!  Restore 'release notes.txt'.
        return None
    prepare_baselines()
    version = 'df_' + str(lnp.df_info.version)[2:].replace('.', '_')
    if os.path.isdir(paths.get('baselines', version)):
        return paths.get('baselines', version)
    if download_missing:
        update.download_df_baseline()
    return False

def find_vanilla_raws(download_missing=True):
    """Finds vanilla raws for the current version."""
    retval = find_vanilla(download_missing)
    if retval:
        return os.path.join(retval, 'raw')
    return retval

def prepare_baselines():
    """Unzip any DF releases found, and discard non-universial files."""
    zipped = glob.glob(os.path.join(paths.get('baselines'), 'df_??_?*.zip'))
    for item in zipped:
        version = os.path.basename(item)
        for s in ['_win', '_legacy', '_s', '.zip']:
            version = version.replace(s, '')
        f = paths.get('baselines', version)
        if not os.path.isdir(f):
            zipfile.ZipFile(item).extractall(f)
            simplify_pack(version, 'baselines')
        os.remove(item)

def set_auto_download(value):
    """Sets the option for auto-download of baselines."""
    lnp.userconfig['downloadBaselines'] = value
    lnp.userconfig.save_data()

def simplify_pack(pack, folder):
    """Removes unnecessary files from LNP/<folder>/<pack>.

    Params:
        pack, folder
            path segments in './LNP/folder/pack/' as strings

    Returns:
        The number of files removed if successful
        False if an exception occurred
        None if folder is empty
    """
    valid_dirs = ('graphics', 'mods', 'baselines')
    if not folder in valid_dirs:
        return False
    files_before = sum(len(f) for (_, _, f) in os.walk(paths.get(folder, pack)))
    if files_before == 0:
        return None
    if folder == 'baselines':
        keep = [os.path.join('raw', '*'),
                os.path.join('data', 'speech', '*'),
                os.path.join('data', 'art', '*'),
                os.path.join('data', 'init', '*')]
    if folder == 'graphics':
        keep = [os.path.join('raw', 'objects', '*'),
                os.path.join('raw', 'graphics', '*'),
                os.path.join('data', 'art', '*'),
                os.path.join('data', 'init', '*')]
    if folder == 'mods':
        keep = [os.path.join('raw', '*'),
                os.path.join('data', 'speech', '*')]
    for root, _, files in os.walk(paths.get(folder, pack)):
        d = paths.get(folder, pack)
        for k in files:
            f = os.path.join(root, k)
            if not any(fnmatch.fnmatch(f, os.path.join(d, p)) for p in keep):
                os.remove(f)
    if not folder == 'mods':
        init_files = ('colors', 'd_init', 'init', 'overrides')
        init_dir = paths.get(folder, pack, 'data', 'init')
        for f in os.listdir(init_dir):
            if not any(p in f for p in init_files):
                full_path = os.path.join(init_dir, f)
                if os.path.isdir(full_path):
                    os.rmdir(full_path)
                else:
                    os.remove(full_path)
    files_after = sum(len(f) for (_, _, f) in os.walk(paths.get(folder, pack)))
    return files_before - files_after

def remove_vanilla_raws_from_pack(pack, folder):
    """Remove files identical to vanilla raws, return files removed

    Params:
        pack, folder
            path segments in './LNP/folder/pack/' as strings

    Returns:
        The number of files removed
    """
    i = 0
    for folder, van_folder in (
            [paths.get(folder, pack, 'raw'), find_vanilla_raws()],
            [paths.get(folder, pack, 'data', 'speech'),
             paths.get('baselines', pack, 'data', 'speech')]):
        for root, _, files in os.walk(folder):
            for k in files:
                f = os.path.join(root, k)
                silently_kill = ('Thumbs.db', 'installed_raws.txt')
                if any(f.endswith(x) for x in silently_kill):
                    os.remove(f)
                    continue
                van_f = os.path.join(van_folder, os.path.relpath(f, folder))
                if os.path.isfile(van_f):
                    try:
                        with open(van_f, mode='r', encoding='cp437',
                                  errors='replace') as v:
                            vtext = v.read()
                        with open(f, mode='r', encoding='cp437',
                                  errors='replace') as m:
                            mtext = m.read()
                    except UnicodeDecodeError:
                        continue
                    if vtext == mtext:
                        os.remove(f)
                        i += 1
    return i

def remove_empty_dirs(pack, folder):
    """Removes empty subdirs in a mods or graphics pack.

    Params:
        pack, folder
            path segments in './LNP/folder/pack/' as strings

    Returns:
        The number of dirs removed
    """
    i = 0
    for _ in range(3):
        # only catches the lowest level each iteration
        for root, dirs, files in os.walk(paths.get(folder, pack)):
            if not dirs and not files:
                os.rmdir(root)
                i += 1
    return i
