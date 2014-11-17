#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Proxy to abstract access to JSON configuration and gracefully handle missing
keys."""
from __future__ import print_function, unicode_literals, absolute_import
import sys, os, json

if sys.version_info[0] == 3:  # Alternate import names
    enc_dict = {}
else:
    enc_dict = {'encoding': 'utf-8'}

class JSONConfiguration(object):
    """Proxy for JSON-based configuration files."""

    def __init__(self, filename):
        """
        Constructor for JSONConfiguration.

        Params:
            filename
                JSON filename to load data from.
        """
        self.filename = filename
        self.data = {}
        if not os.path.isfile(filename):
            print(
                "File " + filename + " does not exist",
                file=sys.stderr)
            return
        try:
            self.data = json.load(open(filename), **enc_dict)
        except:
            print(
                "Note: Failed to read JSON from " + filename +
                ", ignoring data - error details follow", file=sys.stderr)
            sys.excepthook(*sys.exc_info())

    def save_data(self):
        """Saves the data to the JSON file."""
        json.dump(
            self.data, open(self.filename, 'w'), indent=2, **enc_dict)

    def get_value(self, path, default=None):
        """
        Retrieves a value from the configuration.
        Returns default if the path does not exist.

        Params:
            path
                /-delimited path to the string.
            default
                Value returned if path does not exist.
        """
        try:
            path = path.split('/')
            result = self.data
            for p in path:
                result = result[p]
            return result
        except KeyError:
            return default

    def get_string(self, path):
        """
        Retrieves a value from the configuration.
        Returns an empty string if the path does not exist.

        Params:
            path
                /-delimited path to the string.
        """
        return self.get_value(path, "")

    def get_number(self, path):
        """
        Retrieves a value from the configuration.
        Returns 0 if the path does not exist.

        Params:
            path
                /-delimited path to the string.
        """
        return self.get_value(path, 0)

    def get_bool(self, path):
        """
        Retrieves a value from the configuration.
        Returns False if the path does not exist.

        Params:
            path
                /-delimited path to the string.
        """
        return self.get_value(path, False)

    def get_list(self, path):
        """
        Retrieves a value from the configuration.
        Returns an empty list if the path does not exist.

        Params:
            path
                /-delimited path to the string.
        """
        return self.get_value(path, [])

    def get_dict(self, path):
        """
        Retrieves a value from the configuration.
        Returns an empty dictionary if the path does not exist.

        Params:
            path
                /-delimited path to the string.
        """
        return self.get_value(path, {})

    def set_value(self, key, value):
        """
        Writes a value to a key.
        Note: Arbitrary paths not supported - you must refresh entire key.

        Params:
            key
                The key to save the value under.
            value
                The value to save.
        """
        self.__setitem__(key, value)

    def __getitem__(self, key):
        """Accessor for indexing directly into the configuration."""
        return self.get_value(key)

    def __setitem__(self, key, value):
        """Accessor for writing into the configuration with indexing."""
        self.data[key] = value
