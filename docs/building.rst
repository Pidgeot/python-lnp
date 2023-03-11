Running or Building PyLNP
#########################

This document describes how to run PyLNP.  For most users, we suggest
just using `the latest stand-alone executable version
<https://github.com/Pidgeot/python-lnp/releases>`_,
which are available for Windows, OSX, and Linux.
You may wish to download PyLNP as part of a complete package for beginners,
`which can be found here <https://dwarffortresswiki.org/Lazy_Newb_Pack>`_.

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

you most likely need to install the `Microsoft Visual C++ 2015 redistributable
package <https://www.microsoft.com/en-us/download/details.aspx?id=48145>`_.

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

You need Python 3.3 or later installed to run the source code, optionally with
Pillow for better icons.  Linux users may also need to install ``tk``; see
below.

If Pillow is not available and you are using an old version of tk, the log
(:menuselection:`File --> Output`) will contain a line that starts with::

   Note: PIL not found and Tk version too old for PNG support...

PyLNP will still work, it will just look a little less pretty.

Windows
-------
Download a Windows installer for Python from https://python.org, which will
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
required. For 10.6 or earlier, upgrade Python to the latest 3.x release; an
installer is available on https://python.org .

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

The executables are built using `PyInstaller <https://www.pyinstaller.org>`_
(v4.2 or later), which can be usually be installed with
``pip install pyinstaller``.  See below for specific instructions.

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

If ``pip`` is not available on your system, you may need to install it, either from a package manager or by running ``python -m ensurepip`` from the command-line. If you can't use the regular pip command, ``python -m pip <command>`` works too.

Windows
-------
PyInstaller 4.8 introduces a hook script which will break DFHack. A `bug report <https://github.com/pyinstaller/pyinstaller/issues/7118>`_ already exists for Pyinstaller for this issue, but at time of writing, it's still an issue. For now, use an older version; anything from 4.2 to 4.7 should definitely work; 4.6 is being used for the official builds. Use ``pip install PyInstaller==4.6`` to install that one.

Note that your resulting build will have the same Windows requirements as the Python version used to build. To support Windows Vista and 7, you need to use Python 3.8 or earlier.

Linux
-----
If your package manager provides PyInstaller, install it from there. Otherwise, use pip.

OS X
----
You may need to :ref:`install command-line compilers <osx_compilers>`.

