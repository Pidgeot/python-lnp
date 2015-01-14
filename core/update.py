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
from . import launcher, paths, download

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
        simple_dffd_config()
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
        if not lnp.config.get_string('updates/packVersion'):
            lnp.config['updates/packVersion'] = new_version
            lnp.config.save_data()
            return
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
    baseline, in LNP/Baselines/"""
    filename = lnp.df_info.get_archive_name()
    url = 'http://www.bay12games.com/dwarves/' + filename
    target = os.path.join(paths.get('baselines'), filename)
    download.download('baselines', url, target)

def simple_dffd_config():
    """Reduces the configuration required by maintainers using DFFD.
    Values are generated and saved from known URLs and the 'dffdID' field."""
    dffd_num = lnp.config.get_number('updates/dffdID')
    if not dffd_num and lnp.config.get_string('updates/downloadURL'
            '').startswith('http://dffd.wimbli.com/file.php?id='):
        dffd_num = lnp.config.get_string('updates/downloadURL'
            '').replace('http://dffd.wimbli.com/file.php?id=', '')
        lnp.config.save_data()
    if not dffd_num and lnp.config.get_string('updates/checkURL'
            '').startswith('http://dffd.wimbli.com/file_version.php?id='):
        dffd_num = lnp.config.get_string('updates/checkURL'
            '').replace('http://dffd.wimbli.com/file_version.php?id=', '')
        lnp.config.save_data()

    if dffd_num and not lnp.config.get_string('updates/checkURL'):
        lnp.config['updates/checkURL'] = ('http://dffd.wimbli.com/file_'
                                          'version.php?id=' + dffd_num)
        lnp.config.save_data()
    if dffd_num and not lnp.config.get_string('updates/versionRegex'):
        lnp.config['updates/versionRegex'] = 'Version: (.+)'
        lnp.config.save_data()
    if dffd_num and lnp.config.get_string('updates/downloadURL'):
        lnp.config['updates/downloadURL'] = ('http://dffd.wimbli.com/file'
                                             '.php?id=' + dffd_num)            
        lnp.config.save_data()
    if dffd_num and lnp.config.get_string('updates/directURL'):
        # TODO: improve pack name handling; this works but isn't great
        fname = 'new_pack.zip'
        lnp.config['updates/directURL'] = ('http://dffd.wimbli.com/download.'
                                           'php?id=' + dffd_num + '&f=' + fname)
        lnp.config.save_data()
