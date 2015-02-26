=====
PyLNP
=====
------------------------------------------
A third-party launcher for Dwarf Fortress.
------------------------------------------

It has a variety of useful features to manage settings and configure the base
game.  It can also manage, configure, install, and run a wide variety of
related content - from graphics to color schemes, and utility programs to
content-replacing mods.

It forms the core of various bundles for new, lazy, or impatient players -
such as the old "Lazy Newb Pack".  While this project is just the launcher,
you can download a complete bundle for Windows, OSX, or Linux at
http://lazynewbpack.com/

If you have a question that is not answered here, go ahead and ask it in the
`Bay12 forum thread for PyLNP.`__

.. __: http://www.bay12forums.com/smf/index.php?topic=140808

.. contents::

Usage Instructions
==================
There's not much to it:  run the launcher (see below) then click the buttons
to configure your DF install, change settings or graphics, merge and install
mods, run utility programs, start DF, and more.

This section should probably be larger, but it should be clear how things
work from the tooltips if you hover over a button.  If not, ask in the forum
thread linked above!  The customisation section below, intended for advanced
users and those compiling a custom package, may also be helpful.

History
=======
PyLNP started as a port of LucasUP and tolyK's Lazy Newb Pack Launcher to
Python, making a launcher available on all the same platforms as Dwarf
Fortress.

The new edition includes many new and improved features; some of the
non-obvious ones including:

- Dwarf Fortress can be placed in an arbitrarily-named folder.
- If multiple valid DF folders are detected, you will be asked to select the
  desired instance. This allows you to manage multiple installs separately with
  the same launcher, though this is not recommended.
- A new menu item, File > Output log has been added. This opens a window
  containing various messages captured while executing the launcher. If errors
  occur, they will show up here, and are also written to a file.
- In addition to excluding specific file names from utilities, you can also
  *include* specific file names, if they're found. Simply create a file
  include.txt in the Utilities folder and fill it in with the same syntax as
  exclude.txt.
- Multiple utilities can be selected and launched simultaneously.
- Utilities may be automatically started at the same time as Dwarf Fortress.
- Color scheme installation and preview.
- Installing graphics sets by patching instead of replacing init.txt and
  d_init.txt. This preserves all options not strictly related to graphics sets.

--------------------
Running the launcher
--------------------

Platform-specific notes
=======================
On Linux and OS X, it is necessary to spawn a new terminal when using DFHack.
Unfortunately, Linux provides no standard way of doing this; it varies
depending on your setup.

For this reason, a secondary script, ``xdg-terminal``, is used to perform
this task. Unfortunately, this script cannot be guaranteed to work on *all*
Linux systems, and unsupported systems may not behave as intended,
particularly if the launcher is closed while DF is running.

The script should work as intended with any of the following desktop
environments and window managers:

- GNOME
- KDE
- MATE
- xfce
- lxde
- i3wm

For other setups, the script will attempt a fallback, but it is not guaranteed
to work. If it does not work for you, you can configure an alternate command
using File > Configure terminal. For example, if your terminal can be spawned
using:

  term -e <command>

then you should write this as ``term -e`` - the command will be automatically
appended. If you need the command to be placed elsewhere, use ``$`` as a
placeholder for the command.

Depending on your choice of terminal, desktop environment, etc., it may also be
necessary to use ``nohup`` with the command, e.g. ``nohup term
-e``.

To verify if your command works as intended, launch Dwarf Fortress with DFHack
installed and enabled. A working command will cause a new terminal window to
appear, PyLNP itself will remain responsive, and everything will continue to
work correctly even if you close PyLNP while Dwarf Fortress is running.

Pre-built executables
=====================
Stand-alone pre-built executables are available for Windows, Linux and OS X;
see the forum topic. Simply download and extract the appropriate file.

If you think the download is too large, I suggest running from source
instead. There really isn't much to it, especially if you can live with a
slightly less pretty logo.

*Note for Windows users:*
  If the program refuses to start, or gives an error message like:

    The application has failed to start because the side-by-side configuration
    is incorrect. Please see the application event log for more
    details.

  you most likely need to install the `Microsoft Visual C++ 2008
  redistributable package`__

.. __: http://www.microsoft.com/en-us/download/details.aspx?id=29

Running from source
===================
You will need to match the directory structure of the normal LNP. A download
without utilities is available in the topic.

You need Python installed to run the source code, preferably Python 2.7.
Python 3.1 or later should also work, but may not be as well tested.

Python 2.6 or 3.0 do not include the necessary Ttk library. It *may* work if
you install python-ttk__, but you should probably upgrade your Python version,
or use a pre-built executable.

.. __: http://code.google.com/p/python-ttk/

If you already have Python, but don't know which version you're using, open a
command-line or terminal and type "python --version". If this gives you Python
3.0, try "python2 --version"; if that returns Python 2.7, may want to edit the
first line of the .py and .pyw files to read "python2" instead of "python".

Installing prerequisites
------------------------
This program has a few dependencies which you may need to take care of before
running the source code:

- Since the program is written in Python, you will of course need to install
  Python. Linux and OS X 10.7 or later will most likely already have a suitable
  version; see above how to check this.
- The GUI requires the standard Python libraries Tkinter and Ttk, which is
  included in the Python installation on Windows and OS X. Linux users *may*
  need to install it through their package manager (look for python-tk or other
  similarly named package)
- *Optional:* For Python installations built against Tk 8.5: A PIL-compatible
  Python library (e.g. PIL itself or Pillow) will improve the visual quality of
  the logo by using a PNG version instead of a GIF. (On Linux, this also
  applies to the window icon.)

If this final dependency is not met, File > Output log will contain a line
that starts with

  Note: PIL not found and Tk version too old for PNG support...

The program will still work, it will just look a little less pretty.

Windows:
  Download a Windows installer for Python from http://python.org, which will
  contain everything required to run the program. Pick Python 2.7 unless you
  really want Python 3 - the program should work with both, but I'm testing
  it under 2.7, so that might be the simplest version to use.

  To get a better looking logo in Python 2.7, first install setuptools__, then
  open a command-line to the Scripts directory in your Python installation and
  run the command ``easy_install pillow``.  In Python 3.4+, just run the
  command ``pip install pillow``.
  
.. __: https://pypi.python.org/pypi/setuptools/0.9.8#windows

Linux:
  Virtually all Linux distributions these days include Python, although
  especially older installations may not have an appropriate version, and
  some may not have Tk support installed by default.

  If you can't get it to work, you'll need to install those things. This
  assumes a Debian-based distribution (including Ubuntu and Linux Mint). For
  other distributions, look for similar packages in your package manager.

  - **Required:** python-tk
  - Optional: python-imaging-tk (used to show nicer version of icon and logo)

  If you try to install python-imaging-tk, it should automatically bring in
  python-tk.

OS X:
  If you're running OS X 10.7 or later, you should have everything that's
  required. For 10.6 or earlier, upgrade Python to 2.7 or the latest 3.x
  release; an installer is available on http://python.org.

  To make the logo look better, you will need to install Pillow, a python
  library for images. If you have MacPorts installed, use it to install the
  package py-Pillow. If not, keep reading.

  First, you need to install command-line compilers. The easiest way I've
  found is to install Xcode, then open it and go to Preferences > Downloads
  and install them from there. It should also be possible to download these
  compilers directly from https://developer.apple.com/downloads/, but you're
  on your own for that.

  Once the compilers are in place, open a Terminal and type ``sudo
  easy_install pillow``. OS X should come with the libraries needed to build
  Pillow to load the logo.

Running the source code
-----------------------
Windows:
  Double-click launch.py in the LNP folder. If you want to get rid of the
  console window that pops up, rename it to launch.pyw.
Linux:
  Make sure launch.py is executable. Next, double-click and run it, or start
  a terminal and execute it from there with ``python launch.py`` or
  ``./launch.py``.
OS X:
  OS X does not provide a way to launch a Python script from Finder, so start
  a terminal, navigate to the directory, and execute ``python launch.py`` or
  ``./launch.py``.

Modifying the source code
=========================
PyLNP is licensed under the ISC license (see COPYING.txt), which essentially
allows you to modify and distribute changes as you see fit. (This only
applies to the launcher. Any bundled utilities, graphics packs, etc. have
their own licenses; refer to those projects separately.)

Building your own executable
============================
If you want to make your own executable, you can do that. This is
particularly useful on OS X, which doesn't have any good way of launching a
Python script directly from Finder.

The executables are built using PyInstaller. If you want to use a different
executable generator, you'll need to do the appropriate modifications yourself.

These instructions are tested with Python 2.7, but should work with 3.x as
well. You may be able to substitute "easy_install" with "pip install".

Note:
  The resulting executable must be placed in the same directory as the LNP.py
  script is currently placed (it should be next to your Dwarf Fortress
  folder, and the LNP data folder). This is because it relies on a specific
  directory structure in order to find the Dwarf Fortress folder, as well as
  utilities, graphics packs, etc.

Windows
-------
Installing prerequisites:
  You'll need PyInstaller_, preferably version 2.0 or later.  The best way I've
  found to install that is to first install setuptools_, manually install
  pywin32_, and then run ``easy_install pyinstaller`` from the ``Scripts``
  directory in your Python installation.

.. _PyInstaller: http://www.pyinstaller.org/
.. _setuptools: https://pypi.python.org/pypi/setuptools/0.9.8#windows
.. _pywin32: http://sourceforge.net/projects/pywin32/files/pywin32

Building:
  Open the LNP directory in a Command Prompt and type "pyinstaller lnp.spec".
  Wait for the build to finish, and you will find a new folder named dist.
  Inside that folder is the stand-alone executable, named lnp.exe.

Linux
-----
Installing prerequisites:
  You'll need PyInstaller__, preferably version 2.0 or later.

.. __: http://www.pyinstaller.org/

  The easiest way to install it is to use your package manager to install it
  directly (if available), or first install python-pip from your package
  manager and then run ``sudo pip install pyinstaller`` in a terminal.

Building:
  Open the LNP directory in a Terminal and type ``pyinstaller lnp.spec``.
  Wait for the build to finish, and you will find a new folder named dist.
  Inside that folder is the stand-alone executable, named lnp.

OS X
----
Installing prerequisites:
  You'll need PyInstaller__, preferably version 2.0 or later.

.. __: http://www.pyinstaller.org/

  A simple way to install it is to open a terminal and type ``sudo
  easy_install pyinstaller``.

  You may also need to install command-line compilers; see above.

Building:
  Open the LNP directory in a Terminal and type ``pyinstaller lnp.spec``.
  Wait for the build to finish, and you will find a new folder named dist.
  Inside that folder is the application bundle, PyLNP.

When something goes wrong
=========================
You may experience error messages or similar issues while running the
program. As long as it has not crashed, you can retrieve these error messages
by opening File > Output log. The contents shown in here can be very useful
for fixing the problem, so include them if you report an error.

If the program *does* crash, you can look at stdout.txt and stderr.txt which
are automatically created in the application directory and show the same
contents as the output log inside the program. Note that these files get
overwritten every time the program launches.

Please be as specific as possible when reporting an error - tell exactly what
you were doing. If you were installing a graphics pack, mention which one
(provide a link to where you got it). If the problem is with a utility, make
sure the utility works if you launch it manually - if it doesn't, then it's a
problem with the utility, not with PyLNP.

-------------
Customization
-------------

Various aspects of PyLNP can be customized (e.g. for use in packs). This
section details how.

PyLNP.json
==========
For basic pack customization, a JSON file named PyLNP.json is used. This file
must be stored in either the base folder, or in the LNP folder (see below).
If both exist, the one in the LNP folder will be used.

This file configures several aspects of the launcher. All parts are optional
in the sense that the launcher will work even if nothing is there.

Each key in the file is documented below.

``folders``, ``links``
----------------------
``folders`` and ``links`` are both lists containing other lists. These are
used to populate the Folders and Links menu in the program.

Each entry is a list containing 2 values: the caption for the menu item, and
the destination to be opened when the menu item is activated. To insert a
separator, use a dash as a caption (``-``).

Folder paths are relative to the base directory. Use ``<df>`` as a
placeholder for the actual Dwarf Fortress directory.

Example::

  "folders": [
    ["Savegame folder","<df>/data/save"],
    ["Utilities folder","LNP/Utilities"],
    ["Graphics folder","LNP/Graphics"],
    ["-","-"],
    ["Main folder",""],
    ["LNP folder","LNP"],
    ["Dwarf Fortress folder","<df>"],
    ["Init folder","<df>/data/init"]
  ],
  links: [
    ["DF Homepage","http://www.bay12games.com/dwarves/"],
    ["DF Wiki","http://dwarffortresswiki.org/"],
    ["DF Forums","http://www.bay12forums.com/smf/"]
  ]

``hideUtilityPath``, ``hideUtilityExt``
---------------------------------------
These options control whether to hide the path and extension of utilities in
the utility list.

Using "DwarfTool/DwarfTool.exe" as an example:

 ``hideUtilityPath`` is false, ``hideUtilityExt`` is false:
   DwarfTool/DwarfTool.exe

 ``hideUtilityPath`` is false, ``hideUtilityExt`` is true:
   DwarfTool/DwarfTool

 ``hideUtilityPath`` is true, ``hideUtilityExt`` is false:
   DwarfTool.exe

 ``hideUtilityPath`` is true, ``hideUtilityExt`` is true:
   DwarfTool

Only the *last* folder name is ever displayed: if the full path is
"Utilities/Foo/DwarfTool", only "DwarfTool" will be shown for the path name.

For further customization of displayed utility titles, see "Relabeling
utilites" below.

``updates``
-----------
This object contains up to six strings, used to check for pack updates.

If you are using http://dffd.bay12games.com/ for file hosting, ``dffdID`` must
be set, ``packVersion`` may be set, and others should not be set (ie set to
``""``) - they'll be filled automatically.
Note that any file can be downloaded from DFFD as `new_pack.zip`; the
extraction method is chosen based on file properties not extension, and if the
archive extracts to a single directory that will be used instead of the
filename.

If you are using a different site, you must not set ``dffdID``, may set
``directURL``, and must set all other fields.

``dffdID`` is the ID of your file on DFFD (if applicable)
``packVersion`` contains the current version string of your pack.
``checkURL`` must be a URL to a page containing the latest version string of your pack.
``versionRegex`` must be a regular expression that extracts the latest version
from the page contents of the aforementioned URL. If you don't understand
regular expressions, ask on the forums or use DFFD for hosting.
``downloadURL`` is the URL of the pack's download webpage; this is opened in a browser.
``directURL`` is the URL of the (future) package for direct download.

The pack is considered updated if the pack version matches the version
extracted using the regular expression.

``dfhack``
----------
This is an object containing hacks that can be toggled on or off on the
DFHack tab.

Each individual hack consists of three elements: a title, a command to be
executed by DFHack, and a tooltip. The ``dfhack`` object should contain
subobjects where the title is used as the name of the key for a subobject,
and the subobject itself contains two keys: ``command`` and ``tooltip``.

Example::

    "dfhack": {
        "Partial Mouse Control": {
            "command": "mousequery edge enable",
            "tooltip": "allows scrolling by hovering near edge of map"
        },
        "Performance Tweaks": {
            "command": "repeat -time 3 months -command cleanowned x",
            "tooltip": "regularly confiscates worn clothes and old items"
        }
    }

Directory structure
===================
PyLNP expects to see the following directory structure::

  <base folder>
    <Dwarf Fortress main folder>
    LNP
      Baselines
      Colors
      Defaults
      Embarks
      Extras
      Graphics
      Keybinds
      Mods
      Tilesets
      Utilities

PyLNP itself may be placed anywhere, so long as it is somewhere inside the
base folder. It can be placed directly in the base folder, in a subfolder, in
a subfolder of a subfolder, etc. The base folder is determined by checking
the its own directory; if it cannot find a Dwarf Fortress folder, it will try
the parent folder, and continue in this manner until it finds a suitable
folder; that folder is considered the base folder.

Additionally, it will look for a configuration file PyLNP.json (see above) in
either the base folder, or the LNP folder. If both exist, it will use the one
in the LNP folder.

All currently available DF versions are supported. If multiple valid DF
folders are present, a selection dialog will be shown at the start of the
program.

The LNP folder and all subfolders are optional, but certain features will not
work properly if they do not contain the relevant files. If missing, the LNP
folder and any missing subfolders will be created automatically, to make it
easier to create a new setup.

On case-sensitive platforms and filesystems (Linux, OS X), you must use either
this exact case, or all-lowercase names for each pre-defined folder name (e.g.
``LNP`` and ``lnp`` are both okay; ``Lnp`` is not.)

In all folders containing .txt files, any filename starting with ``README``
(arbitrary case) is ignored.

PyLNP.user
----------
This file, found in the base folder, contains user settings such as window
width and height. It should not be distributed if you make a pack.

Baselines
---------
This folder contains full unmodified raws for various versions of DF, and the
settings and images relevant to graphics packs.  These are used to rebuild
the reduced raws used by graphics packs and mods, and should not be modified
or removed - any new graphics or mod install would break.

Add versions by downloading the windows SDL edition of that version and
placing it in the folder (eg "df_40_15_win.zip"), or by attempting an action
that would require that baseline - such as installing a graphics pack - and
accepting the download.

Colors
------
This folder contains color schemes. As of DF 0.31.04, these are stored as
data/init/colors.txt in the Dwarf Fortress folder; in 0.31.03 and below, they
are contained in data/init/init.txt.

Saving the current color scheme only works with DF 0.31.04 or later.

Defaults
--------
This folder should contain two files: init.txt and d_init.txt. These files
will replace the corresponding files in data/init when the user clicks the
Defaults button.

Keep in mind that these files should be kept current with the DF installation
you are using - only use files matching your DF version.

For DF 0.31.03 and below: Only init.txt is used, since these versions do not
have d_init.txt.

Embarks
-------
This folder contains embark profiles, stored as
data/init/embark_profiles.txt. Multiple of these files can be installed at
once.

This feature is only available for DF 0.28.181.40a and later; for earlier
versions it will be hidden.

Extras
------
If this version of PyLNP has not yet been run on the selected DF
installation, any files in here will be copied to the Dwarf Fortress
directory on launch.

Graphics
--------
This folder contains graphics packs, consisting of data and raw folders.  Any
raws identical to vanilla files will be discarded; when installing a graphics
pack the remaining files will be copied over a set of vanilla raws and the
combination installed.  Through more complex merge logic, graphics can also
be used with mods and changed on most modded saves.

Tilesets
--------
This folder contains tilesets; individual image files that the user can use
for the FONT and GRAPHICS_FONT settings (and their fullscreen counterparts).
Tilesets can be installed through the graphics customisation tab, which reads
from <df>/data/art, as they are added to each graphics pack as the pack is
installed - especially useful for TwbT text tiles.

Mods
----
This folder contains mods for Dwarf Fortress, in the form of changes to the
defining raws (which define the content DF uses).  Mods use the same reduced
format for raws as graphics packs.

Keybinds
--------
This folder contains keybindings.

If you intend to use multiple versions of DF, note that legacy Windows and
Mac versions uses a different keybinding syntax, so files from newer
SDL-based versions are not compatible (and vice versa).

Utilities
=========
Each platform will auto-detect different file types in the Utilities pane.

Windows:
  ``*.exe``, ``*.jar``, ``*.bat``
Linux:
  ``*.jar``, ``*.sh``
OS X:
  ``*.app``, ``*.jar``, ``*.sh``

Correcting the auto-detection
-----------------------------
For some platforms, you may wish to include a utility not matched by the
above patterns. Also, some utilities may include subprograms that should not
appear in the list.

To correct these, you can use the files ``include.txt`` and ``exclude.txt``
in the Utilities directory. These files follow a simple format, similar to :
anything contained in square brackets is either included or excluded,
respectively, from the final list of utilities, while anything else is ignored.

Only filenames are considered in these lists; paths are ignored.

For example, to prevent the file ``libfoo.jar`` from appearing, add
``[libfoo.jar]`` to exclude.txt. To include a file ``bar.py``, add
``[bar.py]`` to include.txt.

Alternatively, you can also use the file ``utilities.txt`` to cover both
scenarios, as documented below.

Relabeling utilities
--------------------
By default, the title for a utility is derived from its filename. This can be
overriden using the file ``utilities.txt`` in the Utilites folder, and
tooltips can be added.

The basic syntax is similar to include.txt and exclude.txt detailed above:
anything in square brackets is an entry, while everything else is a comment.

Each entry consists of up to 3 fields, separated with a colon. The first
field specifies the filename to match, the second field provides an override
for the title, and the third field contains the tooltip to use for the utility.

Both title and tooltip are optional; if omitted or left blank, the default
will be used (default title and no tooltip).

To exclude a filename from the auto-detection, give it a title of
``EXCLUDE``. All other file names will be included in the detection, even if
they do not match the normal file name patterns.

Examples::

  [dwarftool.exe:DwarfTool:A utility to do stuff with your dwarves] Custom title and tooltip
  [bar.py] Not covered by auto-detection: any matches will be displayed with default title and no tooltip
  [lib_xyz.jar:EXCLUDE] Exclude lib_xyz.jar from the utility list
  [bar.exe::This is a tooltip] Default name, custom tooltip

DFHack
======
If DFHack is detected in the Dwarf Fortress folder, a DFHack tab is added to
the launcher.

This tab includes a list where preconfigured hacks can be turned on or off.
See the respective section in the description of PyLNP.json for information
on how to configure these hacks.

All active hacks are written to a file named ``PyLNP_dfhack_onload.init`` in
the Dwarf Fortress folder. This file must be loaded by your standard
``dfhack.init`` or ``onload.init`` file to take effect.

Mods
====
If mods are present in LNP/Mods/, a mods tab is added to the launcher.

Multiple mods can be merged, in the order shown in the 'installed' pane.
Those shown in green merged OK; in yellow with minor issues.  Orange
signifies an overlapping merge or other serious issue, and red could not be
merged.  Once you are happy with the combination, you can install them to the
DF folder and generate a new world to start playing.

Note that even an all-green combination might be broken in subtle (or
non-subtle) ways.

Graphics packs are generally compatible with minor mods.  When combining
mods, the current graphics pack is merged first followed by the selected mods
- so it's best to start without graphics, for maximum compatibility.

Because PyLNP logs the installed raws, it can also update the graphics on
modded savegames.  This is done by recreating the logged merge with new
graphics at the base, and replacing the savegame raws, if nothing worse than
overlapping changes was found and the previous set (including graphics) could
be rebuilt exactly.

Notes for Mod Creators
======================

Storage and distribution format
-------------------------------
The raws for mods (and ``data/speech``) are stored, and should be distributed,
in "reduced raw format".

Reduced raw format was designed to maximise ease of installation, compatibility
across DF versions and with other mods, and to minimise file size for storage
and distribution.  It is quite simply a complete ``raw`` folder, identically
structured to vanilla DF, with all unmodified files removed.  It can thus be
installed simply by overwriting a vanilla install of DF, and mods that change
little will have tiny filesizes.  The ``data/speech`` folder is installed as if
it was part of the raws, but should be included in the usual place (ie ``data``
and ``raw`` as sibling dirs) if any files there have been changed.

In all cases, file which are not present are assumed to be identical to the
vanilla file, NOT deleted.  To delete a file, only remove the file contents to
ensure that merging will overwrite with an empty string.  When the 'simplify
mod' option is used, PyLNP uses the presence of more than ten files outside the
raws or ``data/speech`` as a heuristic to indicate that this is a complete raw
folder, and will use this method to preserve deletions.

Only files ending in ``.txt``, ``.init``, ``.lua``, ``.rb`` will be copied or
merged.  This is intended to cover the raws themselves, and also DFHack files
which can be stored in the raw folder.

Merge logic limitations
-----------------------
While the merge logic strives to fit as large a subset of mods as possible,
there are some cases that are not covered.

Due to the narrow scope for filetype mentioned above, images are not handled -
so mods distributed with integrated graphics may behave oddly.  For minor mods,
PyLNP's capability to combine mods and vanilla graphics should suffice; a
solution for major mods is a priority for further development.

Mods are not handled if they require:

* Custom graphics for mod creatures
* Non-standard DFHack scripts outside the raw folder
* Custom worldgen, init, embark, or other settings
* Pre-generated worlds
* User configuration of the raws

Using other aspects of PyLNP can cover most of there limitations, but would
also impact unmodded saves.

Maximising compatibility
------------------------
This section lists tips for maximising compatibility with other mods.  They
also increase the chance that a merge warning will be raised when the
combination is problematic - instead of merging correctly into invalid raws.

* Modify vanilla files, rather than adding new files, where your changes might
  clash with another mod
* Avoid using a graphics pack as your baseline - vanilla raws are more widely
  compatible
* A mod should have a single purpose; if the user wants general tweaks as well
  as new content (or vice versa), that can be a separate mod
* Make minimal changes to achieve the purpose of your mod; decreasing the
  distance to vanilla increases mod compatibility for combinations.
