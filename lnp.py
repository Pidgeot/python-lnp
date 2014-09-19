#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PyLNP main library."""
from __future__ import print_function, unicode_literals, absolute_import

import sys
from tkgui.tkgui import TkGui

import distutils.dir_util as dir_util
import fnmatch
import glob
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
import errorlog
from threading import Thread

from settings import DFConfiguration
from json_config import JSONConfiguration

try:  # Python 2
    # pylint:disable=import-error
    from urllib2 import urlopen, URLError, Request
except ImportError:  # Python 3
    # pylint:disable=import-error, no-name-in-module
    from urllib.request import urlopen, Request
    from urllib.error import URLError

BASEDIR = '.'
VERSION = '0.4'


class PyLNP(object):
    """
    PyLNP library class.

    Acts as an abstraction layer between the UI and the Dwarf Fortress
    instance.
    """
    def __init__(self):
        """Constructor for the PyLNP library."""
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
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        errorlog.start()

        self.lnp_dir = self.identify_folder_name(BASEDIR, 'LNP')
        if not os.path.isdir(self.lnp_dir):
            print('WARNING: LNP folder is missing!', file=sys.stderr)
        self.keybinds_dir = self.identify_folder_name(self.lnp_dir, 'Keybinds')
        self.graphics_dir = self.identify_folder_name(self.lnp_dir, 'Graphics')
        self.utils_dir = self.identify_folder_name(self.lnp_dir, 'Utilities')
        self.colors_dir = self.identify_folder_name(self.lnp_dir, 'Colors')
        self.embarks_dir = self.identify_folder_name(self.lnp_dir, 'Embarks')

        self.folders = []
        self.df_dir = ''
        self.settings = None
        self.init_dir = ''
        self.save_dir = ''
        self.autorun = []
        self.running = {}

        config_file = 'PyLNP.json'
        if os.access(os.path.join(self.lnp_dir, 'PyLNP.json'), os.F_OK):
            config_file = os.path.join(self.lnp_dir, 'PyLNP.json')
        self.config = JSONConfiguration(config_file)
        self.userconfig = JSONConfiguration('PyLNP.user')

        self.load_autorun()
        self.find_df_folder()

        self.new_version = None

        self.ui = TkGui(self)
        self.check_update()
        self.ui.start()

    @staticmethod
    def identify_folder_name(base, name):
        """
        Allows folder names to be lowercase on case-sensitive systems.
        Returns "base/name" where name is lowercase if the lower case version
        exists and the standard case version does not.

        Params:
            base
                The path containing the desired folder.
            name
                The standard case name of the desired folder.
        """
        normal = os.path.join(base, name)
        lower = os.path.join(base, name.lower())
        if os.path.isdir(lower) and not os.path.isdir(normal):
            return lower
        return normal

    def load_params(self):
        """Loads settings from the selected Dwarf Fortress instance."""
        try:
            self.settings.read_settings()
        except IOError:
            sys.excepthook(*sys.exc_info())
            msg = ("Failed to read settings, "
                   "{0} not really a DF dir?").format(self.df_dir)
            raise IOError(msg)

    def save_params(self):
        """Saves settings to the selected Dwarf Fortress instance."""
        self.settings.write_settings()

    def save_config(self):
        """Saves LNP configuration."""
        self.userconfig.save_data()

    def restore_defaults(self):
        """Copy default settings into the selected Dwarf Fortress instance."""
        shutil.copy(
            os.path.join(self.lnp_dir, 'Defaults', 'init.txt'),
            os.path.join(self.init_dir, 'init.txt')
            )
        shutil.copy(
            os.path.join(self.lnp_dir, 'Defaults', 'd_init.txt'),
            os.path.join(self.init_dir, 'd_init.txt')
        )
        self.load_params()

    def run_df(self, force=False):
        """Launches Dwarf Fortress."""
        result = None
        if sys.platform == 'win32':
            result = self.run_program(
                os.path.join(self.df_dir, 'Dwarf Fortress.exe'), force, True)
        else:
            # Linux/OSX: Run DFHack if available
            if os.path.isfile(os.path.join(self.df_dir, 'dfhack')):
                result = self.run_program(
                    os.path.join(self.df_dir, 'dfhack'), force, True, True)
                if result == False:
                    raise Exception('Failed to launch a new terminal.')
            else:
                result = self.run_program(os.path.join(self.df_dir, 'df'))
        for prog in self.autorun:
            if os.access(os.path.join(self.utils_dir, prog), os.F_OK):
                self.run_program(os.path.join(self.utils_dir, prog))
        if self.userconfig.get_bool('autoClose'):
            sys.exit()
        return result

    def run_program(self, path, force=False, is_df=False, spawn_terminal=False):
        """
        Launches an external program.

        Params:
            path
                The path of the program to launch.
            spawn_terminal
                Whether or not to spawn a new terminal for this app.
                Used only for DFHack.
        """
        try:
            path = os.path.abspath(path)
            workdir = os.path.dirname(path)
            run_args = path
            nonchild = False
            if spawn_terminal:
                if sys.platform.startswith('linux'):
                    script = 'xdg-terminal'
                    if self.bundle == "linux":
                        script = os.path.join(sys._MEIPASS, script)
                    if force or self.check_program_not_running(path, True):
                        retcode = subprocess.call(
                            [os.path.abspath(script), path],
                            cwd=os.path.dirname(path))
                        return retcode == 0
                    self.ui.on_program_running(path, is_df)
                    return None
                elif sys.platform == 'darwin':
                    nonchild = True
                    run_args = ['open', '-a', 'Terminal.app', path]
            elif path.endswith('.jar'):  # Explicitly launch JAR files with Java
                run_args = ['java', '-jar', os.path.basename(path)]
            elif path.endswith('.app'):  # OS X application bundle
                nonchild = True
                run_args = ['open', path]
                workdir = path
            if force or self.check_program_not_running(path, nonchild):
                self.running[path] = subprocess.Popen(run_args, cwd=workdir)
                return True
            self.ui.on_program_running(path, is_df)
            return None
        except OSError:
            sys.excepthook(*sys.exc_info())
            return False

    def check_program_not_running(self, path, nonchild=False):
        """
        Returns True if a program is not currently running.

        Params:
            path
                The path of the program.
            nonchild
                If set to True, attempts to check for the process among all
                running processes, not just known child processes. Used for
                DFHack on Linux and OS X; currently unsupported for Windows.
        """
        if nonchild:
            ps = subprocess.Popen('ps axww', shell=True, stdout=subprocess.PIPE)
            ps.wait()
            s = ps.stdout.read()
            return path not in s
        else:
            if path not in self.running:
                return True
            else:
                self.running[path].poll()
                return self.running[path].returncode is not None

    def open_folder_idx(self, i):
        """Opens the folder specified by index i, as listed in PyLNP.json."""
        open_folder(os.path.join(
            BASEDIR, self.config['folders'][i][1].replace(
                '<df>', self.df_dir)))

    def open_savegames(self):
        """Opens the save game folder."""
        open_folder(self.save_dir)

    def open_utils(self):
        """Opens the utilities folder."""
        open_folder(self.utils_dir)

    def open_graphics(self):
        """Opens the graphics pack folder."""
        open_folder(self.graphics_dir)

    @staticmethod
    def open_main_folder():
        """Opens the folder containing the program."""
        open_folder('.')

    def open_lnp_folder(self):
        """Opens the folder containing data for the LNP."""
        open_folder(self.lnp_dir)

    def open_df_folder(self):
        """Opens the Dwarf Fortress folder."""
        open_folder(self.df_dir)

    def open_init_folder(self):
        """Opens the init folder in the selected Dwarf Fortress instance."""
        open_folder(self.init_dir)

    def open_link_idx(self, i):
        """Opens the link specified by index i, as listed in PyLNP.json."""
        self.open_url(self.config['links'][i][1])

    @staticmethod
    def open_url(url):
        """Launches a web browser to the Dwarf Fortress webpage."""
        import webbrowser
        webbrowser.open(url)

    def find_df_folder(self):
        """Locates all suitable Dwarf Fortress installations (folders starting
        with "Dwarf Fortress" or "df")"""
        self.folders = folders = tuple([
            o for o in
            glob.glob(os.path.join(BASEDIR, 'Dwarf Fortress*')) +
            glob.glob(os.path.join(BASEDIR, 'df*')) if os.path.isdir(o)
            ])
        self.df_dir = ''
        if len(folders) == 1:
            self.set_df_folder(folders[0])

    def set_df_folder(self, path):
        """
        Selects the Dwarf Fortress instance to operate on.

        :param path: The path of the Dwarf Fortress instance to use.
        """
        self.df_dir = os.path.abspath(path)
        self.init_dir = os.path.join(self.df_dir, 'data', 'init')
        self.save_dir = os.path.join(self.df_dir, 'data', 'save')
        self.settings = DFConfiguration(self.df_dir)
        self.install_extras()
        self.load_params()
        self.read_hacks()

    @staticmethod
    def get_text_files(directory):
        """
        Returns a list of .txt files in <directory>.
        Excludes all filenames beginning with "readme" (case-insensitive).

        Params:
            directory
                The directory to search.
        """
        temp = glob.glob(os.path.join(directory, '*.txt'))
        result = []
        for f in temp:
            if not os.path.basename(f).lower().startswith('readme'):
                result.append(f)
        return result

    def read_keybinds(self):
        """Returns a list of keybinding files."""
        return tuple([
            os.path.basename(o) for o in self.get_text_files(self.keybinds_dir)
            ])

    def read_graphics(self):
        """Returns a list of graphics directories."""
        packs = [
            os.path.basename(o) for o in
            glob.glob(os.path.join(self.graphics_dir, '*')) if
            os.path.isdir(o)]
        result = []
        for p in packs:
            font = self.settings.read_value(os.path.join(
                self.graphics_dir, p, 'data', 'init', 'init.txt'), 'FONT')
            graphics = self.settings.read_value(
                os.path.join(self.graphics_dir, p, 'data', 'init', 'init.txt'),
                'GRAPHICS_FONT')
            result.append((p, font, graphics))
        return tuple(result)

    def current_pack(self):
        """
        Returns the currently installed graphics pack.
        If the pack cannot be identified, returns "FONT/GRAPHICS_FONT".
        """
        packs = self.read_graphics()
        for p in packs:
            if (self.settings.FONT == p[1] and
                    self.settings.GRAPHICS_FONT == p[2]):
                return p[0]
        return self.settings.FONT+'/'+self.settings.GRAPHICS_FONT

    @staticmethod
    def read_utility_lists(path):
        """
        Reads a list of filenames from a utility list (e.g. include.txt).

        :param path: The file to read.
        """
        result = []
        try:
            util_file = open(path)
            for line in util_file:
                for match in re.findall(r'\[(.+)\]', line):
                    result.append(match)
        except IOError:
            pass
        return result

    def read_utilities(self):
        """Returns a list of utility programs."""
        exclusions = self.read_utility_lists(os.path.join(
            self.utils_dir, 'exclude.txt'))
        # Allow for an include list of filenames that will be treated as valid
        # utilities. Useful for e.g. Linux, where executables rarely have
        # extensions.
        inclusions = self.read_utility_lists(os.path.join(
            self.utils_dir, 'include.txt'))
        progs = []
        patterns = ['*.jar']  # Java applications
        if sys.platform in ['windows', 'win32']:
            patterns.append('*.exe')  # Windows executables
            patterns.append('*.bat')  # Batch files
        else:
            patterns.append('*.sh')  # Shell scripts for Linux and OS X
        for root, dirnames, filenames in os.walk(self.utils_dir):
            if sys.platform == 'darwin':
                for dirname in dirnames:
                    if fnmatch.fnmatch(dirname, '*.app'):
                        # OS X application bundles are really directories
                        progs.append(os.path.relpath(
                            os.path.join(root, dirname),
                            os.path.join(self.utils_dir)))
            for filename in filenames:
                if ((
                        any(fnmatch.fnmatch(filename, p) for p in patterns) or
                        filename in inclusions) and
                        filename not in exclusions):
                    progs.append(os.path.relpath(
                        os.path.join(root, filename),
                        os.path.join(self.utils_dir)))

        return progs

    def read_embarks(self):
        """Returns a list of embark profiles."""
        return tuple([
            os.path.basename(o) for o in self.get_text_files(self.embarks_dir)])

    def toggle_autoclose(self):
        """Toggle automatic closing of the UI when launching DF."""
        self.userconfig['autoClose'] = not self.userconfig.get_bool('autoClose')
        self.userconfig.save_data()

    def toggle_autorun(self, item):
        """
        Toggles autorun for the specified item.

        Params:
            item
                The item to toggle autorun for.
        """
        if item in self.autorun:
            self.autorun.remove(item)
        else:
            self.autorun.append(item)
        self.save_autorun()

    def load_autorun(self):
        """Loads autorun settings."""
        self.autorun = []
        try:
            for line in open(os.path.join(self.utils_dir, 'autorun.txt')):
                self.autorun.append(line)
        except IOError:
            pass

    def save_autorun(self):
        """Saves autorun settings."""
        autofile = open(os.path.join(self.utils_dir, 'autorun.txt'), 'w')
        autofile.write("\n".join(self.autorun))
        autofile.close()

    def cycle_option(self, field):
        """
        Cycles an option field between its possible values.

        :param field: The field to cycle.
        """
        self.settings.cycle_item(field)
        self.save_params()

    def set_option(self, field, value):
        """
        Sets a field to a specific value.

        Params:
            field
                The field to set.
            value
                The new value for the field.
        """
        self.settings.set_value(field, value)
        self.save_params()

    def load_keybinds(self, filename):
        """
        Overwrites Dwarf Fortress keybindings from a file.

        Params:
            filename
                The keybindings file to use.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        target = os.path.join(self.init_dir, 'interface.txt')
        os.rename(target, target+'.bak')
        shutil.copyfile(os.path.join(self.keybinds_dir, filename), target)

    def keybind_exists(self, filename):
        """
        Returns whether or not a keybindings file already exists.

        Params:
            filename
                The filename to check.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        return os.access(os.path.join(self.keybinds_dir, filename), os.F_OK)

    def save_keybinds(self, filename):
        """
        Save current keybindings to a file.

        Params:
            filename
                The name of the new keybindings file.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        filename = os.path.join(self.keybinds_dir, filename)
        shutil.copyfile(os.path.join(self.init_dir, 'interface.txt'), filename)
        self.read_keybinds()

    def delete_keybinds(self, filename):
        """
        Deletes a keybindings file.

        Params:
            filename
                The filename to delete.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        os.remove(os.path.join(self.keybinds_dir, filename))

    def install_graphics(self, pack):
        """
        Installs the graphics pack located in LNP/Graphics/<pack>.

        Params:
            pack
                The name of the pack to install.

        Returns:
            True if successful,
            False if an exception occured
            None if required files are missing (raw/graphics, data/init)
        """
        gfx_dir = os.path.join(self.graphics_dir, pack)
        if (os.path.isdir(gfx_dir) and
                os.path.isdir(os.path.join(gfx_dir, 'raw', 'graphics')) and
                os.path.isdir(os.path.join(gfx_dir, 'data', 'init'))):
            try:
                # Delete old graphics
                if os.path.isdir(os.path.join(self.df_dir, 'raw', 'graphics')):
                    dir_util.remove_tree(
                        os.path.join(self.df_dir, 'raw', 'graphics'))
                # Copy new raws
                dir_util.copy_tree(
                    os.path.join(gfx_dir, 'raw'),
                    os.path.join(self.df_dir, 'raw'))
                if os.path.isdir(os.path.join(self.df_dir, 'data', 'art')):
                    dir_util.remove_tree(
                        os.path.join(self.df_dir, 'data', 'art'))
                dir_util.copy_tree(
                    os.path.join(gfx_dir, 'data', 'art'),
                    os.path.join(self.df_dir, 'data', 'art'))
                self.patch_inits(gfx_dir)
                shutil.copyfile(
                    os.path.join(gfx_dir, 'data', 'init', 'colors.txt'),
                    os.path.join(self.df_dir, 'data', 'init', 'colors.txt'))
                try: # TwbT support
                    os.remove(os.path.join(
                        self.df_dir, 'data', 'init', 'overrides.txt'))
                except:
                    pass
                try: # TwbT support
                    shutil.copyfile(
                        os.path.join(gfx_dir, 'data', 'init', 'overrides.txt'),
                        os.path.join(
                            self.df_dir, 'data', 'init', 'overrides.txt'))
                except:
                    pass
            except Exception:
                sys.excepthook(*sys.exc_info())
                return False
            else:
                return True
        else:
            return None
        self.load_params()

    def patch_inits(self, gfx_dir):
        """
        Installs init files from a graphics pack by selectively changing
        specific fields. All settings outside of the mentioned fields are
        preserved.

        TODO: Consider if there's a better option than listing all fields
        explicitly...
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
            'GRAPHICS_FULLFONT', 'TRUETYPE']
        self.settings.read_file(
            os.path.join(gfx_dir, 'data', 'init', 'init.txt'), init_fields,
            False)
        self.settings.read_file(
            os.path.join(gfx_dir, 'data', 'init', 'd_init.txt'), d_init_fields,
            False)
        self.save_params()

    def update_savegames(self):
        """Update save games with current raws."""
        saves = [
            o for o in glob.glob(os.path.join(self.save_dir, '*'))
            if os.path.isdir(o) and not o.endswith('current')]
        count = 0
        if saves:
            for save in saves:
                count = count + 1
                # Delete old graphics
                if os.path.isdir(os.path.join(save, 'raw', 'graphics')):
                    dir_util.remove_tree(os.path.join(save, 'raw', 'graphics'))
                # Copy new raws
                dir_util.copy_tree(
                    os.path.join(self.df_dir, 'raw'),
                    os.path.join(save, 'raw'))
        return count

    def simplify_graphics(self):
        """Removes unnecessary files from all graphics packs."""
        for pack in self.read_graphics():
            self.simplify_pack(pack)

    def simplify_pack(self, pack):
        """
        Removes unnecessary files from LNP/Graphics/<pack>.

        Params:
            pack
                The pack to simplify.

        Returns:
          The number of files removed if successful
          False if an exception occurred
          None if folder is empty
        """
        pack = os.path.join(self.graphics_dir, pack)
        files_before = sum(len(f) for (_, _, f) in os.walk(pack))
        if files_before == 0:
            return None
        tmp = tempfile.mkdtemp()
        try:
            dir_util.copy_tree(pack, tmp)
            if os.path.isdir(pack):
                dir_util.remove_tree(pack)

            os.makedirs(pack)
            os.makedirs(os.path.join(pack, 'data', 'art'))
            os.makedirs(os.path.join(pack, 'raw', 'graphics'))
            os.makedirs(os.path.join(pack, 'raw', 'objects'))
            os.makedirs(os.path.join(pack, 'data', 'init'))

            dir_util.copy_tree(
                os.path.join(tmp, 'data', 'art'),
                os.path.join(pack, 'data', 'art'))
            dir_util.copy_tree(
                os.path.join(tmp, 'raw', 'graphics'),
                os.path.join(pack, 'raw', 'graphics'))
            dir_util.copy_tree(
                os.path.join(tmp, 'raw', 'objects'),
                os.path.join(pack, 'raw', 'objects'))
            shutil.copyfile(
                os.path.join(tmp, 'data', 'init', 'colors.txt'),
                os.path.join(pack, 'data', 'init', 'colors.txt'))
            shutil.copyfile(
                os.path.join(tmp, 'data', 'init', 'init.txt'),
                os.path.join(pack, 'data', 'init', 'init.txt'))
            shutil.copyfile(
                os.path.join(tmp, 'data', 'init', 'd_init.txt'),
                os.path.join(pack, 'data', 'init', 'd_init.txt'))
            shutil.copyfile(
                os.path.join(tmp, 'data', 'init', 'overrides.txt'),
                os.path.join(pack, 'data', 'init', 'overrides.txt'))
        except IOError:
            sys.excepthook(*sys.exc_info())
            retval = False
        else:
            files_after = sum(len(f) for (_, _, f) in os.walk(pack))
            retval = files_after - files_before
        if os.path.isdir(tmp):
            dir_util.remove_tree(tmp)
        return retval

    def install_extras(self):
        """
        Installs extra utilities to the Dwarf Fortress folder, if this has not
        yet been done.
        """
        extras_dir = os.path.join(self.lnp_dir, 'Extras')
        if not os.path.isdir(extras_dir):
            return
        install_file = os.path.join(self.df_dir, 'PyLNP{0}.txt'.format(VERSION))
        if not os.access(install_file, os.F_OK):
            dir_util.copy_tree(extras_dir, self.df_dir)
            textfile = open(install_file, 'w')
            textfile.write(
                'PyLNP V{0} extras installed!\nTime: {1}'.format(
                    VERSION, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            textfile.close()

    def updates_configured(self):
        """Returns True if update checking have been configured."""
        return self.config.get_string('updates/checkURL') != ''

    def check_update(self):
        """Checks for updates using the URL specified in PyLNP.json."""
        if not self.updates_configured():
            return
        if self.userconfig.get_number('updateDays') == -1:
            return
        if self.userconfig.get_number('nextUpdate') < time.time():
            t = Thread(target=self.perform_update_check)
            t.daemon = True
            t.start()

    def perform_update_check(self):
        """Performs the actual update check. Runs in a thread."""
        try:
            req = Request(
                self.config.get_string('updates/checkURL'),
                headers={'User-Agent':'PyLNP'})
            version_text = urlopen(req, timeout=3).read()
            # Note: versionRegex must capture the version number in a group
            new_version = re.search(
                self.config.get_string('updates/versionRegex'),
                version_text).group(1)
            if new_version != self.config.get_string('updates/packVersion'):
                self.new_version = new_version
                self.ui.on_update_available()
        except URLError as ex:
            print(
                "Error checking for updates: " + str(ex.reason),
                file=sys.stderr)
        except:
            pass

    def next_update(self, days):
        """Sets the next update check to occur in <days> days."""
        self.userconfig['nextUpdate'] = (time.time() + days * 24 * 60 * 60)
        self.userconfig['updateDays'] = days
        self.save_config()

    def start_update(self):
        """Launches a webbrowser to the specified update URL."""
        self.open_url(self.config.get_string('updates/downloadURL'))

    def read_colors(self):
        """Returns a list of color schemes."""
        return tuple([
            os.path.splitext(os.path.basename(p))[0] for p in
            self.get_text_files(self.colors_dir)])

    def get_colors(self, colorscheme=None):
        """
        Returns RGB tuples for all 16 colors in <colorscheme>.txt, or
        data/init/colors.txt if no scheme is provided."""
        result = []
        f = os.path.join(self.df_dir, 'data', 'init', 'colors.txt')
        if colorscheme is not None:
            f = os.path.join(self.lnp_dir, 'colors', colorscheme+'.txt')
        for c in [
                'BLACK', 'BLUE', 'GREEN', 'CYAN', 'RED', 'MAGENTA', 'BROWN',
                'LGRAY', 'DGRAY', 'LBLUE', 'LGREEN', 'LCYAN', 'LRED',
                'LMAGENTA', 'YELLOW', 'WHITE']:
            result.append((
                int(self.settings.read_value(f, c+'_R')),
                int(self.settings.read_value(f, c+'_G')),
                int(self.settings.read_value(f, c+'_B'))))
        return result

    def load_colors(self, filename):
        """
        Replaces the current DF color scheme.

        Params:
          filename
            The name of the new colorscheme to install (filename without
            extension).
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        shutil.copyfile(
            os.path.join(self.lnp_dir, 'colors', filename),
            os.path.join(self.init_dir, 'colors.txt'))

    def save_colors(self, filename):
        """
        Save current keybindings to a file.

        Params:
            filename
                The name of the new keybindings file.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        filename = os.path.join(self.colors_dir, filename)
        shutil.copyfile(os.path.join(self.init_dir, 'colors.txt'), filename)
        self.read_colors()

    def color_exists(self, filename):
        """
        Returns whether or not a color scheme already exists.

        Params:
            filename
                The filename to check.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        return os.access(os.path.join(self.colors_dir, filename), os.F_OK)

    def delete_colors(self, filename):
        """
        Deletes a color scheme file.

        Params:
            filename
                The filename to delete.
        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        os.remove(os.path.join(self.colors_dir, filename))

    def read_hacks(self):
        """Reads which hacks are enabled."""
        try:
            f = open(os.path.join(self.df_dir, 'PyLNP_dfhack_onload.init'))
            hacklines = f.readlines()
            for h in self.get_hacks().values():
                h['enabled'] = h['command']+'\n' in hacklines
            f.close()
        except IOError:
            for h in self.get_hacks().values():
                h['enabled'] = False

    def get_hacks(self):
        """Returns dict of available hacks."""
        return self.config.get_dict('dfhack')

    def get_hack(self, title):
        """
        Returns the hack titled <title>, or None if this does not exist.

        Params:
            title
                The title of the hack.
        """
        try:
            return self.get_hacks()[title]
        except KeyError:
            return None

    def toggle_hack(self, name):
        """
        Toggles the hack <name>.

        Params:
            name
                The name of the hack to toggle.
        """
        self.get_hack(name)['enabled'] = not self.get_hack(name)['enabled']
        self.rebuild_hacks()

    def rebuild_hacks(self):
        """Rebuilds PyLNP_dfhack_onload.init with the enabled hacks."""
        f = open(os.path.join(self.df_dir, 'PyLNP_dfhack_onload.init'), 'w')
        f.write('# Generated by PyLNP\n\n')
        for k, h in self.get_hacks().items():
            if h['enabled']:
                f.write('# '+k+'\n')
                f.write('# '+h['tooltip']+'\n')
                f.write(h['command']+'\n\n')
        f.flush()
        f.close()

    def install_embarks(self, files):
        """
        Installs a list of embark profiles.

        Params:
            files
                List of files to install.
        """
        out = open(os.path.join(self.init_dir, 'embark_profiles.txt'), 'w')
        for f in files:
            embark = open(os.path.join(self.embarks_dir, f))
            out.write(embark.read()+"\n\n")
        out.flush()
        out.close()

def open_folder(path):

    """
    Opens a folder in the system file manager.

    Params:
        path
            The folder path to open.
    """
# http://stackoverflow.com/q/6631299
    path = os.path.normpath(path)
    try:
        if sys.platform == 'darwin':
            subprocess.check_call(['open', '--', path])
        elif sys.platform.startswith('linux'):
            subprocess.check_call(['xdg-open', path])
        elif sys.platform in ['windows', 'win32']:
            subprocess.check_call(['explorer', path])
    except Exception:
        pass

if __name__ == "__main__":
    PyLNP()

# vim:expandtab
