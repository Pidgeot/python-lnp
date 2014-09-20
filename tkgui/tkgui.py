#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name
"""TKinter-based GUI for PyLNP."""
from __future__ import print_function, unicode_literals, absolute_import

import os
import sys

from . import controls, binding
from .child_windows import LogWindow, InitEditor, SelectDF, UpdateWindow
from .child_windows import ConfirmRun

from .options import OptionsTab
from .graphics import GraphicsTab
from .utilities import UtilitiesTab
from .advanced import AdvancedTab
from .dfhack import DFHackTab

if sys.version_info[0] == 3:  # Alternate import names
    # pylint:disable=import-error
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.messagebox as messagebox
else:
    # pylint:disable=import-error
    from Tkinter import *
    from ttk import *
    import tkMessageBox as messagebox

# Workaround to use Pillow in PyInstaller
import pkg_resources  # pylint:disable=unused-import

try:  # PIL-compatible library (e.g. Pillow); used to load PNG images (optional)
    # pylint:disable=import-error,no-name-in-module
    from PIL import Image, ImageTk
    has_PIL = True
except ImportError:  # Some PIL installations live outside of the PIL package
    # pylint:disable=import-error,no-name-in-module
    try:
        import Image
        import ImageTk
        has_PIL = True
    except ImportError:  # No PIL compatible library
        has_PIL = False

has_PNG = has_PIL or (TkVersion >= 8.6)  # Tk 8.6 supports PNG natively

if not has_PNG:
    print(
        'Note: PIL not found and Tk version too old for PNG support ({0}).'
        'Falling back to GIF images.'.format(TkVersion), file=sys.stderr)


def get_image(filename):
    """
    Open the image with the appropriate extension.

    Params:
        filename
            The base name of the image file.

    Returns:
        A PhotoImage object ready to use with Tkinter.
    """
    if has_PNG:
        filename = filename + '.png'
    else:
        filename = filename + '.gif'
    if has_PIL:
        # pylint:disable=maybe-no-member
        return ImageTk.PhotoImage(Image.open(filename))
    else:
        return PhotoImage(file=filename)

def validate_number(value_if_allowed):
    """
    Validation method used by Tkinter. Accepts empty and float-coercable
    strings.

    Params:
        value_if_allowed
            Value to validate.

    Returns:
        True if value_if_allowed is empty, or can be interpreted as a float.
    """
    if value_if_allowed == '':
        return True
    try:
        float(value_if_allowed)
        return True
    except ValueError:
        return False


class TkGui(object):
    """Main GUI window."""
    def __init__(self, lnp):
        """
        Constructor for TkGui.

        Params:
            lnp
                A PyLNP instance to perform actual work.
        """
        self.lnp = lnp
        self.root = root = Tk()
        self.updateDays = IntVar()
        controls.init(self)
        binding.init(lnp)

        root.option_add('*tearOff', FALSE)
        windowing = root.tk.call('tk', 'windowingsystem')
        if windowing == "win32":
            root.tk.call(
                'wm', 'iconbitmap', root, "-default",
                self.get_image_path('LNP.ico'))
        elif windowing == "x11":
            root.tk.call(
                'wm', 'iconphoto', root, "-default",
                get_image(self.get_image_path('LNP')))
        elif windowing == "aqua":  # OS X has no window icons
            pass

        root.title("PyLNP")
        self.vcmd = (root.register(validate_number), '%P')

        main = Frame(root)
        self.logo = logo = get_image(self.get_image_path('LNPSMALL'))
        Label(root, image=logo).pack()
        main.pack(side=TOP, fill=BOTH, expand=Y)
        self.n = n = Notebook(main)

        self.tabs = []
        self.create_tab(OptionsTab, 'Options')
        self.create_tab(GraphicsTab, 'Graphics')
        self.create_tab(UtilitiesTab, 'Utilities')
        self.create_tab(AdvancedTab, 'Advanced')
        if self.lnp.config.get_list('dfhack'):
            self.create_tab(DFHackTab, 'DFHack')
        n.enable_traversal()
        n.pack(fill=BOTH, expand=Y, padx=2, pady=3)

        main_buttons = Frame(main)
        main_buttons.pack(side=BOTTOM)

        controls.create_trigger_button(
            main_buttons, 'Play Dwarf Fortress!', 'Play the game!',
            self.lnp.run_df).grid(column=0, row=0, sticky="nsew")
        controls.create_trigger_button(
            main_buttons, 'Init Editor',
            'Edit init and d_init in a built-in text editor',
            self.run_init).grid(column=1, row=0, sticky="nsew")
        controls.create_trigger_button(
            main_buttons, 'Defaults', 'Reset everything to default settings',
            self.restore_defaults).grid(column=2, row=0, sticky="nsew")

        self.create_menu(root)

        if not self.ensure_df():
            return
        binding.update()
        for tab in self.tabs:
            tab.on_post_df_load()
        root.bind('<<UpdateAvailable>>', lambda e: UpdateWindow(
            self.root, self.lnp, self.updateDays))
        root.minsize(width=root.winfo_width(), height=root.winfo_height())

    def start(self):
        """Starts the UI."""
        self.root.mainloop()

    def on_update_available(self):
        """Called by the main LNP class if an update is available."""
        self.root.event_generate('<<UpdateAvailable>>', when='tail')

    def on_program_running(self, path, is_df):
        """Called by the main LNP class if a program is already running."""
        ConfirmRun(self.root, self.lnp, path, is_df)

    def create_tab(self, class_, caption):
        """
        Creates a new tab and adds it to the main Notebook.

        Params:
            class_
                Reference to the class representing the tab.
            caption
                Caption for the newly created tab.
        """
        tab = class_(self.lnp, self.n)
        self.n.add(tab, text=caption)
        self.tabs.append(tab)

    def ensure_df(self):
        """Ensures a DF installation is active before proceeding."""
        if self.lnp.df_dir == '':
            if self.lnp.folders:
                selector = SelectDF(self.root, self.lnp.folders)
                if selector.result == '':
                    messagebox.showerror(
                        self.root.title(),
                        'No Dwarf Fortress install was selected, quitting.')
                    self.root.destroy()
                    return False
                else:
                    try:
                        self.lnp.set_df_folder(selector.result)
                    except IOError as e:
                        messagebox.showerror(self.root.title(), e.message)
                        self.exit_program()
                        return False
            else:
                messagebox.showerror(
                    self.root.title(),
                    "Could not find Dwarf Fortress, quitting.")
                self.root.destroy()
                return False
        return True


    def get_image_path(self, filename):
        """
        Returns <filename> with its expected path. If running in a bundle,
        this will point to the place internal resources are located; if running
        the script directly, no modification takes place.
        """
        if self.lnp.bundle == 'osx':
            # Image is inside application bundle on OS X
            return os.path.join(
                os.path.dirname(sys.executable), filename)
        elif self.lnp.bundle in ['win', 'linux']:
            # Image is inside executable on Linux and Windows
            # pylint: disable=protected-access, no-member, maybe-no-member
            return os.path.join(sys._MEIPASS, filename)
        else:
            return filename

    def create_menu(self, root):
        """
        Creates the menu bar.

        Params:
            root
                Root window for the menu bar.
        """
        menubar = Menu(root)
        root['menu'] = menubar

        menu_file = Menu(menubar)
        menu_run = Menu(menubar)
        menu_folders = Menu(menubar)
        menu_links = Menu(menubar)
        menu_help = Menu(menubar)
        #menu_beta = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_run, label='Run')
        menubar.add_cascade(menu=menu_folders, label='Folders')
        menubar.add_cascade(menu=menu_links, label='Links')
        menubar.add_cascade(menu=menu_help, label='Help')
        #menubar.add_cascade(menu=menu_beta, label='Testing')

        menu_file.add_command(
            label='Re-load param set', command=self.load_params,
            accelerator='Ctrl+L')
        menu_file.add_command(
            label='Re-save param set', command=self.save_params,
            accelerator='Ctrl+S')
        menu_file.add_command(
            label='Output log', command=lambda: LogWindow(self.root))
        if self.lnp.updates_configured():
            menu_updates = menu_updates = Menu(menubar)
            menu_file.add_cascade(menu=menu_updates, label='Check for updates')
            options = [
                "every launch", "1 day", "3 days", "7 days", "14 days",
                "30 days", "Never"]
            daylist = [0, 1, 3, 7, 14, 30, -1]
            self.updateDays.set(self.lnp.userconfig.get_number('updateDays'))
            for i, o in enumerate(options):
                menu_updates.add_radiobutton(
                    label=o, value=daylist[i], variable=self.updateDays,
                    command=lambda i=i: self.configure_updates(daylist[i]))

        if sys.platform != 'darwin':
            menu_file.add_command(
                label='Exit', command=self.exit_program, accelerator='Alt+F4')
        root.bind_all('<Control-l>', lambda e: self.load_params())
        root.bind_all('<Control-s>', lambda e: self.save_params())

        menu_run.add_command(
            label='Dwarf Fortress', command=self.lnp.run_df,
            accelerator='Ctrl+R')
        menu_run.add_command(
            label='Init Editor', command=self.run_init, accelerator='Ctrl+I')
        root.bind_all('<Control-r>', lambda e: self.lnp.run_df())
        root.bind_all('<Control-i>', lambda e: self.run_init())

        self.populate_menu(
            self.lnp.config.get_list('folders'), menu_folders,
            self.lnp.open_folder_idx)
        self.populate_menu(
            self.lnp.config.get_list('links'), menu_links,
            self.lnp.open_link_idx)

        menu_help.add_command(
            label="Help", command=self.show_help, accelerator='F1')
        menu_help.add_command(
            label="About", command=self.show_about, accelerator='Alt+F1')
        root.bind_all('<F1>', lambda e: self.show_help())
        root.bind_all('<Alt-F1>', lambda e: self.show_about())
        root.createcommand('tkAboutDialog', self.show_about)

    def configure_updates(self, days):
        """Sets the number of days until next update check."""
        self.updateDays.set(days)
        self.lnp.next_update(days)

    @staticmethod
    def populate_menu(collection, menu, method):
        """
        Populates a menu with items from a collection.

        Params:
            collection
                A collection of menu item data.
            menu
                The menu to create the items under.
            method
                The method to be called when the menu item is selected.
        """
        #pylint:disable=unused-variable
        for i, f in enumerate(collection):
            if f[0] == '-':
                menu.add_separator()
            else:
                menu.add_command(label=f[0], command=lambda i=i: method(i))

    def change_entry(self, key, var):
        """
        Commits a change for the control specified by key.

        Params:
            key
                The key for the control that changed.
            var
                The variable bound to the control.
        """
        if var.get() != '':
            self.lnp.set_option(key, var.get())

    def load_params(self):
        """Reads configuration data."""
        try:
            self.lnp.load_params()
        except IOError as e:
            messagebox.showerror(self.root.title(), e.message)
            self.exit_program()
        binding.update()

    def save_params(self):
        """Writes configuration data."""
        self.lnp.save_params()

    def restore_defaults(self):
        """Restores default configuration data."""
        if messagebox.askyesno(
                message='Are you sure? '
                'ALL SETTINGS will be reset to game defaults.\n'
                'You may need to re-install graphics afterwards.',
                title='Reset all settings to Defaults?', icon='question'):
            self.lnp.restore_defaults()
            messagebox.showinfo(
                self.root.title(),
                'All settings reset to defaults!')

    def exit_program(self):
        """Quits the program."""
        self.root.destroy()

    def run_program(self, path):
        """
        Launches another program.

        Params:
            path
                Path to the program to launch.
        """
        path = os.path.abspath(path)
        self.lnp.run_program(path)

    def run_init(self):
        """Opens the init editor."""
        InitEditor(self.root, self)

    @staticmethod
    def show_help():
        """Shows help for the program."""
        messagebox.showinfo(title='How to Use', message="It's really easy.")

    @staticmethod
    def show_about():
        """Shows about dialog for the program."""
        messagebox.showinfo(
            title='About', message="PyLNP - Lazy Newb Pack Python Edition\n\n"
            "Port by Pidgeot\n\nOriginal program: LucasUP, TolyK/aTolyK")

    def cycle_option(self, field):
        """
        Cycles through possible values for an option.

        Params:
            field
                The option to cycle.
        """
        self.lnp.cycle_option(field)
        binding.update()

    def set_option(self, field):
        """
        Sets an option directly.

        Params:
            field
                The field name to change. The corresponding value is
                automatically read.
        """
        self.lnp.set_option(field, binding.get(field))
        binding.update()


# vim:expandtab
