#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys
import errorlog
from tkgui import TkGui

import fnmatch, glob, os, re, shutil, subprocess, tempfile, webbrowser
import distutils.dir_util as dir_util
from datetime import datetime

from settings import DFConfiguration

BASEDIR = '.'
VERSION = '0.1'

class PyLNP():
  def __init__(self):
    self.bundle = ''
    if hasattr(sys, 'frozen'):
      os.chdir(os.path.dirname(sys.executable))
      if sys.platform == 'win32': #In case we want to do something special for py2exe
        self.bundle = 'win'
      elif sys.platform.startswith('linux'):
        self.bundle = 'linux'
      elif sys.platform == 'darwin': #OS X bundles start in different directory
        os.chdir('../../..')
        self.bundle = 'osx'
    else:
      os.chdir(os.path.dirname(os.path.abspath(__file__)))

    self.lnp_dir = os.path.join(BASEDIR,'LNP')
    if not os.path.isdir(self.lnp_dir):
      print('WARNING: LNP folder is missing!', file=sys.stderr)
    self.keybinds_dir = os.path.join(self.lnp_dir,'Keybinds')
    self.graphics_dir = os.path.join(self.lnp_dir,'Graphics')
    self.utils_dir = os.path.join(self.lnp_dir,'Utilities')

    self.load_autorun()
    self.find_df_folder()

    TkGui(self)

  def load_params(self):
    try:
      self.settings.read_settings()
    except IOError as e:
      sys.excepthook(*sys.exc_info())
      msg="Failed to read settings, {0} not really a DF dir?".format(self.df_dir)
      raise IOError(msg)

  def save_params(self):
    self.settings.write_settings()

  def restore_defaults(self):
    shutil.copy(os.path.join(self.lnp_dir,'Defaults','init.txt'), os.path.join(self.init_dir,'init.txt'))
    shutil.copy(os.path.join(self.lnp_dir,'Defaults','d_init.txt'), os.path.join(self.init_dir,'d_init.txt'))
    self.load_params()

  def run_df(self):
    if sys.platform == 'win32':
      self.run_program(os.path.join(self.df_dir,'Dwarf Fortress.exe'))
    else:
      self.run_program(os.path.join(self.df_dir,'df'))
    for p in self.autorun:
      if os.access(os.path.join(self.utils_dir,p), os.F_OK):
        self.run_program(os.path.join(self.utils_dir,p))

  def run_program(self, path):
    try:
      path=os.path.abspath(path)
      if path.endswith('.jar'): #Explicitly launch JAR files with Java
        subprocess.Popen(['java', '-jar', os.path.basename(path)], cwd=os.path.dirname(path))
      elif path.endswith('.app'): #OS X application bundle
        subprocess.Popen(['open',path], cwd=path)
      else:
        subprocess.Popen(path, cwd=os.path.dirname(path))
      return True
    except OSError as e:
      sys.excepthook(*sys.exc_info())
      return False

  def open_savegames(self):
    openFolder(self.save_dir)

  def open_utils(self):
    openFolder(self.utils_dir)

  def open_graphics(self):
    openFolder(self.graphics_dir)

  def open_main_folder(self):
    openFolder('.')

  def open_lnp_folder(self):
    openFolder(self.lnp_dir)

  def open_df_folder(self):
    openFolder(self.df_dir)

  def open_init_folder(self):
    openFolder(self.init_dir)

  def open_df_web(self):
    webbrowser.open('http://www.bay12games.com/dwarves/')

  def open_wiki(self):
    webbrowser.open('http://dwarffortresswiki.org/')

  def open_forums(self):
    webbrowser.open('http://www.bay12forums.com/smf/')

  def find_df_folder(self):
    self.folders = folders = tuple(filter(os.path.isdir, glob.glob(os.path.join(BASEDIR,'Dwarf Fortress*'))+glob.glob(os.path.join(BASEDIR,'df*'))))
    self.df_dir = ''
    if len(folders) == 1:
      self.set_df_folder(folders[0])

  def set_df_folder(self, path):
    self.df_dir = os.path.abspath(path)
    self.init_dir = os.path.join(self.df_dir,'data','init')
    self.save_dir = os.path.join(self.df_dir,'data','save')
    self.settings = DFConfiguration(self.df_dir)
    self.install_extras()
    self.load_params()

  def read_keybinds(self):
    return tuple(map(os.path.basename, glob.glob(os.path.join(self.keybinds_dir,'*.txt'))))

  def read_graphics(self):
    return tuple(map(os.path.basename, [o for o in glob.glob(os.path.join(self.graphics_dir,'*')) if os.path.isdir(o)]))

  def read_utilities(self):
    exclusions = []
    try:
      exclusions_file = open(os.path.join(self.utils_dir,'exclude.txt'))
      for line in exclusions_file:
        for m in re.findall('\[(.+)\]',line):
          exclusions.append(m)
    except IOError:
      pass
    #Allow for an include list of filenames that will be treated as valid utilities.
    #Useful for e.g. Linux, where executables rarely have extensions.
    inclusions = []
    try:
      inclusions_file = open(os.path.join(self.utils_dir,'include.txt'))
      for line in inclusions_file:
        for m in re.findall('\[(.+)\]',line):
          inclusions.append(m)
    except IOError:
      pass
    progs = []
    patterns = ['*.jar'] # Java applications
    if sys.platform in ['windows', 'win32']:
      patterns.append('*.exe') # Windows executables
    else:
      patterns.append('*.sh') # Shell scripts for Linux and OS X
    for root, dirnames, filenames in os.walk(self.utils_dir):
      if sys.platform == 'darwin':
        for dirname in dirnames:
          if fnmatch.fnmatch(dirname, '*.app'): #OS X application bundles are really directories
            progs.append(os.path.relpath(os.path.join(root,dirname),os.path.join(self.utils_dir)))
      for filename in filenames:
        if (any(fnmatch.fnmatch(filename, p) for p in patterns) or filename in inclusions) and (filename not in exclusions):
          progs.append(os.path.relpath(os.path.join(root,filename),os.path.join(self.utils_dir)))

    return progs

  def toggle_autorun(self, item):
    if item in self.autorun:
      self.autorun.remove(item)
    else:
      self.autorun.append(item)
    self.save_autorun()

  def load_autorun(self):
    self.autorun = []
    try:
      for line in open(os.path.join(self.utils_dir,'autorun.txt')):
        self.autorun.append(line)
    except IOError:
      pass

  def save_autorun(self):
    f = open(os.path.join(self.utils_dir,'autorun.txt'),'w')
    f.write("\n".join(self.autorun))
    f.close()

  def cycle_option(self, field):
    self.settings.cycle_item(field)
    self.save_params()

  def set_option(self, field, value):
    self.settings.set_value(field, value)
    self.save_params()

  def load_keybinds(self, filename):
    if not filename.endswith('.txt'):
      filename = filename + '.txt'
    target = os.path.join(self.init_dir,'interface.txt')
    os.rename(target, target+'.bak')
    shutil.copyfile(os.path.join(self.keybinds_dir,filename), target)

  def keybind_exists(self, filename):
    if not filename.endswith('.txt'):
      filename = filename + '.txt'
    return os.access(os.path.join(self.keybinds_dir, filename), os.F_OK)

  def save_keybinds(self, filename):
    if not filename.endswith('.txt'):
      filename = filename + '.txt'
    shutil.copyfile(os.path.join(self.init_dir,'interface.txt'), target)
    self.read_keybinds()

  def delete_keybinds(self, filename):
    if not filename.endswith('.txt'):
      filename = filename + '.txt'
    os.remove(os.path.join(self.keybinds_dir,filename))

  def install_graphics(self, pack):
    """
    Installs the graphics pack located in LNP/Graphics/<pack>.
    install_inits should point to the appropriate method used to handle the inits (copy_inits or patch_inits).

    Returns:
      True if successful,
      False if an exception occured
      None if required files are missing (raw/graphics, data/init)
    """
    gfxDir = os.path.join(self.graphics_dir,pack)
    if os.path.isdir(gfxDir) and os.path.isdir(os.path.join(gfxDir,'raw','graphics')) and os.path.isdir(os.path.join(gfxDir,'data','init')):
      try:
        #Delete old graphics
        if os.path.isdir(os.path.join(self.df_dir,'raw','graphics')):
          dir_util.remove_tree(os.path.join(self.df_dir,'raw','graphics'))
        #Copy new raws
        dir_util.copy_tree(os.path.join(gfxDir,'raw'),os.path.join(self.df_dir,'raw'))
        if os.path.isdir(os.path.join(self.df_dir,'data','art')):
          dir_util.remove_tree(os.path.join(self.df_dir,'data','art'))
        dir_util.copy_tree(os.path.join(gfxDir,'data','art'),os.path.join(self.df_dir,'data','art'))
        self.install_inits(gfxDir)
        shutil.copyfile(os.path.join(gfxDir,'data','init','colors.txt'),os.path.join(self.df_dir,'data','init','colors.txt'))
      except Exception:
        sys.excepthook(*sys.exc_info())
        return False
      else:
        return True
    else:
      return None
    self.load_params()

  def copy_inits(self, gfxDir):
    """
    Installs init files from a graphics pack by overwriting.
    """
    shutil.copyfile(os.path.join(gfxDir,'data','init','init.txt'),os.path.join(self.df_dir,'data','init','init.txt'))
    shutil.copyfile(os.path.join(gfxDir,'data','init','d_init.txt'),os.path.join(self.df_dir,'data','init','d_init.txt'))

  def patch_inits(self, gfxDir):
    """
    Installs init files from a graphics pack by selectively changing specific fields.
    All settings outside of the mentioned fields are preserved.
    """
    d_init_fields = ['WOUND_COLOR_NONE','WOUND_COLOR_MINOR','WOUND_COLOR_INHIBITED','WOUND_COLOR_FUNCTION_LOSS','WOUND_COLOR_BROKEN','WOUND_COLOR_MISSING','SKY','CHASM','PILLAR_TILE','TRACK_N','TRACK_S','TRACK_E','TRACK_W','TRACK_NS','TRACK_NE','TRACK_NW','TRACK_SE','TRACK_SW','TRACK_EW','TRACK_NSE','TRACK_NSW','TRACK_NEW','TRACK_SEW','TRACK_NSEW','TRACK_RAMP_N','TRACK_RAMP_S','TRACK_RAMP_E','TRACK_RAMP_W','TRACK_RAMP_NS','TRACK_RAMP_NE','TRACK_RAMP_NW','TRACK_RAMP_SE','TRACK_RAMP_SW','TRACK_RAMP_EW','TRACK_RAMP_NSE','TRACK_RAMP_NSW','TRACK_RAMP_NEW','TRACK_RAMP_SEW','TRACK_RAMP_NSEW']
    init_fields = ['FONT','FULLFONT','GRAPHICS','GRAPHICS_FONT','GRAPHICS_FULLFONT','TRUETYPE']
    self.settings.read_file(os.path.join(gfxDir,'data','init','init.txt'), init_fields, False)
    self.settings.read_file(os.path.join(gfxDir,'data','init','d_init.txt'), d_init_fields, False)
    self.save_params()

  install_inits = copy_inits

  def update_savegames(self):
    saves = [o for o in glob.glob(os.path.join(self.save_dir,'*')) if os.path.isdir(o) and not o.endswith('current')]
    count = 0
    if saves:
      for save in saves:
        count = count + 1
        #Delete old graphics
        if os.path.isdir(os.path.join(save,'raw','graphics')):
          dir_util.remove_tree(os.path.join(save,'raw','graphics'))
        #Copy new raws
        dir_util.copy_tree(os.path.join(self.df_dir,'raw'),os.path.join(save,'raw'))
    return count

  def simplify_graphics(self):
    for pack in self.read_graphics():
      self.simplify_pack(self.pack)

  def simplify_pack(self, pack):
    """
    Removes unnecessary files from LNP/Graphics/<pack>.

    Returns:
      The number of files removed if successful
      False if an exception occurred
      None if folder is empty
    """
    pack = os.path.join(self.graphics_dir,pack)
    filesBefore = sum(len(f) for (_,_,f) in os.walk(pack))
    if filesBefore == 0:
      return None
    tmp = tempfile.mkdtemp()
    try:
      dir_util.copy_tree(pack,tmp)
      if os.path.isdir(pack):
        dir_util.remove_tree(pack)

      os.makedirs(pack)
      os.makedirs(os.path.join(pack,'data','art'))
      os.makedirs(os.path.join(pack,'raw','graphics'))
      os.makedirs(os.path.join(pack,'raw','objects'))
      os.makedirs(os.path.join(pack,'data','init'))

      dir_util.copy_tree(os.path.join(tmp,'data','art'),os.path.join(pack,'data','art'))
      dir_util.copy_tree(os.path.join(tmp,'raw','graphics'),os.path.join(pack,'raw','graphics'))
      dir_util.copy_tree(os.path.join(tmp,'raw','objects'),os.path.join(pack,'raw','objects'))
      shutil.copyfile(os.path.join(tmp,'data','init','colors.txt'),os.path.join(pack,'data','init','colors.txt'))
      shutil.copyfile(os.path.join(tmp,'data','init','init.txt'),os.path.join(pack,'data','init','init.txt'))
      shutil.copyfile(os.path.join(tmp,'data','init','d_init.txt'),os.path.join(pack,'data','init','d_init.txt'))
    except IOError:
      sys.excepthook(*sys.exc_info())
      retval = False
    else:
      filesAfter = sum(len(f) for (_,_,f) in os.walk(pack))
      retval = filesAfter - filesBefore
    if os.path.isdir(tmp):
      dir_util.remove_tree(tmp)
    return retval

  def install_extras(self):
    extras_dir = os.path.join(self.lnp_dir,'Extras')
    if not os.path.isdir(extras_dir):
      return
    install_file = os.path.join(self.df_dir,'PyLNP{0}.txt'.format(VERSION))
    if not os.access(install_file, os.F_OK):
      dir_util.copy_tree(extras_dir, self.df_dir)
      f = open(install_file, 'w')
      f.write('PyLNP V{0} extras installed!\nTime: {1}'.format(VERSION,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
      f.close()

#http://stackoverflow.com/questions/6631299/python-opening-a-folder-in-explorer-nautilus-mac-thingie
if sys.platform == 'darwin':
  def openFolder(path):
    try:
      subprocess.check_call(['open', '--', path])
    except:
      pass
elif sys.platform.startswith('linux'):
  def openFolder(path):
    try:
      subprocess.check_call(['xdg-open', path])
    except:
      pass
elif sys.platform in ['windows', 'win32']:
  def openFolder(path):
    try:
      subprocess.check_call(['explorer', path])
    except:
      pass

if __name__ == "__main__":
  PyLNP()

# vim:expandtab
