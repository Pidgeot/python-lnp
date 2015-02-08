#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Graphics tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls, binding
from .layout import GridLayouter
from .tab import Tab
import sys, os

from core import colors, graphics, paths, download, baselines
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

class GraphicsTab(Tab):
    """Graphics tab for the TKinter GUI."""
    def create_variables(self):
        self.graphics = Variable()
        self.colors = Variable()
        self.tilesets = Variable()

    def read_data(self):
        self.read_graphics()
        self.read_colors()
        self.read_tilesets()

    def create_controls(self):
        n = Notebook(self)
        n.pack(side=TOP, fill=BOTH, expand=Y, padx=4, pady=4)

        #First tab
        change_graphics_tab = Frame(self)
        change_graphics_tab.pack(side=TOP, fill=BOTH, expand=Y)
        n.add(change_graphics_tab, text="Change Graphics")

        change_graphics = controls.create_control_group(
            change_graphics_tab, 'Change Graphics', True)
        Grid.rowconfigure(change_graphics, 0, weight=1)
        change_graphics.pack(side=TOP, fill=BOTH, expand=Y)

        grid = GridLayouter(2)
        listframe = Frame(change_graphics)
        grid.add(listframe, 2, pady=4)
        _, self.graphicpacks = controls.create_file_list(
            listframe, None, self.graphics, height=8)
        self.graphicpacks.bind(
            '<<ListboxSelect>>', lambda e: self.select_graphics())
        self.graphicpacks.bind(
            "<Double-1>", lambda e: self.install_graphics())

        grid.add(controls.create_trigger_button(
            change_graphics, 'Install Graphics',
            'Install selected graphics pack',
            self.install_graphics))
        grid.add(controls.create_trigger_button(
            change_graphics, 'Update Savegames',
            'Install current graphics pack in all savegames',
            self.update_savegames))
        grid.add(controls.create_trigger_button(
            change_graphics, 'Refresh List', 'Refresh list of graphics packs',
            self.read_graphics), 2)

        advanced = controls.create_control_group(
            change_graphics_tab, 'Advanced', True)
        advanced.pack(fill=X, expand=N)

        grid = GridLayouter(2)
        if 'legacy' not in lnp.df_info.variations:
            grid.add(controls.create_option_button(
                advanced, 'Print Mode',
                'Changes how Dwarf Fortress draws to the screen. "2D" allows '
                'Truetype fonts, "standard" enables advanced graphics tools. '
                'Certain modifications may use other values.',
                'printmode'), 2)
            grid.add(controls.create_option_button(
                advanced, 'TrueType Fonts',
                'Toggles whether to use TrueType fonts or tileset for text. '
                'Only works with Print Mode set to 2D.', 'truetype'), 2)
        grid.add(controls.create_trigger_button(
            advanced, 'Open Graphics Folder',
            'Add your own graphics packs here!', graphics.open_graphics), 2)
        grid.add(controls.create_trigger_button(
            advanced, 'Simplify Graphic Folders',
            'Deletes unnecessary files from graphics packs '
            '(saves space, useful for re-packaging)',
            self.simplify_graphics))

        # Customization tab
        customize_tab = Frame(self)
        customize_tab.pack(side=TOP, fill=BOTH, expand=Y)
        n.add(customize_tab, text="Customization")

        customize = controls.create_control_group(
            customize_tab, 'Change Tilesets', True)
        Grid.rowconfigure(customize, 0, weight=1)
        customize.pack(side=TOP, fill=BOTH, expand=Y)

        grid = GridLayouter(2)
        tempframe = Frame(customize)
        _, self.fonts = controls.create_file_list(
            tempframe, 'FONT', self.tilesets, height=8)
        self.fonts.bind(
            "<Double-1>", lambda e: self.install_tilesets(1))
        if lnp.settings.version_has_option('GRAPHICS_FONT'):
            grid.add(tempframe, pady=4)
            tempframe = Frame(customize)
            grid.add(tempframe, pady=4)
            _, self.graphicsfonts = controls.create_file_list(
                tempframe, 'GRAPHICS_FONT', self.tilesets, height=8)
            self.graphicsfonts.bind(
                "<Double-1>", lambda e: self.install_tilesets(2))
        else:
            grid.add(tempframe, 2, pady=4)

        grid.add(controls.create_trigger_button(
            customize, 'Install Tilesets',
            'Install selected tilesets', self.install_tilesets), 2)
        grid.add(controls.create_trigger_button(
            customize, 'Refresh List', 'Refresh list of tilesets',
            self.read_tilesets))

        advanced = controls.create_control_group(
            customize_tab, 'Advanced', True)
        advanced.pack(fill=X, expand=N)

        # Outside tab
        grid = GridLayouter(2)
        if 'legacy' not in lnp.df_info.variations:
            grid.add(controls.create_option_button(
                advanced, 'Print Mode',
                'Changes how Dwarf Fortress draws to the screen. "2D" allows '
                'Truetype fonts, "standard" enables advanced graphics tools. '
                'Certain modifications may use other values.',
                'printmode'), 2)
            grid.add(controls.create_option_button(
                advanced, 'TrueType Fonts',
                'Toggles whether to use TrueType fonts or tileset for text. '
                'Only works with Print Mode set to 2D.', 'truetype'), 2)
        grid.add(controls.create_trigger_button(
            advanced, 'Open Tilesets Folder',
            'Add your own tilesets here!', graphics.open_tilesets), 2)

        colorframe, self.color_files, buttons = \
            controls.create_file_list_buttons(
                self, 'Color schemes', self.colors, self.load_colors,
                self.read_colors, self.save_colors, self.delete_colors)
        colorframe.pack(side=BOTTOM, fill=BOTH, expand=Y, anchor="s")
        buttons.grid(rowspan=3)
        self.color_files.bind(
            '<<ListboxSelect>>', lambda e: self.select_colors())
        self.color_files.bind(
            "<Double-1>", lambda e: self.load_colors())

        self.color_preview = Canvas(
            colorframe, width=128, height=32, highlightthickness=0,
            takefocus=False)
        self.color_preview.grid(column=0, row=2)

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

    def read_graphics(self):
        """Reads list of graphics packs."""
        packs = [p[0] for p in graphics.read_graphics()]
        self.graphics.set(tuple(packs))
        current = graphics.current_pack()
        for i, p in enumerate(packs):
            if p == current:
                self.graphicpacks.itemconfig(i, bg='pale green')
            else:
                self.graphicpacks.itemconfig(i, bg='white')

        self.select_graphics()

    def install_graphics(self):
        """Installs a graphics pack."""
        if len(self.graphicpacks.curselection()) != 0:
            from .tkgui import TkGui
            if not TkGui.check_vanilla_raws():
                return
            gfx_dir = self.graphicpacks.get(self.graphicpacks.curselection()[0])
            if messagebox.askokcancel(
                    message='Your graphics, settings and raws will be changed.',
                    title='Are you sure?'):
                result = graphics.install_graphics(gfx_dir)
                if result is False:
                    messagebox.showerror(
                        title='Error occurred', message='Something went wrong: '
                        'the graphics folder may be missing important files. '
                        'Graphics may not be installed correctly.\n'
                        'See the output log for error details.')
                elif result:
                    if len(graphics.savegames_to_update()) != 0:
                        if messagebox.askyesno(
                                'Update Savegames?',
                                'Graphics and settings installed!\n'
                                'Would you like to update your savegames to '
                                'properly use the new graphics?'):
                            self.update_savegames()
                    else:
                        messagebox.showinfo(
                            'Graphics installed',
                            'Graphics and settings installed!')
                else:
                    messagebox.showerror(
                        title='Error occurred',
                        message='Nothing was installed.\n'
                        'Folder does not exist or does not have required files '
                        'or folders:\n'+str(gfx_dir))
            binding.update()
            self.read_data()

    @staticmethod
    def update_savegames():
        """Updates saved games with new raws."""
        count = graphics.update_savegames()
        if count > 0:
            messagebox.showinfo(
                title='Update complete',
                message="{0} savegames updated!".format(count))
        else:
            messagebox.showinfo(
                title='Update skipped', message="No savegames to update.")

    def simplify_graphics(self):
        """Removes unnecessary files from graphics packs."""
        from .tkgui import TkGui
        if not TkGui.check_vanilla_raws():
            return
        self.read_graphics()
        for pack in self.graphics.get():
            result = graphics.simplify_pack(pack)
            if result is None:
                messagebox.showinfo(
                    title='Error occurrred', message='No files in: '+str(pack))
            elif result is False:
                messagebox.showerror(
                    title='Error occurred',
                    message='Error simplifying graphics folder. '
                    'It may not have the required files.\n'+str(pack)+'\n'
                    'See the output log for error details.')
            elif result != 0:
                messagebox.showinfo(
                    title='Success',
                    message='Deleted {0} unnecessary file(s) in: {1}'.format(
                        result, pack))
        messagebox.showinfo(title='Success', message='All graphics  {}  '
                            'are simplified!'.format(self.graphics.get()))

    def read_colors(self):
        """Reads list of color schemes."""
        files = colors.read_colors()
        self.colors.set(files)
        current = colors.get_installed_file()
        for i, f in enumerate(files):
            if f == current:
                self.color_files.itemconfig(i, bg='pale green')
            else:
                self.color_files.itemconfig(i, bg='white')

        self.select_colors()

    def load_colors(self):
        """Replaces color scheme with the selected file."""
        if len(self.color_files.curselection()) != 0:
            colors.load_colors(self.color_files.get(
                self.color_files.curselection()[0]))
            self.read_colors()

    def save_colors(self):
        """Saves color scheme to a file."""
        v = simpledialog.askstring(
            "Save Color scheme", "Save current color scheme as:")
        if v is not None:
            if (not colors.color_exists(v) or messagebox.askyesno(
                    message='Overwrite {0}?'.format(v),
                    icon='question', title='Overwrite file?')):
                colors.save_colors(v)
                self.read_colors()

    def delete_colors(self):
        """Deletes the selected color scheme."""
        if len(self.color_files.curselection()) != 0:
            filename = self.color_files.get(self.color_files.curselection()[0])
            if messagebox.askyesno(
                    'Delete file?',
                    'Are you sure you want to delete {0}?'.format(filename)):
                colors.delete_colors(filename)
            self.read_colors()

    def select_graphics(self):
        """Event handler for selecting a graphics pack."""
        colorscheme = None
        if len(self.graphicpacks.curselection()) != 0:
            pack = self.graphicpacks.get(self.graphicpacks.curselection()[0])
            if lnp.df_info.version >= '0.31.04':
                colorscheme = paths.get('graphics', pack, 'data', 'init',
                                        'colors.txt')
            else:
                colorscheme = paths.get('graphics', pack, 'data', 'init',
                                        'init.txt')
        self.paint_color_preview(colorscheme)

    def select_colors(self):
        """Event handler for selecting a colorscheme."""
        colorscheme = None
        if len(self.color_files.curselection()) != 0:
            colorscheme = self.color_files.get(
                self.color_files.curselection()[0])
        self.paint_color_preview(colorscheme)

    def paint_color_preview(self, colorscheme):
        """
        Draws a preview of a color scheme. If no scheme is specified,
        draws the currently installed color scheme.

        Params:
            colorscheme
                Listbox containing the list of color schemes.
        """
        colorlist = colors.get_colors(colorscheme)
        self.color_preview.delete(ALL)

        if not colorlist:
            self.color_preview.create_text(
                0, 0, text="Error reading colorscheme", anchor=NW)
        else:
            for i, c in enumerate(colorlist):
                row = i // 8
                col = i % 8
                self.color_preview.create_rectangle(
                    col*16, row*16, (col+1)*16, (row+1)*16,
                    fill="#%02x%02x%02x" % tuple([int(v % 256) for v in c]),
                    width=0)

    def read_tilesets(self):
        """Reads list of graphics packs."""
        files = graphics.read_tilesets()
        self.tilesets.set(files)
        current = graphics.current_tilesets()
        for i, f in enumerate(files):
            if f == current[0]:
                self.fonts.itemconfig(i, bg='pale green')
            else:
                self.fonts.itemconfig(i, bg='white')
            if f == current[1]:
                self.graphicsfonts.itemconfig(i, bg='pale green')
            else:
                self.graphicsfonts.itemconfig(i, bg='white')

    def install_tilesets(self, mode=3):
        """
        Installs selected tilesets.

        Params:
            mode
                If mode & 1, installs FONT. If mode & 2, installs GRAPHICS_FONT.
        """
        font = None
        graphicsfont = None
        if len(self.fonts.curselection()) != 0 and (mode & 1):
            font = self.fonts.get(self.fonts.curselection()[0])
        if len(self.graphicsfonts.curselection()) != 0 and (mode & 2):
            graphicsfont = self.graphicsfonts.get(
                self.graphicsfonts.curselection()[0])
        graphics.install_tilesets(font, graphicsfont)
        binding.update()
        self.read_data()
