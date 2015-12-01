#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Utilities tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

import sys

# pylint:disable=wrong-import-order
if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *
# pylint:enable=wrong-import-order

from . import controls
from .tab import Tab

from core import launcher, paths, utilities
from core.lnp import lnp


#pylint: disable=too-many-public-methods
class UtilitiesTab(Tab):
    """Utilities tab for the TKinter GUI."""
    def read_data(self):
        self.read_utilities()

        # Fix focus bug
        if self.proglist.get_children():
            self.proglist.focus(self.proglist.get_children()[0])

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

        self.proglist = controls.create_toggle_list(
            progs, ('path', 'tooltip'), {
                'column': 0, 'row': 3, 'columnspan': 2, 'sticky': "nsew"})
        self.configure_proglist()

        refresh = controls.create_trigger_button(
            progs, 'Refresh List', 'Refresh the list of utilities',
            self.read_utilities)
        refresh.grid(column=0, row=4, columnspan=2, sticky="nsew")

    def configure_proglist(self):
        """Configures the treeview."""
        proglist = self.proglist

        # Do not show headings
        proglist.configure(show=['tree'], displaycolumns=())

        for seq in ("<Double-1>", "<Return>"):
            proglist.bind(seq, lambda e: self.run_selected_utilities())

        for seq in ("<space>", "<2>" if sys.platform == 'darwin' else "<3>",):
            proglist.bind(seq, self.toggle_autorun)

        self.list_tooltip = controls.create_tooltip(proglist, '')
        proglist.bind('<Motion>', self.update_tooltip)

        # Make it easy to differentiate between autorun
        proglist.tag_configure('autorun', background='pale green')

        # Deselect everything if blank area is clicked
        proglist.bind("<1>", self.proglist_click)

    def proglist_click(self, event):
        """Deselect everything if event occured in blank area area"""
        region = self.proglist.identify_region(event.x, event.y)
        if region == 'nothing':
            self.proglist.selection_set('')

    def update_tooltip(self, event):
        """
        Event handler for mouse motion over items in the utility list.

        If the mouse has moved out of the last list element, hides the tooltip.
        Then, if the mouse is over a list item, wait controls._TOOLTIP_DELAY
        milliseconds (without mouse movement) before showing the tooltip"""
        tooltip = self.list_tooltip
        proglist = self.proglist
        item = proglist.identify_row(event.y)

        def show(): # pylint:disable=missing-docstring
            tooltip.settext(proglist.set(item, 'tooltip'))
            tooltip.showtip()

        if tooltip.event:
            proglist.after_cancel(tooltip.event)
            tooltip.event = None
        if proglist.set(item, 'tooltip') != tooltip.text:
            tooltip.hidetip()
        if item:
            tooltip.event = proglist.after(controls._TOOLTIP_DELAY, show)

    def read_utilities(self):
        """Reads list of utilities."""
        for prog in self.proglist.get_children():
            self.proglist.delete(prog)

        for prog in utilities.read_utilities():
            self.proglist.insert('', 'end', prog,
                                 text=utilities.get_title(prog),
                                 values=(prog, utilities.get_tooltip(prog)))
        self.update_autorun_list()

    def toggle_autorun(self, event):
        """
        Toggles autorun for a utility.

        Params:
            event
                Data for the click event that triggered this.
        """
        if event.keysym == '??':
            item = self.proglist.identify_row(event.y)
        else:
            item = self.proglist.focus()

        if item:
            utilities.toggle_autorun(item)
            self.proglist.tag_set('autorun', item, item in lnp.autorun)

    def update_autorun_list(self):
        """Updates the autorun list."""
        for item in self.proglist.get_children():
            self.proglist.tag_set('autorun', item, item in lnp.autorun)

    def run_selected_utilities(self):
        """Runs selected utilities."""
        for item in self.proglist.selection():
            #utility_path = self.proglist.item(item, 'text')
            launcher.run_program(paths.get('utilities', item))

