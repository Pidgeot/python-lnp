#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""DFHack tab for the TKinter GUI."""
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

from . import binding, controls
from .tab import Tab

from core import hacks

# pylint:disable=too-many-public-methods
class DFHackTab(Tab):
    """DFHack tab for the TKinter GUI."""
    def read_data(self):
        self.update_hack_list()
        # Fix focus bug
        if self.hacklist.get_children():
            self.hacklist.focus(self.hacklist.get_children()[0])

    def create_controls(self):
        controls.create_trigger_option_button(
            self, 'Enable DFHack',
            'Controls whether DFHack should be enabled. Turning DFHack off '
            'also disables addons like TwbT.',
            self.toggle_dfhack, 'use_dfhack', lambda v: ('NO', 'YES')[
                hacks.is_dfhack_enabled()]).pack(
                    side=TOP, expand=N, fill=X, pady=4)

        controls.create_trigger_button(
            self,
            'Open DFHack Readme',
            'Open the DFHack documentation in your browser.',
            hacks.open_dfhack_readme
            ).pack(side=TOP, expand=N, fill=X, pady=4)

        hacks_frame = controls.create_control_group(self, 'Available hacks')
        hacks_frame.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.columnconfigure(hacks_frame, 0, weight=1)
        Grid.rowconfigure(hacks_frame, 1, weight=1)

        Label(
            hacks_frame, text='Click on a hack to toggle it.').grid(
                column=0, row=0)

        self.hacklist = controls.create_toggle_list(hacks_frame, ('tooltip'), {
            'column': 0, 'row': 1, 'sticky': "nsew"})
        self.hacklist.grid(column=0, row=0, sticky="nsew")
        self.configure_hacklist()

    def configure_hacklist(self):
        """Configures the treeview."""
        hacklist = self.hacklist

        # Do not show headings
        hacklist.configure(show=['tree'], displaycolumns=(), selectmode="none")

        for seq in ("<space>", "<Return>", "<1>",
                    "<2>" if sys.platform == 'darwin' else "<3>"):
            hacklist.bind(seq, self.toggle_hack)

        self.hack_tooltip = controls.create_tooltip(hacklist, '')
        hacklist.bind('<Motion>', self.update_hack_tooltip)

        # Make it easy to differentiate between enabled
        hacklist.tag_configure('enabled', background='pale green')

    def update_hack_tooltip(self, event):
        """
        Event handler for mouse motion over items in the hack list.

        If the mouse has moved out of the last list element, hides the tooltip.
        Then, if the mouse is over a list item, wait controls._TOOLTIP_DELAY
        milliseconds (without mouse movement) before showing the tooltip"""
        tooltip = self.hack_tooltip
        hacklist = self.hacklist
        item = hacklist.identify_row(event.y)

        def show(): # pylint:disable=missing-docstring
            tooltip.settext(hacklist.set(item, 'tooltip'))
            tooltip.showtip()

        if tooltip.event:
            hacklist.after_cancel(tooltip.event)
            tooltip.event = None
        if hacklist.set(item, 'tooltip') != tooltip.text:
            tooltip.hidetip()
        if item:
            tooltip.event = hacklist.after(controls._TOOLTIP_DELAY, show)

    def update_hack_list(self):
        """Updates the hack list."""
        for hack in self.hacklist.get_children():
            self.hacklist.delete(hack)

        for title, hack in hacks.get_hacks().items():
            tags = ('enabled') if hack.get('enabled') else ()
            self.hacklist.insert('', 'end', text=title, tags=tags,
                                 values=(hack['tooltip'],))

    def toggle_hack(self, event):
        """Toggles the selected hack."""
        if event.keysym == '??':
            item = self.hacklist.identify_row(event.y)
        else:
            item = self.hacklist.focus()

        if item:
            title = self.hacklist.item(item, 'text')
            hacks.toggle_hack(title)
            self.hacklist.tag_set('enabled', item,
                                  hacks.get_hack(title).get('enabled'))

    @staticmethod
    def toggle_dfhack():
        """Toggles the use of DFHack."""
        hacks.toggle_dfhack()
        binding.update()
