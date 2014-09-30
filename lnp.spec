# -*- mode: python -*-
# If PIL or similar is available on this system, it will be available for the
# generated executable. Since this is the only factor in whether or not we
# will be able to use non-GIF images, we only include the appropriate version.
try:
    from PIL import Image, ImageTk
    has_PIL = True
except ImportError: # Some PIL installations live outside of the PIL package
    try:
        import Image, ImageTk
        has_PIL = True
    except ImportError: #No PIL compatible library
        has_PIL = False

if sys.hexversion < 0x3000000: # Python 2
    from Tkinter import *
else: # Python 3
    from tkinter import *

if has_PIL or TkVersion >= 8.6:
    logo='LNPSMALL.png'
    icon='LNP.png'
else:
    logo='LNPSMALL.gif'
    icon='LNP.gif'

extension=''
script='lnp.py'
if sys.platform == 'win32':
    icon='LNP.ico'
    extension='.exe'
    script='launch.pyw'

a = Analysis(
  [script], pathex=['.'], hiddenimports=[], hookspath=None, runtime_hooks=None)
a.datas+=[(logo,logo,'DATA'),(icon,icon,'DATA')]
if sys.platform == 'win32':
    # Importing pkg_resources fails with Pillow on Windows due to
    # unnormalized case; this works around the problem
    a.datas = list({tuple(map(str.upper, t)) for t in a.datas})
if sys.platform.startswith('linux'):
    a.datas += [('xdg-terminal','xdg-terminal','DATA')]
pyz = PYZ(a.pure)
if sys.platform != 'darwin':
    exe = EXE(
        pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='PyLNP'+extension,
        debug=False, strip=None, upx=True, console=False, icon='LNP.ico')
else:
    exe = EXE(
        pyz, a.scripts, exclude_binaries=True, name='PyLNP'+extension,
        debug=False, strip=None, upx=True, console=False)
    coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=None, upx=True, name='PyLNP')
    app = BUNDLE(coll,name='PyLNP.app',icon='LNP.icns')

# vim:expandtab
