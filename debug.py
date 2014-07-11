#!/usr/bin/env python
# -*- coding: utf-8 -*-
import lnp
import os

#Use this script to run PyLNP from a different directory than it's normally located in. Useful for development, so you can work on a copy located elsewhere.

lnp.BASEDIR = '..' #Path containing the actual LNP folder.

#If you want to test an alternate UI, you can import it here and make PyLNP use it with
#
#lnp.TkGui = your_class
#
#Note that the class constructor should take exactly one argument, a reference to the PyLNP instance.

lnp.PyLNP()
