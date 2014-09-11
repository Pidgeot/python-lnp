#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""DFHack tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls
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

class DFHackTab(Tab):
    """DFHack tab for the TKinter GUI."""
    def create_variables(self):
        self.volume_var = StringVar()
        self.fps_var = StringVar()
        self.gps_var = StringVar()

    def on_post_df_load(self):
        self.update_hack_list()

    def create_controls(self):
        hacks = Labelframe(self, text='Available hacks')
        hacks.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.columnconfigure(hacks, 0, weight=1)
        Grid.rowconfigure(hacks, 1, weight=1)

        Label(
            hacks, text='Click on a hack to toggle it.').grid(
                column=0, row=0)

        self.hacklist = hacklist = controls.create_toggle_list(
            hacks, ('name', 'enabled'),
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
        item = self.lnp.get_hack(self.hacklist.item(self.hacklist.identify(
            'row', event.x, event.y))['text'])
        if item:
            self.hack_tooltip.settext(item['tooltip'])
        else:
            self.hack_tooltip.settext('')

    def update_hack_list(self):
        """Updates the hack list."""
        for i in self.hacklist.get_children():
            self.hacklist.delete(i)
        for k, h in self.lnp.get_hacks().items():
            self.hacklist.insert('', 'end', text=k, values=(
                k, 'Yes' if h['enabled'] else 'No'))

    def toggle_hack(self):
        """Toggles the selected hack."""
        for item in self.hacklist.selection():
            self.lnp.toggle_hack(self.hacklist.item(item, 'text'))
        self.update_hack_list()


