#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PyLNP main library."""
from __future__ import print_function, unicode_literals, absolute_import
import sys

import os
from . import errorlog

from .json_config import JSONConfiguration

VERSION = '0.6'

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
        errorlog.start()

        from . import df, paths, update, utilities

        paths.register('root', self.BASEDIR)
        paths.register('lnp', self.BASEDIR, 'LNP')
        if not os.path.isdir(paths.get('lnp')):
            print('WARNING: LNP folder is missing!', file=sys.stderr)
        paths.register('keybinds', paths.get('lnp'), 'Keybinds')
        paths.register('graphics', paths.get('lnp'), 'Graphics')
        paths.register('utilities', paths.get('lnp'), 'Utilities')
        paths.register('colors', paths.get('lnp'), 'Colors')
        paths.register('embarks', paths.get('lnp'), 'Embarks')

        self.df_info = None
        self.folders = []
        self.settings = None
        self.autorun = []
        self.running = {}

        config_file = 'PyLNP.json'
        if os.access(os.path.join(paths.get('lnp'), 'PyLNP.json'), os.F_OK):
            config_file = os.path.join(paths.get('lnp'), 'PyLNP.json')
        self.config = JSONConfiguration(config_file)
        self.userconfig = JSONConfiguration('PyLNP.user')

        df.find_df_folder()
        utilities.load_autorun()

        self.new_version = None

        from tkgui.tkgui import TkGui
        self.ui = TkGui()
        update.check_update()
        self.ui.start()

    def save_config(self):
        """Saves LNP configuration."""
        self.userconfig.save_data()

    def detect_basedir(self):
        """Detects the location of Dwarf Fortress by walking up the directory
        tree."""
        prev_path = '.'

        from . import df
        while os.path.abspath(self.BASEDIR) != prev_path:
            df.find_df_folders()
            if len(self.folders) != 0:
                break
            prev_path = os.path.abspath(self.BASEDIR)
            self.BASEDIR = os.path.join(self.BASEDIR, '..')


# vim:expandtab
