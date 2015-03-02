#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name
"""Base class for notebook tabs for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

import sys

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import TOP, BOTH, Y
    from tkinter.ttk import Frame
else:
    # pylint:disable=import-error
    from Tkinter import TOP, BOTH, Y
    from ttk import Frame

#pylint: disable=too-many-public-methods
class Tab(Frame):
    """Base class for notebook tabs for the TKinter GUI."""
    def __init__(self, parent):
        #pylint:disable=super-init-not-called
        Frame.__init__(self, parent)
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
        pass

    def read_data(self):
        """Reads all external data needed. Overridden in child classes."""
        pass

    def create_controls(self):
        """Creates all controls for this tab. Overriden in child classes."""
        pass


