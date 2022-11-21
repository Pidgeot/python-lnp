PyLNP Content Formats
#####################

This document will introduce PyLNP content formats and conventions;
especially for graphics packs, mods, and utilities.


.. contents::


PyLNP.json
==========
For basic pack customization, a JSON file named `PyLNP.json` is used. This file
must be stored in either the base folder (the folder containing the Dwarf
Fortress folder itself), or in `the LNP folder <LNP-directory>`. If both exist, the
one in the LNP folder will be used.


DFHack
======
If DFHack is detected in the Dwarf Fortress folder, a DFHack tab is added to the launcher.
This tab includes a list where preconfigured hacks can be turned on or off.
See `this documentation <pylnp-json-dfhack>` for configuration instructions.


.. _content-manifest:

Content Manifests
=================
Raw-based content - ie graphics packs or mods - may be
distributed with a file titled ``manifest.json`` in their root directory.
This can be used to declare the name, version, and author of the content,
versions of DF known to be incompatible, an explanatory tooltip, and more.

If the manifest does not exist, or a field is missing, PyLNP will use sensible
default values - letting the user make the decision based on autodetection.

For example, in ``LNP/Mods/foo_mod/manifest.json``::

    {
        "author": "Urist McFoo_Modder and friends",
        "content_version": "1.2a",
        "df_min_version": "0.40.03",
        "df_max_version": "",
        "title": "Foo Mod!",
        "tooltip": "The mod all about foo-ing.\nA second line."
    }

"title" and "tooltip" control presentation in the list for that kind of
content.  Both should be strings.  Title is the name in the list; tooltip
is the hovertext - linebreaks are inserted with "\n", since it must be one
line in the manifest file.

"folder_prefix" For graphics, the folder_prefix is the identifier of record (to allow noting resolution
or authorship in the title).

"author" and "content_version" are strings for the author and version of the
content.  Both are for information only at this stage.

"df_min_version" and "df_max_version" allow you to specify versions of DF
with which the content is incompatible.  When playing a version outside the
range, which is open ended if not specified, the content is hidden.  In the
example, the mod will be visible for DF 40.03 and all later versions.

Finally, "df_incompatible_versions" is a list of incompatible DF versions,
and "needs_dfhack" will hide the content if DFHack is not activated -
so use it only when the content is *totally* useless without DFHack.

Utility manifests
-----------------
Utilities may also have manifests, which may be placed in any directory
and disable the global utilities configuration for anything in that or a
lower directory.  They thus offer utility authors control over the presentation
of their work.

Utility manifests include the same keys as content manifests, as well as
the following utility-specific options::

    {
        "win_exe": "My Util.exe",
        "osx_exe": "path/to/My Util.app",
        "linux_exe": "another/path/launcher.sh",
        "launch_with_terminal": false,
        "readme": "My_Readme.txt"
    }

The utility for each OS is configured as the relative path from the manifest
directory to the file, including intermediate directory names and the filename.
**This must be an exact match**, or the utility will not be found by PyLNP!

For Linux and OSX, the "launch_with_terminal" option denotes that the utility
requires launching from a terminal.  This option does nothing on Windows.

The readme entry points to a readme file for your utility. It may point to any
file type; the operating system will try to open it using the default viewer for
that file type, so common types like TXT and PDF are more likely to work. If
absent, PyLNP will try to open the first file it encounters which starts with
either "README", "READ ME", or "READ_ME", using case-insensitive matching (so
"readme.txt" will still be found).


.. _LNP-directory:

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

Additionally, it will look for a configuration file `PyLNP.json` in
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

Add versions by downloading any edition of that version and placing it
in the baselines folder (eg "df_40_15_win.zip"), or by attempting an action
that would require that baseline - such as installing a graphics pack - and
accepting the download.

Colors
------
This folder contains color schemes. As of DF 0.31.04, these are stored as
data/init/colors.txt in the Dwarf Fortress folder; in 0.31.03 and below, they
are contained in data/init/init.txt.

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
be used with mods and changed on most modded saves.  Graphics can be configured
with a content manifest.

Keybinds
--------
This folder contains keybindings.

If you intend to use multiple versions of DF, note that legacy Windows and
Mac versions uses a different keybinding syntax, so files from newer
SDL-based versions are not compatible (and vice versa).

Mods
----
This folder contains mods for Dwarf Fortress, in the form of changes to the
defining raws (which define the content DF uses).  Mods use the same reduced
format for raws as graphics packs.  Mods can be configured with a content
manifest.

If mods are present in LNP/Mods/, a mods tab is added to the launcher.

Multiple mods can be merged, in the order shown in the 'installed' pane.
Those shown in green merged OK; in yellow with minor issues.  Orange
signifies an overlapping merge or other serious issue, and red could not be
merged.  Once you are happy with the combination, you can install them to the
DF folder and generate a new world to start playing.

Note that even an all-green combination might be broken in subtle
(or non-subtle) ways.

Graphics packs are generally compatible with minor mods.  When combining
mods, the current graphics pack is merged first followed by the selected mods
- so it's best to start without graphics, for maximum compatibility.

Because PyLNP logs the installed raws, it can also update the graphics on
modded savegames.  This is done by recreating the logged merge with new
graphics at the base, and replacing the savegame raws, if nothing worse than
overlapping changes was found and the previous set (including graphics) could
be rebuilt exactly.

Tilesets
--------
This folder contains tilesets; individual image files that the user can use
for the FONT and GRAPHICS_FONT settings (and their fullscreen counterparts).
Tilesets can be installed through the graphics customisation tab, which reads
from <df>/data/art, as they are added to each graphics pack as the pack is
installed - especially useful for TwbT text tiles.

Utilities
---------
Utilities may be `configured by a manifest <content-manifest>`, which will override
the global configuration described here for the directory the manifest is in,
and all subdirectories.  This also disables autodetection 'below' a manifest.

Each platform will auto-detect different file types in the Utilities pane.

:Windows:   ``*.exe``, ``*.jar``, ``*.bat``
:Linux:     ``*.jar``, ``*.sh``
:OS X:      ``*.app``, ``*.jar``, ``*.sh``

Correcting the auto-detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

.. _relabeling-utilities:

Relabeling utilities
~~~~~~~~~~~~~~~~~~~~
By default, the title for a utility is derived from its filename. This can be
overriden using the file ``utilities.txt`` in the Utilities folder, and
tooltips can be added.

The basic syntax is similar to ``include.txt`` and ``exclude.txt`` detailed above:
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
little will have tiny file sizes.  The ``data/speech`` folder is installed as if
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
