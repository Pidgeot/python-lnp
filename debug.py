#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Use this script to run PyLNP from a different directory than it's
normally located in. Useful for development, so you can work on a copy
located elsewhere."""
import lnp

lnp.BASEDIR = '..' #Path containing the actual LNP folder.

#If you want to test an alternate UI, import it here and make PyLNP use it with
#
#lnp.TkGui = your_class
#
#The UI constructor should take 1 argument; a reference to the PyLNP instance.

lnp.PyLNP()
