#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update handling."""
from __future__ import print_function, unicode_literals, absolute_import

import re, time, os, threading, zipfile, tarfile

from .lnp import lnp
from . import launcher, paths, download, log
from .json_config import JSONConfiguration

try:  # Python 2
    # pylint:disable=import-error, no-name-in-module
    from urllib import quote, unquote
    from urlparse import urlparse
except ImportError:  # Python 3
    # pylint:disable=import-error, no-name-in-module
    from urllib.parse import quote, unquote, urlparse

def updates_configured():
    """Returns True if update checking have been configured."""
    return prepare_updater() is not None

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
    # pylint:disable=bare-except
    prepare_updater()
    if lnp.updater.update_needed():
        lnp.new_version = lnp.updater.get_version()
        lnp.ui.on_update_available()

def prepare_updater():
    """Returns an Updater object for the configured updater."""
    if lnp.updater:
        return lnp.updater
    updaters = {'regex': RegexUpdater, 'json': JSONUpdater, 'dffd': DFFDUpdater}
    updater_id = lnp.config.get('updates/updateMethod', None)
    if updater_id is None:
        #TODO: Remove this after packs have had time to migrate
        log.w(
            'Update method not configured in PyLNP.json! Will attempt to '
            'auto-detect. Please set this value correctly, auto-detection will '
            'go away eventually!')
        if lnp.config.get_string('updates/dffdID'):
            updater_id = 'dffd'
            log.w('Updater detected: dffd')
        elif lnp.config.get_string('updates/versionRegex'):
            updater_id = 'regex'
            log.w('Updater detected: regex')
        elif lnp.config.get_string('updates/versionJsonPath'):
            updater_id = 'json'
            log.w('Updater detected: json')
        else:
            log.w('Could not detect update method, updates will not work')
            return None
    elif updater_id == '' or not lnp.config.get('updates'):
        return None
    if updater_id not in updaters:
        log.e('Unknown update method: '+updater_id)
        return None
    lnp.updater = updaters[updater_id]()
    return lnp.updater

def next_update(days):
    """Sets the next update check to occur in <days> days."""
    lnp.userconfig['nextUpdate'] = (time.time() + days * 24 * 60 * 60)
    lnp.userconfig['updateDays'] = days
    lnp.save_config()

def start_update():
    """Launches a webbrowser to the specified update URL."""
    launcher.open_url(lnp.updater.get_download_url())

def download_df_baseline():
    """Download the current version of DF from Bay12 Games to serve as a
    baseline, in LNP/Baselines/"""
    filename = lnp.df_info.get_archive_name()
    url = 'http://www.bay12games.com/dwarves/' + filename
    target = os.path.join(paths.get('baselines'), filename)
    download.download('baselines', url, target)

def direct_download_pack():
    """Directly download a new version of the pack to the current BASEDIR"""
    url = lnp.updater.get_direct_url()
    fname = lnp.updater.get_direct_filename()
    target = os.path.join(lnp.BASEDIR, fname)
    download.download('updates', url, target,
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


#pylint: disable=attribute-defined-outside-init, no-self-use

class Updater(object):
    """General class for checking for updates."""
    def update_needed(self):
        """Checks if an update is necessary."""
        self.text = download.download_str(self.get_check_url())
        if self.text is None:
            log.e("Error checking for updates")
        curr_version = lnp.config.get_string('updates/packVersion')
        if not curr_version:
            log.e("Current pack version is not set, cannot check for updates")
            return False
        return (self.get_version() != curr_version)

    def get_check_url(self):
        """Returns the URL used to check for updates."""
        return lnp.config.get_string('updates/checkURL')

    def get_version(self):
        """Returns the version listed at the update URL. Must be overridden by
        subclasses."""
        pass

    def get_download_url(self):
        """Returns a URL from which the user can download the update."""
        return lnp.config.get_string('updates/downloadURL')

    def get_direct_url(self):
        """Returns a URL pointing directly to the update, for download by the
        program."""
        return lnp.config.get_string('updates/directURL')

    def get_direct_filename(self):
        """Returns the filename that should be used for direct downloads."""
        directFilename = lnp.config.get_string('updates/directFilename')
        if directFilename:
            return directFilename
        url_fragments = urlparse(self.get_direct_url())
        return os.path.basename(unquote(url_fragments.path))

class RegexUpdater(Updater):
    """Updater class which uses regular expressions to locate the version (and
    optionally also the download URLs)."""
    def get_version(self):
        versionRegex = lnp.config.get_string('updates/versionRegex')
        if not versionRegex:
            log.e('Version regex not configured!')
        return re.search(versionRegex, self.text).group(1)

    def get_download_url(self):
        urlRegex = lnp.config.get_string('updates/downloadURLRegex')
        result = ''
        if urlRegex:
            result = re.search(urlRegex, self.text).group(1)
        if result:
            return result
        else:
            return super(RegexUpdater, self).get_download_url()

    def get_direct_url(self):
        urlRegex = lnp.config.get_string('updates/directURLRegex')
        result = ''
        if urlRegex:
            result = re.search(urlRegex, self.text).group(1)
        if result:
            return result
        else:
            return super(RegexUpdater, self).get_direct_url()

class JSONUpdater(Updater):
    """Updater class which uses a JSON object to locate the version (and
    optionally also the download URLs)."""
    def get_version(self):
        self.json = JSONConfiguration.from_text(self.text)
        jsonPath = lnp.config.get_string('updates/versionJsonPath')
        if not jsonPath:
            log.e('JSON path to version not configured!')
        return self.json.get_string(jsonPath)

    def get_download_url(self):
        jsonPath = lnp.config.get_string('updates/downloadURLJsonPath')
        result = ''
        if jsonPath:
            result = self.json.get_string(jsonPath)
        if result:
            return result
        else:
            return super(JSONUpdater, self).get_download_url()

    def get_direct_url(self):
        jsonPath = lnp.config.get_string('updates/directURLJsonPath')
        result = ''
        if jsonPath:
            result = self.json.get_string(jsonPath)
        if result:
            return result
        else:
            return super(JSONUpdater, self).get_direct_url()

    def get_direct_filename(self):
        jsonPath = lnp.config.get_string('updates/directFilenameJsonPath')
        result = ''
        if jsonPath:
            result = self.json.get_string(jsonPath)
        if result:
            return result
        else:
            return super(JSONUpdater, self).get_direct_filename()

class DFFDUpdater(Updater):
    """Updater class for DFFD-hosted downloads."""
    def get_check_url(self):
        self.dffd_id = lnp.config.get_string('updates/dffdID')
        return 'http://dffd.bay12games.com/file_data/'+self.dffd_id+'.json'

    def get_version(self):
        self.json = JSONConfiguration.from_text(self.text)
        return self.json.get_string('version')

    def get_download_url(self):
        return 'http://dffd.bay12games.com/file.php?id='+self.dffd_id

    def get_direct_url(self):
        result = 'http://dffd.bay12games.com/download.php?id={0}&f={1}'
        return result.format(
            self.dffd_id, quote(self.json.get_string('filename')))

    def get_direct_filename(self):
        return self.json.get_string('filename')
