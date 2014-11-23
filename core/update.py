#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update handling."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, re, time, os, threading

try:  # Python 2
    # pylint:disable=import-error
    from urllib2 import urlopen, URLError, Request
except ImportError:  # Python 3
    # pylint:disable=import-error, no-name-in-module
    from urllib.request import urlopen, Request
    from urllib.error import URLError

from .lnp import lnp
from .df import DFInstall
from . import launcher, paths

def updates_configured():
    """Returns True if update checking have been configured."""
    return lnp.config.get_string('updates/checkURL') != ''

def check_update():
    """Checks for updates using the URL specified in PyLNP.json."""
    if not updates_configured():
        return
    if lnp.userconfig.get_number('updateDays') == -1:
        return
    if lnp.userconfig.get_number('nextUpdate') < time.time():
        t = threading.Thread(target=perform_update_check)
        t.daemon = True
        t.start()

def perform_update_check():
    """Performs the actual update check. Runs in a thread."""
    try:
        req = Request(
            lnp.config.get_string('updates/checkURL'),
            headers={'User-Agent':'PyLNP'})
        version_text = urlopen(req, timeout=3).read()
        # Note: versionRegex must capture the version number in a group
        new_version = re.search(
            lnp.config.get_string('updates/versionRegex'),
            version_text).group(1)
        if new_version != lnp.config.get_string('updates/packVersion'):
            lnp.new_version = new_version
            lnp.ui.on_update_available()
    except URLError as ex:
        print(
            "Error checking for updates: " + str(ex.reason),
            file=sys.stderr)
    except:
        pass

def next_update(days):
    """Sets the next update check to occur in <days> days."""
    lnp.userconfig['nextUpdate'] = (time.time() + days * 24 * 60 * 60)
    lnp.userconfig['updateDays'] = days
    lnp.save_config()

def start_update():
    """Launches a webbrowser to the specified update URL."""
    launcher.open_url(lnp.config.get_string('updates/downloadURL'))

def download_df_baseline():
    """Download the current version of DF from Bay12 Games to serve as a
    baseline, in LNP/Baselines/

    Returns:
        True if the download was started (in a thread, for availability later)
        False if the download did not start (eg because of another thread)
        None if the version string was invalid
    """
    if not re.match(r'df_\d\d_\d\d\w*', version):
        return None
    filename = DFInstall.get_archive_name()
    if not 'download_' + version in (t.name for t in threading.enumerate()):
        t = threading.Thread(target=download_df_zip_from_bay12,
                             args=(filename,), name='download_' + version)
        t.daemon = True
        t.start()
        return True
    else:
        return False

def download_df_zip_from_bay12(filename):
    """Downloads a zipped version of DF from Bay12 Games.
    'filename' is the full name of the file to retrieve,
    eg 'df_40_07_win.zip'    """
    url = 'http://www.bay12games.com/dwarves/' + filename
    req = Request(url, headers={'User-Agent':'PyLNP'})
    archive = urlopen(req, timeout=3).read()
    with open(os.path.join(paths.get('baselines'), filename), 'wb') as f:
        f.write(archive)
        f.close()
