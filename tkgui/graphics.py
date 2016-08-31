#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Graphics tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

import sys

# pylint:disable=wrong-import-order
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
# pylint:enable=wrong-import-order

from . import controls, binding, tkhelpers
from .layout import GridLayouter
from .tab import Tab

from core import colors, graphics, paths
from core.lnp import lnp

# pylint:disable=too-many-public-methods,too-many-instance-attributes
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
        Style().configure('SubNotebook.TNotebook', tabposition='n')
        n = Notebook(self, style='SubNotebook.TNotebook')
        n.pack(fill=BOTH, expand=Y, pady=(4, 2))

        # Tab: Change Graphics
        change_graphics_tab = Frame(self, pad=(4, 2))
        change_graphics_tab.pack(fill=BOTH, expand=Y)
        n.add(change_graphics_tab, text="Choose")

        self._create_cg_group(change_graphics_tab).pack(fill=BOTH, expand=Y)
        self._create_display_group(change_graphics_tab).pack(fill=X, expand=N)
        self._create_advanced_group(change_graphics_tab).pack(fill=X, expand=N)

        # Tab: Customization
        customize_tab = Frame(self, pad=(4, 2))
        customize_tab.pack(fill=BOTH, expand=Y)
        n.add(customize_tab, text="Customize")

        self._create_tilesets_group(customize_tab).pack(fill=BOTH, expand=Y)
        self._create_cs_group(customize_tab).pack(fill=BOTH, expand=N)

    def _create_cg_group(self, parent, show_title=True):
        title = 'Change Graphics' if show_title else None
        change_graphics = controls.create_control_group(parent, title, True)
        change_graphics.rowconfigure(0, weight=1)

        grid = GridLayouter(2)
        listframe = Frame(change_graphics)
        grid.add(listframe, 2)
        _, self.graphicpacks = controls.create_file_list(
            listframe, None, self.graphics, height=8)
        self.graphicpacks.bind(
            '<<ListboxSelect>>', lambda e: self.select_graphics())
        controls.listbox_dyn_tooltip(
            self.graphicpacks, lambda i: self.packs[i], graphics.get_tooltip)
        for seq in ("<Double-1>", "<Return>"):
            self.graphicpacks.bind(seq, lambda e: self.install_graphics())

        grid.add(controls.create_trigger_button(
            change_graphics, 'Install Graphics',
            'Install selected graphics pack',
            self.install_graphics))
        grid.add(controls.create_trigger_button(
            change_graphics, 'Update Savegames',
            'Install current graphics pack in all savegames',
            self.update_savegames))
        grid.add(controls.create_trigger_button(
            change_graphics, 'Refresh', 'Refresh list of graphics packs',
            self.read_graphics))
        grid.add(controls.create_trigger_button(
            change_graphics, 'Open Folder',
            'Add your own graphics packs here!', graphics.open_graphics))

        return change_graphics

    def _create_advanced_group(self, parent, show_title=True):
        title = 'Advanced' if show_title else None
        advanced = controls.create_control_group(parent, title, True)

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
            advanced, 'Simplify Graphic Folders',
            'Deletes unnecessary files from graphics packs '
            '(saves space, useful for re-packaging)',
            self.simplify_graphics))

        return advanced

    def _create_tilesets_group(self, parent, show_title=True):
        title = 'Change Tilesets' if show_title else None
        customize = controls.create_control_group(parent, title, True)

        _, self.fonts = controls.create_file_list(
            customize, 'FONT', self.tilesets)
        for seq in ("<Double-1>", "<Return>"):
            self.fonts.bind(seq, lambda e: self.install_tilesets(1))

        if lnp.settings.version_has_option('GRAPHICS_FONT'):
            _, self.graphicsfonts = controls.create_file_list(
                customize, 'GRAPHICS_FONT', self.tilesets)
            for seq in ("<Double-1>", "<Return>"):
                self.graphicsfonts.bind(seq, lambda e: self.install_tilesets(2))

        buttons = controls.create_control_group(customize, None, True)
        buttons.pack(fill=X)

        grid = GridLayouter(2)
        grid.add(controls.create_trigger_button(
            buttons, 'Install Tilesets',
            'Install selected tilesets', self.install_tilesets), 2)
        grid.add(controls.create_trigger_button(
            buttons, 'Refresh', 'Refresh list of tilesets',
            self.read_tilesets))
        grid.add(controls.create_trigger_button(
            buttons, 'Open Folder',
            'Add your own tilesets here!', graphics.open_tilesets))

        return customize

    def _create_cs_group(self, parent, show_title=True):
        title = "Color schemes" if show_title else None
        colorframe, self.color_entry, self.color_files = \
            controls.create_list_with_entry(
                parent, title, self.colors,
                [("Save", "Save current color scheme", self.save_colors),
                 ("Load", "Load color scheme", self.load_colors),
                 ("Delete", "Delete color scheme", self.delete_colors),
                 ("Refresh", "Refresh list", self.read_colors)],
                entry_default="Save current color scheme as...")
        self.color_files.bind(
            "<<ListboxSelect>>", lambda e: self.select_colors())
        for seq in ("<Double-1>", "<Return>"):
            self.color_files.bind(seq, lambda e: self.load_colors())

        self.color_preview = Canvas(
            colorframe, width=128, height=32, highlightthickness=0,
            takefocus=False)
        self.color_preview.grid(column=0, row=0, columnspan=2, pady=(0, 4))

        return colorframe

    @staticmethod
    def _create_display_group(parent, show_title=True):
        title = 'Display Options' if show_title else None
        display = controls.create_control_group(parent, title, True)

        grid = GridLayouter(2)
        grid.add(controls.create_option_button(
            display, 'Liquid Depth',
            'Displays the depth of liquids with numbers 1-7',
            'liquidDepth'))
        grid.add(controls.create_option_button(
            display, 'Varied Ground',
            'If ground tiles use a variety of punctuation, or only periods',
            'variedGround'))
        grid.add(controls.create_option_button(
            display, 'Hide Engravings',
            'Make all engravings look the same',
            'engravingsObscured'))
        grid.add(controls.create_option_button(
            display, 'Show Improvement',
            'Show the quality of improvement in name of items',
            'improvementQuality'))

        return display

    def read_graphics(self):
        """Reads list of graphics packs."""
        packs = self.packs = [p[0] for p in graphics.read_graphics()]
        self.graphics.set(tuple([graphics.get_title(p) for p in packs]))
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
            if not tkhelpers.check_vanilla_raws():
                return
            gfx_dir = self.packs[int(self.graphicpacks.curselection()[0])]
            result = None
            if messagebox.askokcancel(
                    message='Your graphics, settings and raws will be changed.'
                    '\n\nAny manually installed mods will be removed in the '
                    'process.\n\nAre you sure you want to continue?',
                    title='Are you sure?'):
                result = graphics.install_graphics(gfx_dir)
                if result is False:
                    messagebox.showerror(
                        title='Error occurred', message='Something went wrong: '
                        'the graphics folder may be missing important files. '
                        'Graphics may not be installed correctly.\n'
                        'See the output log for error details.')
                elif result == 0:
                    messagebox.showerror(
                        title='Not updatable', message='The graphics raws could'
                        ' not be updated due to missing graphics files, or '
                        'your installed mods are incompatible with this '
                        'graphics pack.')
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
            if result:
                self.graphicpacks.selection_clear(
                    self.graphicpacks.curselection())
            binding.update()
            self.read_data()

    @staticmethod
    def update_savegames():
        """Updates saved games with new raws."""
        count, skipped = graphics.update_savegames()
        if count + skipped == 0:
            messagebox.showinfo(
                title='Update skipped', message="No savegames to update.")
        else:
            msg = "{} savegames updated!\n\n".format(count)
            if skipped:
                msg += "{} savegames were skipped (would have broken raws)"\
                       .format(skipped)
            messagebox.showinfo('Update complete', msg)

    def simplify_graphics(self):
        """Removes unnecessary files from graphics packs."""
        if not tkhelpers.check_vanilla_raws():
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
        items = self.color_files.curselection()
        if len(items) > 0:
            self.color_files.selection_clear(items)
            colors.load_colors(self.color_files.get(items[0]))
            self.read_colors()
            self.color_entry.delete(0, END)

    def save_colors(self):
        """Saves color scheme to a file."""
        v = self.color_entry.get()
        if v and not getattr(self.color_entry, 'default_showing', False):
            if (not colors.color_exists(v) or messagebox.askyesno(
                    message='Overwrite {0}?'.format(v),
                    icon='question', title='Overwrite file?')):
                self.color_entry.delete(0, END)
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
            pack = self.packs[int(self.graphicpacks.curselection()[0])]
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
            if lnp.settings.version_has_option('GRAPHICS_FONT'):
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
            self.fonts.selection_clear(self.fonts.curselection())
        if len(self.graphicsfonts.curselection()) != 0 and (mode & 2):
            graphicsfont = self.graphicsfonts.get(
                self.graphicsfonts.curselection()[0])
            self.graphicsfonts.selection_clear(
                self.graphicsfonts.curselection())
        graphics.install_tilesets(font, graphicsfont)
        binding.update()
        self.read_data()
