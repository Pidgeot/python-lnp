#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Modification of Dwarf Fortress raw files."""
from __future__ import print_function, unicode_literals, absolute_import
import io
import re
import sys

if sys.version_info[0] == 3:
    #pylint: disable=redefined-builtin
    basestring = str

class DFRaw(object):
    """Representation of a Dwarf Fortress raw file of reading and writing."""
    _option_disable = ("[{0}]", "!{0}!")
    _option_enable = tuple(reversed(_option_disable))

    def __init__(self, path):
        self.path = path
        self.modified = False
        self.text = self.read(path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.modified:
            self.save()

    @staticmethod
    def open(path, mode):
        """
        Opens a raw file at <path> with mode <mode> and returns a stream
        :param str path: Path to raw file
        :param mode: File mode
        :return io.TextIOWrapper:
        """
        return io.open(path, mode, encoding='cp437', errors='replace')

    @classmethod
    def read(cls, path):
        """
        Returns text of raw file at <path>
        :param str path:
        :return str:
        """
        with cls.open(path, 'rt') as fd:
            return fd.read()

    @classmethod
    def write(cls, path, text):
        """
        Writes <text> to a raw file at <path>
        :param str path:
        :param str text:
        :return:
        """
        with cls.open(path, 'wt') as fd:
            return fd.write(text)

    def save(self):
        """
        Writes current raw file
        :return int: bytes written
        """
        return self.write(self.path, self.text)

    def toggle(self, field, enabled):
        """
        Toggles (disables/enables) a <field> in the raw file
        :param str field: Name of the field
        :param bool enabled:
        :return:
        """
        self.modified = True
        if enabled:
            replace_from, replace_to = self._option_enable
        else:
            replace_from, replace_to = self._option_disable

        self.text = self.text.replace(
            replace_from.format(field),
            replace_to.format(field))

    def set_value(self, field, value):
        """
        Sets the value of <field> to <value>
        :param str field:
        :param str value:
        :return:
        """
        self.modified = True
        self.text = re.sub(
            r'\[{0}:(.+?)\]'.format(field),
            '[{0}:{1}]'.format(
                field, value), self.text)

    def get_value(self, field):
        """
        Returns value of field <field>. If multiple fields with this name exist,
        returns the first one.
        If no such field exists returns None.

        :param str field: The field to read
        :return str or None: The value of the field or None
        """
        match = re.search(r'\['+str(field)+r':(.+?)\]', self.text)
        if match:
            return match.group(1)
        return None

    def get_values(self, *fields):
        """
        Return values of <fields>. The nesting and order of the
        resulting list will match the nesting and order of <fields>
        For any field the behaviour is the same as get_field.
        :param fields:
        :return list:
        """
        result = []
        for field in fields:
            if isinstance(field, (str, basestring)):
                result.append(self.get_value(field))
            elif isinstance(field, (tuple, list)):
                result.append(self.get_values(*field))
            else:
                result.append(None)
        return result
