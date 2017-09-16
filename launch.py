#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is used to launch the program."""
from __future__ import absolute_import
import sys, os
from core import lnp
sys.path.insert(0, os.path.dirname(__file__))
#pylint: disable=redefined-builtin
__package__ = ""

lnp.PyLNP()
