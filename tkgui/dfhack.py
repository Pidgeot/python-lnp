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

#pylint: disable=too-many-public-methods
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

        hacks_frame = Labelframe(self, text='Available hacks')
        hacks_frame.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.columnconfigure(hacks_frame, 0, weight=1)
        Grid.rowconfigure(hacks_frame, 1, weight=1)

        Label(
            hacks_frame, text='Click on a hack to toggle it.').grid(
                column=0, row=0)

        self.hacklist = controls.create_toggle_list(hacks_frame, ('tooltip'),
            {'column': 0, 'row': 1, 'sticky': "nsew"})
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
        Event handler for mouse motion over items in the utility list.

        Hides the tooltip and then wait controls._TOOLTIP_DELAY milliseconds
        (without this event being called) before showing the tooltip"""
        tooltip = self.hack_tooltip
        hacklist = self.hacklist

        if tooltip.event:
            tooltip.hidetip()
            hacklist.after_cancel(tooltip.event)

        item = hacklist.identify_row(event.y)
        if item:
            tooltip.settext(hacklist.set(item, 'tooltip'))
            tooltip.event = hacklist.after(controls._TOOLTIP_DELAY,
                                           tooltip.showtip)

    def update_hack_list(self):
        """Updates the hack list."""
        for hack in self.hacklist.get_children():
            self.hacklist.delete(hack)

        for title, hack in hacks.get_hacks().items():
            tags = ('enabled') if hack['enabled'] else ()
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
            self.tag_set(item, 'enabled', hacks.get_hack(title)['enabled'])

    def tag_set(self, item, tag, state=True, toggle=False):
        """
        Adds or removes a tag from the Treeview item's tags. Returns True if
        tag is now set or False if it is not.

        Params:
            item
                Treeview item id
            state
                True to set the tag; False to remove the tag.
            toggle
                If set to True, will toggle the tag. Overrides on.
        """
        tags = list(self.hacklist.item(item, 'tags'))
        is_set = tag in tags
        if toggle:
            state = not is_set

        if state and (not is_set):
            tags.append(tag)
        elif (not state) and is_set:
            tags.remove(tag)

        self.hacklist.item(item, tags=tags)
        return state

    @staticmethod
    def toggle_dfhack():
        """Toggles the use of DFHack."""
        hacks.toggle_dfhack()
        binding.update()
