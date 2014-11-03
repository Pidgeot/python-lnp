#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import,invalid-name,attribute-defined-outside-init
"""Graphics tab for the TKinter GUI."""
from __future__ import print_function, unicode_literals, absolute_import

from . import controls, binding
from .layout import GridLayouter
from .tab import Tab
import sys

from core import colors, graphics
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

    def read_data(self):
        self.read_graphics()
        self.read_colors()

    def create_controls(self):
        change_graphics = controls.create_control_group(
            self, 'Change Graphics', True)
        Grid.rowconfigure(change_graphics, 1, weight=1)
        change_graphics.pack(side=TOP, fill=BOTH, expand=Y)

        grid = GridLayouter(2)
        curr_pack = Label(change_graphics, text='Current Graphics')
        grid.add(curr_pack, 2)
        binding.bind(curr_pack, 'FONT', lambda x: graphics.current_pack())

        listframe = Frame(change_graphics)
        grid.add(listframe, 2, pady=4)
        _, graphicpacks = controls.create_file_list(
            listframe, None, self.graphics, height=8)

        grid.add(controls.create_trigger_button(
            change_graphics, 'Install Graphics',
            'Install selected graphics pack',
            lambda: self.install_graphics(graphicpacks)))
        grid.add(controls.create_trigger_button(
            change_graphics, 'Update Savegames',
            'Install current graphics pack in all savegames',
            self.update_savegames))
        if 'legacy' not in lnp.df_info.variations:
            grid.add(controls.create_option_button(
                change_graphics, 'TrueType Fonts',
                'Toggles whether to use TrueType fonts or tileset for text. '
                'Only works with Print Mode set to 2D.', 'truetype'))

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

        advanced = controls.create_control_group(
            self, 'Advanced', True)
        advanced.pack(fill=X, expand=N)

        grid = GridLayouter(2)
        if 'legacy' not in lnp.df_info.variations:
            grid.add(controls.create_option_button(
                advanced, 'Print Mode',
                'Changes how Dwarf Fortress draws to the screen. "2D" allows '
                'Truetype fonts, "standard" enables advanced graphics tools. '
                'Certain modifications may use other values.',
                'printmode'), 2)
        grid.add(controls.create_trigger_button(
            advanced, 'Open Graphics Folder',
            'Add your own graphics packs here!', graphics.open_graphics), 2)
        grid.add(controls.create_trigger_button(
            advanced, 'Refresh List', 'Refresh list of graphics packs',
            self.read_graphics))
        grid.add(controls.create_trigger_button(
            advanced, 'Simplify Graphic Folders',
            'Deletes unnecessary files from graphics packs '
            '(saves space, useful for re-packaging)',
            self.simplify_graphics))

        colorframe, color_files, buttons = \
            controls.create_file_list_buttons(
                self, 'Color schemes', self.colors,
                lambda: self.load_colors(color_files),
                self.read_colors, self.save_colors,
                lambda: self.delete_colors(color_files))
        colorframe.pack(side=BOTTOM, fill=BOTH, expand=Y, anchor="s")
        buttons.grid(rowspan=3)

        self.color_files = color_files
        color_files.bind(
            '<<ListboxSelect>>',
            lambda e: self.paint_color_preview(color_files))

        self.color_preview = Canvas(
            colorframe, width=128, height=32, highlightthickness=0,
            takefocus=False)
        self.color_preview.grid(column=0, row=2)

    def read_graphics(self):
        """Reads list of graphics packs."""
        self.graphics.set(tuple([p[0] for p in graphics.read_graphics()]))

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
            else:
                messagebox.showinfo(
                    title='Success',
                    message='Deleted {0} unnecessary file(s) in: {1}'.format(
                        result, pack))
        messagebox.showinfo(title='Success', message='Simplification complete!')

    def read_colors(self):
        """Reads list of color schemes."""
        files = colors.read_colors()
        self.colors.set(files)
        current = colors.get_installed_file()
        for i, f in enumerate(files):
            if f == current:
                self.color_files.itemconfig(i, fg='red')
            else:
                self.color_files.itemconfig(i, fg='black')

        self.paint_color_preview(self.color_files)

    def load_colors(self, listbox):
        """
        Replaces color scheme  with selected file.

        Params:
            listbox
                Listbox containing the list of color schemes.
        """
        if len(listbox.curselection()) != 0:
            colors.load_colors(listbox.get(listbox.curselection()[0]))
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
                colors.delete_colors(filename)
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
        colorlist = colors.get_colors(colorscheme)

        self.color_preview.delete(ALL)
        for i, c in enumerate(colorlist):
            row = i // 8
            col = i % 8
            self.color_preview.create_rectangle(
                col*16, row*16, (col+1)*16, (row+1)*16,
                fill="#%02x%02x%02x" % c, width=0)
