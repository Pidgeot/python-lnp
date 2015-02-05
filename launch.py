#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is used to launch the program."""
from __future__ import absolute_import
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
__package__ = ""

from core import lnp

lnp.PyLNP()
