#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name
"""Base class for notebook tabs for the TKinter GUI."""

from tkinter import BOTH, TOP, Y
from tkinter.ttk import Frame

#pylint: disable=unused-argument
class Tab(Frame):
    """Base class for notebook tabs for the TKinter GUI."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.pack(side=TOP, fill=BOTH, expand=Y)
        self.create_variables()
        self.create_controls()
        self.read_data()

    def create_variables(self):
        """
        Creates all TKinter variables needed by this tab.
        Overridden in child classes.
        """

    def read_data(self):
        """Reads all external data needed. Overridden in child classes."""

    def create_controls(self):
        """Creates all controls for this tab. Overriden in child classes."""
