#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Handles terminal detection on Linux and terminal command lines."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, subprocess, tempfile, time
from .lnp import lnp
from . import log

def get_terminal_command(cmd):
    """Returns a command to launch a program in a new terminal."""
    if sys.platform == 'darwin':
        return ['open', '-a', 'Terminal.app'] + cmd
    elif sys.platform.startswith('linux'):
        term = get_configured_terminal().get_command_line()
        if "$" in term:
            c = []
            for s in term:
                if s == '$':
                    c += cmd
                else:
                    c.append(s)
            return c
        else:
            return term + cmd
        raise Exception('No terminal launcher for platform: ' + sys.platform)

def get_configured_terminal():
    """Retrieves the configured terminal command."""
    s = lnp.userconfig.get_string('terminal_type')
    terminals = get_valid_terminals()
    for t in terminals:
        if s == t.name:
            return t
    return CustomTerminal

def get_valid_terminals():
    """Gets the terminals that are available on this system."""
    result = []
    terminals = _get_terminals()
    for t in terminals:
        log.d("Checking for terminal %s", t.name)
        if t.detect():
            log.d("Found terminal %s", t.name)
            result.append(t)
    return result

def _get_terminals():
    # pylint: disable=no-member
    return LinuxTerminal.__subclasses__()

def configure_terminal(termname):
    """Configures the terminal class used to launch a terminal on Linux."""
    lnp.userconfig['terminal_type'] = termname
    lnp.userconfig.save_data()

def configure_custom_terminal(new_path):
    """Configures the custom command used to launch a terminal on Linux."""
    lnp.userconfig['terminal'] = new_path
    lnp.userconfig.save_data()

class LinuxTerminal(object):
    """
    Class for detecting and launching using a dedicated terminal on Linux.
    """

    # Set this in subclasses to provide a label for the terminal.
    name = "????"

    @staticmethod
    def detect():
        """Detects if this terminal is available."""
        pass

    @staticmethod
    def get_command_line():
        """
        Returns a subprocess-compatible command to launch a command with
        this terminal.
        If the command to be launched should go somewhere other than the end
        of the command line, use $ to indicate the correct place.
        """
        pass

# pylint: disable=bare-except

# Desktop environment-specific terminals
class KDETerminal(LinuxTerminal):
    """Handles terminals on KDE (e.g. Konsole)."""
    name = "KDE"

    @staticmethod
    def detect():
        return os.environ.get('KDE_FULL_SESSION', '') == 'true'

    @staticmethod
    def get_command_line():
        s = subprocess.check_output(
            ['kreadconfig', '--file', 'kdeglobals', '--group', 'General',
             '--key', 'TerminalApplication', '--default', 'konsole'])
        return ['nohup', s, '-e']

class GNOMETerminal(LinuxTerminal):
    """Handles terminals on GNOME (e.g. gnome-terminal)."""
    name = "GNOME"

    @staticmethod
    def detect():
        if os.environ.get('GNOME_DESKTOP_SESSION_ID', ''):
            return True
        FNULL = open(os.devnull, 'w')
        try:
            return subprocess.call(
                [
                    'dbus-send', '--print-reply', '--dest=org.freedesktop.DBus',
                    '/org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner',
                    'string:org.gnome.SessionManager'
                ], stdout=FNULL, stderr=FNULL) == 0
        except:
            return False
        finally:
            FNULL.close()

    @staticmethod
    def get_command_line():
        term = subprocess.check_output([
            'gconftool-2', '--get',
            '/desktop/gnome/applications/terminal/exec'])
        term_arg = subprocess.check_output([
            'gconftool-2', '--get',
            '/desktop/gnome/applications/terminal/exec_arg'])
        return ['nohup', term, term_arg]

class XfceTerminal(LinuxTerminal):
    """Handles terminals in the Xfce desktop environment."""
    name = "Xfce"

    @staticmethod
    def detect():
        try:
            s = subprocess.check_output(
                ['ps', '-eo', 'comm='], stderr=subprocess.STDOUT)
            return 'xfce' in s
        except:
            return False

    @staticmethod
    def get_command_line():
        return ['nohup', 'exo-open', '--launch', 'TerminalEmulator']

class LXDETerminal(LinuxTerminal):
    """Handles terminals in LXDE."""
    name = "LXDE"

    @staticmethod
    def detect():
        if not os.environ.get('DESKTOP_SESSION', '') == 'LXDE':
            return False
        FNULL = open(os.devnull, 'w')
        try:
            return subprocess.call(
                ['which', 'lxterminal'], stdout=FNULL, stderr=FNULL,
                close_fds=True) == 0
        except:
            return False
        finally:
            FNULL.close()

    @staticmethod
    def get_command_line():
        return ['nohup', 'lxterminal', '-e']

class MateTerminal(LinuxTerminal):
    """Handles the Mate desktop environment using mate-terminal."""
    name = "Mate"

    @staticmethod
    def detect():
        if os.environ.get('MATE_DESKTOP_SESSION_ID', ''):
            return True
        FNULL = open(os.devnull, 'w')
        try:
            return subprocess.call(
                [
                    'dbus-send', '--print-reply', '--dest=org.freedesktop.DBus',
                    '/org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner',
                    'string:org.mate.SessionManager'
                ], stdout=FNULL, stderr=FNULL) == 0
        except:
            return False
        finally:
            FNULL.close()
    @staticmethod
    def get_command_line():
        return ['nohup', 'mate-terminal', '-x']

class i3Terminal(LinuxTerminal):
    """Handles terminals in the i3 desktop environment."""
    name = "i3"

    @staticmethod
    def detect():
        return os.environ.get('DESKTOP_STARTUP_ID', '').startswith('i3/')

    @staticmethod
    def get_command_line():
        return ['nohup', 'i3-sensible-terminal', '-e']

# Generic terminals (rxvt, xterm, etc.)
class rxvtTerminal(LinuxTerminal):
    """Handles rxvt and urxvt terminals. urxvt is used if both are available."""
    name = "(u)rxvt"

    @staticmethod
    def detect():
        FNULL = open(os.devnull, 'w')
        try:
            if subprocess.call(
                    ['which', 'urxvt'], stdout=FNULL, stderr=FNULL) == 0:
                rxvtTerminal.exe = 'urxvt'
                return True
            if subprocess.call(
                    ['which', 'rxvt'], stdout=FNULL, stderr=FNULL) == 0:
                rxvtTerminal.exe = 'rxvt'
                return True
        except:
            return False
        finally:
            FNULL.close()

    @staticmethod
    def get_command_line():
        return ['nohup', rxvtTerminal.exe, '-e']

class xtermTerminal(LinuxTerminal):
    """Handles the xterm terminal."""
    name = "xterm"

    @staticmethod
    def detect():
        FNULL = open(os.devnull, 'w')
        try:
            return subprocess.call(
                ['which', 'xterm'], stdout=FNULL, stderr=FNULL,
                close_fds=True) == 0
        except:
            return False
        finally:
            FNULL.close()

    @staticmethod
    def get_command_line():
        return ['nohup', 'xterm', '-e']

class CustomTerminal(LinuxTerminal):
    """Allows custom terminal commands to handle missing cases."""
    name = "Custom command"

    @staticmethod
    def detect():
        # Custom commands are always an option
        return True

    @staticmethod
    def get_command_line():
        cmd = lnp.userconfig.get_string('terminal')
        if cmd:
            cmd = cmd.split(' ')
        return cmd

# pylint: enable=missing-docstring

#Terminal testing algorithm:
#    Main app, in thread:
#        Generate temporary file name for synchronization.
#        Write 0 to file.
#        Start parent w/ file name.
#        Wait for parent to terminate.
#        Report success if file contains 4 within 10 seconds, else report error.
#        Delete temporary file.
#
#    Parent:
#        If child process stops running, terminate.
#        Start child process.
#        Write 1 to file.
#        Ensure file contains 2 within 10 seconds.
#        Write 3 to file. Terminate self.
#
#    Child:
#        Ensure file contains 1 within 10 seconds.
#        Write 2 to file.
#        Ensure file contains 3 within 10 seconds.
#        Wait 3 seconds for parent to terminate.
#        Write 4 to file. Terminate self.

def _terminal_test_wait(fn, value):
    """
    Waits for file named <fn> to contain <value>.
    Returns True on success, False on timeout.
    """
    value = str(value)
    timer = 0
    interval = 0.5
    while timer < 10:
        time.sleep(interval)
        try:
            with open(fn, 'r') as f:
                if value == f.read().strip():
                    return True
        except:
            pass
        timer += interval
    return False

def _terminal_test_report(fn, value):
    """Writes a status value <value> to file named <fn>."""
    while True:
        try:
            with open(fn, 'w+b') as f:
                f.write(str(value))
            return
        except IOError:
            pass

def terminal_test_run(status_callback=None):
    """
    Starts and manages the test of terminal launching.
    Intermittent status messages may be received on function <status_callback>.
    Return value is (a, b), where a is a boolean marking the success of the test
    and b is a status text describing the result.
    """
    progress = {
        '0': 'Spawning parent process...',
        '1': 'Spawning child process...',
        '2': 'Waiting for parent to terminate...',
        '3': 'Waiting for child to terminate...',
        '4': 'Done!'
    }
    endmsg = {
        '0': 'Failed to start test.',
        '1': 'Parent process was blocked by child.',
        '2': 'Parent process died before child reported back.',
        '3': 'Child process was terminated along with parent.',
        '4': 'Success!'
    }

    log.d("Starting terminal test.")
    f = tempfile.NamedTemporaryFile(delete=False)
    t = f.name
    f.close()
    cmd = sys.argv[:] + ['--terminal-test-child', t]
    if sys.executable not in cmd:
        cmd.insert(0, sys.executable)
    cmd = get_terminal_command(cmd)
    p = subprocess.Popen(cmd)
    while not p.poll():
        with open(t, 'r') as f:
            value = f.read()
        try:
            status_callback(progress[value])
        except:
            pass
    timer = 0
    interval = 0.5
    while timer < 10:
        time.sleep(interval)
        try:
            with open(t, 'r') as f:
                if f.read().strip() == '4':
                    break
        except:
            pass
        timer += interval
    os.remove(t)
    return (value == '4', endmsg.get(value, 'Unknown error.'))

def terminal_test_parent(t):
    """Tests the parent side of terminal launching."""
    print("Terminal succesfully started! Test will begin in 3 seconds.")
    time.sleep(3)
    cmd = sys.argv[:-2] + ['--terminal-test-child', t]
    if sys.executable not in cmd:
        cmd.insert(0, sys.executable)
    cmd = get_terminal_command(cmd)
    print("Launching child process...")
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    _terminal_test_report(t, 1)
    if p.poll():
        return 1
    print("Waiting for child process to start...")
    if not _terminal_test_wait(t, 2):
        p.kill()
        return 2
    if p.poll():
        return 1
    print("Terminating parent process...")
    _terminal_test_report(t, 3)
    return 0

def terminal_test_child(t):
    """Tests the child side of terminal launching."""
    t = sys.argv[-1]
    print("Waiting for parent process to continue...")
    if not _terminal_test_wait(t, 1):
        return 1
    _terminal_test_report(t, 2)
    print("Waiting for parent process to terminate...")
    if not _terminal_test_wait(t, 3):
        return 1
    print("Test complete. Will terminate in 3 seconds.")
    time.sleep(3)
    _terminal_test_report(t, 4)
    return 0
