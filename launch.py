#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is used to launch the program."""
from __future__ import absolute_import, print_function
import sys, os
from core import lnp
sys.path.insert(0, os.path.dirname(__file__))
#pylint: disable=redefined-builtin, bare-except
__package__ = ""

try:
    lnp.PyLNP()
except:
    import traceback
    message = traceback.format_exception(*sys.exc_info())
    #Log exception to stderr if possible
    try:
        print(message, file=sys.stderr)
    except:
        pass

    # Also show error in Tkinter message box if possible
    try:
        if sys.version_info[0] == 3:  # Alternate import names
            # pylint:disable=import-error
            import tkinter.messagebox as messagebox
        else:
            # pylint:disable=import-error
            import tkMessageBox as messagebox
        messagebox.showerror(message=message)
    except:
        pass
