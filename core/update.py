#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update handling."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, re, time, os, threading, zipfile, tarfile

try:  # Python 2
    # pylint:disable=import-error
    from urllib2 import urlopen, URLError, Request
except ImportError:  # Python 3
    # pylint:disable=import-error, no-name-in-module
    from urllib.request import urlopen, Request
    from urllib.error import URLError

from .lnp import lnp
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
        # Note: versionRegex must capture the version string in a group
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

def direct_download_pack():
    """Directly download a new version of the pack to the current BASEDIR"""
    fname = 'new_pack.txt'
    url = lnp.config.get_string('updates/directURL')
    target = os.path.join(lnp.BASEDIR, fname)
    # TODO:  confirm this callback works
    download.download(lnp.BASEDIR, url, target,
                      end_callback=extract_new_pack)

def extract_new_pack():
    """Extract a downloaded new pack to a sibling dir of the current pack."""
    exts = ('.zip', '.bz2', '.gz', '.7z', '.xz')
    pack = [f for f in os.listdir(lnp.BASEDIR) if os.path.isfile(f) and
            any((f.endswith(i) for i in exts))]
    if len(pack) == 1:
        fname = pack[0]
    elif len(pack) > 1:
        fname = pack[0]
        for p in pack:
            if (os.path.getmtime(os.path.join(lnp.BASEDIR, p)) >
                    os.path.getmtime(os.path.join(lnp.BASEDIR, fname))):
                fname = p
    if fname:
        archive = os.path.join(lnp.BASEDIR, fname)
        target = os.path.join(lnp.BASEDIR, '..')
        extract_archive(archive, target)

def extract_archive(fname, target):
    """Extract the archive fname to dir target, avoiding explosions."""
    if fname.endswith('.zip'):
        zf = zipfile.ZipFile(fname)
        namelist = zf.namelist()
        topdir = namelist[0].split(os.path.sep)[0]
        if not all(f.startswith(topdir) for f in namelist):
            target = os.path.join(target, fname.split('.')[0])
        zf.extractall(target)
        os.remove(fname)
        return True
    if fname.endswith('.bz2') or fname.endswith('.gz'):
        tf = tarfile.open(fname)
        namelist = tf.getmembers()
        topdir = namelist[0].split(os.path.sep)[0]
        if not all(f.startswith(topdir) for f in namelist):
            target = os.path.join(target, fname.split('.')[0])
        tf.extractall(target)
        os.remove(fname)
        return True
    # TODO:  support '*.xz' and '*.7z' files.
    return False

def simple_dffd_config():
    """Reduces the configuration required by maintainers using DFFD.
    Values are generated and saved from known URLs and the 'dffdID' field."""
    dffd_num = lnp.config.get_number('updates/dffdID')
    if not dffd_num and lnp.config.get_string('updates/downloadURL')\
       .startswith('http://dffd.wimbli.com/file.php?id='):
        dffd_num = lnp.config.get_string('updates/downloadURL')\
                   .replace('http://dffd.wimbli.com/file.php?id=', '')
        lnp.config.save_data()
    if not dffd_num and lnp.config.get_string('updates/checkURL')\
       .startswith('http://dffd.wimbli.com/file_version.php?id='):
        dffd_num = lnp.config.get_string('updates/checkURL')\
                   .replace('http://dffd.wimbli.com/file_version.php?id=', '')
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
        # TODO:  improve pack name handling; this works but isn't great
        fname = 'new_pack.zip'
        lnp.config['updates/directURL'] = ('http://dffd.wimbli.com/download.'
                                           'php?id=' + dffd_num + '&f=' + fname)
        lnp.config.save_data()
