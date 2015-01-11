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

import os, zipfile, glob, subprocess
from . import paths

def get_region_info():
    """Returns a tuple of strings for an available region and date.
    Eg: ('region1', '00250-01-01')
    """
    if glob.glob(paths.get('df', 'region*-*')):
        fname = os.path.basename(glob.glob(paths.get('df', 'region*-*'))[0])
        idx = fname.index('-')
        date = fname[idx+1:idx+12]
        if date[6] == '-':
            date = fname[idx+1:idx+13]
        elif date[7] == '-':
            date = fname[idx+1:idx+14]
        return (fname[:idx], date)

def compress_bitmaps():
    """Compresses all bitmap maps."""
    try:
        from PIL import Image
    except ImportError:
        try:
            import Image
        except ImportError:
            print('Please install PIL or Pillow to compress bitmaps.')
            call_optipng()
    else:
        for fname in glob.glob(paths.get(
                'df', '-'.join(get_region_info()) + '-*.bmp')):
            f = Image.open(fname)
            f.save(fname[:-3] + 'png', format='PNG', optimize=True)
            os.remove(fname)

def call_optipng():
    """Calling optipng can work well, but isn't very portable."""
    if os.name == 'nt' and os.path.isfile(paths.get('df', 'optipng.exe')):
        print('Falling back to optipng for image compression.')
        for fname in glob.glob(paths.get(
                'df', '-'.join(get_region_info()) + '-*.bmp')):
            ret = subprocess.call([paths.get('df', 'optipng'), '-zc9', '-zm9',
                                   '-zs0', '-f0', fname],
                                  creationflags=0x00000008)
            if ret == 0:
                os.remove(fname)

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
    if all([os.path.isfile(f) for f in l]):
        with zipfile.ZipFile(pattern[:-1] + '_legends_archive.zip',
                             'w', zipfile.ZIP_DEFLATED) as zipped:
            for f in l:
                zipped.write(f)
                os.remove(f)
    elif os.path.isfile(pattern + 'legends.xml'):
        with zipfile.ZipFile(pattern[:-1] + '_legends_xml.zip',
                             'w', zipfile.ZIP_DEFLATED) as zipped:
            zipped.write(pattern + 'legends.xml')
            os.remove(pattern + 'legends.xml')

def move_files():
    """Moves files to a subdir, and subdir to ../User Generated Content if
    that dir exists."""
    pattern = paths.get('df', '-'.join(get_region_info()))
    dirname = get_region_info()[0] + '_legends_exports'
    if os.path.isdir(os.path.join('..', 'User Generated Content')):
        dirname = os.path.join('..', 'User Generated Content', dirname)
    else: dirname = paths.get('df', dirname)
    for site_map in glob.glob(pattern + '-site_map-*'):
        os.renames(site_map, os.path.join(dirname, 'site_maps', site_map))
    maps = ('world_map', 'bm', 'detailed', 'dip', 'drn', 'el', 'elw',
            'evil', 'hyd', 'nob', 'rain', 'sal', 'sav', 'str', 'tmp',
            'trd', 'veg', 'vol')
    for m in maps:
        m = glob.glob(pattern + '-' + m + '.???')
        if m:
            os.renames(m[0], os.path.join(dirname, 'region_maps', m[0]))
    files = (glob.glob(pattern + '*') +
             [get_region_info()[0] + '-world_gen_param.txt'])
    for file in files:
        os.renames(file, os.path.join(dirname, file))

def process_legends():
    """Process all legends exports in sets."""
    if lnp.df_info.version >= '0.40.09':
        i = 0
        while get_region_info():
            compress_bitmaps()
            create_archive()
            move_files()
            i += 1
        return i
    else:
        # TODO:  support legends exports from before 40.09 (best-effort)
        pass
