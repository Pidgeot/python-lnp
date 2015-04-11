#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Graphics pack management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, shutil, glob
from .launcher import open_folder
from .lnp import lnp
from . import colors, df, paths, baselines, mods
from .dfraw import DFRaw

def open_graphics():
    """Opens the graphics pack folder."""
    open_folder(paths.get('graphics'))

def current_pack():
    """Returns the currently installed graphics pack.
    If the pack cannot be identified, returns "FONT/GRAPHICS_FONT".
    """
    p = paths.get('df', 'raw', 'installed_raws.txt')
    if os.path.isfile(p):
        if logged_graphics(p):
            return logged_graphics(p)
    packs = read_graphics()
    for p in packs:
        if (lnp.settings.FONT == p[1] and
                lnp.settings.GRAPHICS_FONT == p[2]):
            return p[0]
    result = str(lnp.settings.FONT)
    if lnp.settings.version_has_option('GRAPHICS_FONT'):
        result += '/'+str(lnp.settings.GRAPHICS_FONT)
    return result

def logged_graphics(logfile):
    """Returns the graphics pack from an 'installed_raws.txt' file"""
    if os.path.isfile(logfile):
        with open(logfile) as f:
            for l in f.readlines():
                if l.startswith('graphics/'):
                    return l.strip().replace('graphics/', '')
    return ''

def read_graphics():
    """Returns a list of tuples of (graphics dir, FONT, GRAPHICS_FONT)."""
    packs = [os.path.basename(o) for o in
             glob.glob(paths.get('graphics', '*')) if os.path.isdir(o)]
    result = []
    for p in packs:
        if not validate_pack(p):
            continue
        init_path = paths.get('graphics', p, 'data', 'init', 'init.txt')
        #pylint: disable=unbalanced-tuple-unpacking
        font, graphics = DFRaw(init_path).get_values('FONT', 'GRAPHICS_FONT')
        result.append((p, font, graphics))
    return tuple(result)

def install_graphics(pack):
    """Installs the graphics pack located in LNP/Graphics/<pack>.

    Params:
        pack
            The name of the pack to install.

    Returns:
        True if successful,
        False if an exception occured
        None if baseline vanilla raws are missing
    """
    if not baselines.find_vanilla_raws():
        return None
    try:
        # Update raws
        if not update_graphics_raws(paths.get('df', 'raw'), pack):
            return 0
        # Copy art
        shutil.rmtree(paths.get('data', 'art'))
        shutil.copytree(paths.get('graphics', pack, 'data', 'art'),
                        paths.get('data', 'art'))
        for item in glob.glob(paths.get('tilesets', '*')):
            if not os.path.exists(paths.get('data', 'art',
                                            os.path.basename(item))):
                if os.path.isfile(item):
                    shutil.copy2(item, paths.get('data', 'art'))
                else:
                    shutil.copytree(item, paths.get('data', 'art'))
        # Handle init files
        patch_inits(paths.get('graphics', pack))
        # Install colorscheme
        if lnp.df_info.version >= '0.31.04':
            colors.load_colors(paths.get('graphics', pack, 'data', 'init',
                                         'colors.txt'))
            shutil.copyfile(paths.get('graphics', pack, 'data', 'init',
                                      'colors.txt'),
                            paths.get('colors', ' Current graphics pack.txt'))
        else:
            colors.load_colors(paths.get('graphics', pack, 'data', 'init',
                                         'init.txt'))
            if os.path.isfile(paths.get('colors',
                                        ' Current graphics pack.txt')):
                os.remove(paths.get('colors', ' Current graphics pack.txt'))
        # TwbT overrides
        #pylint: disable=bare-except
        try:
            os.remove(paths.get('init', 'overrides.txt'))
        except:
            pass
        try:
            shutil.copyfile(
                paths.get('graphics', pack, 'data', 'init', 'overrides.txt'),
                paths.get('init', 'overrides.txt'))
        except:
            pass
    except:
        sys.excepthook(*sys.exc_info())
        df.load_params()
        return False
    df.load_params()
    return True

def validate_pack(pack):
    """Checks for presence of all required files for a pack install."""
    result = True
    gfx_dir = paths.get('graphics', pack)
    result &= os.path.isdir(gfx_dir)
    result &= os.path.isdir(os.path.join(gfx_dir, 'data', 'init'))
    result &= os.path.isdir(os.path.join(gfx_dir, 'data', 'art'))
    result &= os.path.isfile(os.path.join(gfx_dir, 'data', 'init', 'init.txt'))
    if lnp.df_info.version >= '0.31.04':
        result &= os.path.isfile(os.path.join(
            gfx_dir, 'data', 'init', 'd_init.txt'))
        result &= os.path.isfile(os.path.join(
            gfx_dir, 'data', 'init', 'colors.txt'))
    return result

def patch_inits(gfx_dir):
    """Installs init files from a graphics pack by selectively changing
    specific fields. All settings but the mentioned fields are preserved.
    """
    d_init_fields = [
        'WOUND_COLOR_NONE', 'WOUND_COLOR_MINOR',
        'WOUND_COLOR_INHIBITED', 'WOUND_COLOR_FUNCTION_LOSS',
        'WOUND_COLOR_BROKEN', 'WOUND_COLOR_MISSING', 'SKY', 'CHASM',
        'PILLAR_TILE',
        # Tracks
        'TRACK_N', 'TRACK_S', 'TRACK_E', 'TRACK_W', 'TRACK_NS',
        'TRACK_NE', 'TRACK_NW', 'TRACK_SE', 'TRACK_SW', 'TRACK_EW',
        'TRACK_NSE', 'TRACK_NSW', 'TRACK_NEW', 'TRACK_SEW',
        'TRACK_NSEW', 'TRACK_RAMP_N', 'TRACK_RAMP_S', 'TRACK_RAMP_E',
        'TRACK_RAMP_W', 'TRACK_RAMP_NS', 'TRACK_RAMP_NE',
        'TRACK_RAMP_NW', 'TRACK_RAMP_SE', 'TRACK_RAMP_SW',
        'TRACK_RAMP_EW', 'TRACK_RAMP_NSE', 'TRACK_RAMP_NSW',
        'TRACK_RAMP_NEW', 'TRACK_RAMP_SEW', 'TRACK_RAMP_NSEW',
        # Trees
        'TREE_ROOT_SLOPING', 'TREE_TRUNK_SLOPING',
        'TREE_ROOT_SLOPING_DEAD', 'TREE_TRUNK_SLOPING_DEAD',
        'TREE_ROOTS', 'TREE_ROOTS_DEAD', 'TREE_BRANCHES',
        'TREE_BRANCHES_DEAD', 'TREE_SMOOTH_BRANCHES',
        'TREE_SMOOTH_BRANCHES_DEAD', 'TREE_TRUNK_PILLAR',
        'TREE_TRUNK_PILLAR_DEAD', 'TREE_CAP_PILLAR',
        'TREE_CAP_PILLAR_DEAD', 'TREE_TRUNK_N', 'TREE_TRUNK_S',
        'TREE_TRUNK_N_DEAD', 'TREE_TRUNK_S_DEAD', 'TREE_TRUNK_EW',
        'TREE_TRUNK_EW_DEAD', 'TREE_CAP_WALL_N', 'TREE_CAP_WALL_S',
        'TREE_CAP_WALL_N_DEAD', 'TREE_CAP_WALL_S_DEAD', 'TREE_TRUNK_E',
        'TREE_TRUNK_W', 'TREE_TRUNK_E_DEAD', 'TREE_TRUNK_W_DEAD',
        'TREE_TRUNK_NS', 'TREE_TRUNK_NS_DEAD', 'TREE_CAP_WALL_E',
        'TREE_CAP_WALL_W', 'TREE_CAP_WALL_E_DEAD',
        'TREE_CAP_WALL_W_DEAD', 'TREE_TRUNK_NW', 'TREE_CAP_WALL_NW',
        'TREE_TRUNK_NW_DEAD', 'TREE_CAP_WALL_NW_DEAD', 'TREE_TRUNK_NE',
        'TREE_CAP_WALL_NE', 'TREE_TRUNK_NE_DEAD',
        'TREE_CAP_WALL_NE_DEAD', 'TREE_TRUNK_SW', 'TREE_CAP_WALL_SW',
        'TREE_TRUNK_SW_DEAD', 'TREE_CAP_WALL_SW_DEAD', 'TREE_TRUNK_SE',
        'TREE_CAP_WALL_SE', 'TREE_TRUNK_SE_DEAD',
        'TREE_CAP_WALL_SE_DEAD', 'TREE_TRUNK_NSE',
        'TREE_TRUNK_NSE_DEAD', 'TREE_TRUNK_NSW', 'TREE_TRUNK_NSW_DEAD',
        'TREE_TRUNK_NEW', 'TREE_TRUNK_NEW_DEAD', 'TREE_TRUNK_SEW',
        'TREE_TRUNK_SEW_DEAD', 'TREE_TRUNK_NSEW',
        'TREE_TRUNK_NSEW_DEAD', 'TREE_TRUNK_BRANCH_N',
        'TREE_TRUNK_BRANCH_N_DEAD', 'TREE_TRUNK_BRANCH_S',
        'TREE_TRUNK_BRANCH_S_DEAD', 'TREE_TRUNK_BRANCH_E',
        'TREE_TRUNK_BRANCH_E_DEAD', 'TREE_TRUNK_BRANCH_W',
        'TREE_TRUNK_BRANCH_W_DEAD', 'TREE_BRANCH_NS',
        'TREE_BRANCH_NS_DEAD', 'TREE_BRANCH_EW', 'TREE_BRANCH_EW_DEAD',
        'TREE_BRANCH_NW', 'TREE_BRANCH_NW_DEAD', 'TREE_BRANCH_NE',
        'TREE_BRANCH_NE_DEAD', 'TREE_BRANCH_SW', 'TREE_BRANCH_SW_DEAD',
        'TREE_BRANCH_SE', 'TREE_BRANCH_SE_DEAD', 'TREE_BRANCH_NSE',
        'TREE_BRANCH_NSE_DEAD', 'TREE_BRANCH_NSW',
        'TREE_BRANCH_NSW_DEAD', 'TREE_BRANCH_NEW',
        'TREE_BRANCH_NEW_DEAD', 'TREE_BRANCH_SEW',
        'TREE_BRANCH_SEW_DEAD', 'TREE_BRANCH_NSEW',
        'TREE_BRANCH_NSEW_DEAD', 'TREE_TWIGS', 'TREE_TWIGS_DEAD',
        'TREE_CAP_RAMP', 'TREE_CAP_RAMP_DEAD', 'TREE_CAP_FLOOR1',
        'TREE_CAP_FLOOR2', 'TREE_CAP_FLOOR1_DEAD',
        'TREE_CAP_FLOOR2_DEAD', 'TREE_CAP_FLOOR3', 'TREE_CAP_FLOOR4',
        'TREE_CAP_FLOOR3_DEAD', 'TREE_CAP_FLOOR4_DEAD',
        'TREE_TRUNK_INTERIOR', 'TREE_TRUNK_INTERIOR_DEAD']
    init_fields = [
        'FONT', 'FULLFONT', 'GRAPHICS', 'GRAPHICS_FONT',
        'GRAPHICS_FULLFONT', 'TRUETYPE', 'PRINT_MODE']
    init_fields = [f for f in init_fields if lnp.settings.version_has_option(f)]
    d_init_fields = [
        f for f in d_init_fields if lnp.settings.version_has_option(f)]
    init = os.path.join(gfx_dir, 'data', 'init', 'init.txt')
    if lnp.df_info.version <= '0.31.03':
        d_init = init
    else:
        d_init = os.path.join(gfx_dir, 'data', 'init', 'd_init.txt')
    lnp.settings.read_file(init, init_fields, False)
    lnp.settings.read_file(d_init, d_init_fields, False)
    df.save_params()

def simplify_graphics():
    """Removes unnecessary files from all graphics packs."""
    for pack in read_graphics():
        simplify_pack(pack)

def simplify_pack(pack):
    """Removes unnecessary files from one graphics pack."""
    a = baselines.simplify_pack(pack, 'graphics')
    b = baselines.remove_vanilla_raws_from_pack(pack, 'graphics')
    c = baselines.remove_empty_dirs(pack, 'graphics')
    if not all(isinstance(n, int) for n in (a, b, c)):
        return False
    return a + b + c

def savegames_to_update():
    """Returns a list of savegames that will be updated."""
    return [o for o in glob.glob(paths.get('save', '*'))
            if os.path.isdir(o) and not o.endswith('current')]

def update_graphics_raws(raw_dir, pack):
    """Updates raws in place for a new graphics pack.

    Params:
        raw_dir
            Full path to the dir to update
        pack
            The name of the graphics pack to add (eg 'Phoebus')

    Returns:
        True if successful
        False if aborted
    """
    if not validate_pack(pack):
        return None
    built_log = paths.get('baselines', 'temp', 'raw', 'installed_raws.txt')
    built_graphics = logged_graphics(built_log)
    return mods.update_raw_dir(raw_dir, gfx=(pack, built_graphics))

def update_savegames():
    """Update save games with current raws."""
    count, skipped, saves = 0, 0, savegames_to_update()
    for save_raws in [paths.get('saves', s, 'raw') for s in saves]:
        r = can_rebuild(os.path.join(save_raws, 'installed_raws.txt'))
        if r:
            if update_graphics_raws(save_raws, current_pack()):
                count += 1
            else:
                skipped += 1
    return count, skipped

def can_rebuild(log_file, strict=True):
    """Test if user can exactly rebuild a raw folder, returning a bool."""
    if not os.path.isfile(log_file):
        return not strict
    graphic_ok = logged_graphics(log_file) in [k[0] for k in read_graphics()]
    if graphic_ok and mods.can_rebuild(log_file, strict=strict):
        return True
    return False

def open_tilesets():
    """Opens the tilesets folder."""
    open_folder(paths.get('tilesets'))

def read_tilesets():
    """Returns a list of tileset files."""
    files = glob.glob(paths.get('data', 'art', '*.bmp'))
    if 'legacy' not in lnp.df_info.variations:
        files += glob.glob(paths.get('data', 'art', '*.png'))
    return tuple([os.path.basename(o) for o in files if not (
        o.endswith('mouse.png') or o.endswith('mouse.bmp')
        or o.endswith('shadows.png'))])

def current_tilesets():
    """Returns the current tilesets as a tuple (FONT, GRAPHICS_FONT)."""
    if lnp.settings.version_has_option('GRAPHICS_FONT'):
        return (lnp.settings.FONT, lnp.settings.GRAPHICS_FONT)
    return (lnp.settings.FONT, None)

def install_tilesets(font, graphicsfont):
    """Installs the provided tilesets as [FULL]FONT and GRAPHICS_[FULL]FONT.
    To skip either option, use None as the parameter.
    """
    if font is not None and os.path.isfile(paths.get('data', 'art', font)):
        df.set_option('FONT', font)
        df.set_option('FULLFONT', font)
    if (lnp.settings.version_has_option('GRAPHICS_FONT') and
            graphicsfont is not None and os.path.isfile(
                paths.get('data', 'art', graphicsfont))):
        df.set_option('GRAPHICS_FONT', graphicsfont)
        df.set_option('GRAPHICS_FULLFONT', graphicsfont)
