#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced raw and data folder management, for mods or graphics packs."""

import fnmatch
import glob
import os
import shutil
import tarfile
import zipfile

from . import log, paths, update
from .lnp import lnp


def find_vanilla(download_missing=True):
    """Finds the vanilla baseline for the current version.

    Starts by unzipping any DF releases in baselines and preprocessing them.
    If download_missing is set to True, missing baselines will be downloaded.

    Returns:
        Path to the vanilla folder, eg ``'LNP/Baselines/df_40_15'``,
        ``False`` if baseline not available (and start download),
        ``None`` if version detection is not accurate
    """
    if lnp.df_info.source == "init detection":
        log.w('Baseline DF version from init detection; highly unreliable!')
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
    """Unzip any DF releases found, and discard non-universal files."""
    archives = glob.glob(os.path.join(paths.get('baselines'), 'df_??_?*.???'))
    if archives:
        log.i('Extracting archives in baselines: ' + str(archives))
    for item in archives:
        version = os.path.basename(item)
        for s in ('_win32', '_osx32', '_linux32', '_legacy32',
                  '_win', '_osx', '_linux', '_legacy', '_s',
                  '.zip', '.tar.bz2'):
            version = version.replace(s, '')
        f = paths.get('baselines', version)
        if not os.path.isdir(f):
            if item.endswith('.zip'):
                with zipfile.ZipFile(item) as zipped:
                    zipped.extractall(f)
            elif item.endswith('.tar.bz2'):
                with tarfile.TarFile(item) as tarred:
                    tarred.extractall(f)
                for k in glob.glob(os.path.join(f, 'df_*x', '*')):
                    shutil.move(k, f)
            simplify_pack(version, 'baselines')
        os.remove(item)


def set_auto_download(value):
    """Sets the option for auto-download of baselines."""
    lnp.userconfig['downloadBaselines'] = value
    lnp.userconfig.save_data()


def simplify_pack(pack, folder):
    """Removes unnecessary files from LNP/<folder>/<pack>.

    Args:
        pack, folder: path segments in ``'./LNP/folder/pack/'`` as strings

    Returns:
        The number of files removed if successful,
        ``False`` if an exception occurred,
        ``None`` if folder is empty
    """
    if folder not in ('graphics', 'mods', 'baselines'):
        return False
    log.i('Simplifying {}: {}'.format(folder, pack))
    packdir = paths.get(folder, pack)
    files_before = sum(len(f) for _, _, f in os.walk(packdir))
    if files_before == 0:
        return None
    keep = [('raw',), ('data', 'speech')]
    if folder == 'graphics':
        keep = [('raw', 'objects'), ('raw', 'graphics')]
    if folder != 'mods':
        keep += [('data', 'art')] + [
            ('data', 'init', f + '.txt') for f in
            ('colors', 'd_init', 'init', 'overrides')]
    if folder == 'baselines':
        keep.append(('data', 'init', 'interface.txt'))
    keep = [os.path.join(*k) for k in keep]
    for root, _, files in os.walk(packdir):
        for k in files:
            if k == 'manifest.json' or 'readme' in k.lower():
                continue
            f = os.path.join(root, k)
            if not any(fnmatch.fnmatch(f, os.path.join(packdir, pattern, '*'))
                       for pattern in keep):
                os.remove(f)
    files_after = sum(len(f) for _, _, f in os.walk(packdir))
    log.v('Removed {} files'.format(files_before - files_after))
    return files_before - files_after


def remove_vanilla_raws_from_pack(pack, folder):
    """Remove files identical to vanilla raws, return files removed

    Args:
        pack, folder: path segments in ``'./LNP/folder/pack/'`` as strings

    Returns:
        int: the number of files removed
    """
    if not find_vanilla():
        return 0
    i = 0
    for _folder, van_folder in (
            [paths.get(folder, pack, 'raw'), find_vanilla_raws()],
            [paths.get(folder, pack, 'data', 'speech'),
             os.path.join(find_vanilla(), 'data', 'speech')]):
        for root, _, files in os.walk(_folder):
            for k in files:
                f = os.path.join(root, k)
                silently_kill = ('Thumbs.db', 'installed_raws.txt')
                if any(f.endswith(x) for x in silently_kill):
                    os.remove(f)
                    continue
                van_f = os.path.join(van_folder, os.path.relpath(f, _folder))
                if os.path.isfile(van_f):
                    with open(van_f, encoding='cp437', errors='replace') as v:
                        vtext = v.read()
                    with open(f, encoding='cp437', errors='replace') as m:
                        mtext = m.read()
                    if vtext == mtext:
                        os.remove(f)
                        i += 1
    return i


def remove_empty_dirs(pack, folder):
    """Removes empty subdirs in a mods or graphics pack.

    Args:
        pack, folder: path segments in ``'./LNP/folder/pack/'`` as strings

    Returns:
        int: the number of dirs removed
    """
    i = 0
    for _ in range(3):
        # only catches the lowest level each iteration
        for root, dirs, files in os.walk(paths.get(folder, pack)):
            if not dirs and not files:
                os.rmdir(root)
                i += 1
    return i
