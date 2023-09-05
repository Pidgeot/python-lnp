:orphan:

.. _PyLNP.json:

PyLNP.json
##########

For basic pack customization, a JSON file named PyLNP.json is used. This file
must be stored in either the base folder (the folder containing the Dwarf
Fortress folder itself), or in `the LNP folder <LNP-directory>`. If both exist, the
one in the LNP folder will be used.

This file configures several aspects of the launcher. All parts are optional
in the sense that the launcher will work even if nothing is there.

Each key in the file is documented below.


.. contents::


``folders``, ``links``
----------------------
``folders`` and ``links`` are both lists containing other lists. These are
used to populate the Folders and Links menu in the program.

Each entry is a list containing 2 values: the caption for the menu item, and
the destination to be opened when the menu item is activated. To insert a
separator, use a dash as a caption (``-``).

Folder paths are relative to the base directory, meaning the directory
containing the Dwarf Fortress directory. Use ``<df>`` as a placeholder for the
actual Dwarf Fortress directory.

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
    ["DF Homepage","https://www.bay12games.com/dwarves/"],
    ["DF Wiki","https://dwarffortresswiki.org/"],
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

For customization of displayed utility titles, see `relabeling-utilities`.

``updates``
-----------
This object contains information used to check for pack updates.

The most important field in this object is ``updateMethod``, which controls how
PyLNP checks for updates.

There are three methods available, ``dffd``, ``regex`` and ``json``, each of
which require additional fields to be specified. These will be described below.

If ``updateMethod`` is missing, a warning will be printed when checking for
updates, and the program will attempt to auto-detect the correct method. *Please
set this field correctly*, since auto-detection is a temporary measure to
handle backwards compatibility.

When checking for updates, the version retrieved online will be compared with
the ``packVersion`` field. If they are different, PyLNP will show a notice that
updates are available. *All update methods require this field to be specified.*

If you do not want update checking, remove the ``updates`` object, or set
``updateMethod`` to a blank string.

By default, the user must explicitly enable automatic checking for updates.
However, pack authors may add an additional field to the ``updates`` object,
``defaultInterval`` which specifies the suggested number of days between each
check. If this field is present in PyLNP.json, and the user has not previously
chosen an update frequency, the user will be prompted to enable updates when
they first launch the program, using the specified frequency as the default.

It is strongly recommended that you use one of the options already visible in
the program (0, 1, 3, 7, 14, 30).

Note that the time for the next update check is determined when the option is
set, i.e. when the user makes a choice. If you default to 0 days (every
launch), the first check will happen immediately after the user has been
prompted.

``dffd``
~~~~~~~~
For files hosted on https://dffd.bay12games.com/, simply add a field ``dffdID``
which contains the ID of your hosted file. No other configuration is necessary.
Example::

  "updates": {
    "updateMethod": "dffd",
    "packVersion": "x.yy.zz r2",
    "dffdID": "1234"
  }


``regex``
~~~~~~~~~
This method extracts version information using a regular expression. All regular
expressions must capture a single group containing the appropriate value.

This method uses five extra values:

* ``checkURL``: A URL to a page containing the latest version string of
  your pack.
* ``versionRegex``: A regular expression that extracts the latest version
  from the page contents of the aforementioned URL. If you do not understand
  regular expressions, ask on the forums or use DFFD for hosting.
* ``downloadURL``: the URL of the pack's download webpage, to be opened in a
  browser **or**
* ``downloadURLRegex``: A regular expression that extracts the pack's download
  webpage from the same URL that contained the version string.
* ``directURL`` is the URL of the (future) package for direct download **or**
* ``directURLRegex``: A regular expression that extracts the pack's direct
  download webpage from the same URL that contained the version string.
* ``directFilename``: Filename to use when downloading directly (optional)
  **or**
* ``directFilenameRegex``: A regular expression that extracts the file name to
  use when downloading directly.

``downloadURL`` and ``directURL`` are both optional, but at least one should be
provided (or their regular expression counterparts).

When doing direct downloads, the URL's file name will be used as the target file
name (e.g. ``https://example.com/downloads/my_pack.zip`` gets downloaded as
``my_pack.zip``) if neither ``directFilename`` or ``directFilenameRegex`` is
set.

Example::

  "updates": {
    "updateMethod": "regex",
    "packVersion": "x.yy.zz r2",
    "checkURL": "https://example.com/my_df_pack.html",
    "downloadURL": "https://example.com/my_df_pack.html",
    "versionRegex": "Version: (.+)"
  }

``json``
~~~~~~~~~
This method extracts version information from a JSON document.

This method uses *JSON paths*, which are strings which provide a path into the
JSON object. The path is specified by a slash-separated string of object names.
Example::

    {
      "foo": ""       //path is "foo"
      "bar": {        //path is "bar"
        "baz": ""     //path is "bar/baz"
        "quux": {     //path is "bar/quux"
          "xyzzy": "" //path is "bar/quux/xyzzy"
        }
      }
    }

This method requires four extra values:

* ``checkURL``: A URL to a JSON document containing the necessary information.
* ``versionJsonPath``: A JSON path that points to the latest version of your
  pack.
* ``downloadURL``: the URL of the pack's download webpage, to be opened in a
  browser **or**
* ``downloadURLJsonPath``: A JSON path that points to the pack's download
  webpage.
* ``directURL`` is the URL of the (future) package for direct download **or**
* ``directURLJsonPath``: A JSON path that points to the pack's direct download
  webpage from the same URL that contained the version string.
* ``directFilename``: Filename to use when downloading directly (optional)
  **or**
* ``directFilenameJsonPath``: A JSON path that points to the file name to use
  when downloading directly

``downloadURL`` and ``directURL`` are both optional, but at least one should be
provided (or their JSON path counterparts).

When doing direct downloads, the URL's file name will be used as the target file
name (e.g. ``https://example.com/downloads/my_pack.zip`` gets downloaded as
``my_pack.zip``) if neither ``directFilename`` or ``directFilenameJsonPath`` is
set.

Example::

  "updates": {
    "updateMethod": "json",
    "packVersion": "x.yy.zz r2",
    "checkURL": "https://example.com/my_df_pack_version.json",
    "downloadURL": "https://example.com/my_df_pack.html",
    "versionJsonPath": "version"
  }


.. _pylnp-json-dfhack:

``dfhack``
----------
This is an object containing hacks that can be toggled on or off on the
DFHack tab.

Each individual hack consists of three elements: a title, a command to be
executed by DFHack, and a tooltip. The ``dfhack`` object should contain
subobjects where the title is used as the name of the key for a subobject,
and the subobject itself contains two keys: ``command`` and ``tooltip``.

The ``enabled`` and ``file`` keys are optional; ``file`` may be any of
"dfhack" (default), "onLoad", or "onMapLoad" and if "enabled" is ``true``
the command will be saved to ``<file>_PyLNP.init`` and executed by DFHack
at the appropriate time.  See the `DFHack docs on init files`__.

.. __: https://dfhack.readthedocs.org/en/stable/docs/Core.html#init-files

Example::

    "dfhack": {
        "Partial Mouse Control": {
            "command": "mousequery edge enable",
            "tooltip": "allows scrolling by hovering near edge of map"
        },
        "Performance Tweaks": {
            "command": "repeat -time 3 months -command cleanowned x",
            "tooltip": "regularly confiscates worn clothes and old items"
            "enabled": true,
            "file": "onMapLoad"
        }
    }

``to_import``
-------------
This configuration lists paths and strategies used to import user content
from an older install or package (triggered from the ``file>Import...``
menu).  Each item in the list is of the form [strategy, source, dest];
if the destination is not different to the source it may be omitted.

Available strategies are:

:copy_add:      Copies the given file or directory contents.  A source file
                which exists at the destination will be skipped.
                A destination directory will be created if it does not exist;
                files and subdirectories are copied without overwriting.
                This is safe for e.g. save files.
:text_prepend:  Prepends the text of source to dest (for logfiles).

Example::

    "to_import": [
        ["text_prepend", "<df>/gamelog.txt"],
        ["copy_add", "<df>/data/save"],
        ["copy_add", "<df>/soundsense", "LNP/Utilities/Soundsense/packs"]
    ]
