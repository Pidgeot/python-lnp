#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint:disable=unused-wildcard-import,wildcard-import
"""Controls used by the TKinter GUI."""

import sys
import tkinter.font as tkFont
import types
from tkinter import *  # noqa: F403
from tkinter import simpledialog
from tkinter.ttk import *  # noqa: F403

from core.lnp import lnp

from . import binding

# Monkeypatch simpledialog to use themed dialogs from ttk
if sys.platform != 'darwin':  # OS X looks better without patch
    simpledialog.Toplevel = Toplevel
    simpledialog.Entry = Entry
    simpledialog.Frame = Frame
    simpledialog.Button = Button

# Make Enter on button with focus activate it
TtkButton = Button


class Button(TtkButton):  # pylint:disable=function-redefined,missing-class-docstring
    def __init__(self, master=None, **kw):
        TtkButton.__init__(self, master, **kw)
        if 'command' in kw:
            self.bind('<Return>', lambda e: kw['command']())


# http://effbot.org/zone/tkinter-autoscrollbar.htm
class _AutoScrollbar(Scrollbar):
    """A scrollbar that hides itself if it's not needed."""
    def set(self, first, last):
        """Only show scrollbar when there's more content than will fit."""
        # pylint:disable=no-member
        if not lnp.userconfig.get_bool('tkgui_show_scroll'):
            if (float(first) <= 0.0 and float(last) >= 1.0) or (
                    hasattr(self, 'hidden') and self.hidden):
                self.grid_remove()
            else:
                self.grid()
        Scrollbar.set(self, first, last)


# http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387
class _ToolTip(object):
    """Tooltip widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.event = None
        self.text = text
        self.active = False

    def showtip(self):
        """Displays the tooltip."""
        self.active = True
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_pointerx() + 16
        y = self.widget.winfo_pointery() + 16
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # pylint:disable=protected-access
            # For OS X
            tw.tk.call(
                "::tk::unsupported::MacWindowStyle", "style", tw._w, "help",
                "noActivates")
        except TclError:
            pass
        label = Label(
            tw, text=self.text, justify=LEFT, background="#ffffe0",
            relief=SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hidetip(self):
        """Hides the tooltip."""
        tw = self.tipwindow
        self.tipwindow = None
        self.active = False
        if tw:
            tw.destroy()

    def settext(self, text):
        """
        Sets the tooltip text and redraws it if necessary.

        Args:
            text: the new tooltip text.
        """
        if text == self.text:
            return
        self.text = text
        if self.active:
            self.hidetip()
            self.showtip()


_TOOLTIP_DELAY = 500
__ui = None


# pylint:disable=too-few-public-methods
class _FakeControl(object):
    """Fake control returned if an option doesn't exist."""
    # pylint:disable=unused-argument
    @staticmethod
    def grid(*args, **kwargs):
        """Prevents breaking for code that tries to lay out the control."""
        return
    pack = grid


fake_control = _FakeControl()


def init(ui):
    """Connect to a TkGui instance."""
    # pylint:disable=global-statement
    global __ui
    __ui = ui


def create_tooltip(widget, text):
    """
    Creates and returns a tooltip for a widget.

    Args:
        widget: the widget to associate the tooltip to.
        text: the tooltip text.
    """
    tooltip = _ToolTip(widget, text)

    # pylint:disable=unused-argument
    def enter(event):
        """
        Event handler on mouse enter.

        Args:
            event: the event data."""
        if tooltip.event:
            widget.after_cancel(tooltip.event)
        tooltip.event = widget.after(_TOOLTIP_DELAY, tooltip.showtip)

    def leave(event):
        """
        Event handler on mouse exit.

        Args:
            event: the event data.
        """
        if tooltip.event is not None:
            widget.after_cancel(tooltip.event)
            tooltip.event = None
        tooltip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    return tooltip


def create_control_group(parent, text, dual_column=False):
    """
    Creates and returns a Frame or Labelframe to group controls.

    Args:
        text: the caption for the Labelframe. If None, returns a Frame.
        dual_column: configure the frame for a dual-column grid layout if True.
    """
    f = None
    if text is not None:
        f = Labelframe(parent, text=text)
    else:
        f = Frame(parent)
    f.configure(pad=(2, 0, 2, 2))
    if dual_column:
        f.columnconfigure((0, 1), weight=1, uniform=1)
    return f


def create_option_button(
        parent, text, tooltip, option, update_func=None):
    """
    Creates and returns a button bound to an option.

    Args:
        parent: the parent control for the button.
        text: the button text.
        tooltip: the tooltip for the button.
        option: the keyword used for the option.
        update_func: if given, a reference to a function that pre-processes the
            given option for display.
    """
    return create_trigger_option_button(
        parent, text, tooltip, lambda: __ui.cycle_option(option), option,
        update_func)


def create_trigger_button(parent, text, tooltip, command):
    """
    Creates and returns a button that triggers an action when clicked.

    Args:
        parent
            The parent control for the button.
        text
            The button text.
        tooltip
            The tooltip for the button.
        command
            Reference to the function called when the button is clicked.
    """
    b = Button(parent, text=text, command=command)
    create_tooltip(b, tooltip)
    return b


# pylint: disable=too-many-arguments
def create_trigger_option_button(
        parent, text, tooltip, command, option, update_func=None):
    """
    Creates and returns a button bound to an option, with a special action
    triggered on click.

    Args:
        parent: the parent control for the button.
        text: the button text.
        tooltip: the tooltip for the button.
        command: Reference to the function called when the button is clicked.
        option: the keyword used for the option.
        update_func: f given, a reference to a function that pre-processes the
            given option for display.
    """
    if not binding.version_has_option(option):
        return fake_control
    b = create_trigger_button(parent, text, tooltip, command)
    binding.bind(b, option, update_func)
    return b


def create_scrollbar(parent, control, **gridargs):
    """
    Creates and layouts a vertical scrollbar associated to <control>.

    Args:
        parent: the parent control for the scrollbar.
        control: the control to attach the scrollbar to.
        gridargs: Keyword arguments used to apply grid layout to the scrollbar.
    """
    s = _AutoScrollbar(parent, orient=VERTICAL, command=control.yview)
    control['yscrollcommand'] = s.set
    s.grid(sticky="ns", **gridargs)
    if not lnp.userconfig.get_bool('tkgui_show_scroll'):
        s.grid_remove()
    return s


def listbox_identify(listbox, y):
    """Returns the index of the listbox item at the supplied (relative) y
    coordinate"""
    item = listbox.nearest(y)
    if item != -1 and listbox.bbox(item)[1] + listbox.bbox(item)[3] > y:
        return item
    return None


def listbox_dyn_tooltip(listbox, item_get, tooltip_get):
    """Attaches a dynamic tooltip to a listbox.

    Args:
        listbox: The listbox to attach to.
        item_get: A function taking the index of the item and returning a
            reference to the item.
        tooltip_get: A function taking a reference to an item and returning
            its tooltip (or the empty string for no tooltip).
    """
    tooltip = create_tooltip(listbox, '')

    def motion_handler(event):
        """
        Event handler for mouse motion over items in a listbox.

        If the mouse has moved out of the last list element, hides the tooltip.
        Then, if the mouse is over a list item, wait controls._TOOLTIP_DELAY
        milliseconds (without mouse movement) before showing the tooltip"""
        item = listbox.identify(event.y)
        if item is not None:
            item = item_get(item)

        def show():
            """Sets and shows a tooltip"""
            tooltip.settext(tooltip_get(item))
            tooltip.showtip()

        if tooltip.event:
            listbox.after_cancel(tooltip.event)
            tooltip.event = None
        if not item or tooltip_get(item) != tooltip.text:
            tooltip.hidetip()
        if item:
            tooltip.event = listbox.after(_TOOLTIP_DELAY, show)

    listbox.bind('<Motion>', motion_handler)


def treeview_tag_set(tree, tag, item, state=True, toggle=False):
    """
    Adds or removes a tag from the Treeview item's tags. Returns True if
    tag is now set or False if it is not.

    Args:
        item: Treeview item id
        state: True to set the tag; False to remove the tag.
        toggle: If set to True, will toggle the tag. Overrides on.
    """
    # This is necessary because tag_add and tag_remove are not in the Python
    # bindings for Tk, and this is more readable (and likely not any slower)
    # than using arcane tk.call() syntax
    tags = list(tree.item(item, 'tags'))
    is_set = tag in tags
    if toggle:
        state = not is_set

    if state and (not is_set):
        tags.append(tag)
    elif (not state) and is_set:
        tags.remove(tag)

    tree.item(item, tags=tags)
    return state


def create_file_list(parent, title, listvar, **args):
    """
    Creates a file list with a scrollbar. Returns a tuple (frame, listbox).

    Args:
        parent: The parent control for the list.
        title: The title for the frame.
        listvar: The variable containing the list items.
        args: Additions keyword arguments for the file list itself.

    Returns:
        (tuple, listbox)
    """
    if 'height' not in args:
        args['height'] = 4
    lf = create_control_group(parent, title)
    lf.pack(fill=BOTH, expand=Y)
    Grid.columnconfigure(lf, 0, weight=2)
    Grid.rowconfigure(lf, 1, weight=1)
    lb = Listbox(
        lf, listvariable=listvar, activestyle='dotbox', exportselection=0,
        **args)
    lb.identify = types.MethodType(listbox_identify, lb)
    lb.grid(column=0, row=0, rowspan=2, sticky="nsew")
    create_scrollbar(lf, lb, column=1, row=0, rowspan=2)
    return (lf, lb)


def create_readonly_file_list_buttons(
        parent, title, listvar, load_fn, refresh_fn, **args):
    """
    Creates a file list with load and refresh buttons. Returns a tuple
    (frame, listbox, buttons).

    Args:
        parent: The parent control for the list.
        title: The title for the frame.
        listvar: The variable containing the list items.
        load_fn: Reference to a function to be called when the Load button
            is clicked.
        refresh_fn: Reference to a function to be called when the Refresh
            button is clicked.
        args: Additions keyword arguments for the file list itself.

    Returns:
        (frame, listbox, buttons)
    """
    (lf, lb) = create_file_list(parent, title, listvar, **args)
    buttons = Frame(lf)
    load = create_trigger_button(buttons, 'Load', 'Load selected', load_fn)
    load.pack(side=TOP)
    refresh = create_trigger_button(
        buttons, 'Refresh', 'Refresh list', refresh_fn)
    refresh.pack(side=TOP)
    buttons.grid(column=2, row=0, sticky="n")
    return (lf, lb, buttons)


# pylint: disable=too-many-arguments
def create_file_list_buttons(
        parent, title, listvar, load_fn, refresh_fn, save_fn,
        delete_fn, **args):
    """
    Creates a file list with load, refresh, save and delete buttons.
    Returns a tuple (frame, listbox, buttons).

    Args:
        parent: The parent control for the list.
        title: The title for the frame.
        listvar: The variable containing the list items.
        load_fn: Reference to a function to be called when the Load button
            is clicked.
        refresh_fn: Reference to a function to be called when the Refresh
            button is clicked.
        save_fn: Reference to a function to be called when the Save button
            is clicked.
        delete_fn: Reference to a function to be called when the Delete button
            is clicked.
        args: Additions keyword arguments for the file list itself.

    Returns:
        (frame, listbox, buttons)
    """
    (lf, lb, buttons) = create_readonly_file_list_buttons(
        parent, title, listvar, load_fn, refresh_fn, **args)
    save = create_trigger_button(buttons, 'Save', 'Save current', save_fn)
    save.pack(side=TOP)
    delete = create_trigger_button(
        buttons, 'Delete', 'Delete selected', delete_fn)
    delete.pack(side=TOP)
    return (lf, lb, buttons)


def add_default_to_entry(entry, default_text):
    """Adds bindings to entry such that when there is no user text in the
    entry, the entry will display default_text in grey and italics."""
    normal_font = tkFont.Font(font='TkDefaultFont')
    default_font = tkFont.Font(font='TkDefaultFont')
    default_font.config(slant=tkFont.ITALIC)
    entry.default_showing = True

    def focus_out(_):
        """Insert text and focus"""
        if len(entry.get()) == 0:
            entry.insert(0, default_text)
            entry.configure(font=default_font, foreground='grey')
            entry.default_showing = True

    def focus_in(_):
        """Insert text but don't focus"""
        if entry.default_showing:
            entry.delete(0, END)
            entry.configure(font=normal_font, foreground='black')
            entry.default_showing = False

    entry.bind('<FocusIn>', focus_in)
    entry.bind('<FocusOut>', focus_out)

    focus_out(0)


def create_list_with_entry(parent, title, listvar, buttonspec, **kwargs):
    """
    Creates a control group with a listbox, a text entry, and any number of
    buttons specified with buttonspec. Does not lay out the control group in
    its parent.

    Args:
        parent: The parent control for the list.
        title: The title for the frame.
        listvar: The variable containing the list items.
        buttonspec: A list of tuples (title, tooltip, function) specifying the
            buttons

    Returns:
        a tuple (frame, entry, lsitbox)
    """
    entry_default = kwargs.pop('entry_default', None)
    if 'height' not in kwargs:
        kwargs['height'] = 4

    kf = create_control_group(parent, title)
    kf.columnconfigure(0, weight=1)
    kf.rowconfigure(2, weight=1)

    ke = Entry(kf)  # text box
    ke.grid(row=1, column=0, sticky='ewn', pady=(1, 4))

    lf = Frame(kf)  # Listbox and scrollbar
    kb = Listbox(lf, listvariable=listvar, activestyle='dotbox',
                 exportselection=0, **kwargs)
    lf.configure(borderwidth=kb['borderwidth'], relief=kb['relief'])
    kb.configure(borderwidth=0, relief='flat')
    kb.grid(row=0, column=0, sticky='nsew')
    create_scrollbar(lf, kb, row=0, column=1)
    lf.rowconfigure(0, weight=1)
    lf.columnconfigure(0, weight=1)
    lf.grid(row=2, column=0, rowspan=1, sticky='nsew')

    bf = Frame(kf)  # buttons
    for i, bn in enumerate(buttonspec):
        pad = 0 if i == 0 else (5, 0)
        create_trigger_button(bf, *bn).grid(row=i, pady=pad)
    bf.grid(column=1, row=1, rowspan=2, sticky='ns', padx=(4, 0))

    if entry_default:
        add_default_to_entry(ke, entry_default)

    return (kf, ke, kb)


def create_toggle_list(parent, columns, framegridopts, listopts=None):
    """
    Creates and returns a two-column Treeview in a frame to show toggleable
    items in a list.

    Args:
        parent: The parent control for the Treeview.
        columns: Column data for the Treeview.
        framegridopts: Additional options for grid layout of the frame.
        listopts: Additional options for the Treeview.
    """
    if listopts is None:
        listopts = {}
    lf = Frame(parent)
    lf.grid(**framegridopts)
    Grid.rowconfigure(lf, 0, weight=1)
    Grid.columnconfigure(lf, 0, weight=1)
    lst = Treeview(lf, columns=columns, show=['headings'], **listopts)
    lst.tag_set = types.MethodType(treeview_tag_set, lst)
    lst.grid(column=0, row=0, sticky="nsew")
    create_scrollbar(lf, lst, column=1, row=0)
    return lst


def create_numeric_entry(parent, variable, option, tooltip):
    """
    Creates and returns an Entry suitable for input of small, numeric values
    and hooks up notification of changes.

    Args:
        parent: The parent control for the Entry.
        variable: The StringVar used to store the value internally.
        option: The keyword used for the option.
        tooltip: The tooltip for the Entry.
    """
    if not binding.version_has_option(option):
        return fake_control
    e = Entry(
        parent, width=4, validate='key', justify='center',
        validatecommand=__ui.vcmd, textvariable=variable)
    variable.trace(
        "w", lambda name, index, mode: __ui.change_entry(option, variable))
    create_tooltip(e, tooltip)
    binding.bind(e, option)
    return e

# vim:expandtab
