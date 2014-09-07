#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import
"""TKinter-based GUI for PyLNP."""
from __future__ import print_function, unicode_literals, absolute_import

import os
import sys

from . import controls, binding
from .child_windows import LogWindow, InitEditor, SelectDF, UpdateWindow

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

        root.resizable(0, 0)
        root.title("PyLNP")
        self.vcmd = (root.register(validate_number), '%P')
        self.keybinds = Variable(root)
        self.graphics = Variable(root)
        self.progs = Variable(root)
        self.colors = Variable(root)
        self.embarks = Variable(root)

        self.volume_var = StringVar()
        self.fps_var = StringVar()
        self.gps_var = StringVar()

        self.proglist = None
        self.color_files = None
        self.color_preview = None
        self.hacklist = None
        self.hack_tooltip = None

        main = Frame(root)
        logo = get_image(self.get_image_path('LNPSMALL'))
        Label(root, image=logo).pack()
        main.pack(side=TOP, fill=BOTH, expand=Y)
        n = Notebook(main)
        n.add(self.create_options(n), text='Options')
        n.add(self.create_graphics(n), text='Graphics')
        n.add(self.create_utilities(n), text='Utilities')
        n.add(self.create_advanced(n), text='Advanced')
        if self.lnp.config.get_list('dfhack'):
            n.add(self.create_dfhack(n), text='DFHack')
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

        if lnp.df_dir == '':
            if lnp.folders:
                selector = SelectDF(self.root, lnp.folders)
                if selector.result == '':
                    messagebox.showerror(
                        self.root.title(),
                        'No Dwarf Fortress install was selected, quitting.')
                    self.root.destroy()
                    return
                else:
                    try:
                        lnp.set_df_folder(selector.result)
                    except IOError as e:
                        messagebox.showerror(self.root.title(), e.message)
                        self.exit_program()
                        return
            else:
                messagebox.showerror(
                    self.root.title(),
                    "Could not find Dwarf Fortress, quitting.")
                self.root.destroy()
                return

        self.read_keybinds()
        self.read_graphics()
        self.read_utilities()
        binding.update()
        self.read_colors()
        self.read_embarks()
        if self.lnp.config.get_list('dfhack'):
            self.update_hack_list()

        if self.lnp.new_version is not None:
            UpdateWindow(self.root, self.lnp)

        root.mainloop()

    def get_image_path(self, filename):
        """
        Returns <filename> with its expected path. If running in a bundle,
        this will point to the place internal resources are located; if running
        the script directly, no modification takes place.
        """
        if self.lnp.bundle == 'osx':
            # Image is inside application bundle on OS X
            return os.path.join(
                os.path.dirname(sys.executable), '..', 'Resources', filename)
        elif self.lnp.bundle in ['win', 'linux']:
            # Image is inside executable on Linux and Windows
            # pylint: disable=protected-access, no-member, maybe-no-member
            return os.path.join(sys._MEIPASS, filename)
        else:
            return filename

    def create_options(self, n):
        """
        Creates the Options tab.

        Params:
            n
                Notebook instance to create the tab in.
        """
        f = Frame(n)
        f.pack(side=TOP, fill=BOTH, expand=Y)
        options = controls.create_control_group(f, 'Options', True)
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
            f, 'Modifications')
        mods.pack(side=TOP, expand=N, anchor="w")

        controls.create_option_button(
            mods, 'Aquifers', 'Whether newly created worlds will have Aquifers '
            'in them (Infinite sources of underground water, but may flood '
            'your fort', 'aquifers').grid(column=0, row=0, sticky="nsew")

        keybindings, keybinding_files, _ = \
            controls.create_file_list_buttons(
                f, 'Key Bindings', self.keybinds,
                lambda: self.load_keybinds(keybinding_files),
                self.read_keybinds, self.save_keybinds,
                lambda: self.delete_keybinds(keybinding_files))
        keybindings.pack(side=BOTTOM, fill=BOTH, expand=Y)

        embarks, embark_files, _ = \
            controls.create_readonly_file_list_buttons(
                f, 'Embark profiles', self.embarks,
                lambda: self.install_embarks(embark_files),
                self.read_embarks, selectmode='multiple')
        embarks.pack(side=BOTTOM, fill=BOTH, expand=Y)

        return f

    def create_graphics(self, n):
        """
        Creates the Graphics tab.

        Params:
            n
                Notebook instance to create the tab in.
        """
        f = Frame(n)
        f.pack(side=TOP, fill=BOTH, expand=Y)

        change_graphics = controls.create_control_group(
            f, 'Change Graphics', True)
        change_graphics.pack(side=TOP, fill=BOTH, expand=Y)

        curr_pack = Label(change_graphics, text='Current Graphics')
        curr_pack.grid(column=0, row=0, columnspan=2, sticky="nsew")
        binding.bind(curr_pack, 'FONT', lambda x: self.lnp.current_pack())

        listframe = Frame(change_graphics)
        listframe.grid(column=0, row=1, columnspan=2, sticky="nsew", pady=4)
        _, graphicpacks = controls.create_file_list(
            listframe, None, self.graphics, height=8)

        controls.create_trigger_button(
            change_graphics, 'Install Graphics',
            'Install selected graphics pack',
            lambda: self.install_graphics(graphicpacks)).grid(
                column=0, row=2, sticky="nsew")
        controls.create_trigger_button(
            change_graphics, 'Update Savegames',
            'Install current graphics pack in all savegames',
            self.update_savegames).grid(column=1, row=2, sticky="nsew")
        controls.create_option_button(
            change_graphics, 'TrueType Fonts',
            'Toggles whether to use TrueType fonts or tileset for text',
            'truetype').grid(column=0, row=3, columnspan=2, sticky="nsew")

        advanced = controls.create_control_group(
            f, 'Advanced', True)
        advanced.pack(side=BOTTOM, fill=X, expand=Y)

        controls.create_trigger_button(
            advanced, 'Open Graphics Folder',
            'Add your own graphics packs here!', self.lnp.open_graphics).grid(
                column=0, row=0, columnspan=2, sticky="nsew")
        controls.create_trigger_button(
            advanced, 'Refresh List', 'Refresh list of graphics packs',
            self.read_graphics).grid(column=0, row=1, sticky="nsew")
        controls.create_trigger_button(
            advanced, 'Simplify Graphic Folders',
            'Deletes unnecessary files from graphics packs '
            '(saves space, useful for re-packaging)',
            self.simplify_graphics).grid(column=1, row=1, sticky="nsew")

        colors, color_files, buttons = \
            controls.create_file_list_buttons(
                f, 'Color schemes', self.colors,
                lambda: self.load_colors(color_files),
                self.read_colors, self.save_colors,
                lambda: self.delete_colors(color_files))
        colors.pack(side=BOTTOM, fill=BOTH, expand=Y, anchor="s")
        buttons.grid(rowspan=3)

        self.color_files = color_files
        color_files.bind(
            '<<ListboxSelect>>',
            lambda e: self.paint_color_preview(color_files))

        self.color_preview = Canvas(
            colors, width=128, height=32, highlightthickness=0, takefocus=False)
        self.color_preview.grid(column=0, row=2)

        return f

    def create_utilities(self, n):
        """
        Creates the Utilities tab.

        Params:
            n
                Notebook instance to create the tab in.
        """
        f = Frame(n)
        f.pack(side=TOP, fill=BOTH, expand=Y)

        progs = controls.create_control_group(
            f, 'Programs/Utilities', True)
        progs.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.rowconfigure(progs, 3, weight=1)

        controls.create_trigger_button(
            progs, 'Run Program', 'Runs the selected program(s).',
            self.run_selected_utilities).grid(column=0, row=0, sticky="nsew")
        controls.create_trigger_button(
            progs, 'Open Utilities Folder', 'Open the utilities folder',
            self.lnp.open_utils).grid(column=1, row=0, sticky="nsew")
        Label(
            progs, text='Double-click on a program to launch it.').grid(
                column=0, row=1, columnspan=2)
        Label(
            progs, text='Right-click on a program to toggle auto-launch.').grid(
                column=0, row=2, columnspan=2)

        self.proglist = proglist = controls.create_toggle_list(
            progs, ('exe', 'launch'),
            {'column': 0, 'row': 3, 'columnspan': 2, 'sticky': "nsew"})
        proglist.column('exe', width=1, anchor='w')
        proglist.column('launch', width=35, anchor='e', stretch=NO)
        proglist.heading('exe', text='Executable')
        proglist.heading('launch', text='Auto')
        proglist.bind("<Double-1>", lambda e: self.run_selected_utilities())
        if sys.platform == 'darwin':
            proglist.bind("<2>", self.toggle_autorun)
        else:
            proglist.bind("<3>", self.toggle_autorun)

        refresh = controls.create_trigger_button(
            progs, 'Refresh List', 'Refresh the list of utilities',
            self.read_utilities)
        refresh.grid(column=0, row=4, columnspan=2, sticky="nsew")
        return f

    def create_advanced(self, n):
        """
        Creates the Advanced tab.

        Params:
            n
                Notebook instance to create the tab in.
        """
        f = Frame(n)
        f.pack(side=TOP, fill=BOTH, expand=Y)
        Grid.columnconfigure(f, 0, weight=1)
        Grid.columnconfigure(f, 1, weight=1)

        sound = controls.create_control_group(f, 'Sound')
        sound.grid(column=0, row=0, sticky="nsew")

        controls.create_option_button(
            sound, 'Sound', 'Turn game music on/off', 'sound').pack(side=LEFT)
        controls.create_numeric_entry(
            sound, self.volume_var, 'volume', 'Music volume (0 to 255)').pack(
                side=LEFT)
        Label(sound, text='/255').pack(side=LEFT)

        fps = controls.create_control_group(f, 'FPS')
        fps.grid(column=1, row=0, rowspan=2, sticky="nsew")

        controls.create_option_button(
            fps, 'FPS Counter', 'Whether or not to display your FPS',
            'fpsCounter').pack(fill=BOTH)
        Label(fps, text='Calculation FPS Cap:').pack(anchor="w")
        controls.create_numeric_entry(
            fps, self.fps_var, 'fpsCap', 'How fast the game runs').pack(
                anchor="w")
        Label(fps, text='Graphical FPS Cap:').pack(anchor="w")
        controls.create_numeric_entry(
            fps, self.gps_var, 'gpsCap', 'How fast the game visually updates.\n'
            'Lower value may give small boost to FPS but will be less '
            'reponsive.').pack(anchor="w")

        startup = controls.create_control_group(f, 'Startup')
        startup.grid(column=0, row=1, sticky="nsew")
        Grid.columnconfigure(startup, 0, weight=1)

        controls.create_option_button(
            startup, 'Intro Movie',
            'Do you want to see the beautiful ASCII intro movie?',
            'introMovie').grid(column=0, row=0, sticky="nsew")
        controls.create_option_button(
            startup, 'Windowed', 'Start windowed or fullscreen',
            'startWindowed').grid(column=0, row=1, sticky="nsew")

        saverelated = controls.create_control_group(
            f, 'Save-related', True)
        saverelated.grid(column=0, row=2, columnspan=2, sticky="nsew")

        controls.create_option_button(
            saverelated, 'Autosave',
            'How often the game will automatically save', 'autoSave').grid(
                column=0, row=0, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Initial Save', 'Saves as soon as you embark',
            'initialSave').grid(column=1, row=0, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Pause on Save', 'Pauses the game after auto-saving',
            'autoSavePause').grid(column=0, row=1, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Pause on Load', 'Pauses the game as soon as it loads',
            'pauseOnLoad').grid(column=1, row=1, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Backup Saves', 'Makes a backup of every autosave',
            'autoBackup').grid(column=0, row=2, sticky="nsew")
        controls.create_option_button(
            saverelated, 'Compress Saves', 'Whether to compress the savegames '
            '(keep this on unless you experience problems with your saves',
            'compressSaves').grid(column=1, row=2, sticky="nsew")
        controls.create_trigger_button(
            saverelated, 'Open Savegame Folder', 'Open the savegame folder',
            self.lnp.open_savegames).grid(
                column=0, row=3, columnspan=2, sticky="nsew")

        Frame(f, height=30).grid(column=0, row=3)
        controls.create_option_button(
            f, 'Processor Priority',
            'Adjusts the priority given to Dwarf Fortress by your OS',
            'procPriority').grid(column=0, row=4, columnspan=2, sticky="nsew")

        controls.create_trigger_option_button(
            f, 'Close GUI on launch',
            'Whether this GUI should close when Dwarf Fortress is launched',
            self.toggle_autoclose, 'autoClose', lambda v: ('NO', 'YES')[
                self.lnp.userconfig.get_bool('autoClose')]).grid(
                    column=0, row=5, columnspan=2, sticky="nsew")
        return f

    def create_dfhack(self, n):
        """
        Creates the DFHack tab.

        Params:
            n
                Notebook instance to create the tab in.
        """
        f = Frame(n)
        f.pack(side=TOP, fill=BOTH, expand=Y)
        hacks = Labelframe(f, text='Available hacks')
        hacks.pack(side=TOP, expand=Y, fill=BOTH)
        Grid.columnconfigure(hacks, 0, weight=1)
        Grid.rowconfigure(hacks, 1, weight=1)

        Label(
            hacks, text='Click on a hack to toggle it.').grid(
                column=0, row=0)

        self.hacklist = hacklist = controls.create_toggle_list(
            hacks, ('name', 'enabled'),
            {'column': 0, 'row': 1, 'sticky': "nsew"},
            {'selectmode': 'browse'})
        hacklist.column('name', width=1, anchor='w')
        hacklist.column('enabled', width=50, anchor='c', stretch=NO)
        hacklist.heading('name', text='Hack')
        hacklist.heading('enabled', text='Enabled')
        hacklist.grid(column=0, row=0, sticky="nsew")
        hacklist.bind("<<TreeviewSelect>>", lambda e: self.toggle_hack())

        self.hack_tooltip = controls.create_tooltip(hacklist, '')
        hacklist.bind('<Motion>', self.update_hack_tooltip)
        return f

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

    def update_hack_tooltip(self, event):
        """
        Event handler for mouse motion over the hack list.
        Used to update the tooltip.
        """
        item = self.lnp.get_hack(self.hacklist.item(self.hacklist.identify(
            'row', event.x, event.y))['text'])
        if item:
            self.hack_tooltip.settext(item['tooltip'])
        else:
            self.hack_tooltip.settext('')

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
        menu_beta = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_run, label='Run')
        menubar.add_cascade(menu=menu_folders, label='Folders')
        menubar.add_cascade(menu=menu_links, label='Links')
        menubar.add_cascade(menu=menu_help, label='Help')
        menubar.add_cascade(menu=menu_beta, label='Testing')

        menu_file.add_command(
            label='Re-load param set', command=self.load_params,
            accelerator='Ctrl+L')
        menu_file.add_command(
            label='Re-save param set', command=self.save_params,
            accelerator='Ctrl+S')
        menu_file.add_command(
            label='Output log', command=lambda: LogWindow(self.root))
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

        # pylint:disable=unused-variable
        for i, f in enumerate(self.lnp.config['folders']):
            if f[0] == '-':
                menu_folders.add_separator()
            else:
                menu_folders.add_command(
                    label=f[0],
                    command=lambda i=i: self.lnp.open_folder_idx(i))

        for i, f in enumerate(self.lnp.config['links']):
            if f[0] == '-':
                menu_links.add_separator()
            else:
                menu_links.add_command(
                    label=f[0],
                    command=lambda i=i: self.lnp.open_link_idx(i))

        menu_help.add_command(
            label="Help", command=self.show_help, accelerator='F1')
        menu_help.add_command(
            label="About", command=self.show_about, accelerator='Alt+F1')
        root.bind_all('<F1>', lambda e: self.show_help())
        root.bind_all('<Alt-F1>', lambda e: self.show_about())
        root.createcommand('tkAboutDialog', self.show_about)

        menu_beta.add_command(
            label='Toggle graphics pack patching', command=self.toggle_patching)

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

    def read_keybinds(self):
        """Reads list of keybinding files."""
        self.keybinds.set(self.lnp.read_keybinds())

    def read_graphics(self):
        """Reads list of graphics packs."""
        self.graphics.set(tuple([p[0] for p in self.lnp.read_graphics()]))

    def read_utilities(self):
        """Reads list of utilities."""
        self.progs = self.lnp.read_utilities()
        self.update_autorun_list()

    def read_colors(self):
        """Reads list of color schemes."""
        self.colors.set(self.lnp.read_colors())
        self.paint_color_preview(self.color_files)

    def read_embarks(self):
        """Reads list of embark profiles."""
        self.embarks.set(self.lnp.read_embarks())

    def toggle_autorun(self, event):
        """
        Toggles autorun for a utility.

        Params:
            event
                Data for the click event that triggered this.
        """
        self.lnp.toggle_autorun(self.proglist.item(self.proglist.identify(
            'row', event.x, event.y), 'text'))
        self.update_autorun_list()

    def update_autorun_list(self):
        """Updates the autorun list."""
        for i in self.proglist.get_children():
            self.proglist.delete(i)
        for p in self.progs:
            exe = os.path.join(
                os.path.basename(os.path.dirname(p)), os.path.basename(p))
            if self.lnp.config["hideUtilityPath"]:
                exe = os.path.basename(exe)
            if self.lnp.config["hideUtilityExt"]:
                exe = os.path.splitext(exe)[0]
            self.proglist.insert('', 'end', text=p, values=(
                exe, 'Yes' if p in self.lnp.autorun else 'No'))

    def set_pop_cap(self):
        """Requests new population cap from the user."""
        v = simpledialog.askinteger(
            "Settings", "Population cap:",
            initialvalue=self.lnp.settings.popcap, parent=self.root)
        if v is not None:
            self.lnp.set_option('popcap', str(v))
            binding.update()

    def set_child_cap(self):
        """Requests new child cap from the user."""
        child_split = list(self.lnp.settings.childcap.split(':'))
        child_split.append('0')  # In case syntax is invalid
        v = simpledialog.askinteger(
            "Settings", "Absolute cap on babies + children:",
            initialvalue=child_split[0], parent=self.root)
        if v is not None:
            v2 = simpledialog.askinteger(
                "Settings", "Max percentage of children in fort:\n"
                "(lowest of the two values will be used as the cap)",
                initialvalue=child_split[1], parent=self.root)
            if v2 is not None:
                self.lnp.set_option('childcap', str(v)+':'+str(v2))
                binding.update()

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
            "Save Keybindings", "Save current keybindings as:",
            parent=self.root)
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

    def load_colors(self, listbox):
        """
        Replaces color scheme  with selected file.

        Params:
            listbox
                Listbox containing the list of color schemes.
        """
        if len(listbox.curselection()) != 0:
            self.lnp.load_colors(listbox.get(listbox.curselection()[0]))

    def save_colors(self):
        """Saves color scheme to a file."""
        v = simpledialog.askstring(
            "Save Color scheme", "Save current color scheme as:",
            parent=self.root)
        if v is not None:
            if (not self.lnp.color_exists(v) or messagebox.askyesno(
                    message='Overwrite {0}?'.format(v),
                    icon='question', title='Overwrite file?')):
                self.lnp.save_colors(v)
                self.read_colors()

    def delete_colors(self, listbox):
        """
        Deletes a color scheme.

        Params:
            listbox
                Listbox containing the list of color schemes.
        """
        if len(listbox.curselection()) != 0:
            filename = listbox.get(listbox.curselection()[0])
            if messagebox.askyesno(
                    'Delete file?',
                    'Are you sure you want to delete {0}?'.format(filename)):
                self.lnp.delete_colors(filename)
            self.read_colors()

    def paint_color_preview(self, listbox):
        """
        Draws a preview of the selected color scheme. If no scheme is selected,
        draws the currently installed color scheme.

        Params:
            listbox
                Listbox containing the list of color schemes.
        """
        colorscheme = None
        if len(listbox.curselection()) != 0:
            colorscheme = listbox.get(listbox.curselection()[0])
        colors = self.lnp.get_colors(colorscheme)

        self.color_preview.delete(ALL)
        for i, c in enumerate(colors):
            row = i / 8
            col = i % 8
            self.color_preview.create_rectangle(
                col*16, row*16, (col+1)*16, (row+1)*16,
                fill="#%02x%02x%02x" % c, width=0)

    def toggle_autoclose(self):
        """Toggle automatic closing of the UI when launching DF."""
        self.lnp.toggle_autoclose()
        binding.update()

    def update_hack_list(self):
        """Updates the hack list."""
        for i in self.hacklist.get_children():
            self.hacklist.delete(i)
        for k, h in self.lnp.get_hacks().items():
            self.hacklist.insert('', 'end', text=k, values=(
                k, 'Yes' if h['enabled'] else 'No'))

    def toggle_hack(self):
        """Toggles the selected hack."""
        for item in self.hacklist.selection():
            self.lnp.toggle_hack(self.hacklist.item(item, 'text'))
        self.update_hack_list()

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

    def install_graphics(self, listbox):
        """
        Installs a graphics pack.

        Params:
            listbox
                Listbox containing the list of graphics packs.
        """
        if len(listbox.curselection()) != 0:
            gfx_dir = listbox.get(listbox.curselection()[0])
            if messagebox.askokcancel(
                    message='Your graphics, settings and raws will be changed.',
                    title='Are you sure?'):
                result = self.lnp.install_graphics(gfx_dir)
                if result is False:
                    messagebox.showerror(
                        title=self.root.title(),
                        message='Something went wrong: '
                        'the graphics folder may be missing important files. '
                        'Graphics may not be installed correctly.\n'
                        'See the output log for error details.')
                elif result:
                    if messagebox.askyesno(
                            'Update Savegames?',
                            'Graphics and settings installed!\n'
                            'Would you like to update your savegames to '
                            'properly use the new graphics?'):
                        self.update_savegames()
                else:
                    messagebox.showerror(
                        title=self.root.title(),
                        message='Nothing was installed.\n'
                        'Folder does not exist or does not have required files '
                        'or folders:\n'+gfx_dir)
            self.load_params()

    def update_savegames(self):
        """Updates saved games with new raws."""
        count = self.lnp.update_savegames()
        if count > 0:
            messagebox.showinfo(
                title=self.root.title(),
                message="{0} savegames updated!".format(count))
        else:
            messagebox.showinfo(
                title=self.root.title(), message="No savegames to update.")

    def simplify_graphics(self):
        """Removes unnecessary files from graphics packs."""
        self.read_graphics()
        for pack in self.graphics.get():
            result = self.lnp.simplify_pack(pack)
            if result is None:
                messagebox.showinfo(
                    title=self.root.title(), message='No files in: '+pack)
            elif result is False:
                messagebox.showerror(
                    title=self.root.title(),
                    message='Error simplifying graphics folder. '
                    'It may not have the required files.\n'+pack+'\n'
                    'See the output log for error details.')
            else:
                messagebox.showinfo(
                    title=self.root.title(),
                    message='Deleted {0} unnecessary file(s) in: {1}'.format(
                        result, pack))
        messagebox.showinfo(
            title=self.root.title(), message='Simplification complete!')

    def run_selected_utilities(self):
        """Runs selected utilities."""
        for item in self.proglist.selection():
            utility_path = self.proglist.item(item, 'text')
            self.lnp.run_program(os.path.join(self.lnp.utils_dir, utility_path))

    def toggle_patching(self):
        """Toggles the use of patchingfor installing graphics packs."""
        if self.lnp.install_inits == self.lnp.copy_inits:
            self.lnp.install_inits = self.lnp.patch_inits
            messagebox.showinfo(
                title=self.root.title(),
                message='Enabled patching of init.txt and d_init.txt during '
                'installation of graphics packs. Note: This is still an '
                'experimental feature; backup your files first.')
        else:
            self.lnp.install_inits = self.lnp.copy_inits
            messagebox.showinfo(
                title=self.root.title(),
                message='Disabled patching of init.txt and d_init.txt during '
                'installation of graphics packs. Files will be replaced.')

# vim:expandtab
