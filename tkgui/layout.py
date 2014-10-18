#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Layout helpers for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls

class GridLayouter(object):
    """Class to automate grid layouts."""
    def __init__(self, cols):
        """
        Constructor for GridLayouter.

        Params:
            cols
                Number of columns for the grid.
        """
        self.cols = cols
        self.controls = []
        self.used = []

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
        for i, c in enumerate(self.controls):
            while True:
                row = cells_used // self.cols
                col = cells_used % self.cols
                if (row, col) not in self.used:
                    break
                cells_used += 1
            c[0].grid(
                row=row, column=col, sticky="nsew", columnspan=c[1], **c[2])
            if 'rowspan' in c[2]:
                for n in range(1, c[2]['rowspan']+1):
                    self.used.append((row+n, col))
            cells_used += c[1]
            if i == len(self.controls) - 1 and col != self.cols - 1:
                colspan = self.cols - col
                for n in range(col + 1, self.cols):
                    if (row, n) in self.used:
                        colspan = n - col
                        break
                c[0].grid(columnspan=colspan)
