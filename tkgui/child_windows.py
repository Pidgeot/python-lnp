#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import
"""Contains base class used for child windows."""

import os
from tkinter import *  # noqa: F403
from tkinter import messagebox
from tkinter.ttk import *  # noqa: F403

from core import errorlog, launcher, paths, terminal, update
from core.dfraw import DFRaw
from core.lnp import lnp

from . import controls


class ChildWindow(object):
    """Base class for child windows."""
    def __init__(self, parent, title):
        """
        Constructor for child windows.

        Args:
            parent: parent widget for the window.
            title: title for the window.
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

        Args:
            container: the frame the controls are to be created in.
        """

    def make_modal(self, on_cancel):
        """
        Change the window to work as a modal dialog.

        Args:
            on_cancel: method to be called if the user closes the window.
        """
        if self.parent.state() != "withdrawn":
            self.top.transient(self.parent)
        self.top.wait_visibility()
        self.top.grab_set()
        self.top.focus_set()
        self.top.protocol("WM_DELETE_WINDOW", on_cancel)
        self.top.wait_window(self.top)

    def close(self):
        """Called when the window is closed."""
        self.top.destroy()


class DualTextWindow(ChildWindow):
    """Window containing a row of buttons and two scrollable text fields."""
    def __init__(self, parent, title):
        self.f = None
        self.left = None
        self.left_scroll = None
        self.right = None
        self.right_scroll = None
        super().__init__(parent, title)

    def create_controls(self, container):
        self.create_buttons(container)

        self.f = f = Frame(container)
        Grid.rowconfigure(f, 0, weight=1)
        Grid.columnconfigure(f, 0, weight=1)
        Grid.columnconfigure(f, 2, weight=1)
        self.left = Text(f, width=40, height=20, wrap="word")
        self.left.grid(column=0, row=0, sticky="nsew")
        self.left_scroll = controls.create_scrollbar(
            f, self.left, column=1, row=0)
        self.right = Text(f, width=40, height=20, wrap="word")
        self.right.grid(column=2, row=0, sticky="nsew")
        self.right_scroll = controls.create_scrollbar(
            f, self.right, column=3, row=0)
        f.pack(side=BOTTOM, fill=BOTH, expand=Y)

    def create_buttons(self, container):
        """
        Creates buttons for this window. Must be overriden in child classes.

        Args:
            container: the frame the controls are to be created in.
        """


class LogWindow(DualTextWindow):
    """Window used for displaying an error log."""
    def __init__(self, parent):
        """
        Constructor for LogWindow.

        Args:
            parent: parent widget for the window.
        """
        super().__init__(parent, 'Output log')
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
        super().__init__(parent, 'Init Editor')
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
        self.left.insert('1.0', DFRaw.read(paths.get('init', 'init.txt')))
        self.right.delete('1.0', END)
        if os.path.isfile(paths.get('init', 'd_init.txt')):
            self.right.insert(
                '1.0', DFRaw.read(paths.get('init', 'd_init.txt')))
        else:
            Grid.columnconfigure(self.f, 2, weight=0)
            self.right.grid_forget()
            self.right_scroll.hidden = True

    def save(self):
        """Saves configuration data from the text widgets."""
        DFRaw.write(
            paths.get('init', 'init.txt'), self.left.get('1.0', 'end'))
        if os.path.isfile(paths.get('init', 'd_init.txt')):
            DFRaw.write(
                paths.get('init', 'd_init.txt'), self.right.get('1.0', 'end'))
        self.gui.load_params()


class SelectDF(ChildWindow):
    """Window to select an instance of Dwarf Fortress to operate on."""
    def __init__(self, parent, folders):
        """
        Constructor for SelectDF.

        Args:
            parent: parent widget for the window.
            folders: list of suitable folder paths.
        """
        self.parent = parent
        self.listvar = Variable(parent)
        self.folderlist = None
        super().__init__(parent, 'Select DF instance')
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
        self.folderlist.focus()
        ok = controls.Button(f, text='OK', command=self.ok, default='active')
        ok.grid(column=0, row=2, columnspan=2, sticky="s")
        self.top.bind('<Return>', lambda e, b=ok: b.invoke())
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
    def __init__(self, parent):
        """
        Constructor for UpdateWindow.

        Args:
            parent: parent widget for the window.
            lnp: reference to the PyLNP object.
        """
        self.parent = parent
        super().__init__(parent, 'Update available')
        self.make_modal(self.close)

    def create_controls(self, container):
        f = Frame(container)
        Label(
            f, text='An update is available (version '
            + str(lnp.new_version) + '). Download now?').grid(
                column=0, row=0)
        Label(f, text='You can control the frequency of update checks from the '
              'menu Options > Check for Updates.').grid(column=0, row=1)

        f.pack(fill=BOTH, expand=Y)

        buttons = Frame(container)
        if lnp.updater.get_direct_url():
            Button(
                buttons, text='Direct Download', command=self.download
            ).pack(side=LEFT)
        if lnp.updater.get_download_url():
            Button(
                buttons, text='Open in Browser', command=self.browser
            ).pack(side=LEFT)
        Button(
            buttons, text='Not now', command=self.close
        ).pack(side=LEFT)
        buttons.pack(side=BOTTOM)

    def browser(self):
        """Called when the browser button is clicked."""
        update.start_update()
        self.close()

    def download(self):
        """Called when the download button is clicked."""
        update.direct_download_pack()
        messagebox.showinfo(
            message='The updated pack is being downloaded. Once complete, the '
            'new pack will be extracted automatically.',
            title='Download in progress')
        self.close()


class ConfirmRun(ChildWindow):
    """Confirmation dialog for already running programs."""
    def __init__(self, parent, path, is_df):
        """
        Constructor for ConfirmRun.

        Args:
            parent: Parent widget for the window.
            lnp: Reference to the PyLNP object.
            path: Path to the executable.
            is_df: True if the program is DF itself.
        """
        self.parent = parent
        self.path = path
        self.is_df = is_df
        super().__init__(parent, 'Program already running')
        self.make_modal(self.close)

    def create_controls(self, container):
        f = Frame(container)
        f.after(20000, self.close)
        Label(
            f,
            text='The below program is already running. Launch it again?').grid(
                column=0, row=0)
        Label(f, text=self.path).grid(column=0, row=1)
        f.pack(fill=BOTH, expand=Y)

        buttons = Frame(container)
        Button(buttons, text='Yes', command=self.yes).pack(side=LEFT)
        Button(buttons, text='No', command=self.close).pack(side=LEFT)
        buttons.pack(side=BOTTOM)

    def yes(self):
        """Called when the Yes button is clicked."""
        if self.is_df:
            launcher.run_df()
        else:
            launcher.run_program(self.path)
        self.close()


class TerminalSelector(ChildWindow):
    """Used to select a terminal for launching child programs on Linux."""
    def __init__(self, parent, first_run):
        self.first_run = first_run
        super().__init__(parent, 'Configure terminal')
        self.running_test = False
        self.running_status = ''
        self.make_modal(self.top.destroy)

    def create_controls(self, container):
        f = Frame(container)
        Label(f, text='Please select which terminal should be used when '
              'launching programs requiring it (e.g. DFHack).').grid(
                  column=0, row=0)
        terminals = [t.name for t in terminal.get_valid_terminals()]
        self.term = StringVar(self.parent)
        if self.first_run:
            cur = terminals[0]
        else:
            try:
                cur = terminal.get_configured_terminal().name
            except NameError:
                pass
        self.term.set(cur)
        OptionMenu(f, self.term, self.term.get(), *terminals).grid(
            column=0, row=1)

        Label(f, text='If you use a custom command, put it here. Use $ as a '
              'placeholder for the actual command.\nIf no $ is used, '
              'the command will automatically be put at the end.').grid(
                  column=0, row=2)
        self.cmd = StringVar()
        self.cmd.set(terminal.get_custom_terminal_cmd())
        Entry(f, textvariable=self.cmd).grid(column=0, row=3, sticky='nsew')

        f.pack(fill=BOTH, expand=Y)

        buttons = Frame(container)
        Button(buttons, text='OK', command=self.close).pack(side=LEFT)
        Button(
            buttons, text='Test custom terminal',
            command=self.run_test).pack(side=LEFT)
        buttons.pack(side=BOTTOM)

    def close(self):
        terminal.configure_terminal(self.term.get())
        terminal.configure_custom_terminal(self.cmd.get())
        del self.term
        del self.cmd
        super().close()

    def run_test(self):
        """Tests the custom terminal provided to see if it works correctly."""
        if not messagebox.askokcancel(
                message="This will run a test to determine if your custom "
                "terminal command is working correctly.\n\n"
                "When you start the test, you will see one or two terminal "
                "windows spawn. If you do not see either of these windows, "
                "the terminal is not being launched correctly."
                "\n\nThe test may take anywhere from a few seconds to about a "
                "minute to execute. PyLNP will not respond until the test is "
                "complete.\n\nPress OK to start the test, or Cancel to abort.",
                title="PyLNP"):
            return
        try:
            terminal.configure_custom_terminal(self.cmd.get())
            r = terminal.terminal_test_run()
            if r[0]:
                messagebox.showinfo(message="Test successful.", title="PyLNP")
            else:
                messagebox.showerror(
                    message="Test failed: %s" % r[1], title="PyLNP")
        except Exception:
            messagebox.showerror(
                message="Test failed, see the log for details.", title="PyLNP")
