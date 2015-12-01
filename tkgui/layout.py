#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Layout helpers for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls

class GridLayouter(object):
    """Class to automate grid layouts."""
    def __init__(self, cols, pad=(0, 0)):
        """
        Constructor for GridLayouter.

        Params:
            cols
                Number of columns for the grid.
            pad
                The amount (x, y) of padding between elements
        """
        self.cols = cols
        self.controls = []
        self.used = []
        try:
            self.pad = (int(pad), int(pad))
        except TypeError: # not an int; assume tuple
            self.pad = pad

    def add(self, control, span=1, **opts):
        """
        Adds a control to the grid.

        Params:
            control
                The control to add.
            span
                The number of columns to span (defaults to 1).
            opts
                Extra options for the grid layout.
        """
        if control is controls.fake_control:
            return
        self.controls.append((control, span, opts))
        self.layout()

    def layout(self):
        """Applies layout to the added controls."""
        cells_used = 0
        max_index = len(self.controls) - 1
        for i, c in enumerate(self.controls):
            c = list(c)
            while True:
                row = cells_used // self.cols
                col = cells_used % self.cols
                if (row, col) not in self.used:
                    break
                cells_used += 1

            padx = 0 if col == 0 else (self.pad[0], 0)
            pady = 0 if row == 0 else (self.pad[1], 0)

            if ((i == max_index and col != self.cols - 1) or (
                    i < max_index and
                    col + c[1] + self.controls[i+1][1] > self.cols)):
                # Pad colspan if last control, or next control won't fit
                colspan = self.cols - col
                for n in range(col + 1, self.cols):
                    if (row, n) in self.used:
                        colspan = n - col
                        break
                c[1] = colspan

            c[0].grid(
                row=row, column=col, sticky="nsew", columnspan=c[1], padx=padx,
                pady=pady, **c[2])
            if 'rowspan' in c[2]:
                for n in range(1, c[2]['rowspan']+1):
                    self.used.append((row+n, col))
            cells_used += c[1]
