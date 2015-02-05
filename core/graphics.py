#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Graphics pack management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, shutil, glob, tempfile, filecmp
import distutils.dir_util as dir_util
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
    if os.path.isfile(paths.get('df', 'raw', 'installed_raws.txt')):
        with open(paths.get('df', 'raw', 'installed_raws.txt')) as f:
            for l in f.readlines():
                if l.startswith('graphics/'):
                    return l.replace('graphics/', '')
    packs = read_graphics()
    for p in packs:
        if (lnp.settings.FONT == p[1] and
                lnp.settings.GRAPHICS_FONT == p[2]):
            return p[0]
    result = str(lnp.settings.FONT)
    if lnp.settings.version_has_option('GRAPHICS_FONT'):
        result += '/'+str(lnp.settings.GRAPHICS_FONT)
    return result

def read_graphics():
    """Returns a list of graphics directories."""
    packs = [os.path.basename(o) for o in
             glob.glob(paths.get('graphics', '*')) if os.path.isdir(o)]
    result = []
    for p in packs:
        if not validate_pack(p):
            continue
        init_path = paths.get('graphics', p, 'data', 'init', 'init.txt')
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
    gfx_dir = tempfile.mkdtemp()
    try:
        # Update raws
        if not update_graphics_raws(os.path.join(gfx_dir, 'raw'), pack):
            return False
        # Copy art
        if os.path.isdir(os.path.join(paths.get('data'), 'art')):
            dir_util.remove_tree(paths.get('data', 'art'))
        dir_util.copy_tree(os.path.join(gfx_dir, 'data', 'art'),
                           paths.get('data', 'art'))
        for tiles in glob.glob(paths.get('tilesets', '*')):
            shutil.copy(tiles, paths.get('data', 'art'))
        # Handle init files
        patch_inits(gfx_dir)
        # Install colorscheme
        if lnp.df_info.version >= '0.31.04':
            colors.load_colors(os.path.join(
                gfx_dir, 'data', 'init', 'colors.txt'))
            shutil.copyfile(os.path.join(gfx_dir, 'data', 'init', 'colors.txt'),
                            paths.get('colors', '_Current graphics pack.txt'))
        else:
            colors.load_colors(os.path.join(
                gfx_dir, 'data', 'init', 'init.txt'))
            if os.path.isfile(paths.get('colors',
                                        '_Current graphics pack.txt')):
                os.remove(paths.get('colors', '_Current graphics pack.txt'))
        # TwbT overrides
        try:
            os.remove(paths.get('init', 'overrides.txt'))
        except FileNotFoundError:
            pass
        try:
            shutil.copyfile(
                os.path.join(gfx_dir, 'data', 'init', 'overrides.txt'),
                paths.get('init', 'overrides.txt'))
        except FileNotFoundError:
            pass
    except Exception:
        sys.excepthook(*sys.exc_info())
        retval = False
    else:
        retval = True
    if os.path.isdir(gfx_dir):
        dir_util.remove_tree(gfx_dir)
    df.load_params()
    return retval

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
    baselines.simplify_pack(pack, 'graphics')
    baselines.remove_vanilla_raws_from_pack(pack, 'graphics')
    baselines.remove_empty_dirs(pack, 'graphics')

def savegames_to_update():
    """Returns a list of savegames that will be updated."""
    return [o for o in glob.glob(paths.get('save', '*'))
            if os.path.isdir(o) and not o.endswith('current')]

def update_graphics_raws(raw_dir, gfx_dir=None):
    """Updates raws for a new graphics pack.

    Params:
        raw_dir
            Full path to the dir to update
        gfx_dir
            The name of the graphics pack to add (eg 'Phoebus')

    Returns:
        True if successful,
        False if an exception occured
    """
    if gfx_dir is None:
        gfx_dir = current_pack()
        if '/' in gfx_dir:
            return False
    if not gfx_dir in read_graphics():
        return False
    mods_list = mods.read_installation_log(
        os.path.join(raw_dir, 'installed_raws.txt'))
    if not mods_list:
        if os.path.isdir(raw_dir):
            dir_util.remove_tree(raw_dir)
        dir_util.copy_tree(baselines.find_vanilla_raws(), raw_dir)
        dir_util.copy_tree(paths.get('graphics', gfx_dir, 'raw'), raw_dir)
        return True
    else:
        mods.clear_temp()
        add_to_mods_merge(gfx_dir)
        for m in mods_list:
            if mods.merge_a_mod(m) > 2:
                return False
        dir_util.copy_tree(paths.get('baselines', 'temp', 'raw'), raw_dir)
        return True

def add_to_mods_merge(gfx_dir=None):
    """Adds graphics to the mod merge in baselines/temp."""
    if gfx_dir is None:
        gfx_dir = current_pack()
    g_folder = paths.get('graphics', gfx_dir, 'raw')
    b_folder = paths.get('baselines', 'temp', 'raw')
    for root, _, files in os.walk(g_folder):
        for k in files:
            f = os.path.relpath(os.path.join(root, k), g_folder)
            if os.path.isfile(os.path.join(b_folder, f)):
                os.remove(os.path.join(b_folder, f))
            shutil.copyfile(k, os.path.join(b_folder, f))
    with open(paths.get('baselines', 'temp', 'raw', 'installed_raws.txt'),
              'a') as log:
        log.write('graphics/' + gfx_dir)

def update_savegames():
    """Update save games with current raws."""
    count, saves = 0, savegames_to_update()
    if saves:
        for save in saves:
            temp_dir = tempfile.mkdtemp()
            shutil.copytree(os.path.join(save, 'raw'), temp_dir)
            rebuild = can_rebuild(paths.get('baselines', 'temp',
                                            'raw', 'installed_raws.txt'))
            if update_graphics_raws(temp_dir) and rebuild:
                shutil.rmtree(os.path.join(save, 'raw'))
                shutil.copytree(temp_dir, os.path.join(save, 'raw'))
            shutil.rmtree(temp_dir)
            count += 1
    return count

def can_rebuild(log_file):
    """Test if user can exactly rebuild a raw folder, returning a bool."""
    mods.clear_temp()
    try:
        with open(log_file) as f:
            file_contents = list(f.readlines())
    except IOError:
        return False
    mods_list = []
    for line in file_contents:
        if line.startswith('graphics/'):
            add_to_mods_merge(gfx_dir=line.replace('graphics/', ''))
        if line.startswith('mods/'):
            mods_list.append(line.strip().replace('mods/', ''))
    for m in mods_list:
        mods.merge_a_mod(m)
    save_raws = os.path.dirname(log_file)
    gen_raws = paths.get('baselines', 'raw')
    for root, _, files in os.walk(save_raws):
        for k in files:
            f = os.path.relpath(os.path.join(root, k), save_raws)
            if filecmp.cmp(k, os.path.join(gen_raws, f), shallow=False):
                os.remove(os.path.join(gen_raws, f))
    baselines.remove_empty_dirs('temp', 'baselines')
    if os.listdir('temp', 'baselines'):
        return False
    return True

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
