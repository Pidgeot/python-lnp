#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Advanced tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls, binding
from .tab import Tab
import sys

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *

class AdvancedTab(Tab):
    """Advanced tab for the TKinter GUI."""
    def create_variables(self):
        self.volume_var = StringVar()
        self.fps_var = StringVar()
        self.gps_var = StringVar()

    def create_controls(self):
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        sound = controls.create_control_group(self, 'Sound')
        sound.grid(column=0, row=0, sticky="nsew")

        controls.create_option_button(
            sound, 'Sound', 'Turn game music on/off', 'sound').pack(side=LEFT)
        controls.create_numeric_entry(
            sound, self.volume_var, 'volume', 'Music volume (0 to 255)').pack(
                side=LEFT)
        Label(sound, text='/255').pack(side=LEFT)

        fps = controls.create_control_group(self, 'FPS')
        fps.grid(column=1, row=0, rowspan=2, sticky="nsew")

        controls.create_option_button(
            fps, 'FPS Counter', 'Whether or not to display your FPS',
            'fpsCounter').pack(fill=BOTH)
        Label(fps, text='Calculation FPS Cap:').pack(anchor="w")
        controls.create_numeric_entry(
            fps, self.fps_var, 'fpsCap', 'How fast the game runs').pack(
                anchor="w")
        Label(fps, text='Graphical FPS Cap:').pack(anchor="w")
        controls.create_numeric_entry(
            fps, self.gps_var, 'gpsCap', 'How fast the game visually updates.\n'
            'Lower value may give small boost to FPS but will be less '
            'reponsive.').pack(anchor="w")

        startup = controls.create_control_group(self, 'Startup')
        startup.grid(column=0, row=1, sticky="nsew")
        Grid.columnconfigure(startup, 0, weight=1)

        controls.create_option_button(
            startup, 'Intro Movie',
            'Do you want to see the beautiful ASCII intro movie?',
            'introMovie').grid(column=0, row=0, sticky="nsew")
        controls.create_option_button(
            startup, 'Windowed', 'Start windowed or fullscreen',
            'startWindowed').grid(column=0, row=1, sticky="nsew")

        saverelated = controls.create_control_group(
            self, 'Save-related', True)
        saverelated.grid(column=0, row=2, columnspan=2, sticky="nsew")

        controls.create_option_button(
            saverelated, 'Autosave',
            'How often the game will automatically save', 'autoSave').grid(
                column=0, row=0, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Initial Save', 'Saves as soon as you embark',
            'initialSave').grid(column=1, row=0, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Pause on Save', 'Pauses the game after auto-saving',
            'autoSavePause').grid(column=0, row=1, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Pause on Load', 'Pauses the game as soon as it loads',
            'pauseOnLoad').grid(column=1, row=1, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Backup Saves', 'Makes a backup of every autosave',
            'autoBackup').grid(column=0, row=2, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Compress Saves', 'Whether to compress the savegames '
            '(keep this on unless you experience problems with your saves',
            'compressSaves').grid(column=1, row=2, sticky="nsew")
        controls.create_trigger_button(
            saverelated, 'Open Savegame Folder', 'Open the savegame folder',
            self.lnp.open_savegames).grid(
                column=0, row=3, columnspan=2, sticky="nsew")

        Frame(self, height=30).grid(column=0, row=3)
        controls.create_option_button(
            self, 'Processor Priority',
            'Adjusts the priority given to Dwarf Fortress by your OS',
            'procPriority').grid(column=0, row=4, columnspan=2, sticky="nsew")

        controls.create_trigger_option_button(
            self, 'Close GUI on launch',
            'Whether this GUI should close when Dwarf Fortress is launched',
            self.toggle_autoclose, 'autoClose', lambda v: ('NO', 'YES')[
                self.lnp.userconfig.get_bool('autoClose')]).grid(
                    column=0, row=5, columnspan=2, sticky="nsew")

    def toggle_autoclose(self):
        """Toggle automatic closing of the UI when launching DF."""
        self.lnp.toggle_autoclose()
        binding.update()

