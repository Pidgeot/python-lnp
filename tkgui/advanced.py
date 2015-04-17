#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Advanced tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls, binding
from .layout import GridLayouter
from .tab import Tab
import sys

from core import launcher, legends_processor
from core.lnp import lnp

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.messagebox as messagebox
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *
    import tkMessageBox as messagebox

#pylint: disable=too-many-public-methods
class AdvancedTab(Tab):
    """Advanced tab for the TKinter GUI."""
    def create_variables(self):
        self.volume_var = StringVar()
        self.fps_var = StringVar()
        self.gps_var = StringVar()
        self.winX_var = StringVar()
        self.winY_var = StringVar()
        self.fullX_var = StringVar()
        self.fullY_var = StringVar()

    def create_controls(self):
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        main_grid = GridLayouter(2)

        if lnp.settings.version_has_option('sound'):
            sound = controls.create_control_group(self, 'Sound')
            main_grid.add(sound)

            controls.create_option_button(
                sound, 'Sound', 'Turn game music on/off', 'sound').pack(
                    side=LEFT, fill=X, expand=Y)
            if lnp.settings.version_has_option('volume'):
                controls.create_numeric_entry(
                    sound, self.volume_var, 'volume',
                    'Music volume (0 to 255)').pack(side=LEFT, padx=(6, 0))
                Label(sound, text='/255').pack(side=LEFT)
        if lnp.settings.version_has_option('fpsCounter'):
            fps = controls.create_control_group(self, 'FPS')
            main_grid.add(fps, rowspan=2)

            controls.create_option_button(
                fps, 'FPS Counter', 'Whether or not to display your FPS',
                'fpsCounter').pack(fill=BOTH)
            if lnp.settings.version_has_option('fpsCap'):
                Label(fps, text='Calculation FPS Cap:').pack(anchor="w")
                controls.create_numeric_entry(
                    fps, self.fps_var, 'fpsCap', 'How fast the game runs').pack(
                        anchor="w")
            if lnp.settings.version_has_option('gpsCap'):
                Label(fps, text='Graphical FPS Cap:').pack(anchor="w")
                controls.create_numeric_entry(
                    fps, self.gps_var, 'gpsCap', 'How fast the game visually '
                    'updates.\nLower value may give small boost to FPS but '
                    'will be less reponsive.').pack(anchor="w")

        if lnp.settings.version_has_option('introMovie'):
            startup = controls.create_control_group(self, 'Startup')
            main_grid.add(startup)
            Grid.columnconfigure(startup, 0, weight=1)

            controls.create_option_button(
                startup, 'Intro Movie',
                'Do you want to see the beautiful ASCII intro movie?',
                'introMovie').grid(column=0, row=0, sticky="nsew")
            controls.create_option_button(
                startup, 'Windowed', 'Start windowed or fullscreen',
                'startWindowed').grid(column=0, row=1, sticky="nsew")

        resolution = controls.create_control_group(self, 'Resolution')
        main_grid.add(resolution, 2)
        resolution['pad'] = (4, 0, 4, 8)
        resolution.columnconfigure(5, weight=10)
        resolution.columnconfigure(0, weight=10)
        resolution.rowconfigure(2, minsize=3)

        Label(resolution, text='Windowed').grid(row=1, column=4, sticky='w')
        Label(resolution, text='Fullscreen').grid(row=3, column=4, sticky='w')
        Label(resolution, text='Width').grid(row=0, column=1)
        Label(resolution, text='Height').grid(row=0, column=3)
        Label(resolution, text='x').grid(row=1, column=2)
        Label(resolution, text='x').grid(row=3, column=2)
        controls.create_numeric_entry(
            resolution, self.winX_var, ('WINDOWEDX', 'GRAPHICS_WINDOWEDX'),
            'Horizontal resolution in windowed mode. Values <= 255 represent '
            'number of tiles, values > 255 represent number of pixels.') \
            .grid(row=1, column=1)
        controls.create_numeric_entry(
            resolution, self.winY_var, ('WINDOWEDY', 'GRAPHICS_WINDOWEDY'),
            'Vertical resolution in windowed mode. Values <= 255 represent '
            'number of tiles, values > 255 represent number of pixels.') \
            .grid(row=1, column=3)
        controls.create_numeric_entry(
            resolution, self.fullX_var, ('FULLSCREENX', 'GRAPHICS_FULLSCREENX'),
            'Horizontal resolution in fullscreen. Values <= 255 represent '
            'number of tiles, values > 255 represent number of pixels.') \
            .grid(row=3, column=1)
        controls.create_numeric_entry(
            resolution, self.fullY_var, ('FULLSCREENY', 'GRAPHICS_FULLSCREENY'),
            'Vertical resolution in fullscreen. Values <= 255 represent '
            'number of tiles, values > 255 represent number of pixels.') \
            .grid(row=3, column=3)

        saverelated = controls.create_control_group(
            self, 'Save-related', True)
        main_grid.add(saverelated, 2)

        grid = GridLayouter(2)
        grid.add(controls.create_option_button(
            saverelated, 'Autosave',
            'How often the game will automatically save', 'autoSave'))
        grid.add(controls.create_option_button(
            saverelated, 'Initial Save', 'Saves as soon as you embark',
            'initialSave'))
        grid.add(controls.create_option_button(
            saverelated, 'Pause on Save', 'Pauses the game after auto-saving',
            'autoSavePause'))
        grid.add(controls.create_option_button(
            saverelated, 'Pause on Load', 'Pauses the game as soon as it loads',
            'pauseOnLoad'))
        grid.add(controls.create_option_button(
            saverelated, 'Backup Saves', 'Makes a backup of every autosave',
            'autoBackup'))
        if lnp.df_info.version >= '0.31.01':
            grid.add(controls.create_option_button(
                saverelated, 'Compress Saves', 'Whether to compress the '
                'savegames (keep this on unless you experience problems with '
                'your saves', 'compressSaves'))
        grid.add(controls.create_trigger_button(
            saverelated, 'Open Savegame Folder', 'Open the savegame folder',
            launcher.open_savegames))

        main_grid.add(Frame(self, height=30), 2)
        main_grid.add(controls.create_option_button(
            self, 'Processor Priority',
            'Adjusts the priority given to Dwarf Fortress by your OS',
            'procPriority'), 2)

        main_grid.add(controls.create_trigger_option_button(
            self, 'Close GUI on launch',
            'Whether this GUI should close when Dwarf Fortress is launched',
            self.toggle_autoclose, 'autoClose', lambda v: ('NO', 'YES')[
                lnp.userconfig.get_bool('autoClose')]), 2)

        if lnp.df_info.version >= '0.40.09':
            main_grid.add(controls.create_trigger_button(
                self, 'Process Legends Exports',
                'Compress and sort files exported from legends mode',
                self.process_legends), 2)

    @staticmethod
    def process_legends():
        """Process legends exports."""
        if not legends_processor.get_region_info():
            messagebox.showinfo('No legends exports',
                                'There were no legends exports to process.')
        else:
            messagebox.showinfo('Exports will be compressed',
                                'Maps exported from legends mode will be '
                                'converted to .png format, a compressed archive'
                                ' will be made, and files will be sorted and '
                                'moved to a subfolder.  Please wait...')
            i = legends_processor.process_legends()
            string = str(i) + ' region'
            if i > 1:
                string += 's'
            messagebox.showinfo(string + ' processed',
                                'Legends exported from ' + string +
                                ' were found and processed')

    @staticmethod
    def toggle_autoclose():
        """Toggle automatic closing of the UI when launching DF."""
        launcher.toggle_autoclose()
        binding.update()

