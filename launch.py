#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is used to launch the program."""

import os
import sys

from core import lnp

sys.path.insert(0, os.path.dirname(__file__))
# pylint: disable=redefined-builtin
__package__ = ""

try:
    lnp.PyLNP()
except SystemExit:
    raise
except Exception:
    import traceback
    message = ''.join(traceback.format_exception(*sys.exc_info()))
    # Log exception to stderr if possible
    try:
        print(message, file=sys.stderr)
    except Exception:
        pass

    # Also show error in Tkinter message box if possible
    try:
        from tkinter import messagebox
        messagebox.showerror(message=message)
    except Exception:
        pass
