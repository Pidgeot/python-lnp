#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=invalid-name
"""Handles control binding for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

import sys

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import END
    from tkinter.ttk import Entry
else:
    # pylint:disable=import-error
    from Tkinter import END
    from ttk import Entry

__controls = dict()
__lnp = None

def init(lnp):
    """Connect to an LNP instance."""
    # pylint:disable=global-statement
    global __lnp
    __lnp = lnp

def bind(control, option, update_func=None):
    """Binds a control to an option."""

    if update_func:
        __controls[option] = (control, update_func)
    else:
        __controls[option] = control

def get(field):
    """Returns the value of the control known as <field>."""
    return __controls[field].get()

def update():
    """Updates configuration displays (buttons, etc.)."""
    for key in __controls.keys():
        try:
            value = getattr(__lnp.settings, key)
        except KeyError:
            value = None
        if hasattr(__controls[key], '__iter__'):
            # Allow (control, func) tuples, etc. to customize value
            control = __controls[key][0]
            value = __controls[key][1](value)
        else:
            control = __controls[key]
        if isinstance(control, Entry):
            control.delete(0, END)
            control.insert(0, value)
        else:
            control["text"] = (
                control["text"].split(':')[0] + ': ' +
                str(value))

# vim:expandtab
