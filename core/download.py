#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Background download management."""
from __future__ import print_function, unicode_literals, absolute_import

import os, shutil, tempfile
from threading import Thread, Lock
from .lnp import VERSION

from . import log

try:  # Python 2
    # pylint:disable=import-error
    from urllib2 import urlopen, Request, URLError
except ImportError:  # Python 3
    # pylint:disable=import-error, no-name-in-module
    from urllib.request import urlopen, Request
    from urllib.error import URLError

__download_queues = {}

def download(queue, url, destination, end_callback=None):
    """Adds a download to the specified queue."""
    return get_queue(queue).add(url, destination, end_callback)

def queue_empty(queue):
    """Returns True if the specified queue does not exist, or is empty;
    otherwise False."""
    return queue not in __download_queues or __download_queues[queue].empty()

def get_queue(queue):
    """Returns the specified queue object, creating a new queue if necessary."""
    __download_queues.setdefault(queue, DownloadQueue(queue))
    return __download_queues[queue]

class DownloadQueue(object):
    """Queue used for downloading files."""
    def __init__(self, name):
        self.name = name
        self.queue = []
        self.on_start_queue = []
        self.on_begin_download = []
        self.on_progress = []
        self.on_end_download = []
        self.on_end_queue = []
        self.thread = None
        self.lock = Lock()

    def add(self, url, target, end_callback):
        """Adds a download to the queue.

        Params:
            url
                The URL to download.
            target
                The target path for the download.
            end_callback
                A function(url, filename, success) which is called
                when the download finishes."""
        with self.lock:
            if url not in [q[0] for q in self.queue]:
                self.queue.append((url, target, end_callback))
                log.d(self.name+': queueing '+url+' for download to '+target)
            else:
                log.d(self.name+': skipping add of '+url+', already in queue')
            if not self.thread:
                log.d('Download queue '+self.name+' not running, starting it')
                self.thread = t = Thread(target=self.__process_queue)
                t.daemon = True
                t.start()

    def empty(self):
        """Returns True if the queue is empty, otherwise False."""
        return len(self.queue) == 0

    def register_start_queue(self, func):
        """Registers a function func(queue_name) to be called when the queue is
        started. If False is returned by any function, the queue is cleared."""
        self.on_start_queue.append(func)

    def unregister_start_queue(self, func):
        """Unregisters a function func from being called when the queue is
        started."""
        self.on_start_queue.remove(func)

    def register_begin_download(self, func):
        """Registers a function func(queue_name, url) to be called when a
        download is started."""
        self.on_begin_download.append(func)

    def unregister_begin_download(self, func):
        """Unregisters a function func from being called when a download is
        started."""
        self.on_begin_download.remove(func)

    def register_progress(self, func):
        """Registers a function func(queue_name, url, downloaded, total_size) to
        be called for download progress reports.
        If total size is unknown, None will be sent."""
        self.on_progress.append(func)

    def unregister_progress(self, func):
        """Unregisters a function from being called for download progress
        reports."""
        self.on_progress.remove(func)

    def register_end_download(self, func):
        """Registers a function func(queue_name, url, filename, success) to be
        called when a download is finished."""
        self.on_end_download.append(func)

    def unregister_end_download(self, func):
        """Unregisters a function func from being called when a download is
        finished."""
        self.on_end_download.remove(func)

    def register_end_queue(self, func):
        """Registers a function func(queue_name) to be called when the
        queue is emptied."""
        self.on_end_queue.append(func)

    def unregister_end_queue(self, func):
        """Unregisters a function func from being called when the queue is
        emptied."""
        self.on_end_queue.remove(func)

    def __process_callbacks(self, callbacks, *args):
        """Calls the provided set of callback functions with <args>."""
        results = []
        for c in callbacks:
            # pylint: disable=bare-except
            try:
                results.append(c(self.name, *args))
            except:
                results.append(None)
        return results

    def __process_queue(self):
        """Processes the download queue."""
        # pylint: disable=bare-except
        if False in self.__process_callbacks(self.on_start_queue):
            with self.lock:
                self.queue = []
                self.thread = None
                return

        while True:
            with self.lock:
                if self.empty():
                    self.thread = None
                    break
            url, target, end_callback = self.queue[0]
            log.d(self.name+': About to download '+url+' to '+target)
            self.__process_callbacks(self.on_begin_download, url, target)
            dirname = os.path.dirname(target)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            outhandle, outpath = tempfile.mkstemp(dir=dirname)
            outfile = os.fdopen(outhandle, 'wb')
            try:
                req = Request(url, headers={'User-Agent':'PyLNP/'+VERSION})
                response = urlopen(req, timeout=5)
                data = 0
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    total = response.info().get('Content-Length')
                    data += len(chunk)
                    outfile.write(chunk)
                    self.__process_callbacks(self.on_progress, url, data, total)
            except:
                outfile.close()
                os.remove(outpath)
                log.e(self.name+': Error downloading ' + url, stack=True)
                self.__process_callbacks(
                    self.on_end_download, url, target, False)
                if end_callback:
                    end_callback(url, target, False)
            else:
                outfile.close()
                shutil.move(outpath, target)
                log.d(self.name+': Finished downloading '+url)
                self.__process_callbacks(
                    self.on_end_download, url, target, True)
                if end_callback:
                    end_callback(url, target, True)
            with self.lock:
                self.queue.pop(0)

        self.__process_callbacks(self.on_end_queue)
