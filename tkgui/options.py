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

#pylint: disable=too-many-public-methods
class OptionsTab(Tab):
    """Options tab for the TKinter GUI."""
    def create_variables(self):
        self.keybinds = Variable()
        self.embarks = Variable()

    def read_data(self):
        self.read_keybinds()
        if lnp.df_info.version >= '0.28.181.40a':
            self.read_embarks()

    def create_controls(self):
        options = controls.create_control_group(self, 'Gameplay Options', True)
        options.pack(side=TOP, fill=BOTH, expand=N)

        grid = GridLayouter(2)
        grid.add(controls.create_trigger_option_button(
            options, 'Population Cap', 'Maximum population in your fort. '
            'Setting this too low may disable certain gameplay features.',
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
        grid.add(controls.create_trigger_option_button(
            options, 'Graze Coefficient',
            'Scales how often grazing animals need to eat.  Larger numbers '
            'require less food.', self.set_graze_coef, 'grazeCoef'), 2)
        if lnp.df_info.version >= '0.34.03':
            if lnp.df_info.version <= '0.34.06':
                tooltip = 'Whether labors are enabled by default.'
            else:
                tooltip = (
                    'Which labors are enabled by default: by skill level of '
                    'dwarves, by their unit type, or none')
            grid.add(controls.create_option_button(
                options, 'Starting Labors', tooltip, 'laborLists'), 2)

        mods = controls.create_control_group(
            self, 'Modifications')
        mods.pack(side=TOP, expand=N, anchor="w")

        controls.create_option_button(
            mods, 'Aquifers', 'Whether newly created worlds will have Aquifers '
            'in them (Infinite sources of underground water, but may flood '
            'your fort', 'aquifers').grid(column=0, row=0, sticky="nsew")

        keybindings, self.keybinding_entry, self.keybinding_files = \
            controls.create_list_with_entry(
                self, "Key Bindings", self.keybinds,
                [("Load", "Load keybindings", self.load_keybinds),
                 ("Save", "Save current keybindings", self.save_keybinds),
                 ("Delete", "Delete keybindings", self.delete_keybinds),
                 ("Refresh", "Refresh list", self.read_keybinds)])
        keybindings.pack(side=BOTTOM, fill=BOTH, expand=N)
        for seq in ("<Double-1>", "<Return>"):
            self.keybinding_files.bind(seq, lambda e: self.load_keybinds())

        if lnp.df_info.version >= '0.28.181.40a':
            embarkframe, self.embark_files = \
                controls.create_file_list(self, 'Embark profiles', self.embarks)
            self.embark_files.configure(selectmode="single")

            refresh = controls.create_trigger_button(
                embarkframe, 'Refresh Profiles', 'Refresh list of profiles',
                self.read_embarks)
            refresh.grid(column=0, row=3, columnspan=2, sticky="sew")

            # This hack ensures the listbox never selects anything itself. This
            # is much better than the alternative hack required to prevent the
            # list selecting the last element when clicking in empty space.
            def deselect_all(event):
                for item in event.widget.curselection():
                    event.widget.selection_clear(item)
            self.embark_files.bind("<<ListboxSelect>>", deselect_all)

            for seq in ("<space>", "<Return>", "<1>",
                        "<2>" if sys.platform == 'darwin' else "<3>"):
                self.embark_files.bind(seq, self.toggle_embark)

    @staticmethod
    def set_pop_cap():
        """Requests new population cap from the user."""
        v = simpledialog.askinteger(
            "Settings", "Population cap:",
            initialvalue=lnp.settings.popcap)
        if v is not None:
            df.set_option('popcap', str(v))
            binding.update()

    @staticmethod
    def set_strict_pop_cap():
        """Requests new strict population cap from the user."""
        v = simpledialog.askinteger(
            "Settings", "Strict population cap:",
            initialvalue=lnp.settings.strictPopcap)
        if v is not None:
            df.set_option('strictPopcap', str(v))
            binding.update()

    @staticmethod
    def set_child_cap():
        """Requests new child cap from the user."""
        child_split = list(lnp.settings.childcap.split(':'))
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

    @staticmethod
    def set_graze_coef():
        """Requests new graze coefficient from the user."""
        v = simpledialog.askinteger(
            "Settings", "Graze coefficient:",
            initialvalue=lnp.settings.grazeCoef)
        if v is not None:
            df.set_option('grazeCoef', str(v))
            binding.update()


    def read_keybinds(self):
        """Reads list of keybinding files."""
        files = keybinds.read_keybinds()
        self.keybinds.set(files)
        current = keybinds.get_installed_file()
        for i, f in enumerate(files):
            if f == current:
                self.keybinding_files.itemconfig(i, bg='pale green')
            else:
                self.keybinding_files.itemconfig(i, bg='white')

    def load_keybinds(self):
        """Replaces keybindings with selected file."""
        listbox = self.keybinding_files
        items = listbox.curselection()
        if len(items) > 0:
            listbox.selection_clear(items)
            keybinds.load_keybinds(listbox.get(items[0]))
            self.read_keybinds()
            self.keybinding_entry.delete(0, END)

    def save_keybinds(self):
        """Saves keybindings to a file."""
        v = self.keybinding_entry.get()
        if v:
            if not v.endswith('.txt'):
                v = v + '.txt'
            if (not keybinds.keybind_exists(v) or messagebox.askyesno(
                    message='Overwrite {0}?'.format(v),
                    icon='question', title='Overwrite file?')):
                self.keybinding_entry.delete(0, END)
                keybinds.save_keybinds(v)
                self.read_keybinds()

    def delete_keybinds(self):
        """Deletes a keybinding file."""
        listbox = self.keybinding_files
        if len(listbox.curselection()) > 0:
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
                self.embark_files.itemconfig(i, bg='pale green')
            else:
                self.embark_files.itemconfig(i, bg='white')

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

    def toggle_embark(self, event):
        """Toggles selected embark profile."""
        item = self.embark_files.index('active')
        if event.keysym == '??':
            item = self.embark_files.identify(event.y)

        if item is not None:
            embark_file = self.embark_files.get(item)
            files = embarks.get_installed_files()
            if embark_file in files:
                files.remove(embark_file)
            else:
                files.append(embark_file)
            embarks.install_embarks(files)
            self.read_embarks()
