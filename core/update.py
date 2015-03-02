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
    simple_dffd_config()
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
    # pylint:disable=bare-except
    try:
        req = Request(
            lnp.config.get_string('updates/checkURL'),
            headers={'User-Agent':'PyLNP'})
        version_text = urlopen(req, timeout=3).read().decode('utf-8')
        # Note: versionRegex must capture the version string in a group
        new_version = re.search(
            lnp.config.get_string('updates/versionRegex'),
            version_text).group(1)
        if not lnp.config.get_string('updates/packVersion'):
            lnp.config.get_dict('updates')['packVersion'] = new_version
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
    url = lnp.config.get_string('updates/directURL')
    fname = os.path.basename(url).split('=')[-1]
    target = os.path.join(lnp.BASEDIR, fname)
    download.download(lnp.BASEDIR, url, target,
                      end_callback=extract_new_pack)

def extract_new_pack(_, fname, bool_val):
    """Extract a downloaded new pack to a sibling dir of the current pack."""
    exts = ('.zip', '.bz2', '.gz', '.7z', '.xz')
    if not bool_val or not any(fname.endswith(ext) for ext in exts):
        return None
    archive = os.path.join(lnp.BASEDIR, os.path.basename(fname))
    return extract_archive(archive, os.path.join(lnp.BASEDIR, '..'))

def extract_archive(fname, target):
    """Extract the archive fname to dir target, avoiding explosions."""
    if zipfile.is_zipfile(fname):
        zf = zipfile.ZipFile(fname)
        namelist = zf.namelist()
        topdir = namelist[0].split(os.path.sep)[0]
        if not all(f.startswith(topdir) for f in namelist):
            target = os.path.join(target, os.path.basename(fname).split('.')[0])
        zf.extractall(target)
        os.remove(fname)
        return True
    if tarfile.is_tarfile(fname):
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
    c = lnp.config
    u = lnp.config.get_dict('updates')
    download_patt = 'http://dffd.bay12games.com/file.php?id='
    check_patt = 'http://dffd.bay12games.com/file_version.php?id='
    direct = 'http://dffd.bay12games.com/download.php?id={0}&f=new_pack.zip'
    if (not c['updates/dffdID'] and
            c.get_string('updates/downloadURL').startswith(download_patt)):
        u['dffdID'] = c['updates/downloadURL'].replace(download_patt, '')
    if (not c['updates/dffdID'] and
            c.get_string('updates/checkURL').startswith(check_patt)):
        u['dffdID'] = c['updates/checkURL'].replace(check_patt, '')
    if c['updates/dffdID'] and not c['updates/checkURL']:
        u['checkURL'] = check_patt + c['updates/dffdID']
    if c['updates/dffdID'] and not c['updates/versionRegex']:
        u['versionRegex'] = 'Version: (.+)'
    if c['updates/dffdID'] and not c['updates/downloadURL']:
        u['downloadURL'] = download_patt + c['updates/dffdID']
    if c['updates/dffdID'] and not c['updates/directURL']:
        u['directURL'] = direct.format(c['updates/dffdID'])
    if u != lnp.config.get_dict('updates'):
        lnp.config['updates'] = u
        lnp.config.save_data()
