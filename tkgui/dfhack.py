#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,attribute-defined-outside-init
"""DFHack tab for the TKinter GUI."""

import sys
from tkinter import *  # noqa: F403
from tkinter.ttk import *  # noqa: F403

from core import hacks

from . import binding, controls
from .layout import GridLayouter
from .tab import Tab


class DFHackTab(Tab):
    """DFHack tab for the TKinter GUI."""
    def read_data(self):
        self.update_hack_list()
        # Fix focus bug
        if self.hacklist.get_children():
            self.hacklist.focus(self.hacklist.get_children()[0])

    def create_controls(self):
        button_group = controls.create_control_group(self, None, True)
        button_group.pack(side=TOP, fill=BOTH, expand=N)
        grid = GridLayouter(2)
        grid.add(controls.create_trigger_option_button(
            button_group, 'Enable DFHack',
            'Controls whether DFHack should be enabled. Turning DFHack off '
            'also disables addons like TwbT.',
            self.toggle_dfhack, 'use_dfhack', lambda v: ('NO', 'YES')[
                hacks.is_dfhack_enabled()]))

        grid.add(controls.create_trigger_button(
            button_group, 'Open DFHack Readme',
            'Open the DFHack documentation in your browser.',
            hacks.open_dfhack_readme))

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

        def show():
            """Sets and shows a tooltip"""
            tooltip.settext(hacklist.set(item, 'tooltip'))
            tooltip.showtip()

        if tooltip.event:
            hacklist.after_cancel(tooltip.event)
            tooltip.event = None
        if hacklist.set(item, 'tooltip') != tooltip.text:
            tooltip.hidetip()
        if item:
            # pylint: disable=protected-access
            tooltip.event = hacklist.after(controls._TOOLTIP_DELAY, show)

    def update_hack_list(self):
        """Updates the hack list."""
        for hack in self.hacklist.get_children():
            self.hacklist.delete(hack)

        enabled = set(hacks.read_hacks())
        for title, hack in hacks.get_hacks().items():
            tags = ('enabled') if title in enabled else ()
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
            is_enabled = hacks.toggle_hack(title)
            # pylint: disable=not-callable
            self.hacklist.tag_set('enabled', item, is_enabled)
            # pylint: enable=not-callable

    @staticmethod
    def toggle_dfhack():
        """Toggles the use of DFHack."""
        hacks.toggle_dfhack()
        binding.update()
