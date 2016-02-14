#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration and raw manipulation for Dwarf Fortress."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, re
from .dfraw import DFRaw
from . import log, hacks

if sys.version_info[0] == 3:
    #pylint:disable=redefined-builtin
    basestring = str

# Markers to read certain settings correctly
# pylint:disable=too-few-public-methods,too-many-instance-attributes,too-many-statements,too-many-arguments
class _DisableValues(object):
    """Marker class for DFConfiguration. Value is disabled by replacing [ and ]
    with !."""
    pass

_disabled = _DisableValues()

class _NegatedBool(object):
    """Marker class for DFConfiguration. Swaps YES and NO."""
    pass

_negated_bool = _NegatedBool()

# Format: Key = tag name, value = list of version numbers
# First value indicates first version with the tag
# Second value, if present, indicates first version WITHOUT the tag
# When adding data here, keep the list sorted using the following ordering:
# 1) First version containing the field
# 2) Last version containing the field (fields that are still present go last)
# 3) Field name
_option_version_data = {
    'EXTENDED_ASCII': ['0.21.93.19a', '0.21.104.19d'],
    'BLACK_B': ['0.21.93.19a', '0.31.04'],
    'BLACK_G': ['0.21.93.19a', '0.31.04'],
    'BLACK_R': ['0.21.93.19a', '0.31.04'],
    'BLUE_B': ['0.21.93.19a', '0.31.04'],
    'BLUE_G': ['0.21.93.19a', '0.31.04'],
    'BLUE_R': ['0.21.93.19a', '0.31.04'],
    'BROWN_B': ['0.21.93.19a', '0.31.04'],
    'BROWN_G': ['0.21.93.19a', '0.31.04'],
    'BROWN_R': ['0.21.93.19a', '0.31.04'],
    'CYAN_B': ['0.21.93.19a', '0.31.04'],
    'CYAN_G': ['0.21.93.19a', '0.31.04'],
    'CYAN_R': ['0.21.93.19a', '0.31.04'],
    'DGRAY_B': ['0.21.93.19a', '0.31.04'],
    'DGRAY_G': ['0.21.93.19a', '0.31.04'],
    'DGRAY_R': ['0.21.93.19a', '0.31.04'],
    'GREEN_B': ['0.21.93.19a', '0.31.04'],
    'GREEN_G': ['0.21.93.19a', '0.31.04'],
    'GREEN_R': ['0.21.93.19a', '0.31.04'],
    'LBLUE_B': ['0.21.93.19a', '0.31.04'],
    'LBLUE_G': ['0.21.93.19a', '0.31.04'],
    'LBLUE_R': ['0.21.93.19a', '0.31.04'],
    'LCYAN_B': ['0.21.93.19a', '0.31.04'],
    'LCYAN_G': ['0.21.93.19a', '0.31.04'],
    'LCYAN_R': ['0.21.93.19a', '0.31.04'],
    'LGRAY_B': ['0.21.93.19a', '0.31.04'],
    'LGRAY_G': ['0.21.93.19a', '0.31.04'],
    'LGRAY_R': ['0.21.93.19a', '0.31.04'],
    'LGREEN_B': ['0.21.93.19a', '0.31.04'],
    'LGREEN_G': ['0.21.93.19a', '0.31.04'],
    'LGREEN_R': ['0.21.93.19a', '0.31.04'],
    'LMAGENTA_B': ['0.21.93.19a', '0.31.04'],
    'LMAGENTA_G': ['0.21.93.19a', '0.31.04'],
    'LMAGENTA_R': ['0.21.93.19a', '0.31.04'],
    'LRED_B': ['0.21.93.19a', '0.31.04'],
    'LRED_G': ['0.21.93.19a', '0.31.04'],
    'LRED_R': ['0.21.93.19a', '0.31.04'],
    'MAGENTA_B': ['0.21.93.19a', '0.31.04'],
    'MAGENTA_G': ['0.21.93.19a', '0.31.04'],
    'MAGENTA_R': ['0.21.93.19a', '0.31.04'],
    'RED_B': ['0.21.93.19a', '0.31.04'],
    'RED_G': ['0.21.93.19a', '0.31.04'],
    'RED_R': ['0.21.93.19a', '0.31.04'],
    'WHITE_B': ['0.21.93.19a', '0.31.04'],
    'WHITE_G': ['0.21.93.19a', '0.31.04'],
    'WHITE_R': ['0.21.93.19a', '0.31.04'],
    'YELLOW_B': ['0.21.93.19a', '0.31.04'],
    'YELLOW_G': ['0.21.93.19a', '0.31.04'],
    'YELLOW_R': ['0.21.93.19a', '0.31.04'],
    'DISPLAY_LENGTH': ['0.21.93.19a'],
    'FONT': ['0.21.93.19a'],
    'FULLFONT': ['0.21.93.19a'],
    'FULLSCREENX': ['0.21.93.19a'],
    'FULLSCREENY': ['0.21.93.19a'],
    'MORE': ['0.21.93.19a'],
    'VARIED_GROUND_TILES': ['0.21.93.19a'],
    'WINDOWEDX': ['0.21.93.19a'],
    'WINDOWEDY': ['0.21.93.19a'],
    'INTRO': ['0.21.100.19a'],
    'SOUND': ['0.21.100.19a'],
    'KEY_HOLD_MS': ['0.21.101.19a'],
    'NICKNAME_ADVENTURE': ['0.21.102.19a'],
    'NICKNAME_DWARF': ['0.21.102.19a'],
    'NICKNAME_LEGENDS': ['0.21.102.19a'],
    'WINDOWED': ['0.21.102.19a'],
    'ENGRAVINGS_START_OBSCURED': ['0.21.104.19d'],
    'MOUSE': ['0.21.104.21a'],
    'MOUSE_PICTURE': ['0.21.104.21a'],
    'ADVENTURER_TRAPS': ['0.22.110.23a'],
    'BLACK_SPACE': ['0.22.120.23a'],
    'GRAPHICS': ['0.22.120.23a'],
    'GRAPHICS_BLACK_SPACE': ['0.22.120.23a'],
    'GRAPHICS_FONT': ['0.22.120.23a'],
    'GRAPHICS_FULLFONT': ['0.22.120.23a'],
    'GRAPHICS_FULLSCREENX': ['0.22.120.23a'],
    'GRAPHICS_FULLSCREENY': ['0.22.120.23a'],
    'GRAPHICS_WINDOWEDX': ['0.22.120.23a'],
    'GRAPHICS_WINDOWEDY': ['0.22.120.23a'],
    'FPS': ['0.22.121.23b'],
    'TEMPERATURE': ['0.22.121.23b'],
    'WEATHER': ['0.22.121.23b'],
    'FPS_CAP': ['0.23.130.23a'],
    'POPULATION_CAP': ['0.23.130.23a'],
    'ADVENTURER_ALWAYS_CENTER': ['0.27.169.32a'],
    'ADVENTURER_Z_VIEWS': ['0.27.169.32a'],
    'AQUIFER': ['0.27.169.32a'],
    'ARTIFACTS': ['0.27.169.32a'],
    'AUTOBACKUP': ['0.27.169.32a'],
    'AUTOSAVE': ['0.27.169.32a'],
    'CAVEINS': ['0.27.169.32a'],
    'CHASM': ['0.27.169.32a'],
    'COFFIN_NO_PETS_DEFAULT': ['0.27.169.32a'],
    'ECONOMY': ['0.27.169.32a'],
    'G_FPS_CAP': ['0.27.169.32a'],
    'INITIAL_SAVE': ['0.27.169.32a'],
    'INVADERS': ['0.27.169.32a'],
    'LOG_MAP_REJECTS': ['0.27.169.32a'],
    'PATH_COST': ['0.27.169.32a'],
    'RECENTER_INTERFACE_SHUTDOWN_MS': ['0.27.169.32a'],
    'SHOW_FLOW_AMOUNTS': ['0.27.169.32a'],
    'SHOW_IMP_QUALITY': ['0.27.169.32a'],
    'SKY': ['0.27.169.32a'],
    'TEXTURE_PARAM': ['0.27.169.32a'],
    'TOPMOST': ['0.27.169.32a'],
    'VOLUME': ['0.27.169.32a'],
    'VSYNC': ['0.27.169.32a'],
    'PRIORITY': ['0.27.169.33c'],
    'EMBARK_RECTANGLE': ['0.27.169.33g'],
    'PAUSE_ON_LOAD': ['0.27.169.33g'],
    'BABY_CHILD_CAP': ['0.27.176.38a'],
    'ZERO_RENT': ['0.27.176.38a'],
    'AUTOSAVE_PAUSE': ['0.27.176.38b'],
    'EMBARK_WARNING_ALWAYS': ['0.27.176.38b'],
    'IDLERS': ['0.28.181.39a'],
    'SHOW_ALL_HISTORY_IN_DWARF_MODE': ['0.28.181.39a'],
    'SHOW_EMBARK_CHASM': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_M_PIPE': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_M_POOL': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_OTHER': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_PIT': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_POOL': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_RIVER': ['0.28.181.39d', '0.31.01'],
    'SHOW_EMBARK_TUNNEL': ['0.28.181.39d'],
    'GRID': ['0.28.181.39f'],
    'STORE_DIST_BARREL_COMBINE': ['0.28.181.40a'],
    'STORE_DIST_BIN_COMBINE': ['0.28.181.40a'],
    'STORE_DIST_BUCKET_COMBINE': ['0.28.181.40a'],
    'STORE_DIST_ITEM_DECREASE': ['0.28.181.40a'],
    'STORE_DIST_SEED_COMBINE': ['0.28.181.40a'],
    'FULLGRID': ['0.28.181.40b'],
    'PARTIAL_PRINT': ['0.28.181.40b'],
    'COMPRESSED_SAVES': ['0.31.01'],
    'TESTING_ARENA': ['0.31.01'],
    'WOUND_COLOR_BROKEN': ['0.31.01'],
    'WOUND_COLOR_FUNCTION_LOSS': ['0.31.01'],
    'WOUND_COLOR_INHIBITED': ['0.31.01'],
    'WOUND_COLOR_MINOR': ['0.31.01'],
    'WOUND_COLOR_MISSING': ['0.31.01'],
    'WOUND_COLOR_NONE': ['0.31.01'],
    'PILLAR_TILE': ['0.31.08'],
    'ZOOM_SPEED': ['0.31.13'],
    'ARB_SYNC': ['0.31.13'],
    'KEY_REPEAT_ACCEL_LIMIT': ['0.31.13'],
    'KEY_REPEAT_ACCEL_START': ['0.31.13'],
    'KEY_REPEAT_MS': ['0.31.13'],
    'MACRO_MS': ['0.31.13'],
    'PRINT_MODE': ['0.31.13'],
    'RESIZABLE': ['0.31.13'],
    'SINGLE_BUFFER': ['0.31.13'],
    'TRUETYPE': ['0.31.13'],
    'WALKING_SPREADS_SPATTER_ADV': ['0.31.16'],
    'WALKING_SPREADS_SPATTER_DWF': ['0.31.16'],
    'SET_LABOR_LISTS': ['0.34.03'],
    'TRACK_E': ['0.34.08'],
    'TRACK_EW': ['0.34.08'],
    'TRACK_N': ['0.34.08'],
    'TRACK_NE': ['0.34.08'],
    'TRACK_NEW': ['0.34.08'],
    'TRACK_NS': ['0.34.08'],
    'TRACK_NSE': ['0.34.08'],
    'TRACK_NSEW': ['0.34.08'],
    'TRACK_NSW': ['0.34.08'],
    'TRACK_NW': ['0.34.08'],
    'TRACK_RAMP_E': ['0.34.08'],
    'TRACK_RAMP_EW': ['0.34.08'],
    'TRACK_RAMP_N': ['0.34.08'],
    'TRACK_RAMP_NE': ['0.34.08'],
    'TRACK_RAMP_NEW': ['0.34.08'],
    'TRACK_RAMP_NS': ['0.34.08'],
    'TRACK_RAMP_NSE': ['0.34.08'],
    'TRACK_RAMP_NSEW': ['0.34.08'],
    'TRACK_RAMP_NSW': ['0.34.08'],
    'TRACK_RAMP_NW': ['0.34.08'],
    'TRACK_RAMP_S': ['0.34.08'],
    'TRACK_RAMP_SE': ['0.34.08'],
    'TRACK_RAMP_SEW': ['0.34.08'],
    'TRACK_RAMP_SW': ['0.34.08'],
    'TRACK_RAMP_W': ['0.34.08'],
    'TRACK_S': ['0.34.08'],
    'TRACK_SE': ['0.34.08'],
    'TRACK_SEW': ['0.34.08'],
    'TRACK_SW': ['0.34.08'],
    'TRACK_W': ['0.34.08'],
    'FORTRESS_SEED_CAP': ['0.40.01'],
    'SPECIFIC_SEED_CAP': ['0.40.01'],
    'TREE_BRANCH_EW': ['0.40.01'],
    'TREE_BRANCH_EW_DEAD': ['0.40.01'],
    'TREE_BRANCH_NE': ['0.40.01'],
    'TREE_BRANCH_NE_DEAD': ['0.40.01'],
    'TREE_BRANCH_NEW': ['0.40.01'],
    'TREE_BRANCH_NEW_DEAD': ['0.40.01'],
    'TREE_BRANCH_NS': ['0.40.01'],
    'TREE_BRANCH_NS_DEAD': ['0.40.01'],
    'TREE_BRANCH_NSE': ['0.40.01'],
    'TREE_BRANCH_NSE_DEAD': ['0.40.01'],
    'TREE_BRANCH_NSEW': ['0.40.01'],
    'TREE_BRANCH_NSEW_DEAD': ['0.40.01'],
    'TREE_BRANCH_NSW': ['0.40.01'],
    'TREE_BRANCH_NSW_DEAD': ['0.40.01'],
    'TREE_BRANCH_NW': ['0.40.01'],
    'TREE_BRANCH_NW_DEAD': ['0.40.01'],
    'TREE_BRANCH_SE': ['0.40.01'],
    'TREE_BRANCH_SE_DEAD': ['0.40.01'],
    'TREE_BRANCH_SEW': ['0.40.01'],
    'TREE_BRANCH_SEW_DEAD': ['0.40.01'],
    'TREE_BRANCH_SW': ['0.40.01'],
    'TREE_BRANCH_SW_DEAD': ['0.40.01'],
    'TREE_BRANCHES': ['0.40.01'],
    'TREE_BRANCHES_DEAD': ['0.40.01'],
    'TREE_CAP_FLOOR1': ['0.40.01'],
    'TREE_CAP_FLOOR1_DEAD': ['0.40.01'],
    'TREE_CAP_FLOOR2': ['0.40.01'],
    'TREE_CAP_FLOOR2_DEAD': ['0.40.01'],
    'TREE_CAP_FLOOR3': ['0.40.01'],
    'TREE_CAP_FLOOR3_DEAD': ['0.40.01'],
    'TREE_CAP_FLOOR4': ['0.40.01'],
    'TREE_CAP_FLOOR4_DEAD': ['0.40.01'],
    'TREE_CAP_PILLAR': ['0.40.01'],
    'TREE_CAP_PILLAR_DEAD': ['0.40.01'],
    'TREE_CAP_RAMP': ['0.40.01'],
    'TREE_CAP_RAMP_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_E': ['0.40.01'],
    'TREE_CAP_WALL_E_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_N': ['0.40.01'],
    'TREE_CAP_WALL_N_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_NE': ['0.40.01'],
    'TREE_CAP_WALL_NE_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_NW': ['0.40.01'],
    'TREE_CAP_WALL_NW_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_S': ['0.40.01'],
    'TREE_CAP_WALL_S_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_SE': ['0.40.01'],
    'TREE_CAP_WALL_SE_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_SW': ['0.40.01'],
    'TREE_CAP_WALL_SW_DEAD': ['0.40.01'],
    'TREE_CAP_WALL_W': ['0.40.01'],
    'TREE_CAP_WALL_W_DEAD': ['0.40.01'],
    'TREE_ROOT_SLOPING': ['0.40.01'],
    'TREE_ROOT_SLOPING_DEAD': ['0.40.01'],
    'TREE_ROOTS': ['0.40.01'],
    'TREE_ROOTS_DEAD': ['0.40.01'],
    'TREE_SMOOTH_BRANCHES': ['0.40.01'],
    'TREE_SMOOTH_BRANCHES_DEAD': ['0.40.01'],
    'TREE_TRUNK_BRANCH_E': ['0.40.01'],
    'TREE_TRUNK_BRANCH_E_DEAD': ['0.40.01'],
    'TREE_TRUNK_BRANCH_N': ['0.40.01'],
    'TREE_TRUNK_BRANCH_N_DEAD': ['0.40.01'],
    'TREE_TRUNK_BRANCH_S': ['0.40.01'],
    'TREE_TRUNK_BRANCH_S_DEAD': ['0.40.01'],
    'TREE_TRUNK_BRANCH_W': ['0.40.01'],
    'TREE_TRUNK_BRANCH_W_DEAD': ['0.40.01'],
    'TREE_TRUNK_E': ['0.40.01'],
    'TREE_TRUNK_E_DEAD': ['0.40.01'],
    'TREE_TRUNK_EW': ['0.40.01'],
    'TREE_TRUNK_EW_DEAD': ['0.40.01'],
    'TREE_TRUNK_INTERIOR': ['0.40.01'],
    'TREE_TRUNK_INTERIOR_DEAD': ['0.40.01'],
    'TREE_TRUNK_N': ['0.40.01'],
    'TREE_TRUNK_N_DEAD': ['0.40.01'],
    'TREE_TRUNK_NE': ['0.40.01'],
    'TREE_TRUNK_NE_DEAD': ['0.40.01'],
    'TREE_TRUNK_NEW': ['0.40.01'],
    'TREE_TRUNK_NEW_DEAD': ['0.40.01'],
    'TREE_TRUNK_NS': ['0.40.01'],
    'TREE_TRUNK_NS_DEAD': ['0.40.01'],
    'TREE_TRUNK_NSE': ['0.40.01'],
    'TREE_TRUNK_NSE_DEAD': ['0.40.01'],
    'TREE_TRUNK_NSEW': ['0.40.01'],
    'TREE_TRUNK_NSEW_DEAD': ['0.40.01'],
    'TREE_TRUNK_NSW': ['0.40.01'],
    'TREE_TRUNK_NSW_DEAD': ['0.40.01'],
    'TREE_TRUNK_NW': ['0.40.01'],
    'TREE_TRUNK_NW_DEAD': ['0.40.01'],
    'TREE_TRUNK_PILLAR': ['0.40.01'],
    'TREE_TRUNK_PILLAR_DEAD': ['0.40.01'],
    'TREE_TRUNK_S': ['0.40.01'],
    'TREE_TRUNK_S_DEAD': ['0.40.01'],
    'TREE_TRUNK_SE': ['0.40.01'],
    'TREE_TRUNK_SE_DEAD': ['0.40.01'],
    'TREE_TRUNK_SEW': ['0.40.01'],
    'TREE_TRUNK_SEW_DEAD': ['0.40.01'],
    'TREE_TRUNK_SLOPING': ['0.40.01'],
    'TREE_TRUNK_SLOPING_DEAD': ['0.40.01'],
    'TREE_TRUNK_SW': ['0.40.01'],
    'TREE_TRUNK_SW_DEAD': ['0.40.01'],
    'TREE_TRUNK_W': ['0.40.01'],
    'TREE_TRUNK_W_DEAD': ['0.40.01'],
    'TREE_TWIGS': ['0.40.01'],
    'TREE_TWIGS_DEAD': ['0.40.01'],
    'STRICT_POPULATION_CAP': ['0.40.05'],
    'POST_PREPARE_EMBARK_CONFIRMATION': ['0.40.09'],
    'GRAZE_COEFFICIENT': ['0.40.13'],
    'VISITOR_CAP': ['0.42.01'],
    'INVASION_SOLDIER_CAP': ['0.42.01'],
    'INVASION_MONSTER_CAP': ['0.42.01'],
}

def _option_item_to_value(item):
    """Removes any validation expression from <item>."""
    if not isinstance(item, basestring):
        return item[0]
    return item

class DFConfiguration(object):
    """Reads and modifies Dwarf Fortress configuration textfiles."""
    def __init__(self, base_dir, df_info):
        """
        Constructor for DFConfiguration.

        Params:
            base_dir
                Path containing the Dwarf Fortress instance to operate on.
        """
        self.base_dir = base_dir
        self.settings = dict()
        self.options = dict()
        self.field_names = dict()
        self.inverse_field_names = dict()
        self.files = dict()
        self.in_files = dict()
        self.missing_fields = []

        self.df_info = df_info
        # init.txt
        boolvals = ("YES", "NO")
        init = (os.path.join(base_dir, 'data', 'init', 'init.txt'),)
        self.create_option(
            "truetype", "TRUETYPE", "YES", boolvals, init,
            'legacy' not in df_info.variations)
        self.create_option("sound", "SOUND", "YES", boolvals, init)
        self.create_option("volume", "VOLUME", "255", None, init)
        self.create_option("introMovie", "INTRO", "YES", boolvals, init)
        self.create_option(
            "startWindowed", "WINDOWED", "YES", ("YES", "NO", "PROMPT"), init)
        self.create_option("fpsCounter", "FPS", "NO", boolvals, init)
        self.create_option("fpsCap", "FPS_CAP", "100", None, init)
        self.create_option("gpsCap", "G_FPS_CAP", "50", None, init)
        self.create_option(
            "procPriority", "PRIORITY", "NORMAL", (
                "REALTIME", "HIGH", "ABOVE_NORMAL", "NORMAL", "BELOW_NORMAL",
                "IDLE"), init)
        self.create_option(
            "compressSaves", "COMPRESSED_SAVES", "YES", boolvals, init)
        twbt_validate = hacks.is_dfhack_enabled
        printmodes = ["2D", "STANDARD"]
        if 'twbt' in df_info.variations:
            printmodes += [
                ("TWBT", twbt_validate), ("TWBT_LEGACY", twbt_validate)]
        self.create_option(
            "printmode", "PRINT_MODE", "2D", tuple(printmodes), init,
            'legacy' not in df_info.variations)
        # d_init.txt
        dinit = (os.path.join(base_dir, 'data', 'init', 'd_init.txt'),)
        if df_info.version <= '0.31.03':
            dinit = init
        self.create_option("popcap", "POPULATION_CAP", "200", None, dinit)
        self.create_option(
            "strictPopcap", "STRICT_POPULATION_CAP", "220", None, dinit)
        self.create_option(
            "childcap", "BABY_CHILD_CAP", "100:1000", None, dinit)
        self.create_option("invaders", "INVADERS", "YES", boolvals, dinit)
        self.create_option(
            "temperature", "TEMPERATURE", "YES", boolvals, dinit)
        self.create_option("weather", "WEATHER", "YES", boolvals, dinit)
        self.create_option("caveins", "CAVEINS", "YES", boolvals, dinit)
        self.create_option(
            "liquidDepth", "SHOW_FLOW_AMOUNTS", "YES", boolvals, dinit)
        self.create_option(
            "variedGround", "VARIED_GROUND_TILES", "YES", boolvals, dinit)
        if df_info.version <= '0.34.06':
            self.create_option(
                "laborLists", "SET_LABOR_LISTS", "YES", boolvals, dinit)
        else:
            self.create_option("laborLists", "SET_LABOR_LISTS", "SKILLS", (
                "NO", "SKILLS", "BY_UNIT_TYPE"), dinit)
        self.create_option("autoSave", "AUTOSAVE", "SEASONAL", (
            "NONE", "SEASONAL", "YEARLY"), dinit)
        self.create_option("autoBackup", "AUTOBACKUP", "YES", boolvals, dinit)
        self.create_option(
            "autoSavePause", "AUTOSAVE_PAUSE", "YES", boolvals, dinit)
        self.create_option(
            "initialSave", "INITIAL_SAVE", "YES", boolvals, dinit)
        self.create_option(
            "pauseOnLoad", "PAUSE_ON_LOAD", "YES", boolvals, dinit)
        self.create_option(
            "entombPets", "COFFIN_NO_PETS_DEFAULT", "NO", _negated_bool, dinit)
        self.create_option("artifacts", "ARTIFACTS", "YES", boolvals, dinit)
        self.create_option("grazeCoef", "GRAZE_COEFFICIENT", "100", None, dinit)
        self.create_option("visitorCap", "VISITOR_CAP", "100", None, dinit)
        self.create_option(
            "invSoldierCap", "INVASION_SOLDIER_CAP", "120", None, dinit)
        self.create_option(
            "invMonsterCap", "INVASION_MONSTER_CAP", "40", None, dinit)
        # special
        if df_info.version < '0.31':
            aquifer_files = [
                'matgloss_stone_layer.txt', 'matgloss_stone_mineral.txt',
                'matgloss_stone_soil.txt']
        else:
            aquifer_files = [
                'inorganic_stone_layer.txt', 'inorganic_stone_mineral.txt',
                'inorganic_stone_soil.txt']
        self.create_option("aquifers", "AQUIFER", "NO", _disabled, tuple(
            os.path.join(base_dir, 'raw', 'objects', a) for a in aquifer_files))

    def create_option(
            self, name, field_name, default, values, files, cond=True):
        """
        Register an option to write back for changes. If the field_name has
        been registered before, no changes are made. Fields that do not exist in
        the current DF version are simply registered with a field name mapping,
        but they will not be expected in the init files.

        Params:
          name
            The name you want to use to refer to this field (becomes available
            as an attribute on this class).
          field_name
            The field name used in the file. If this is different from the name
            argument, this will also become available as an attribute.
          default
            The value to initialize this setting to.
          values
            An iterable of valid values for this field. Used in cycle_list.
            Special values defined in this file:
              None
                Unspecified value; cycling has no effect.
              disabled:
                Boolean option toggled by replacing the [] around the field
                name with !!.
              force_bool:
                Values other than "YES" and "NO" are interpreted as "YES".
          files
            A tuple of files this value is read from. Used for e.g. aquifer
            toggling, which requires editing multiple files.
          cond
            A boolean which must be True in order for the field to be valid.
            If False, this will merely register the field name mapping.
            Defaults to True.
        """

        # Don't allow re-registration of a known field
        if name in self.settings or name in self.inverse_field_names:
            return
        # Ignore registration if version doesn't have tag
        self.field_names[name] = field_name
        if not (cond and self.version_has_option(field_name)):
            return
        self.settings[name] = default
        self.options[name] = values
        if field_name != name:
            self.inverse_field_names[field_name] = name
        self.files[name] = files
        self.in_files.setdefault(files, [])
        self.in_files[files].append(name)

    def __iter__(self):
        for key, value in list(self.settings.items()):
            yield key, value

    def set_value(self, name, value):
        """
        Sets the setting <name> to <value>.

        Params:
            name
                Name of the setting to alter.
            value
                New value for the setting.
        """
        self.settings[name] = value

    def cycle_item(self, name):
        """
        Cycle the setting <name>.

        Params:
            name
                Name of the setting to cycle.
        """
        self.settings[name] = self.cycle_list(
            self.settings[name], self.options[name])

    @staticmethod
    def cycle_list(current, items):
        """Cycles setting between a list of items.

        Params:
            current
                Current value.
            items
                List of possible values (optionally a special value).

        Returns:
            If no list of values is given, returns current.
            If the current value is the last value in the list, or the value
            does not exist in the list, returns the first value in the list.
            Otherwise, returns the value from items immediately following the
            current value.
        """
        if items is None:
            return current
        if items is _disabled or items is _negated_bool:
            items = ("YES", "NO")
        if current not in items:
            for i in items:
                if not isinstance(i, basestring) and i[0] == current:
                    current = i
                    break
            else: #item not found
                result = items[0]
                return _option_item_to_value(result)

        i = 1
        while i < len(items):
            result = items[(items.index(current) + i) % len(items)]
            if isinstance(result, basestring):
                break
            if result[1]():
                break
            i = i + 1
        return _option_item_to_value(result)

    def read_settings(self):
        """Read settings from known filesets. If fileset only contains one
        file, all options will be registered automatically."""
        for files in self.in_files.keys():
            for filename in files:
                self.read_file(filename, self.in_files[files], len(files) == 1)

    def read_file(self, filename, fields, auto_add):
        """
        Reads DF settings from the file <filename>.

        Params:
          filename
            The file to read from.
          fields
            An iterable containing the field names to read.
          auto_add
            Whether to automatically register all unknown fields for changes by
            calling create_option(field_name, field_name, value, None,
            (filename,)).
        """
        text = DFRaw.read(filename)
        if auto_add:
            for match in re.findall(r'\[(.+?):(.+?)\]', text):
                self.create_option(
                    match[0], match[0], match[1], None, (filename,))
        for field in fields:
            if field in self.inverse_field_names:
                field = self.inverse_field_names[field]
            if self.options[field] is _disabled:
                # If there is a single match, flag the option as enabled
                if "[{0}]".format(self.field_names[field]) in text:
                    self.settings[field] = "YES"
            else:
                match = re.search(r'\[{0}:(.+?)\]'.format(
                    self.field_names[field]), text)
                if match:
                    value = match.group(1)
                    if self.options[field] is _negated_bool:
                        value = ["YES", "NO"][["NO", "YES"].index(value)]
                    self.settings[field] = value
                else:
                    self.missing_fields.append(self.field_names[field])
                    log.w(
                        'Field ' + str(self.field_names[field]) +
                        ' seems to be missing from file ' + str(filename) +
                        '!', file=sys.stderr)

    @staticmethod
    def has_field(filename, field, num_params=-1, min_params=-1, max_params=-1):
        """
        Returns True if <field> exists in <filename> and has the specified
        number of parameters.

        Params:
            filename
                The file to check.
            field
                The field to look for.
            num_params
                The exact number of parameters for the field. -1 for no limit.
            min_params
                The minimum number of parameters for the field. -1 for no limit.
            max_params
                The maximum number of parameters for the field. -1 for no limit.
        """
        try:
            match = re.search(
                r'\['+str(field)+r'(:.+?)\]', DFRaw.read(filename))
            if match is None:
                return False
            params = match.group(1)
            param_count = params.count(":")
            if num_params != -1 and param_count != num_params:
                return False
            if min_params != -1 and param_count < min_params:
                return False
            if max_params != -1 and param_count > max_params:
                return False
            return True
        except IOError:
            return False

    def write_settings(self):
        """Write all settings to their respective files."""
        for files in self.in_files:
            for filename in files:
                self.update_file(filename, self.in_files[files])

    def update_file(self, filename, fields):
        """
        Write settings to a specific file.

        Params:
            filename
                Name of the file to write.
            fields
                List of all field names to change.
        """
        with DFRaw(filename) as raw:
            for field in fields:
                field_name = self.field_names[field]
                if self.options[field] is _disabled:
                    raw.set_all(field_name, self.settings[field] != "NO")
                else:
                    value = self.settings[field]
                    if self.options[field] is _negated_bool:
                        value = ["YES", "NO"][["NO", "YES"].index(value)]
                    raw.set_value(field_name, value)

    def create_file(self, filename, fields):
        """
        Create a new file containing the specified fields.

        Params:
            filename
                Name of the file to write.
            fields
                List of all field names to write.
        """
        with DFRaw.open(filename, 'wt') as newfile:
            for field in fields:
                if self.options[field] is _disabled:
                    if self.settings[field] == "NO":
                        text = "!{0}!"
                    else:
                        text = "[{0}]"
                    newfile.write(text.format(self.field_names[field])+'\n')
                else:
                    value = self.settings[field]
                    if self.options[field] is _negated_bool:
                        value = ["YES", "NO"][["NO", "YES"].index(value)]
                    newfile.write('[' + field + ':' + value + ']\n')

    def version_has_option(self, option_name):
        """Returns True if <option_name> exists in the current DF version."""
        if option_name in self.field_names:
            option_name = self.field_names[option_name]
        if option_name in self.missing_fields:
            # Field was missing when expected, pretend it doesn't exist yet
            return False
        if option_name[0] == option_name.lower()[0]:
            # Internal name, let it pass by
            return True
        if option_name not in _option_version_data:
            log.w("Unknown option: %s", option_name)
            # Unknown option, must be a later DF than this knows about
            return False
        option = _option_version_data[option_name]
        if len(option) == 2:
            return option[0] <= self.df_info.version < option[1]
        else:
            return option[0] <= self.df_info.version

    def __str__(self):
        return (
            "base_dir = {0}\nsettings = {1}\noptions = {2}\n"
            "field_names ={3}\ninverse_field_names = {4}\nfiles = {5}\n"
            "in_files = {6}").format(
                self.base_dir, self.settings, self.options, self.field_names,
                self.inverse_field_names, self.files, self.in_files)

    def __getattr__(self, name):
        """Exposes all registered options through both their internal and
        registered names."""
        if name in self.inverse_field_names:
            return self.settings[self.inverse_field_names[name]]
        return self.settings[name]

# vim:expandtab
