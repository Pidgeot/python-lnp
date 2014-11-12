#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Code used for modifying DF RAW files"""
from __future__ import print_function, unicode_literals, absolute_import
import io
import re


class Raw:
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
        return io.open(path, mode, encoding='cp437', errors='replace')

    @classmethod
    def read(cls, path):
        with cls.open(path, 'rt') as fd:
            return fd.read()

    @classmethod
    def write(cls, path, text):
        with cls.open(path, 'wt') as fd:
            return fd.write(text)

    def save(self):
        return self.write(self.path, self.text)

    def toggle(self, field, enabled):
        self.modified = True
        if enabled:
            replace_from, replace_to = self._option_enable
        else:
            replace_from, replace_to = self._option_disable

        self.text = self.text.replace(
            replace_from.format(field),
            replace_to.format(field))

    def set_value(self, field, value):
        self.modified = True
        self.text = re.sub(
            r'\[{0}:(.+?)\]'.format(field),
            '[{0}:{1}]'.format(
                field, value), self.text)