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
    __controls.clear()

def bind(control, option, update_func=None):
    """Binds a control to an option."""

    if option not in __controls:
        __controls[option] = []

    if update_func:
        value = (control, update_func)
    else:
        value = control
    __controls[option].append(value)

def version_has_option(field):
    o = field
    if hasattr(field, '__iter__'):
        o = field[0]
    return __lnp.settings.version_has_option(o)

def get(field):
    """
    Returns the value of the control known as <field>.
    If multiple controls are bound, the earliest binding is used.
    """
    return __controls[field][0].get()

def update():
    """Updates configuration displays (buttons, etc.)."""
    for key in __controls.keys():
        try:
            k = key
            if hasattr(key, '__iter__'):
                k = key[0]
            value = getattr(__lnp.settings, k)
        except KeyError:
            value = None
        for entry in __controls[key]:
            if hasattr(entry, '__iter__'):
                # Allow (control, func) tuples, etc. to customize value
                control = entry[0]
                value = entry[1](value)
            else:
                control = entry
            if isinstance(control, Entry):
                control.delete(0, END)
                control.insert(0, value)
            else:
                control["text"] = (
                    control["text"].split(':')[0] + ': ' +
                    str(value))

# vim:expandtab
