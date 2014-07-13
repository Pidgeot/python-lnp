#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from distutils.core import setup

mainscript = 'lnp.py'

#If PIL or similar is available on this system, it will be available for the
#generated executable. Since this is the only factor in whether or not we will
#be able to use non-GIF images, we only include the appropriate version.
try:
    #pylint:disable=import-error,no-name-in-module
    from PIL import Image, ImageTk, PngImagePlugin
    has_PIL = True
    print("Note: Found PIL package")
except ImportError: #Some PIL installations live outside of the PIL package
    #pylint:disable=import-error,no-name-in-module
    try:
        import Image, ImageTk, PngImagePlugin
        has_PIL = True
        print("Note: Found PIL support outside of package")
    except ImportError: #No PIL compatible library
        has_PIL = False
        print("Note: PIL not found")

if sys.hexversion < 0x3000000: #Python 2
    #pylint:disable=import-error,wildcard-import,unused-wildcard-import
    from Tkinter import *
else: #Python 3
    #pylint:disable=import-error,wildcard-import,unused-wildcard-import
    from tkinter import *

if has_PIL or TkVersion >= 8.6:
    logo = 'LNPSMALL.png'
    icon = 'LNP.png'
else:
    logo = 'LNPSMALL.gif'
    icon = 'LNP.gif'

if sys.platform in ('linux2', 'win32'):
    print(
        "setup.py-based building is only supported on OS X. "
        "Use PyInstaller instead.")
    sys.exit()
elif sys.platform == 'darwin':
    import py2app
    extra_options = dict(
        app=[mainscript], options=dict(py2app=dict(
            resources=[logo], iconfile='LNP.icns')))
else:
    extra_options = dict(scripts=[mainscript])

setup(
    name="PyLNP",
    **extra_options
)

# vim:expandtab
