#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Launching of programs, folders, URLs, etc.."""
from __future__ import print_function, unicode_literals, absolute_import

import sys
import os
import subprocess

from .helpers import get_resource
from .lnp import lnp
from . import hacks, paths

def toggle_autoclose():
    """Toggle automatic closing of the UI when launching DF."""
    lnp.userconfig['autoClose'] = not lnp.userconfig.get_bool('autoClose')
    lnp.userconfig.save_data()

def get_df_executable():
    """Returns the path of the executable needed to launch Dwarf Fortress."""
    spawn_terminal = False
    if sys.platform == 'win32':
        if ('legacy' in lnp.df_info.variations and
                lnp.df_info.version <= '0.31.14'):
            df_filename = 'dwarfort.exe'
        else:
            df_filename = 'Dwarf Fortress.exe'
    elif sys.platform == 'darwin' and lnp.df_info.version <= '0.28.181.40d':
        df_filename = 'Dwarf Fortress.app'
    else:
        # Linux/OSX: Run DFHack if available and enabled
        if (os.path.isfile(paths.get('df', 'dfhack')) and
                hacks.is_dfhack_enabled()):
            df_filename = 'dfhack'
            spawn_terminal = True
        else:
            df_filename = 'df'

    return df_filename, spawn_terminal

def run_df(force=False):
    """Launches Dwarf Fortress."""
    df_filename, spawn_terminal = get_df_executable()

    executable = paths.get('df', df_filename)
    result = run_program(executable, force, True, spawn_terminal)
    if (force and not result) or result is False:
        raise Exception('Failed to run Dwarf Fortress.')

    for prog in lnp.autorun:
        utility = paths.get('utilities', prog)
        if os.access(utility, os.F_OK):
            run_program(utility)

    if lnp.userconfig.get_bool('autoClose'):
        sys.exit()
    return result

def get_terminal_launcher():
    """Returns a command prefix to launch a program in a new terminal."""
    if sys.platform == 'darwin':
        return ['open', '-a', 'Terminal.app']
    elif sys.platform.startswith('linux'):
        return [get_resource('xdg-terminal')]
    raise Exception('No terminal launcher for platform: ' + sys.platform)

def run_program(path, force=False, is_df=False, spawn_terminal=False):
    """
    Launches an external program.

    Params:
        path
            The path of the program to launch.
        spawn_terminal
            Whether or not to spawn a new terminal for this app.
            Used only for DFHack.
    """
    path = os.path.abspath(path)
    check_nonchild = ((spawn_terminal and sys.platform.startswith('linux')) or
                      (sys.platform == 'darwin' and (
                          path.endswith('.app') or spawn_terminal)))

    is_running = program_is_running(path, check_nonchild)
    if not force and is_running:
        lnp.ui.on_program_running(path, is_df)
        return None

    try:
        workdir = os.path.dirname(path)
        run_args = path
        if spawn_terminal and not sys.platform.startswith('win'):
            term = get_terminal_launcher()
            retcode = subprocess.call(term + [path], cwd=workdir)
            return retcode == 0
        elif path.endswith('.jar'):  # Explicitly launch JAR files with Java
            run_args = ['java', '-jar', os.path.basename(path)]
        elif path.endswith('.app'):  # OS X application bundle
            run_args = ['open', path]
            workdir = path

        lnp.running[path] = subprocess.Popen(run_args, cwd=workdir)
        return True
    except OSError:
        sys.excepthook(*sys.exc_info())
        return False

def program_is_running(path, nonchild=False):
    """
    Returns True if a program is currently running.

    Params:
        path
            The path of the program.
        nonchild
            If set to True, attempts to check for the process among all
            running processes, not just known child processes. Used for
            DFHack on Linux and OS X; currently unsupported for Windows.
    """
    if nonchild:
        ps = subprocess.Popen(['ps', 'axww'], stdout=subprocess.PIPE)
        s = ps.stdout.read()
        ps.wait()
        encoding = sys.getfilesystemencoding()
        if encoding is None:
            #Encoding was not detected, assume UTF-8
            encoding = 'UTF-8'
        return path in s.decode(sys.getfilesystemencoding(), 'replace')
    else:
        if path not in lnp.running:
            return False
        else:
            lnp.running[path].poll()
            return lnp.running[path].returncode is None

def open_folder_idx(i):
    """Opens the folder specified by index i, as listed in PyLNP.json."""
    open_folder(os.path.join(
        paths.get('root'), lnp.config['folders'][i][1].replace(
            '<df>', paths.get('df'))))

def open_savegames():
    """Opens the save game folder."""
    open_folder(paths.get('save'))

def open_link_idx(i):
    """Opens the link specified by index i, as listed in PyLNP.json."""
    open_url(lnp.config['links'][i][1])

def open_url(url):
    """Launches a web browser to the Dwarf Fortress webpage."""
    import webbrowser
    webbrowser.open(url)

def open_folder(path):
    """
    Opens a folder in the system file manager.

    Params:
        path
            The folder path to open.
    """
    # http://stackoverflow.com/q/6631299
    path = os.path.normpath(path)
    # pylint: disable=broad-except, bare-except
    try:
        if sys.platform == 'darwin':
            subprocess.check_call(['open', '--', path])
        elif sys.platform.startswith('linux'):
            subprocess.check_call(['xdg-open', path])
        elif sys.platform in ['windows', 'win32']:
            subprocess.check_call(['explorer', path])
    except:
        pass
