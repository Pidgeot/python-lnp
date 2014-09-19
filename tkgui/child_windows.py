#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import, invalid-name
"""Contains base class used for child windows."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, errorlog

from . import controls

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *

class ChildWindow(object):
    """Base class for child windows."""
    def __init__(self, parent, title):
        """
        Constructor for child windows.

        Params:
            parent
                Parent widget for the window.
            title
                Title for the window.
        """
        top = self.top = Toplevel(parent)
        self.parent = parent
        top.title(title)
        f = Frame(top)
        self.create_controls(f)
        f.pack(fill=BOTH, expand=Y)

    def create_controls(self, container):
        """
        Constructs controls for the window. To be overridden in child classes.

        Params:
            container
                The frame the controls are to be created in.
        """
        pass

    def make_modal(self, on_cancel):
        """
        Change the window to work as a modal dialog.

        Params:
            on_cancel
                Method to be called if the user closes the window.
        """
        self.top.transient(self.parent)
        self.top.wait_visibility()
        self.top.grab_set()
        self.top.focus_set()
        self.top.protocol("WM_DELETE_WINDOW", on_cancel)
        self.top.wait_window(self.top)

class DualTextWindow(ChildWindow):
    """Window containing a row of buttons and two scrollable text fields."""
    def __init__(self, parent, title):
        self.left = None
        self.right = None
        super(DualTextWindow, self).__init__(parent, title)

    def create_controls(self, container):
        self.create_buttons(container)

        f = Frame(container)
        Grid.rowconfigure(f, 0, weight=1)
        Grid.columnconfigure(f, 0, weight=1)
        Grid.columnconfigure(f, 2, weight=1)
        self.left = Text(f, width=40, height=20, wrap="word")
        self.left.grid(column=0, row=0, sticky="nsew")
        controls.create_scrollbar(f, self.left, column=1, row=0)
        self.right = Text(f, width=40, height=20, wrap="word")
        self.right.grid(column=2, row=0, sticky="nsew")
        controls.create_scrollbar(f, self.right, column=3, row=0)
        f.pack(side=BOTTOM, fill=BOTH, expand=Y)

    def create_buttons(self, container):
        """
        Creates buttons for this window. Must be overriden in child classes.

        Params:
            container
                The frame the controls are to be created in.
        """
        pass

class LogWindow(DualTextWindow):
    """Window used for displaying an error log."""
    def __init__(self, parent):
        """
        Constructor for LogWindow.

        Params:
            parent
                Parent widget for the window.
        """
        super(LogWindow, self).__init__(parent, 'Output log')
        self.load()

    def create_buttons(self, container):
        f = Frame(container)
        Button(f, text='Refresh', command=self.load).pack(side=LEFT)
        f.pack(side=TOP, anchor='w')

    def load(self):
        """Loads log data into the text widgets."""
        self.left.delete('1.0', END)
        self.right.delete('1.0', END)
        self.left.insert('1.0', '\n'.join(errorlog.out.lines))
        self.right.insert('1.0', '\n'.join(errorlog.err.lines))

class InitEditor(DualTextWindow):
    """Basic editor for d_init.txt and init.txt."""
    def __init__(self, parent, gui):
        super(InitEditor, self).__init__(parent, 'Init Editor')
        self.gui = gui
        self.load()

    def create_buttons(self, container):
        f = Frame(container)
        Button(f, text="Load", command=self.load).pack(side=LEFT)
        Button(f, text="Save", command=self.save).pack(side=LEFT)
        f.pack(side=TOP, anchor="w")

    def load(self):
        """Loads configuration data into the text widgets."""
        self.gui.save_params()
        self.left.delete('1.0', END)
        self.left.insert('1.0', open(
            os.path.join(self.gui.lnp.init_dir, 'init.txt')).read())
        self.right.delete('1.0', END)
        self.right.insert('1.0', open(
            os.path.join(self.gui.lnp.init_dir, 'd_init.txt')).read())

    def save(self):
        """Saves configuration data from the text widgets."""
        f = open(os.path.join(self.gui.lnp.init_dir, 'init.txt'), 'w')
        f.write(self.left.get('1.0', 'end'))
        f.close()
        f = open(os.path.join(self.gui.lnp.init_dir, 'd_init.txt'), 'w')
        f.write(self.right.get('1.0', 'end'))
        f.close()
        self.gui.load_params()

class SelectDF(ChildWindow):
    """Window to select an instance of Dwarf Fortress to operate on."""
    def __init__(self, parent, folders):
        """
        Constructor for SelectDF.

        Params:
            parent
                Parent widget for the window.
            folders
                List of suitable folder paths.
        """
        self.parent = parent
        self.listvar = Variable(parent)
        self.folderlist = None
        super(SelectDF, self).__init__(parent, 'Select DF instance')
        self.result = ''
        self.listvar.set(folders)
        self.make_modal(self.cancel)

    def create_controls(self, container):
        f = Frame(container)
        Grid.rowconfigure(f, 1, weight=1)
        Grid.columnconfigure(f, 0, weight=1)
        Label(
            f, text='Please select the Dwarf Fortress folder '
            'you would like to use.').grid(column=0, row=0, columnspan=2)
        self.folderlist = Listbox(
            f, listvariable=self.listvar, activestyle='dotbox')
        self.folderlist.grid(column=0, row=1, sticky="nsew")
        controls.create_scrollbar(f, self.folderlist, column=1, row=1)
        Button(
            f, text='OK', command=self.ok
            ).grid(column=0, row=2, columnspan=2, sticky="s")
        self.folderlist.bind("<Double-1>", lambda e: self.ok())
        f.pack(fill=BOTH, expand=Y)

    def ok(self):
        """Called when the OK button is clicked."""
        if len(self.folderlist.curselection()) != 0:
            self.result = self.folderlist.get(self.folderlist.curselection()[0])
            self.top.protocol('WM_DELETE_WINDOW', None)
            self.top.destroy()

    def cancel(self):
        """Called when the Cancel button is clicked."""
        self.top.destroy()

class UpdateWindow(ChildWindow):
    """Notification of a new update."""
    def __init__(self, parent, lnp, parentVar):
        """
        Constructor for UpdateWindow.

        Params:
            parent
                Parent widget for the window.
            lnp
                Reference to the PyLNP object.
        """
        self.parent = parent
        self.lnp = lnp
        self.parentVar = parentVar
        self.options = [
            "next launch", "1 day", "3 days", "7 days", "14 days", "30 days",
            "Never"]
        self.daylist = [0, 1, 3, 7, 14, 30, -1]
        self.var = StringVar(parent)
        super(UpdateWindow, self).__init__(parent, 'Update available')
        self.make_modal(self.close)

    def create_controls(self, container):
        f = Frame(container)
        Grid.rowconfigure(f, 1, weight=1)
        Grid.columnconfigure(f, 0, weight=1)
        Label(
            f, text='Update is available (version '+str(self.lnp.new_version) +
            '). Update now?').grid(column=0, row=0, columnspan=2)
        Label(f, text='Check again in').grid(column=0, row=1)

        try:
            default_idx = self.daylist.index(
                self.lnp.userconfig.get_number('updateDays'))
        except ValueError:
            default_idx = 0
        self.var.set(self.options[default_idx])
        OptionMenu(f, self.var, self.options[default_idx], *self.options).grid(
            column=1, row=1)
        f.pack(fill=BOTH, expand=Y)

        buttons = Frame(container)
        Button(
            buttons, text='Yes', command=self.yes
            ).pack(side=LEFT)
        Button(
            buttons, text='No', command=self.close
            ).pack(side=LEFT)
        buttons.pack(side=BOTTOM, anchor="e")

    def yes(self):
        """Called when the Yes button is clicked."""
        self.lnp.start_update()
        self.close()

    def close(self):
        """Called when the window is closed."""
        days = self.daylist[self.options.index(self.var.get())]
        self.parentVar.set(days)
        self.lnp.next_update(days)
        self.top.destroy()
