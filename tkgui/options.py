#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Options tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls, binding
from .tab import Tab
import sys

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
        options = controls.create_control_group(self, 'Options', True)
        options.pack(side=TOP, fill=BOTH, expand=N)

        controls.create_trigger_option_button(
            options, 'Population Cap', 'Maximum population in your fort',
            self.set_pop_cap, 'popcap').grid(column=0, row=0, sticky="nsew")
        controls.create_option_button(
            options, 'Invaders',
            'Toggles whether invaders (goblins, etc.) show up',
            'invaders').grid(column=1, row=0, sticky="nsew")
        controls.create_trigger_option_button(
            options, 'Child Cap', 'Maximum children in your fort',
            self.set_child_cap, 'childcap').grid(column=0, row=1, sticky="nsew")
        controls.create_option_button(
            options, 'Cave-ins',
            'Toggles whether unsupported bits of terrain will collapse',
            'caveins').grid(column=1, row=1, sticky="nsew")
        controls.create_option_button(
            options, 'Temperature',
            'Toggles whether things will burn, melt, freeze, etc.',
            'temperature').grid(column=0, row=2, sticky="nsew")
        controls.create_option_button(
            options, 'Liquid Depth',
            'Displays the depth of liquids with numbers 1-7',
            'liquidDepth').grid(column=1, row=2, sticky="nsew")
        controls.create_option_button(
            options, 'Weather', 'Rain, snow, etc.', 'weather').grid(
                column=0, row=3, sticky="nsew")
        controls.create_option_button(
            options, 'Varied Ground',
            'If ground tiles use a variety of punctuation, or only periods',
            'variedGround').grid(column=1, row=3, sticky="nsew")
        controls.create_option_button(
            options, 'Starting Labors', 'Which labors are enabled by default:'
            'by skill level of dwarves, by their unit type, or none',
            'laborLists').grid(column=0, row=4, columnspan=2, sticky="nsew")

        mods = controls.create_control_group(
            self, 'Modifications')
        mods.pack(side=TOP, expand=N, anchor="w")

        controls.create_option_button(
            mods, 'Aquifers', 'Whether newly created worlds will have Aquifers '
            'in them (Infinite sources of underground water, but may flood '
            'your fort', 'aquifers').grid(column=0, row=0, sticky="nsew")

        keybindings, keybinding_files, _ = \
            controls.create_file_list_buttons(
                self, 'Key Bindings', self.keybinds,
                lambda: self.load_keybinds(keybinding_files),
                self.read_keybinds, self.save_keybinds,
                lambda: self.delete_keybinds(keybinding_files))
        keybindings.pack(side=BOTTOM, fill=BOTH, expand=Y)

        embarks, embark_files, _ = \
            controls.create_readonly_file_list_buttons(
                self, 'Embark profiles', self.embarks,
                lambda: self.install_embarks(embark_files),
                self.read_embarks, selectmode='multiple')
        embarks.pack(side=BOTTOM, fill=BOTH, expand=Y)

    def set_pop_cap(self):
        """Requests new population cap from the user."""
        v = simpledialog.askinteger(
            "Settings", "Population cap:",
            initialvalue=self.lnp.settings.popcap)
        if v is not None:
            self.lnp.set_option('popcap', str(v))
            binding.update()

    def set_child_cap(self):
        """Requests new child cap from the user."""
        child_split = list(self.lnp.settings.childcap.split(':'))
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
                self.lnp.set_option('childcap', str(v)+':'+str(v2))
                binding.update()

    def load_keybinds(self, listbox):
        """
        Replaces keybindings with selected file.

        Params:
            listbox
                Listbox containing the list of keybinding files.
        """
        if len(listbox.curselection()) != 0:
            self.lnp.load_keybinds(listbox.get(listbox.curselection()[0]))

    def save_keybinds(self):
        """Saves keybindings to a file."""
        v = simpledialog.askstring(
            "Save Keybindings", "Save current keybindings as:")
        if v is not None:
            if not v.endswith('.txt'):
                v = v + '.txt'
            if (not self.lnp.keybind_exists(v) or messagebox.askyesno(
                    message='Overwrite {0}?'.format(v),
                    icon='question', title='Overwrite file?')):
                self.lnp.save_keybinds(v)
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
                self.lnp.delete_keybinds(filename)
            self.read_keybinds()

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
            self.lnp.install_embarks(files)

    def read_keybinds(self):
        """Reads list of keybinding files."""
        self.keybinds.set(self.lnp.read_keybinds())

    def read_embarks(self):
        """Reads list of embark profiles."""
        self.embarks.set(self.lnp.read_embarks())
