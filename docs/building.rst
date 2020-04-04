Running or Building PyLNP
#########################

This document describes how to run PyLNP.  For most users, we suggest
just using `the latest stand-alone executable version
<https://github.com/Pidgeot/python-lnp/releases>`_,
which are available for Windows, OSX, and Linux.
You may wish to download PyLNP as part of a complete package for beginners,
`which can be found here <http://dwarffortresswiki.org/Lazy_Newb_Pack>`_.

If you have configuration problems or other errors, want to run the source
code directly, or want to build your own stand-alone executable, the
remainder of this page is for you.


.. contents::


Platform-specific notes
=======================
Windows
-------
If the program refuses to start, or gives an error message like:

    *The application has failed to start because the side-by-side configuration
    is incorrect. Please see the application event log for more details.*

you most likely need to install the `Microsoft Visual C++ 2008 redistributable
package <http://www.microsoft.com/en-us/download/details.aspx?id=29>`_.

The user interface library used by PyLNP has issues with high-DPI displays.
For builds made after February 28, 2016 (ie PyLNP v0.11 and later),
Windows should automatically scale the PyLNP window to match your
DPI settings, thereby avoiding these problems.

Linux
-----
On Linux and OS X, it is necessary to spawn a new terminal when using DFHack.
This is handled automatically on OS X, but unfortunately Linux provides no
standard way of doing this; it varies depending on your setup.

PyLNP will attempt to detect which terminals are available on your system. On
first launch, you will be asked to select which terminal to use; only terminals
available on your system will appear in the list.

PyLNP should be able to detect the GNOME, KDE, i3, LXDE, Mate, Xfce desktop
environments and window managers.  It can also handle the [u]rxvt
(urxvt is used if available, else rxvt) and xterm stand-alone terminals.

For other setups, you must configure a custom command.
For example, if your terminal can be spawned using::

  term -e <command>

then you should write this as ``term -e`` - the command will be automatically
appended. If you need the command to be placed elsewhere, use ``$`` as a
placeholder for the command.

Depending on your choice of terminal, desktop environment, etc., it may also be
necessary to use ``nohup`` with the command, e.g. ``nohup term -e``.

The terminal configuration UI includes a button to test if your custom command
is able to launch terminals correctly. The test consists of two processes - a
parent and a child - which will communicate with each other in various ways to
ensure that they are running independently of the other.

If the test fails, you will get an error message describing the issue briefly.
You will have to adjust your command accordingly.


Running from source
===================
If you think the download is too large, I suggest running from source
instead. There really isn't much to it, especially if you can live with a
slightly less pretty logo.

You will need to match the directory structure of the normal LNP. A download
without utilities is available in the Bay12 Forums thread for PyLNP.

You need Python installed to run the source code, either Python 2.7 or 3.3
and later, optionally with Pillow for better icons.  Linux users may also
need to install ``tk``; see below.

If Pillow is not available and you are using an old version of tk, the log
(:menuselection:`File --> Output`) will contain a line that starts with::

   Note: PIL not found and Tk version too old for PNG support...

PyLNP will still work, it will just look a little less pretty.

Windows
-------
Download a Windows installer for Python from http://python.org, which will
contain everything required to run PyLNP.  To get a better looking logo,
run the command ``pip install pillow`` in a terminal.

To run the code, double-click ``launch.py`` in the LNP folder. If you want
to get rid of the console window that pops up, rename it to ``launch.pyw``.

Linux
-----
Virtually all Linux distributions these days include Python, although
especially older installations may not have an appropriate version, and
some may not have Tk support installed by default.

If you can't get it to work, you'll need to install those things.
For Debian-based distributions, including Ubuntu and Linux Mint, the
``python-tk`` package is required, while ``python-imaging-tk`` is optional
(used to show nicer version of icon and logo).  For other distributions,
look for similar packages in your package manager.

To run the code, make sure launch.py is executable. Next, double-click and run it, or start
a terminal and execute it from there with ``python launch.py`` or
``./launch.py``.

OS X
----
If you're running OS X 10.7 or later, you should have everything that's
required. For 10.6 or earlier, upgrade Python to 2.7 or the latest 3.x
release; an installer is available on http://python.org .

To make the logo look better, you will need to install Pillow, a python
library for images. If you have MacPorts installed, use it to install the
package py-Pillow. If not, keep reading.

.. _osx_compilers:

First, you need to install command-line compilers. The easiest way I've
found is to install Xcode, then open it and go to :menuselection:`Preferences --> Downloads`
and install them from there. It should also be possible to download these
compilers directly from `Apple <https://developer.apple.com/downloads>`_,
but you're on your own for that.

Once the compilers are in place, open a Terminal and type ``sudo
easy_install pillow``. OS X should come with the libraries needed to build
Pillow to load the logo.

OS X does not provide a way to launch a Python script from Finder, so
to run the code you will need to start a terminal, navigate to the directory,
and execute ``python launch.py`` or ``./launch.py``.


Building your own executable
============================
If you want to make your own executable, you can do that. This is
particularly useful on OS X, which doesn't have any good way of launching a
Python script directly from Finder.

The executables are built using `PyInstaller <http://www.pyinstaller.org>`_
(v2.0 or later), which can be usually be installed with
``pip install pyintstaller``.  See below for specific instructions.

Open the PyLNP directory in a terminal and type ``pyinstaller lnp.spec``.
Wait for the build to finish, and you will find a new folder named dist.
Inside that folder is the stand-alone executable, named ``lnp.exe`` on Windows,
``lnp`` on Linux, and ``PyLNP`` (an application bundle) on OS X.

.. note::
    The resulting executable must be placed somewhere such that the program can
    find the folder containing Dwarf Fortress by navigating up the folder tree.
    For example, if Dwarf Fortress is located in ``/Games/Dwarf Fortress``, the
    PyLNP executable may be located in ``/Games``, ``/Games/PyLNP``,
    ``/Games/Utilities/Launcher``, etc.

These instructions are tested with Python 2.7, but should work with 3.x as
well. You may be able to substitute ``easy_install`` with ``pip install``.

Windows
-------
The best way I've found to install Pyinstaller is to first install setuptools_,
manually install pywin32_, and then run ``easy_install pyinstaller`` from
the ``Scripts`` directory in your Python installation.

.. _setuptools: https://pypi.python.org/pypi/setuptools/0.9.8#windows
.. _pywin32: http://sourceforge.net/projects/pywin32/files/pywin32

.. note::
  Depending on the exact package versions, you may experience issues running
  the generated executable. PyInstaller 2.1 with setuptools 18.2 is known to
  work, other combinations may not.

Linux
-----
The easiest way to install it is to use your package manager to install it
directly (if available), or first install python-pip from your package
manager and then run ``sudo pip install pyinstaller`` in a terminal.

OS X
----
A simple way to install Pyinstaller is to open a terminal and type
``sudo easy_install pyinstaller``.  You may also need to
:ref:`install command-line compilers <osx_compilers>`.

