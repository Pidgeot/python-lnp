#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Utilities tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls
from .tab import Tab
import sys

from core import launcher, paths, utilities
from core.lnp import lnp

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *

#pylint: disable=too-many-public-methods
class UtilitiesTab(Tab):
    """Utilities tab for the TKinter GUI."""
    def create_variables(self):
        self.progs = Variable()

    def read_data(self):
        self.read_utilities()

    def create_controls(self):
        progs = controls.create_control_group(
            self, 'Programs/Utilities', True)
        progs.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.rowconfigure(progs, 3, weight=1)

        controls.create_trigger_button(
            progs, 'Run Program', 'Runs the selected program(s).',
            self.run_selected_utilities).grid(column=0, row=0, sticky="nsew")
        controls.create_trigger_button(
            progs, 'Open Utilities Folder', 'Open the utilities folder',
            utilities.open_utils).grid(column=1, row=0, sticky="nsew")
        Label(
            progs, text='Double-click on a program to launch it.').grid(
                column=0, row=1, columnspan=2)
        Label(
            progs, text='Right-click on a program to toggle auto-launch.').grid(
                column=0, row=2, columnspan=2)

        self.proglist = proglist = controls.create_toggle_list(
            progs, ('exe', 'launch'),
            {'column': 0, 'row': 3, 'columnspan': 2, 'sticky': "nsew"})
        proglist.column('exe', width=1, anchor='w')
        proglist.column('launch', width=35, anchor='e', stretch=NO)
        proglist.heading('exe', text='Executable')
        proglist.heading('launch', text='Auto')
        proglist.bind("<Double-1>", lambda e: self.run_selected_utilities())
        if sys.platform == 'darwin':
            proglist.bind("<2>", self.toggle_autorun)
        else:
            proglist.bind("<3>", self.toggle_autorun)

        self.list_tooltip = controls.create_tooltip(proglist, '')
        proglist.bind('<Motion>', self.update_tooltip)

        refresh = controls.create_trigger_button(
            progs, 'Refresh List', 'Refresh the list of utilities',
            self.read_utilities)
        refresh.grid(column=0, row=4, columnspan=2, sticky="nsew")

    def update_tooltip(self, event):
        """
        Event handler for mouse motion over the utility list.
        Used to update the tooltip.
        """
        tip = utilities.get_tooltip(self.proglist.item(self.proglist.identify(
            'row', event.x, event.y))['text'])
        self.list_tooltip.settext(tip)

    def read_utilities(self):
        """Reads list of utilities."""
        self.progs = utilities.read_utilities()
        self.update_autorun_list()

    def toggle_autorun(self, event):
        """
        Toggles autorun for a utility.

        Params:
            event
                Data for the click event that triggered this.
        """
        utilities.toggle_autorun(self.proglist.item(self.proglist.identify(
            'row', event.x, event.y), 'text'))
        self.update_autorun_list()

    def update_autorun_list(self):
        """Updates the autorun list."""
        for i in self.proglist.get_children():
            self.proglist.delete(i)
        for p in self.progs:
            title = utilities.get_title(p)
            self.proglist.insert('', 'end', text=p, values=(
                title, 'Yes' if p in lnp.autorun else 'No'))

    def run_selected_utilities(self):
        """Runs selected utilities."""
        for item in self.proglist.selection():
            utility_path = self.proglist.item(item, 'text')
            launcher.run_program(paths.get('utilities', utility_path))

