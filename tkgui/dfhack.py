#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""DFHack tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import binding, controls
from .tab import Tab
import sys

from core import hacks

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *

class DFHackTab(Tab):
    """DFHack tab for the TKinter GUI."""
    def create_variables(self):
        self.volume_var = StringVar()
        self.fps_var = StringVar()
        self.gps_var = StringVar()

    def read_data(self):
        self.update_hack_list()

    def create_controls(self):
        controls.create_trigger_option_button(
            self, 'Enable DFHack',
            'Controls whether DFHack should be enabled. Turning DFHack off '
            'also disables addons like TwbT.',
            self.toggle_dfhack, 'use_dfhack', lambda v: ('NO', 'YES')[
                hacks.is_dfhack_enabled()]).pack(
                    side=TOP, expand=N, fill=X, pady=4)

        hacks_frame = Labelframe(self, text='Available hacks')
        hacks_frame.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.columnconfigure(hacks_frame, 0, weight=1)
        Grid.rowconfigure(hacks_frame, 1, weight=1)

        Label(
            hacks_frame, text='Click on a hack to toggle it.').grid(
                column=0, row=0)

        self.hacklist = hacklist = controls.create_toggle_list(
            hacks_frame, ('name', 'enabled'),
            {'column': 0, 'row': 1, 'sticky': "nsew"},
            {'selectmode': 'browse'})
        hacklist.column('name', width=1, anchor='w')
        hacklist.column('enabled', width=50, anchor='c', stretch=NO)
        hacklist.heading('name', text='Hack')
        hacklist.heading('enabled', text='Enabled')
        hacklist.grid(column=0, row=0, sticky="nsew")
        hacklist.bind("<<TreeviewSelect>>", lambda e: self.toggle_hack())

        self.hack_tooltip = controls.create_tooltip(hacklist, '')
        hacklist.bind('<Motion>', self.update_hack_tooltip)

    def update_hack_tooltip(self, event):
        """
        Event handler for mouse motion over the hack list.
        Used to update the tooltip.
        """
        item = hacks.get_hack(self.hacklist.item(self.hacklist.identify(
            'row', event.x, event.y))['text'])
        if item:
            self.hack_tooltip.settext(item['tooltip'])
        else:
            self.hack_tooltip.settext('')

    def update_hack_list(self):
        """Updates the hack list."""
        for i in self.hacklist.get_children():
            self.hacklist.delete(i)
        for k, h in hacks.get_hacks().items():
            self.hacklist.insert('', 'end', text=k, values=(
                k, 'Yes' if h['enabled'] else 'No'))

    def toggle_hack(self):
        """Toggles the selected hack."""
        for item in self.hacklist.selection():
            hacks.toggle_hack(self.hacklist.item(item, 'text'))
        self.update_hack_list()

    @staticmethod
    def toggle_dfhack():
        """Toggles the use of DFHack."""
        hacks.toggle_dfhack()
        binding.update()
