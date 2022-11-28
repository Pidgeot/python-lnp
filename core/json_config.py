#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Proxy to abstract access to JSON configuration and gracefully handle missing
keys."""

import json
import os

from . import log


class JSONConfiguration(object):
    """Proxy for JSON-based configuration files."""

    def __init__(self, filename, default=None, warn=True):
        """
        Constructor for JSONConfiguration.

        Args:
            filename: JSON filename to load data from.
                Use None to only use object from default.
            default: default value to use in case loading fails.
            warn (bool): Log a warning if the file is missing, default True.
        """
        self.filename = filename
        self.data = default if default else {}
        if filename is None:
            return
        if not os.path.isfile(filename):
            if warn:
                log.w("JSONConfiguration: File " + filename + " does not exist")
            return
        try:
            #pylint: disable=bare-except
            with open(filename, encoding="utf-8") as file:
                self.data = json.load(file)
        except:
            log.e('Note: Failed to read JSON from ' + filename +
                  ', ignoring data - details follow', stack=True)

    @staticmethod
    def from_text(text):
        """Create a JSONConfiguration object from a string."""
        return JSONConfiguration(None, json.loads(text))

    def save_data(self):
        """Saves the data to the original JSON file. Has no effect if no
        filename was given during construction."""
        if self.filename:
            with open(self.filename, 'w', encoding="utf-8") as file:
                json.dump(self.data, file, indent=2)

    def get(self, path, default=None):
        """
        Retrieves a value from the configuration.
        Returns default if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
            default: value returned if path does not exist.
        """
        try:
            path = path.split('/')
            result = self.data
            for p in path:
                result = result[p]
            return result
        except KeyError:
            return default

    def has_value(self, path):
        """Returns True if the path exists in the configuration."""
        return self.get_value(path) is not None

    def get_value(self, path, default=None):
        """
        Retrieves a value from the configuration.
        Returns default if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
            default: value returned if path does not exist.
        """
        return self.get(path, default)

    def get_string(self, path):
        """
        Retrieves a value from the configuration.
        Returns an empty string if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
        """
        return self.get_value(path, "")

    def get_number(self, path):
        """
        Retrieves a value from the configuration.
        Returns 0 if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
        """
        return self.get_value(path, 0)

    def get_bool(self, path):
        """
        Retrieves a value from the configuration.
        Returns False if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
        """
        return self.get_value(path, False)

    def get_list(self, path):
        """
        Retrieves a value from the configuration.
        Returns an empty list if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
        """
        return self.get_value(path, [])

    def get_dict(self, path):
        """
        Retrieves a value from the configuration.
        Returns an empty dictionary if the path does not exist.

        Args:
            path: ``/``-delimited path to the string.
        """
        return self.get_value(path, {})

    def set_value(self, key, value):
        """
        Writes a value to a key.
        Note: Arbitrary paths not supported - you must refresh entire key.

        Args:
            key: the key to save the value under.
            value: the value to save.
        """
        self.__setitem__(key, value)  # pylint: disable=unnecessary-dunder-call

    def __getitem__(self, key):
        """Accessor for indexing directly into the configuration."""
        return self.get_value(key)

    def __setitem__(self, key, value):
        """Accessor for writing into the configuration with indexing."""
        self.data[key] = value
