#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module to compress and sort legends exports from DF 0.40.09 and later.

.bmp converted to .png where possible.
Archive for Legends Viewer created if possible, or just
    compress the (huge) xml.
Sort files into region folder, with maps subfolders,
    and move to user content folder if found.
"""

from __future__ import print_function, unicode_literals, absolute_import

import glob
import os
import re
import subprocess
import zipfile

from . import paths, log
from .lnp import lnp

def get_region_info():
    """Returns a tuple of strings for an available region and date.
    Eg: ('region1', '00250-01-01')
    """
    files = [f for f in glob.glob(paths.get('df', 'region*-*-??-??-*')) if
             os.path.isfile(f)]
    if files:
        fname = os.path.basename(files[0])
        region = fname.partition('-')[0]
        date = re.search(r'\d+-\d\d\-\d\d', fname).group()
        return region, date

def compress_bitmaps():
    """Compresses all bitmap maps."""
    #pylint: disable=import-error, no-name-in-module
    try:
        from PIL import Image
    except ImportError:
        try:
            import Image
        except ImportError:
            call_optipng()
    else:
        log.i('Compressing bitmaps with PIL/Pillow')
        for fname in glob.glob(paths.get(
                'df', '-'.join(get_region_info()) + '-*.bmp')):
            f = Image.open(fname)
            f.save(fname[:-3] + 'png', format='PNG', optimize=True)
            os.remove(fname)

def call_optipng():
    """Calling optipng can work well, but isn't very portable."""
    if os.name == 'nt' and os.path.isfile(paths.get('df', 'optipng.exe')):
        log.w('Falling back to optipng for image compression. '
              'It is recommended to install PIL.')
        for fname in glob.glob(paths.get(
                'df', '-'.join(get_region_info()) + '-*.bmp')):
            ret = subprocess.call([paths.get('df', 'optipng'), '-zc9', '-zm9',
                                   '-zs0', '-f0', fname],
                                  creationflags=0x00000008)
            if ret == 0:
                os.remove(fname)
    else:
        log.e('A PIL-compatible library is required to compress bitmaps.')

def choose_region_map():
    """Returns the most-prefered region map available, or fallback."""
    pattern = paths.get('df', '-'.join(get_region_info()) + '-')
    for name in ('detailed', 'world_map'):
        for ext in ('.png', '.bmp'):
            if os.path.isfile(pattern + name + ext):
                return pattern + name + ext
    return pattern + 'world_map.bmp'

def create_archive():
    """Creates a legends archive, or zips the xml if files are missing."""
    pattern = paths.get('df', '-'.join(get_region_info()) + '-')
    l = [pattern + 'legends.xml', pattern + 'world_history.txt',
         choose_region_map(), pattern + 'world_sites_and_pops.txt']
    if os.path.isfile(pattern + 'legends_plus.xml'):
        l.append(pattern + 'legends_plus.xml')
    if all([os.path.isfile(f) for f in l]):
        with zipfile.ZipFile(pattern + 'legends_archive.zip',
                             'w', zipfile.ZIP_DEFLATED) as zipped:
            for f in l:
                zipped.write(f, os.path.basename(f))
                os.remove(f)
    elif os.path.isfile(pattern + 'legends.xml'):
        with zipfile.ZipFile(pattern + 'legends_xml.zip',
                             'w', zipfile.ZIP_DEFLATED) as zipped:
            zipped.write(pattern + 'legends.xml',
                         os.path.basename(pattern + 'legends.xml'))
            os.remove(pattern + 'legends.xml')

def move_files():
    """Moves files to a subdir, and subdir to ../User Generated Content if
    that dir exists."""
    pattern = paths.get('df', '-'.join(get_region_info()))
    region = get_region_info()[0]
    dirname = get_region_info()[0] + '_legends_exports'
    if os.path.isdir(os.path.join(lnp.BASEDIR, 'User Generated Content')):
        dirname = os.path.join(lnp.BASEDIR, 'User Generated Content', dirname)
    else:
        dirname = paths.get('df', dirname)
    for site_map in glob.glob(pattern + '-site_map-*'):
        target = os.path.join(dirname, 'site_maps', os.path.basename(site_map))
        if os.path.isfile(target):
            os.remove(site_map)
            continue
        os.renames(site_map, target)
    maps = ('world_map', 'bm', 'detailed', 'dip', 'drn', 'el', 'elw',
            'evil', 'hyd', 'nob', 'rain', 'sal', 'sav', 'str', 'tmp',
            'trd', 'veg', 'vol')
    for m in maps:
        m = glob.glob(pattern + '-' + m + '.???')
        if m:
            log.d('Found the following region map:  ' + str(m[0]))
            t = os.path.join(dirname, 'region_maps', os.path.basename(m[0]))
            if os.path.isfile(t):
                os.remove(m[0])
                continue
            os.renames(m[0], t)
    for f in glob.glob(paths.get('df', region + '-*')):
        log.d('Found the following misc files:  ' + str(f))
        if os.path.isfile(f):
            target = os.path.join(dirname, os.path.basename(f))
            if os.path.isfile(target):
                os.remove(f)
                continue
            os.renames(f, target)
    for f in glob.glob(paths.get('df', '*_color_key.txt')):
        os.remove(f)

def process_legends():
    """Process all legends exports in sets."""
    if lnp.df_info.version >= '0.40.09':
        i = 0
        while get_region_info():
            log.i('Processing legends from ' + get_region_info()[0])
            compress_bitmaps()
            create_archive()
            move_files()
            i += 1
        return i
