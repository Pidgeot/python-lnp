#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from distutils.core import setup

mainscript = 'lnp.py'

#If PIL or similar is available on this system, it will be available for the generated executable.
#Since this is the only factor in whether or not we will be able to use non-GIF images, we only include the appropriate version.
try:
  from PIL import Image, ImageTk, PngImagePlugin
  has_PIL = True
  print("Note: Found PIL package")
except ImportError: #Some PIL installations live outside of the PIL package
  try:
    import Image, ImageTk, PngImagePlugin
    has_PIL = True
    print("Note: Found PIL support outside of package")
  except ImportError: #No PIL compatible library
    has_PIL = False
    print("Note: PIL not found")

if sys.hexversion < 0x3000000: #Python 2
  from Tkinter import *
else: #Python 3
  from tkinter import *

if has_PIL or TkVersion >= 8.6:
  logo='LNPSMALL.png'
  icon='LNP.png'
else:
  logo='LNPSMALL.gif'
  icon='LNP.gif'

if sys.platform == 'linux2':
  print("setup.py-based building is not supported on Linux. Use PyInstaller instead.")
  sys.exit()
elif sys.platform == 'darwin':
  import py2app
  extra_options = dict(app=[mainscript],options=dict(py2app=dict(resources=[logo],iconfile='LNP.icns')))
elif sys.platform == 'win32':
  import py2exe
  #We don't want a lot of files cluttering everything, but Tcl and Tk require their DLLs in the directory.
  #Unfortunately, py2exe doesn't know that. Therefore, we patch it to include these automatically.
  py2exe.build_exe.py2exe.old_prepare = py2exe.build_exe.py2exe.plat_prepare
  def new_prep(self):
    self.old_prepare()
    # Rather than hard-coding to specific versions, we retrieve the ones used by Python.
    from _tkinter import TK_VERSION, TCL_VERSION
    self.dlls_in_exedir.append('tcl{0}.dll'.format(TCL_VERSION.replace('.','')))
    self.dlls_in_exedir.append('tk{0}.dll'.format(TK_VERSION.replace('.','')))
  py2exe.build_exe.py2exe.plat_prepare = new_prep
  extra_options = dict(windows=[{'script':mainscript, "icon_resources":[(1, "LNP.ico")]}], data_files=[('.',['LNP.ico',logo])], options=dict(py2exe=dict(bundle_files=1,dll_excludes=['w9xpopen.exe'])), zipfile=None)
else:
  extra_options = dict(scripts=[mainscript])

setup(
  name="PyLNP",
  **extra_options
)

# vim:expandtab
