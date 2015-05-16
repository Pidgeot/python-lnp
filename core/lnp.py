#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PyLNP main library."""
from __future__ import print_function, unicode_literals, absolute_import
import sys

import os
from . import log

from .json_config import JSONConfiguration

VERSION = '0.10'

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
        if sys.platform == 'win32':
            self.os = 'win'
        elif sys.platform.startswith('linux'):
            self.os = 'linux'
        elif sys.platform == 'darwin':
            self.os = 'osx'

        self.bundle = ''
        if hasattr(sys, 'frozen'):
            self.bundle = self.os
            os.chdir(os.path.dirname(sys.executable))
            if self.bundle == 'osx':
                # OS X bundles start in different directory
                os.chdir('../../..')
        else:
            os.chdir(os.path.join(os.path.dirname(__file__), '..'))

        from . import update

        self.folders = []
        self.df_info = None
        self.settings = None
        self.running = {}
        self.autorun = []
        self.updater = None
        self.config = None
        self.userconfig = None
        self.ui = None

        self.initialize_program()

        self.initialize_df()

        self.new_version = None

        self.initialize_ui()
        update.check_update()
        self.ui.start()

    def initialize_program(self):
        """Initializes the main program (errorlog, path registration, etc.)."""
        from . import paths, utilities, errorlog
        self.BASEDIR = '.'
        self.detect_basedir()
        paths.clear()
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
                "updateMethod": ""
            }
        }
        self.config = JSONConfiguration(config_file, default_config)
        self.userconfig = JSONConfiguration('PyLNP.user')
        self.autorun = []
        utilities.load_autorun()

    def initialize_df(self):
        """Initializes the DF folder and related variables."""
        from . import df
        self.df_info = None
        self.folders = []
        self.settings = None
        df.find_df_folder()

    def initialize_ui(self):
        """Instantiates the UI object."""
        from tkgui.tkgui import TkGui
        self.ui = TkGui()

    def reload_program(self):
        """Reloads the program to allow the user to change DF folders."""
        self.args.df_folder = None
        self.initialize_program()
        self.initialize_df()
        self.initialize_ui()
        self.ui.start()

    def parse_commandline(self):
        """Parses and acts on command line options."""
        args = self.get_commandline_args()
        if args.debug == 1:
            log.set_level(log.DEBUG)
        elif args.debug > 1:
            log.set_level(log.VERBOSE)
        log.d(args)
        return args

    @staticmethod
    def get_commandline_args():
        """Responsible for the actual parsing of command line options."""
        import argparse
        parser = argparse.ArgumentParser(
            description="PyLNP " +VERSION)
        parser.add_argument(
            '-d', '--debug', action='count',
            help='Turn on debugging output (use twice for extra verbosity)')
        parser.add_argument(
            '--raw-lint', action='store_true',
            help='Verify contents of raw files and exit')
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
                    return
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
        log.e("Could not find any Dwarf Fortress installations.")
        sys.exit(2)


# vim:expandtab
