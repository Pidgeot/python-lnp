#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Launching of programs, folders, URLs, etc.."""

import copy
import os
import re
import subprocess
import sys

from . import hacks, log, paths, terminal
from .lnp import lnp


def toggle_autoclose():
    """Toggle automatic closing of the UI when launching DF."""
    lnp.userconfig['autoClose'] = not lnp.userconfig.get_bool('autoClose')
    lnp.userconfig.save_data()


def get_df_executable():
    """Returns the path of the executable needed to launch Dwarf Fortress."""
    spawn_terminal = False
    if sys.platform == 'win32':
        if ('legacy' in lnp.df_info.variations
                and lnp.df_info.version <= '0.31.14'):
            df_filename = 'dwarfort.exe'
        else:
            df_filename = 'Dwarf Fortress.exe'
    elif sys.platform == 'darwin' and lnp.df_info.version <= '0.28.181.40d':
        df_filename = 'Dwarf Fortress.app'
    else:
        # Linux/OSX: Run DFHack if available and enabled
        if (os.path.isfile(paths.get('df', 'dfhack'))
                and hacks.is_dfhack_enabled()):
            df_filename = 'dfhack'
            spawn_terminal = True
        else:
            df_filename = 'df'
    if lnp.args.df_executable:
        df_filename = lnp.args.df_executable
    return df_filename, spawn_terminal


def run_df(force=False):
    """Launches Dwarf Fortress."""
    validation_result = lnp.settings.validate_config()
    if validation_result:
        if not lnp.ui.on_invalid_config(validation_result):
            return None
    df_filename, spawn_terminal = get_df_executable()

    executable = paths.get('df', df_filename)
    result = run_program(executable, force, True, spawn_terminal)
    if (force and not result) or result is False:
        log.e('Could not launch ' + executable)
        raise Exception('Failed to run Dwarf Fortress.')

    for prog in lnp.autorun:
        utility = paths.get('utilities', prog)
        if os.access(utility, os.F_OK):
            run_program(utility)

    if lnp.userconfig.get_bool('autoClose'):
        sys.exit()
    return result


def run_program(path, force=False, is_df=False, spawn_terminal=False):
    """
    Launches an external program.

    Args:
        path: the path of the program to launch.
        spawn_terminal: whether to spawn a new terminal for this app.
            Used only for DFHack.
    """
    path = os.path.abspath(path)
    check_nonchild = ((spawn_terminal and sys.platform.startswith('linux'))
                      or (sys.platform == 'darwin' and (
                          path.endswith('.app') or spawn_terminal)))

    is_running = program_is_running(path, check_nonchild)
    if not force and is_running:
        log.i(path + ' is already running')
        lnp.ui.on_program_running(path, is_df)
        return None

    try:
        workdir = os.path.dirname(path)
        run_args = path
        if spawn_terminal and not sys.platform.startswith('win'):
            run_args = terminal.get_terminal_command([path,])
        elif path.endswith('.jar'):  # Explicitly launch JAR files with Java
            run_args = ['java', '-jar', os.path.basename(path)]
        elif path.endswith('.app'):  # OS X application bundle
            run_args = ['open', path]
            workdir = path

        environ = os.environ
        if lnp.bundle:
            # pylint: disable=protected-access
            environ = copy.deepcopy(os.environ)
            if ('TCL_LIBRARY' in environ
                    and sys._MEIPASS in environ['TCL_LIBRARY']):
                del environ['TCL_LIBRARY']
            if ('TK_LIBRARY' in environ
                    and sys._MEIPASS in environ['TK_LIBRARY']):
                del environ['TK_LIBRARY']
            if 'LD_LIBRARY_PATH' in environ:
                del environ['LD_LIBRARY_PATH']
            if 'PYTHONPATH' in environ:
                del environ['PYTHONPATH']

        with subprocess.Popen(run_args, cwd=workdir, env=environ) as p:
            lnp.running[path] = p
        return True
    except OSError:
        sys.excepthook(*sys.exc_info())
        return False


def program_is_running(path, nonchild=False):
    """
    Returns True if a program is currently running.

    Args:
        path: the path of the program.
        nonchild: if set to True, attempts to check for the process among all
            running processes, not just known child processes. Used for
            DFHack on Linux and OS X; currently unsupported for Windows.
    """
    if nonchild:
        with subprocess.Popen(['ps', 'axww'], stdout=subprocess.PIPE) as ps:
            s = ps.stdout.read()
        encoding = sys.getfilesystemencoding()
        if encoding is None:
            # Encoding was not detected, assume UTF-8
            encoding = 'UTF-8'
        s = s.decode(encoding, 'replace')
        return re.search('\\B%s( |$)' % re.escape(path), s, re.M) is not None
    if path not in lnp.running:
        return False
    lnp.running[path].poll()
    return lnp.running[path].returncode is None


def open_folder_idx(i):
    """Opens the folder specified by index i, as listed in PyLNP.json."""
    open_file(os.path.join(
        paths.get('root'), lnp.config['folders'][i][1].replace(
            '<df>', paths.get('df'))))


def open_savegames():
    """Opens the save game folder."""
    open_file(paths.get('save'))


def open_link_idx(i):
    """Opens the link specified by index i, as listed in PyLNP.json."""
    open_url(lnp.config['links'][i][1])


def open_url(url):
    """Launches a web browser to the Dwarf Fortress webpage."""
    import webbrowser
    webbrowser.open(url)


def open_file(path):
    """
    Opens a file with the system default viewer for the respective file type.

    Args:
        path: the file path to open.
    """
    path = os.path.normpath(path)
    try:
        if sys.platform == 'darwin':
            subprocess.check_call(['open', '--', path])
        elif sys.platform.startswith('linux'):
            subprocess.check_call(['xdg-open', path])
        elif sys.platform in ['windows', 'win32']:
            os.startfile(path)
        else:
            log.e('Unknown platform, cannot open file')
    except Exception:
        log.e('Could not open file ' + path)
