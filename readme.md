# Craftr: `maxon.c4d`

A [Craftr][] module to compile Cinema 4D plugins on Windows and OSX
from Cinema R13 to R17!

## Plugin Structure

    build/                 (build products)
    plugin/
      res/
      plugin-binary.dylib  (OSX plugin binary)
      plugin-binary.cdl64  (Windows plugin binary)
    source/
      main.cpp
    Craftfile              (build definitions)

## Getting Started

First, you have to copy this repository into your Cinema 4D plugins
directory. Next, you can kick off by making a copy of the `template`
folder and put it into your Cinema 4D plugins folder, too! You should
rename the folder and change the first line in `Craftfile` to update
the project name.

To build, you simply run `craftr -eb`. You can also add the `-Ddebug -d build_dbg`
option to produce a debug build (for which the build products will be put
into the `build_dbg/` folder instead).

## Python Tools

This Craftr extension also comes with the `maxon.c4d.python` module that
can be used to prepare Python plugins for distribution.

__Resource Symbols__

You can exract the resource symbols of your plugin and put them into a
format that can be used in Python. This takes off a lot of work, as you
previously had to copy them to your Python source code by hand.

Simply create a Craftfile and put the following in it:

```python
# craftr_module(my_name.my_plugin)
from craftr import path
from craftr.ext.maxon.c4d.python import symbols_format

def symbols():
  symbols_format(project_dir, path.local('devel/res.py'), format='file')
```

If you now run `craftr -F symbols`, the function will be executed and
create a `devel/res.py` that can be imported from Python.

> __Important Note__: Make sure to use [localimpor][] when you import
> Python modules from your plugin distribution!!

__External Modules__

Craftr can create Python eggs from third party modules you use in your
plugin which you can then distribute instead of the original source code.
You can use the `C4DDistro` class to specify the modules that should be
packed into a Python egg.

```python
# craftr_module(my_name.my_plugin)
from craftr import path
from craftr.ext.maxon.c4d.python import C4DDistro

class bdist(C4DDistro):
  # The base directory where all your third party code is.
  source_dir = path.local('devel')

  # The directory that the compiled modules will be put into. A
  # subdirectory for Python 2.6 and Python 2.7 will be created.
  res_dir = path.local('res')

  # The Python versions to build for. You will need python2.6 and
  # python2.7 in your PATH.
  versions = ['2.6', '2.7']

  # A list of the modules that you want to zip and the respective
  # output filename.
  manual_packages = [
    ('my-third-party-libs-{py}.egg', [
      'res.py',
      'requests/requests',
      # etc...
      ])
  ]
```

Run `craftr -F bdist` and you'll get `res/modules2.6` and `res/modules2.7`
directories with a `my-third-party-libs-2.6.egg` and `my-third-party-libs-2.7.egg`
file in each respectively. Use [localimport][] to import the modules in your
plugin!

```python
lib_dir = os.path.join(os.path.dirname(__file__), 'res', 'modules' + sys.version[:3])
with _localimport(lib_dir):
  import res
  import requests
```

  [Craftr]: https://github.com/craftr-build/craftr
  [localimport]: https://github.com/NiklasRosenstein/localimport
