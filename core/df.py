#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Code relating to a specific Dwarf Fortress installation."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, shutil, re
from datetime import datetime
from distutils import dir_util
from glob import glob
from functools import total_ordering

from .settings import DFConfiguration
from . import hacks, paths
from .lnp import lnp, VERSION

def find_df_folders():
    """Locates all suitable Dwairf Fortress installations (folders starting
    with "Dwarf Fortress" or "df")"""
    lnp.folders = tuple([
        os.path.basename(o) for o in
        glob(os.path.join(lnp.BASEDIR, 'Dwarf Fortress*')) +
        glob(os.path.join(lnp.BASEDIR, 'df*')) if os.path.isdir(o)
        ])

def find_df_folder():
    """Locates all suitable Dwairf Fortress installations (folders starting
    with "Dwarf Fortress" or "df")"""
    find_df_folders()
    if len(lnp.folders) == 1:
        set_df_folder(lnp.folders[0])

def set_df_folder(path):
    """
    Selects the Dwarf Fortress instance to operate on.

    :param path: The path of the Dwarf Fortress instance to use.
    """
    paths.register('df', lnp.BASEDIR, path)
    paths.register('data', paths.get('df'), 'data')
    paths.register('init', paths.get('data'), 'init')
    paths.register('save', paths.get('data'), 'save')
    paths.register('extras', paths.get('lnp'), 'Extras')
    paths.register('defaults', paths.get('lnp'), 'Defaults')
    lnp.df_info = DFInstall(paths.get('df'))
    lnp.settings = lnp.df_info.settings
    install_extras()
    load_params()
    hacks.read_hacks()

def install_extras():
    """
    Installs extra utilities to the Dwarf Fortress folder, if this has not
    yet been done.
    """
    extras_dir = paths.get('extras')
    if not os.path.isdir(extras_dir):
        return
    install_file = os.path.join(paths.get('df'), 'PyLNP{0}.txt'.format(VERSION))
    if not os.access(install_file, os.F_OK):
        dir_util.copy_tree(extras_dir, paths.get('df'))
        textfile = open(install_file, 'w')
        textfile.write(
            'PyLNP V{0} extras installed!\nTime: {1}'.format(
                VERSION, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        textfile.close()

def cycle_option(field):
    """
    Cycles an option field between its possible values.

    :param field: The field to cycle.
    """
    lnp.settings.cycle_item(field)
    save_params()

def set_option(field, value):
    """
    Sets a field to a specific value.

    Params:
        field
            The field to set.
        value
            The new value for the field.
    """
    lnp.settings.set_value(field, value)
    save_params()

def load_params():
    """Loads settings from the selected Dwarf Fortress instance."""
    try:
        lnp.settings.read_settings()
    except IOError:
        sys.excepthook(*sys.exc_info())
        msg = ("Failed to read settings, "
               "{0} not really a DF dir?").format(paths.get('df'))
        raise IOError(msg)

def save_params():
    """Saves settings to the selected Dwarf Fortress instance."""
    lnp.settings.write_settings()

def restore_defaults():
    """Copy default settings into the selected Dwarf Fortress instance."""
    shutil.copy(
        os.path.join(paths.get('defaults'), 'init.txt'),
        os.path.join(paths.get('init'), 'init.txt')
        )
    shutil.copy(
        os.path.join(paths.get('defaults'), 'd_init.txt'),
        os.path.join(paths.get('init'), 'd_init.txt')
    )
    load_params()

class DFInstall(object):
    """Contains properties and paths for a given Dwarf Fortress installation."""
    def __init__(self, path):
        self.df_dir = path
        self.init_dir = os.path.join(path, 'data', 'init')
        self.save_dir = os.path.join(path, 'data', 'save')
        self.version, self.source = self.detect_version()
        self.variations = self.detect_variations()
        self.settings = DFConfiguration(path, self)

    def __str__(self):
        result = 'Dwarf Fortress version: {0} (detected using {1})'.format(
            self.version, self.source)
        if self.variations:
            result += '\nVariations detected: ' + ', '.join(self.variations)
        return result

    def detect_version(self):
        """
        Attempts to detect Dwarf Fortress version based on release notes or
        init file contents. Init detection currently supports 0.31 and up;
        assumes 40d if detection fails.
        """
        notes = os.path.join(self.df_dir, 'release notes.txt')
        if os.path.isfile(notes):
            try:
                # If the release notes exist, get the version from there
                notes_text = open(notes).read()
                m = re.search(r"Release notes for ([\d.]+)", notes_text)
                return (Version(m.group(1)), 'release notes')
            # pylint:disable=bare-except
            except:
                # If we can't find a match in the release notes,
                # fall back to using init detection
                pass
        init = os.path.join(self.init_dir, 'init.txt')
        d_init = os.path.join(self.init_dir, 'd_init.txt')
        versions = [
            (d_init, 'GRAZE_COEFFICIENT', '0.40.13'),
            (d_init, 'POST_PREPARE_EMBARK_CONFIRMATION', '0.40.09'),
            (d_init, 'STRICT_POPULATION_CAP', '0.40.05'),
            (d_init, 'TREE_ROOTS', '0.40.01'),
            (d_init, 'TRACK_N', '0.34.08'),
            (d_init, 'SET_LABOR_LISTS', '0.34.03'),
            (d_init, 'WALKING_SPREADS_SPATTER_DWF', '0.31.16'),
            (d_init, 'PILLAR_TILE', '0.31.08'),
            (d_init, 'AUTOSAVE', '0.31.04'),
            (init, 'COMPRESSED_SAVES', '0.31.01')]
        for v in versions:
            if DFConfiguration.has_field(v[0], v[1]):
                return (Version(v[2]), 'init detection')
        return (Version('0.28.181.40d'), 'fallback')

    def detect_variations(self):
        """
        Detect known variations to allow the launcher to adjust accordingly.
        Currently supports DFHack, TWBT, and legacy builds.
        """
        result = []
        if (os.path.exists(os.path.join(self.df_dir, 'dfhack')) or
                os.path.exists(os.path.join(self.df_dir, 'SDLreal.dll')) or
                os.path.exists(os.path.join(self.df_dir, 'SDLhack.dll'))):
            result.append('dfhack')
            if glob(os.path.join(
                    self.df_dir, 'hack', 'plugins', 'twbt.plug.*')):
                result.append('twbt')
        if self.version < '0.31.12' or not DFConfiguration.has_field(
                os.path.join(self.init_dir, 'init.txt'), 'PRINT_MODE'):
            result.append('legacy')
        return result

@total_ordering
class Version(object):
    """Container for a version number for easy comparisons."""
    def __init__(self, version):
        s = ""
        data = []
        for c in version:
            if c < '0' or c > '9':
                data.append(int(s))
                if c != '.':
                    data.append(c)
                s = ""
            else:
                s = s + c
        if s != '':
            data.append(int(s))
        self.data = tuple(data)

    def __lt__(self, other):
        if type(self) != Version:
            return Version(self) < other
        if type(other) != Version:
            return self < Version(other)
        return self.data < other.data

    def __eq__(self, other):
        if type(self) != Version:
            return Version(self) == other
        if type(other) != Version:
            return self == Version(other)
        return self.data == other.data

    def __str__(self):
        return ".".join([str(i) for i in self.data])
