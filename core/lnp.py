#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PyLNP main library."""
from __future__ import print_function, unicode_literals, absolute_import
import sys

import os
from . import errorlog, log

from .json_config import JSONConfiguration

VERSION = '0.9.4'

lnp = None
class PyLNP(object):
    """
    PyLNP library class.

    Acts as an abstraction layer between the UI and the Dwarf Fortress
    instance.
    """
    def __init__(self):
        """Constructor for the PyLNP library."""
        # pylint:disable=global-statement
        global lnp
        lnp = self
        self.args = self.parse_commandline()

        self.BASEDIR = '.'
        self.bundle = ''
        if hasattr(sys, 'frozen'):
            os.chdir(os.path.dirname(sys.executable))
            if sys.platform == 'win32':
                self.bundle = 'win'
            elif sys.platform.startswith('linux'):
                self.bundle = 'linux'
            elif sys.platform == 'darwin':
                self.bundle = 'osx'
                # OS X bundles start in different directory
                os.chdir('../../..')
        else:
            os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        self.detect_basedir()

        from . import df, paths, update, utilities

        paths.register('root', self.BASEDIR)
        errorlog.start()

        paths.register('lnp', self.BASEDIR, 'LNP')
        if not os.path.isdir(paths.get('lnp')):
            print('WARNING: LNP folder is missing!', file=sys.stderr)
        paths.register('keybinds', paths.get('lnp'), 'Keybinds')
        paths.register('graphics', paths.get('lnp'), 'Graphics')
        paths.register('utilities', paths.get('lnp'), 'Utilities')
        paths.register('colors', paths.get('lnp'), 'Colors')
        paths.register('embarks', paths.get('lnp'), 'Embarks')
        paths.register('tilesets', paths.get('lnp'), 'Tilesets')
        paths.register('baselines', paths.get('lnp'), 'Baselines')
        paths.register('mods', paths.get('lnp'), 'Mods')

        self.df_info = None
        self.folders = []
        self.settings = None
        self.autorun = []
        self.running = {}

        config_file = 'PyLNP.json'
        if os.access(paths.get('lnp', 'PyLNP.json'), os.F_OK):
            config_file = paths.get('lnp', 'PyLNP.json')

        default_config = {
            "folders": [
                ["Savegame folder", "<df>/data/save"],
                ["Utilities folder", "LNP/Utilities"],
                ["Graphics folder", "LNP/Graphics"],
                ["-", "-"],
                ["Main folder", ""],
                ["LNP folder", "LNP"],
                ["Dwarf Fortress folder", "<df>"],
                ["Init folder", "<df>/data/init"]
            ],
            "links": [
                ["DF Homepage", "http://www.bay12games.com/dwarves/"],
                ["DF Wiki", "http://dwarffortresswiki.org/"],
                ["DF Forums", "http://www.bay12forums.com/smf/"]
            ],
            "hideUtilityPath": False,
            "hideUtilityExt": False,
            "updates": {
                "dffdID": "",
                "packVersion": "",
                "checkURL": "",
                "versionRegex": "",
                "downloadURL": "",
                "directURL": ""
            }
        }
        self.config = JSONConfiguration(config_file, default_config)
        self.userconfig = JSONConfiguration('PyLNP.user')

        df.find_df_folder()
        utilities.load_autorun()

        self.new_version = None

        from tkgui.tkgui import TkGui
        self.ui = TkGui()
        update.check_update()
        self.ui.start()

    def parse_commandline(self):
        """Parses and acts on command line options."""
        args = self.get_commandline_args()
        if args.debug:
            log.set_level(log.DEBUG)
        log.d(args)
        return args

    @staticmethod
    def get_commandline_args():
        """Responsible for the actual parsing of command line options."""
        import argparse
        parser = argparse.ArgumentParser(
            description="PyLNP " +VERSION)
        parser.add_argument(
            '-d', '--debug', action='store_true',
            help='turn on extra debugging output')
        parser.add_argument(
            'df_folder', nargs='?',
            help='Dwarf Fortress folder to use (if it exists)')
        parser.add_argument(
            '--version', action='version', version="PyLNP "+VERSION)
        return parser.parse_known_args()[0]

    def save_config(self):
        """Saves LNP configuration."""
        self.userconfig.save_data()

    def detect_basedir(self):
        """Detects the location of Dwarf Fortress by walking up the directory
        tree."""
        prev_path = '.'

        from . import df
        try:
            while os.path.abspath(self.BASEDIR) != prev_path:
                df.find_df_folders()
                if len(self.folders) != 0:
                    break
                prev_path = os.path.abspath(self.BASEDIR)
                self.BASEDIR = os.path.join(self.BASEDIR, '..')
        except UnicodeDecodeError:
            print(
                "ERROR: PyLNP is being stored in a path containing non-ASCII "
                "characters, and cannot continue. Folder names may only use "
                "the characters A-Z, 0-9, and basic punctuation.\n"
                "Alternatively, you may run PyLNP from source using Python 3.",
                file=sys.stderr)
            sys.exit(1)


# vim:expandtab
