#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os, re, shutil

# Markers to read certain settings correctly

class _DisableValues:
    """Marker class for DFConfiguration. Value is disabled by replacing [ and ] with !."""
    pass

disabled = _DisableValues()

class _ForceBool:
    """Marker class for DFConfiguration. Values other than YES or NO are interpreted as YES."""
    pass

force_bool = _ForceBool()

class DFConfiguration:

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.settings = dict()
        self.options = dict()
        self.field_names = dict()
        self.inverse_field_names = dict()
        self.files = dict()
        self.in_files = dict()
        #init.txt
        boolvals = ("YES", "NO")
        init = (os.path.join(base_dir,'data','init','init.txt'),)
        self.create_option("truetype", "TRUETYPE", "YES", force_bool, init)
        self.create_option("sound", "SOUND", "YES", boolvals, init)
        self.create_option("volume", "VOLUME", "255", None, init)
        self.create_option("introMovie", "INTRO", "YES", boolvals, init)
        self.create_option("startWindowed", "WINDOWED", "YES", boolvals, init)
        self.create_option("fpsCounter", "FPS", "NO", boolvals, init)
        self.create_option("fpsCap", "FPS_CAP", "100", None, init)
        self.create_option("gpsCap", "G_FPS_CAP", "50", None, init)
        self.create_option("procPriority", "PRIORITY", "NORMAL", ("REALTIME","HIGH","ABOVE_NORMAL","NORMAL","BELOW_NORMAL","IDLE"), init)
        self.create_option("compressSaves", "COMPRESSED_SAVES", "YES", boolvals, init)
        #d_init.txt
        dinit = (os.path.join(base_dir,'data','init','d_init.txt'),)
        self.create_option("popcap", "POPULATION_CAP", "200", None, dinit)
        self.create_option("childcap", "BABY_CHILD_CAP", "100:1000", None, dinit)
        self.create_option("invaders", "INVADERS", "YES", boolvals, dinit)
        self.create_option("temperature", "TEMPERATURE", "YES", boolvals, dinit)
        self.create_option("weather", "WEATHER", "YES", boolvals, dinit)
        self.create_option("caveins", "CAVEINS", "YES", boolvals, dinit)
        self.create_option("liquidDepth", "SHOW_FLOW_AMOUNTS", "YES", boolvals, dinit)
        self.create_option("variedGround", "VARIED_GROUND_TILES", "YES", boolvals, dinit)
        self.create_option("laborLists", "SET_LABOR_LISTS", "SKILLS", ("NO","SKILLS","BY_UNIT_TYPE"), dinit)
        self.create_option("autoSave", "AUTOSAVE", "SEASONAL", ("NONE", "SEASONAL", "YEARLY"), dinit)
        self.create_option("autoBackup", "AUTOBACKUP", "YES", boolvals, dinit)
        self.create_option("autoSavePause", "AUTOSAVE_PAUSE", "YES", boolvals, dinit)
        self.create_option("initialSave", "INITIAL_SAVE", "YES", boolvals, dinit)
        self.create_option("pauseOnLoad", "PAUSE_ON_LOAD", "YES", boolvals, dinit)
        #special
        self.create_option("aquifers", "AQUIFER", "YES", disabled, tuple(os.path.join(base_dir, 'raw','objects', a) for a in ['inorganic_stone_layer.txt','inorganic_stone_mineral.txt','inorganic_stone_soil.txt']))

    def create_option(self, name, field_name, default, values, files):
        """
        Register an option to write back for changes. If the field_name has been registered before, no changes are made.

        Params:
          name
            The name you want to use to refer to this field (becomes available as an attribute on this class).
          field_name
            The field name used in the file. If this is different from the name argument, this will also become available as an attribute.
          default
            The value to initialize this setting to.
          values
            An iterable of valid values for this field. Used in cycle_list.
            Special values defined in this file:
              None
                Unspecified value; cycling has no effect.
              disabled:
                Boolean option toggled by replacing the [] around the field name with !!.
              force_bool:
                Values other than "YES" and "NO" are interpreted as "YES".
          files
            A tuple of files this value is read from. Used for e.g. aquifer toggling, which requires editing multiple files.
        """

        if name in self.settings or name in self.inverse_field_names: # Don't allow re-registration of a known field
            return
        self.settings[name] = default
        self.options[name] = values
        self.field_names[name] = field_name
        if field_name != name:
            self.inverse_field_names[field_name] = name
        self.files[name] = files
        self.in_files.setdefault(files, [])
        self.in_files[files].append(name)

    def __iter__(self):
        for key, value in list(self.settings.items()):
            yield key, value

    def set_value(self, name, value):
        self.settings[name] = value

    def cycle_item(self, name):
        self.settings[name] = self.cycle_list(self.settings[name], self.options[name])

    def cycle_list(self, current, items):
        if items is None:
            return current
        if items is disabled or items is force_bool:
            items = ("YES", "NO")
        return items[(items.index(current) + 1) % len(items)]

    def read_settings(self):
        """Read settings from known filesets. If fileset only contains one file, all options will be registered automatically."""
        for files in self.in_files.keys():
            for filename in files:
                self.read_file(filename, self.in_files[files], len(files) == 1)

    def read_file(self, filename, fields, auto_add):
        """
        Reads DF settings from the file <filename>.

        Params:
          filename
            The file to read from.
          fields:
            An iterable containing the field names to read
          auto_add
            Whether to automatically register all unknown fields for changes by calling create_option(field_name, field_name, value, None, (filename)).
        """
        f = open(filename)
        text = f.read()
        if auto_add:
            for m in re.findall('\[(.+?):(.+?)\]', text):
                self.create_option(m[0], m[0], m[1], None, (filename,))
        for field in fields:
            if field in self.inverse_field_names:
                field = self.inverse_field_names[field]
            if self.options[field] is disabled:
                self.settings[field] = "NO" #Assume option is disabled unless there is a single match
                if "[{0}]".format(self.field_names[field]) in text:
                    self.settings[field] = "YES"
            else:
                m = re.search('\[{0}:(.+?)\]'.format(self.field_names[field]), text)
                if self.options[field] is force_bool and m.group(1) != "NO": #Interpret everything other than "NO" as "YES"
                    self.settings[field] = "YES"
                else:
                    self.settings[field] = m.group(1)

    def write_settings(self):
        for files in self.in_files:
            for filename in files:
                self.write_file(filename, self.in_files[files])

    def write_file(self, filename, fields):
        f = open(filename, 'r')
        text = f.read()
        for field in fields:
            if self.options[field] is disabled:
                replace_from = None
                replace_to = None
                if self.settings[field] == "NO":
                    replace_from = "[{0}]"
                    replace_to = "!{0}!"
                else:
                    replace_from = "!{0}!"
                    replace_to = "[{0}]"
                text = text.replace(replace_from.format(self.field_names[field]), replace_to.format(self.field_names[field]))
            else:
                text = re.sub('\[{0}:(.+?)\]'.format(self.field_names[field]), '[{0}:{1}]'.format(self.field_names[field], self.settings[field]), text)
        f.close()
        #Backup old file
        backup = filename+'.bak'
        shutil.copyfile(filename, backup)
        f = open(filename, 'w')
        f.write(text)
        f.close()

    def __str__(self):
        return "base_dir = {0}\nsettings = {1}\noptions = {2}\nfield_names = {3}\ninverse_field_names = {4}\nfiles = {5}\nin_files = {6}".format(self.base_dir, self.settings, self.options, self.field_names, self.inverse_field_names, self.files, self.in_files)

    def __getattr__(self, name):
        """Exposes all registered options through both their internal and registered names."""
        if name in self.inverse_field_names:
            return self.settings[self.inverse_field_names[name]]
        return self.settings[name]

# vim:expandtab
