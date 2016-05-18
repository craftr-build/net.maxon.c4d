Cinema 4D Craftr Extension
~~~~~~~~~~~~~~~~~~~~~~~~~~

This repository provides a Craftr module to compile the Cinema 4D SDK and
plugins on Windows/OSX. It is tested with R13 through R17. For more
information on Craftr visit: https://github.com/craftr-build/craftr

Getting Started
===============

Grab the whole `templates/` folder from the repository and use it to
kick off your Cinema 4D plugin.

::

    build/                 (build products)
    plugin/
      res/
      plugin-binary.dylib  (OSX plugin binary)
      plugin-binary.cdl64  (Windows plugin binary)
    source/
      main.cpp
    vendor/                (for Craftr submodules)
    Craftfile              (build definitions)

To build the project, run the following command:

::

    craftr -eb

To enable a debug build:

::

    craftr -ebDdebug

To use the Cinema 4D SDK from another version:

::

    craftr -ebDmaxon.c4d.path="C:\maxon\Cinema 4D R17 Dev"

``craftr.ext.maxon.c4d.python``
===============================

This Craftr modules contains useful functions to help developing
Cinema 4D Python plugins. It allows you to easily create Python eggs
of external modules that you are using in a Plugin, extract Cinema 4D
dialog and description resource symbols and automatically protect
your Python plugin files (requires the [apex][] plugin to be installed).

  **Note**: This file is a Craftr module but must be compatible with most
  Python versions as some of its functions run this file as a script
  in a sub-process.

Resource symbols
----------------

The Python API does not come with a built-in functionality to access
the dialog and description resource symbols of a Cinema 4D plugin. Manually
hardcoding the symbols into a Python plugin's source is not an option for
larger plugins. This module allows you to extract the resource symbols and
format them as a Python file, a class or in JSON format.

.. code-block:: python

  # craftr_module(my_plugin)
  from craftr import *
  from craftr.ext.maxon.c4d.python import export_res_symbols

  @task
  def symbols():
    export_res_symbols(project_dir, None, format='class')
    # or
    export_res_symbols(project_dir, path.local('devel/res.py'), fmt='file')

This will format the symbols as a Python class and output it to stdout
or write the symbols formatted as a Python file to the `devel/res.py`
file.

External modules
----------------

First, you *must* use `_localimport`_ to import libraries that are
distributed with your plugin. If you want to use, and therefore also
distribute, external Python modules with your plugin that you don't want
to distribute in source (make sure that is allowed by the modules license),
you can generate binary Python eggs using the functionality in this module.

The following examples assume that you have external Python modules
in a `devel` directory. For distribution, they shall be compiled and
archived to the `res/modules2.6` and `res/modules2.7` directories.

::

    my_plugin\
      devel\
        res.py
        my_plugin_tools\
          __init__.py
          some_tools.py
        some_package\
          setup.py
          src\
            some_package\
              __init__.py
          etc...

This script does exactly that.

.. code-block:: python

  # craftr_module(my_plugin)
  from craftr import *
  from craftr.ext.maxon.c4d.python import create_distro_task, Egg

  bdist = create_distro_task(
    source_dir = path.local('devel'),
    res_dir = path.local('res'),
    eggs = [Egg(
      name = 'storage-libs-{py}.egg',
      zipped = False,
      files = [
        'res.py',
        'nr.concurrency/nr',
        'nr.c4d/nr',
        'requests/requests',
        'requests-toolbelt/requests_toolbelt'
      ])
    ],
  )

Now run this in the console to execute the task:

::

  craftr -b .bdist

It requires an executable ``python2.6`` and ``python2.7`` in your ``PATH``.

Protecting your Python plugin from the command-line
---------------------------------------------------

**Important**: This requires the `apex`_ plugin to be installed to the
Cinema 4D version you are developing the plugin in.

.. code-block:: python

  def protect():
    pyp_file = join(project_dir, 'my_plugin.pyp')
    maxon.c4d.python.protect_pyp(pyp_file)

.. _apex: https://github.com/nr-plugins/apex
.. __localimport: https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556
