#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PyLNP main library."""
from __future__ import print_function, unicode_literals

import sys
from tkgui import TkGui

import fnmatch, glob, json, os, re, shutil, subprocess, tempfile, webbrowser
import distutils.dir_util as dir_util
from datetime import datetime
import time

from settings import DFConfiguration

try: #Python 2
    #pylint:disable=import-error
    from urllib2 import urlopen, URLError
except ImportError: # Python 3
    #pylint:disable=import-error, no-name-in-module
    from urllib.request import urlopen
    from urllib.error import URLError

BASEDIR = '.'
VERSION = '0.1'

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
                #OS X bundles start in different directory
                os.chdir('../../..')
        else:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

        self.lnp_dir = os.path.join(BASEDIR, 'LNP')
        if not os.path.isdir(self.lnp_dir):
            print('WARNING: LNP folder is missing!', file=sys.stderr)
        self.keybinds_dir = os.path.join(self.lnp_dir, 'Keybinds')
        self.graphics_dir = os.path.join(self.lnp_dir, 'Graphics')
        self.utils_dir = os.path.join(self.lnp_dir, 'Utilities')

        self.folders = []
        self.df_dir = ''
        self.settings = None
        self.init_dir = ''
        self.save_dir = ''
        self.autorun = []

        self.load_autorun()
        self.find_df_folder()

        self.config = json.load(open('PyLNP.json'), encoding='utf-8')
        try:
            self.userconfig = json.load(open('PyLNP.user'), encoding='utf-8')
        except:
            self.userconfig = {'nextUpdate': 0}
        self.new_version = None

        self.check_update()

        TkGui(self)

    def load_params(self):
        """Loads settings from the selected Dwarf Fortress instance."""
        try:
            self.settings.read_settings()
        except IOError:
            sys.excepthook(*sys.exc_info())
            msg = ("Failed to read settings, "
                   "{0} not really a DF dir?"
                  ).format(self.df_dir)
            raise IOError(msg)

    def save_params(self):
        """Saves settings to the selected Dwarf Fortress instance."""
        self.settings.write_settings()

    def save_config(self):
        """Saves LNP configuration."""
        json.dump(self.userconfig, open('PyLNP.user','w'))

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

    def run_df(self):
        """Launches Dwarf Fortress."""
        if sys.platform == 'win32':
            self.run_program(os.path.join(self.df_dir, 'Dwarf Fortress.exe'))
        else:
            self.run_program(os.path.join(self.df_dir, 'df'))
        for prog in self.autorun:
            if os.access(os.path.join(self.utils_dir, prog), os.F_OK):
                self.run_program(os.path.join(self.utils_dir, prog))

    @staticmethod
    def run_program(path):
        """
        Launches an external program.

        :param path: The path of the program to launch.
        """
        try:
            path = os.path.abspath(path)
            if path.endswith('.jar'): #Explicitly launch JAR files with Java
                subprocess.Popen(
                    ['java', '-jar', os.path.basename(path)],
                    cwd=os.path.dirname(path))
            elif path.endswith('.app'): #OS X application bundle
                subprocess.Popen(['open', path], cwd=path)
            else:
                subprocess.Popen(path, cwd=os.path.dirname(path))
            return True
        except OSError:
            sys.excepthook(*sys.exc_info())
            return False

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
        webbrowser.open(self.config['links'][i][1])

    @staticmethod
    def open_df_web():
        """Launches a web browser to the Dwarf Fortress webpage."""
        webbrowser.open('http://www.bay12games.com/dwarves/')

    @staticmethod
    def open_wiki():
        """Launches a web browser to the Dwarf Fortress Wiki."""
        webbrowser.open('http://dwarffortresswiki.org/')

    @staticmethod
    def open_forums():
        """Launches a web browser to the Dwarf Fortress forums."""
        webbrowser.open('http://www.bay12forums.com/smf/')

    def find_df_folder(self):
        """Locates all suitable Dwarf Fortress installations (folders starting
        with "Dwarf Fortress" or "df")"""
        self.folders = folders = tuple([
            o for o in
            glob.glob(os.path.join(BASEDIR, 'Dwarf Fortress*'))+
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

    def read_keybinds(self):
        """Returns a list of keybinding files."""
        return tuple([
            os.path.basename(o) for o in
            glob.glob(os.path.join(self.keybinds_dir, '*.txt'))
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
        #Allow for an include list of filenames that will be treated as valid
        #utilities. Useful for e.g. Linux, where executables rarely have
        #extensions.
        inclusions = self.read_utility_lists(os.path.join(
            self.utils_dir, 'include.txt'))
        progs = []
        patterns = ['*.jar'] # Java applications
        if sys.platform in ['windows', 'win32']:
            patterns.append('*.exe') # Windows executables
            patterns.append('*.bat') # Batch files
        else:
            patterns.append('*.sh') # Shell scripts for Linux and OS X
        for root, dirnames, filenames in os.walk(self.utils_dir):
            if sys.platform == 'darwin':
                for dirname in dirnames:
                    if fnmatch.fnmatch(dirname, '*.app'):
                        #OS X application bundles are really directories
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
        install_inits should point to the appropriate method used to handle the
        inits (copy_inits or patch_inits).

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
                #Delete old graphics
                if os.path.isdir(os.path.join(self.df_dir, 'raw', 'graphics')):
                    dir_util.remove_tree(
                        os.path.join(self.df_dir, 'raw', 'graphics'))
                #Copy new raws
                dir_util.copy_tree(
                    os.path.join(gfx_dir, 'raw'),
                    os.path.join(self.df_dir, 'raw'))
                if os.path.isdir(os.path.join(self.df_dir, 'data', 'art')):
                    dir_util.remove_tree(
                        os.path.join(self.df_dir, 'data', 'art'))
                dir_util.copy_tree(
                    os.path.join(gfx_dir, 'data', 'art'),
                    os.path.join(self.df_dir, 'data', 'art'))
                self.install_inits(gfx_dir)
                shutil.copyfile(
                    os.path.join(gfx_dir, 'data', 'init', 'colors.txt'),
                    os.path.join(self.df_dir, 'data', 'init', 'colors.txt'))
            except Exception:
                sys.excepthook(*sys.exc_info())
                return False
            else:
                return True
        else:
            return None
        self.load_params()

    def copy_inits(self, gfx_dir):
        """
        Installs init files from a graphics pack by overwriting.
        """
        shutil.copyfile(
            os.path.join(gfx_dir, 'data', 'init', 'init.txt'),
            os.path.join(self.df_dir, 'data', 'init', 'init.txt'))
        shutil.copyfile(
            os.path.join(gfx_dir, 'data', 'init', 'd_init.txt'),
            os.path.join(self.df_dir, 'data', 'init', 'd_init.txt'))

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
            #Tracks
            'TRACK_N', 'TRACK_S', 'TRACK_E', 'TRACK_W', 'TRACK_NS',
            'TRACK_NE', 'TRACK_NW', 'TRACK_SE', 'TRACK_SW', 'TRACK_EW',
            'TRACK_NSE', 'TRACK_NSW', 'TRACK_NEW', 'TRACK_SEW',
            'TRACK_NSEW', 'TRACK_RAMP_N', 'TRACK_RAMP_S', 'TRACK_RAMP_E',
            'TRACK_RAMP_W', 'TRACK_RAMP_NS', 'TRACK_RAMP_NE',
            'TRACK_RAMP_NW', 'TRACK_RAMP_SE', 'TRACK_RAMP_SW',
            'TRACK_RAMP_EW', 'TRACK_RAMP_NSE', 'TRACK_RAMP_NSW',
            'TRACK_RAMP_NEW', 'TRACK_RAMP_SEW', 'TRACK_RAMP_NSEW',
            #Trees
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

    install_inits = copy_inits

    def update_savegames(self):
        """Update save games with current raws."""
        saves = [
            o for o in glob.glob(os.path.join(self.save_dir, '*'))
            if os.path.isdir(o) and not o.endswith('current')]
        count = 0
        if saves:
            for save in saves:
                count = count + 1
                #Delete old graphics
                if os.path.isdir(os.path.join(save, 'raw', 'graphics')):
                    dir_util.remove_tree(os.path.join(save, 'raw', 'graphics'))
                #Copy new raws
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

    def check_update(self):
        """Checks for updates using the URL specified in PyLNP.json."""
        if self.config['updates']['checkURL'] == '':
            return
        if self.userconfig['nextUpdate'] < time.time():
            try:
                version_text = urlopen(
                    self.config['updates']['checkURL']).read()
                # Note: versionRegex must capture the version number in a group.
                new_version = re.search(
                    self.config['updates']['versionRegex'],
                    version_text).group(1)
                if new_version != self.config['updates']['packVersion']:
                    self.new_version = new_version
            except URLError as ex:
                print("Error checking for updates: " + ex.reason, file=sys.stderr)
                pass
            except:
                pass

    def next_update(self, days):
        """Sets the next update check to occur in <days> days."""
        self.userconfig['nextUpdate'] = (time.time() + days * 24 * 60 * 60)
        self.save_config()

    def start_update(self):
        """Launches a webbrowser to the specified update URL."""
        webbrowser.open(self.config['updates']['downloadURL'])

def open_folder(path):
    """
    Opens a folder in the system file manager.

    Params:
        path
            The folder path to open.
    """
#http://stackoverflow.com/q/6631299
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
