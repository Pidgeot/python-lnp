PyLNP:  A launcher for Dwarf Fortress
#####################################

PyLNP has a variety of useful features to manage settings and configure the base
game.  It can also manage, configure, install, and run a wide variety of
related content - from graphics to color schemes, and utility programs to
content-replacing mods.

It forms the core of various bundles for new, lazy, or impatient players -
such as the old "Lazy Newb Pack".  While this project is just the launcher,
you can download a complete bundle for Windows, OSX, or Linux put together by members of
the community. See http://dwarffortresswiki.org/Lazy_Newb_Pack for current links to these.

If you have a question that is not answered here, go ahead and ask it in the
`Bay12 forum thread for PyLNP <http://www.bay12forums.com/smf/index.php?topic=140808>`_.


.. contents::


Documentation
=============
.. toctree::
   :maxdepth: 1

   content
   developer
   building

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


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
