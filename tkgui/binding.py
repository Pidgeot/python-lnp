#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Handles control binding for the TKinter GUI."""

from tkinter import END
from tkinter.ttk import Entry

__controls = {}
__lnp = None
__ui = None

def init(lnp, ui):
    """Connect to LNP and TkGui instances."""
    # pylint:disable=global-statement
    global __lnp, __ui
    __lnp = lnp
    __ui = ui
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
    """Returns True if the current DF version has the provided field."""
    o = field
    if not isinstance(field, str):
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
    def disabled_change_entry(*args, **kwargs):  #pylint: disable=unused-argument
        """Prevents entry change callbacks from being processed."""

    old_change_entry = __ui.change_entry
    __ui.change_entry = disabled_change_entry
    for key, option in __controls.items():
        try:
            k = key
            if not isinstance(k, str):
                k = key[0]
            value = getattr(__lnp.settings, k)
        except KeyError:
            value = ''
        for entry in option:
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
    __ui.change_entry = old_change_entry

# vim:expandtab
