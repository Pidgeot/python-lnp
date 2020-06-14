# -*- mode: python -*-
# If PIL or similar is available on this system, it will be available for the
# generated executable. Since this is the only factor in whether or not we
# will be able to use non-GIF images, we only include the appropriate version.
import sys

if sys.platform == 'win32':
    try:
      from PyInstaller.utils.winmanifest import Manifest
    except ImportError:
      # Newer PyInstaller versions
      from PyInstaller.utils.win32.winmanifest import Manifest
    Manifest.old_toprettyxml = Manifest.toprettyxml
    def new_toprettyxml(self, indent="  ", newl=os.linesep, encoding="UTF-8"):
      s = self.old_toprettyxml(indent, newl, encoding)
      # Make sure we only modify our own manifest
      if 'name="lnp"' in s:
        d = indent + '<asmv3:application xmlns:asmv3="urn:schemas-microsoft-com:asm.v3"><windowsSettings xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings"><dpiAware>false</dpiAware></windowsSettings></asmv3:application>' + newl
        s = s.replace('</assembly>',d+'</assembly>')
      return s
    Manifest.toprettyxml = new_toprettyxml

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
script='launch.py'
if sys.platform == 'win32':
    icon='LNP.ico'
    extension='.exe'

hiddenimports = []
if sys.platform.startswith('linux'):
    hiddenimports = ['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder']

needs_tcl_copy = False

if sys.platform == 'darwin' and sys.hexversion >= 0x3070000:
    needs_tcl_copy = True
    try:
      # HACK: PyInstaller is not handling the bundled Tcl and Tk in Python 3.7 from python.org properly.
      # This patch intercepts the value that causes PyInstaller to attempt to use the wrong Tcl/Tk version
      # and triggers a fallback to treat Tcl/Tk as a Unix-style build.
      # See https://github.com/pyinstaller/pyinstaller/issues/3753 for the relevant bug report for PyInstaller
      from PyInstaller.depend import bindepend
      old_selectImports = bindepend.selectImports
      def patched_selectImports(pth, xtrapath=None):
          rv = old_selectImports(pth, xtrapath)
          if '_tkinter' in pth:
              import inspect
              caller = inspect.stack()[1]
              if 'hook-_tkinter.py' in caller.filename and 'Library/Frameworks' in rv[0][1] and 'Python' in rv[0][1]:
                  return [('libtcl8.6.dylib', ''), ('libtk8.6.dylib','')]
          return rv
      bindepend.selectImports = patched_selectImports
    except ImportError:
      pass

a = Analysis(
  [script], pathex=['.'], hiddenimports=hiddenimports, hookspath=None, runtime_hooks=None)
a.datas+=[(logo,logo,'DATA'),(icon,icon,'DATA')]
if sys.platform == 'win32':
    # Importing pkg_resources fails with Pillow on Windows due to
    # unnormalized case; this works around the problem
    a.datas = list({tuple(map(str.upper, t)) for t in a.datas})
pyz = PYZ(a.pure)
if sys.platform != 'darwin':
    exe = EXE(
        pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='PyLNP'+extension,
        debug=False, strip=None, upx=False, console=False, icon='LNP.ico')
else:
    info = {'NSHighResolutionCapable': 'True'}
    exe = EXE(
        pyz, a.scripts, exclude_binaries=True, name='PyLNP'+extension,
        debug=False, strip=None, upx=True, console=False)
    coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=None, upx=True, name='PyLNP')
    app = BUNDLE(coll,name='PyLNP.app',icon='LNP.icns', info_plist=info)
    if needs_tcl_copy:
        import shutil
        import os
        def copytree(src, dst, symlinks=False, ignore=None):
            if not os.path.exists(dst):
                os.makedirs(dst)
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    copytree(s, d, symlinks, ignore)
                else:
                    if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                        shutil.copy2(s, d)

        # Manually copy tcl/tk files into .app - based on copy commands mentioned here:
        # https://github.com/pyinstaller/pyinstaller/issues/3753#issuecomment-432464838
        # https://stackoverflow.com/questions/56092383/how-to-fix-msgcatmc-error-after-running-app-from-pyinstaller-on-macos-mojave
        basepath = os.path.normpath(os.path.join(os.path.dirname(sys.executable), '..', 'lib'))
        for e in os.listdir(basepath):
            p = os.path.join(basepath, e)
            if not os.path.isdir(p):
                continue
            if e == 'tcl8':
                dst = os.path.abspath(os.path.join(app.name, 'Contents', 'MacOS', 'tcl8'))
            elif e.startswith('tcl'):
                dst = os.path.abspath(os.path.join(app.name, 'Contents', 'MacOS', 'tcl'))
            elif e.startswith('tk') or e.startswith('Tk'):
                dst = os.path.abspath(os.path.join(app.name, 'Contents', 'MacOS', 'tk'))
            else:
                continue
            copytree(p, dst)

# vim:expandtab

