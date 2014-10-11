#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Options tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls, binding
from .layout import GridLayouter
from .tab import Tab
import sys

from core import df, keybinds, embarks
from core.lnp import lnp

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *
    import tkMessageBox as messagebox
    import tkSimpleDialog as simpledialog

class OptionsTab(Tab):
    """Options tab for the TKinter GUI."""
    def create_variables(self):
        self.keybinds = Variable()
        self.embarks = Variable()

    def read_data(self):
        self.read_keybinds()
        self.read_embarks()

    def create_controls(self):
        options = controls.create_control_group(self, 'Gameplay Options', True)
        options.pack(side=TOP, fill=BOTH, expand=N)

        grid = GridLayouter(2)
        grid.add(controls.create_trigger_option_button(
            options, 'Population Cap', 'Maximum population in your fort',
            self.set_pop_cap, 'popcap'))
        grid.add(controls.create_trigger_option_button(
            options, 'Child Cap', 'Maximum children in your fort',
            self.set_child_cap, 'childcap'))
        if lnp.df_info.version >= '0.40.05':
            grid.add(controls.create_trigger_option_button(
                options, 'Strict Population Cap',
                'Strict limit on population in your fort (blocks births)',
                self.set_strict_pop_cap, 'strictPopcap'), 2)
        grid.add(controls.create_option_button(
            options, 'Invaders',
            'Toggles whether invaders (goblins, etc.) show up',
            'invaders'))
        grid.add(controls.create_option_button(
            options, 'Cave-ins',
            'Toggles whether unsupported bits of terrain will collapse',
            'caveins'))
        grid.add(controls.create_option_button(
            options, 'Temperature',
            'Toggles whether things will burn, melt, freeze, etc.',
            'temperature'))
        grid.add(controls.create_option_button(
            options, 'Weather', 'Rain, snow, etc.', 'weather'))
        grid.add(controls.create_option_button(
            options, 'Entomb Pets',
            'Whether deceased pets should be entombed in coffins by default.',
            'entombPets'))
        grid.add(controls.create_option_button(
            options, 'Artifacts',
            'Whether dwarfs should enter artifact producing moods.',
            'artifacts'))
        if lnp.df_info.version >= '0.34.03':
            if lnp.df_info.version <= '0.34.06':
                tooltip = 'Whether labors are enabled by default.'
            else:
                tooltip = (
                    'Which labors are enabled by default: by skill level of '
                    'dwarves, by their unit type, or none')
            grid.add(controls.create_option_button(
                options, 'Starting Labors', tooltip, 'laborLists'), 2)

        display = controls.create_control_group(self, 'Display Options', True)
        display.pack(side=TOP, fill=BOTH, expand=N)

        grid = GridLayouter(2)
        grid.add(controls.create_option_button(
            display, 'Liquid Depth',
            'Displays the depth of liquids with numbers 1-7',
            'liquidDepth'))
        grid.add(controls.create_option_button(
            display, 'Varied Ground',
            'If ground tiles use a variety of punctuation, or only periods',
            'variedGround'))

        mods = controls.create_control_group(
            self, 'Modifications')
        mods.pack(side=TOP, expand=N, anchor="w")

        controls.create_option_button(
            mods, 'Aquifers', 'Whether newly created worlds will have Aquifers '
            'in them (Infinite sources of underground water, but may flood '
            'your fort', 'aquifers').grid(column=0, row=0, sticky="nsew")

        keybindings, self.keybinding_files, _ = \
            controls.create_file_list_buttons(
                self, 'Key Bindings', self.keybinds,
                lambda: self.load_keybinds(self.keybinding_files),
                self.read_keybinds, self.save_keybinds,
                lambda: self.delete_keybinds(self.keybinding_files))
        keybindings.pack(side=BOTTOM, fill=BOTH, expand=Y)

        embarkframe, self.embark_files, _ = \
            controls.create_readonly_file_list_buttons(
                self, 'Embark profiles', self.embarks,
                lambda: self.install_embarks(self.embark_files),
                self.read_embarks, selectmode='multiple')
        embarkframe.pack(side=BOTTOM, fill=BOTH, expand=Y)

    @staticmethod
    def set_pop_cap():
        """Requests new population cap from the user."""
        v = simpledialog.askinteger(
            "Settings", "Population cap:",
            initialvalue=df.settings.popcap)
        if v is not None:
            df.set_option('popcap', str(v))
            binding.update()

    @staticmethod
    def set_strict_pop_cap():
        """Requests new strict population cap from the user."""
        v = simpledialog.askinteger(
            "Settings", "Strict population cap:",
            initialvalue=df.settings.strictPopcap)
        if v is not None:
            df.set_option('strictPopcap', str(v))
            binding.update()

    @staticmethod
    def set_child_cap():
        """Requests new child cap from the user."""
        child_split = list(df.settings.childcap.split(':'))
        child_split.append('0')  # In case syntax is invalid
        v = simpledialog.askinteger(
            "Settings", "Absolute cap on babies + children:",
            initialvalue=child_split[0])
        if v is not None:
            v2 = simpledialog.askinteger(
                "Settings", "Max percentage of children in fort:\n"
                "(lowest of the two values will be used as the cap)",
                initialvalue=child_split[1])
            if v2 is not None:
                df.set_option('childcap', str(v)+':'+str(v2))
                binding.update()

    def read_keybinds(self):
        """Reads list of keybinding files."""
        files = keybinds.read_keybinds()
        self.keybinds.set(files)
        current = keybinds.get_installed_file()
        for i, f in enumerate(files):
            if f == current:
                self.keybinding_files.itemconfig(i, fg='red')
            else:
                self.keybinding_files.itemconfig(i, fg='black')

    def load_keybinds(self, listbox):
        """
        Replaces keybindings with selected file.

        Params:
            listbox
                Listbox containing the list of keybinding files.
        """
        if len(listbox.curselection()) != 0:
            keybinds.load_keybinds(listbox.get(listbox.curselection()[0]))
            self.read_keybinds()

    def save_keybinds(self):
        """Saves keybindings to a file."""
        v = simpledialog.askstring(
            "Save Keybindings", "Save current keybindings as:")
        if v is not None:
            if not v.endswith('.txt'):
                v = v + '.txt'
            if (not keybinds.keybind_exists(v) or messagebox.askyesno(
                    message='Overwrite {0}?'.format(v),
                    icon='question', title='Overwrite file?')):
                keybinds.save_keybinds(v)
                self.read_keybinds()

    def delete_keybinds(self, listbox):
        """
        Deletes a keybinding file.

        Params:
            listbox
                Listbox containing the list of keybinding files.
        """
        if len(listbox.curselection()) != 0:
            filename = listbox.get(listbox.curselection()[0])
            if messagebox.askyesno(
                    'Delete file?',
                    'Are you sure you want to delete {0}?'.format(filename)):
                keybinds.delete_keybinds(filename)
            self.read_keybinds()

    def read_embarks(self):
        """Reads list of embark profiles."""
        files = embarks.read_embarks()
        self.embarks.set(files)
        current = embarks.get_installed_files()
        for i, f in enumerate(files):
            if f in current:
                self.embark_files.itemconfig(i, fg='red')
            else:
                self.embark_files.itemconfig(i, fg='black')

    def install_embarks(self, listbox):
        """
        Installs selected embark profiles.

        Params:
            listbox
                Listbox containing the list of embark profiles.
        """
        if len(listbox.curselection()) != 0:
            files = []
            for f in listbox.curselection():
                files.append(listbox.get(f))
            embarks.install_embarks(files)
            self.read_embarks()
