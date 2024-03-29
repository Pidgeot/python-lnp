#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Static utility methods that are needed in several parts of the TkGui module.
"""

from tkinter import messagebox

from core import baselines, download
from core.lnp import lnp


def check_vanilla_raws():
    """Validates status of vanilla raws are ready."""
    if not download.get_queue('baselines').empty():
        return False
    raw_status = baselines.find_vanilla_raws()
    if raw_status is None:
        messagebox.showerror(
            message='Your Dwarf Fortress version could not be detected '
            'accurately, which is necessary to process this request.'
            '\n\nYou will need to restore the file "release notes.txt" in '
            'order to use this launcher feature.', title='Cannot continue')
        return False
    if raw_status is False:
        if lnp.userconfig.get_bool('downloadBaselines'):
            messagebox.showinfo(
                message='A copy of Dwarf Fortress needs to be '
                'downloaded in order to use this. The download is '
                'currently in progress.\n\nPlease note: You '
                'will need to retry the action after the download '
                'completes.', title='Download required')
        return False
    return True
