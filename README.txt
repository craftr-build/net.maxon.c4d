This repository provides a Craftr module to compile the Cinema 4D SDK and
plugins on Windows/OSX. It is tested with R13 through R17. For more
information on Craftr visit:

  https://github.com/craftr-build/craftr


Getting Started
===============

Grab the whole `templates/` folder from the repository and use it to
kick off your Cinema 4D plugin.

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

    craftr -eb

To enable a debug build:

    craftr -ebDdebug

To use the Cinema 4D SDK from another version:

    craftr -ebDmaxon.c4d.path="C:\maxon\Cinema 4D R17 Dev"


Python Plugin Development Tools
===============================

This Craftr extension also comes with the `maxon.c4d.python` module that
can be used to prepare Python plugins for distribution.

Resource Symbols
----------------

You can exract the resource symbols of your plugin and put them into a
format that can be used in Python. This takes off a lot of work, as you
previously had to copy them to your Python source code by hand.

Simply create a Craftfile and put the following in it:

  # craftr_module(my_name.my_plugin)
  from craftr import path
  from craftr.ext.maxon.c4d.python import symbols_format

  def symbols():
    symbols_format(project_dir, path.local('devel/res.py'), format='file')

If you now run `craftr -F symbols`, the function will be executed and
create a `devel/res.py` that can be imported from Python.

> __Important Note__: Make sure to use [localimpor][] when you import
> Python modules from your plugin distribution!!

External Modules
~~~~~~~~~~~~~~~~

Craftr can create Python eggs from third party modules you use in your
plugin which you can then distribute instead of the original source code.
You can use the `C4DDistro` class to specify the modules that should be
packed into a Python egg.

  # craftr_module(my_name.my_plugin)
  from craftr import path
  from craftr.ext.maxon.c4d.python import C4DDistro, Egg

  class bdist(C4DDistro):
    # The base directory where all your third party code is.
    source_dir = path.local('devel')

    # The directory that the compiled modules will be put into. A
    # subdirectory for Python 2.6 and Python 2.7 will be created.
    res_dir = path.local('res')

    # A list of the modules that you want to zip and the respective
    # output filename.
    eggs = [
      Egg('my-third-party-libs-{py}.egg', files=[
        'res.py',
        'requests/requests',
        # etc...
        ])
    ]

Run

    craftr -F bdist

to compile the Python libraries into a Python Egg in your plugins resource
directory.

    res/
      modules2.6/
        my-third-party-libs-2.6.egg
      modules2.7/
        my-third-party-libs-2.7.egg

You should only load third party libraries using _localimport.

  lib_dir = os.path.join(os.path.dirname(__file__), 'res', 'modules' + sys.version[:3])
  with _localimport(lib_dir):
    import res
    import requests

You can find the _localimport class here: https://github.com/NiklasRosenstein/localimport
