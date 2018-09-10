## Module `net.maxon.c4d`

[![Build Status](https://travis-ci.org/craftr-build/craftr-maxon.c4d.svg?branch=master)](https://travis-ci.org/craftr-build/craftr-maxon.c4d)
[![Build status](https://ci.appveyor.com/api/projects/status/nqvbfo3u7qpw6mkk?svg=true)](https://ci.appveyor.com/project/NiklasRosenstein/craftr-maxon-c4d)

  [Craftr]: https://craftr.net

&ndash; Build Cinema 4D plugins with [Craftr 4][Craftr].

__Contents__

* [Features](#features)
* [Legacy / Bridge API](#legacy--dual-api)
* [Todolist](#todolist)
* [Configuration](#configuration)
* [Version Matrix](#version-matrix)
* [Example build script](#example-build-script)
* [A note about R20](#a-note-about-r20)
* [FAQ](#faq)
* [Known Issues](#known-issues)

### Features

- Supports compiling plugins for Cinema 4D R12 &ndash; R20
- Provides legacy / dual API headers <sup>1) More info below</sup>
- Compiles plugins on Windows (MSVC), macOS (Clang) and Linux (GCC)
- Can automatically detect your Cinema 4D release and compiler version to
  adjust command-line flags accordingly (given that you installed Cinema 4D
  to a directory that is called `Cinema 4D RX.YYY`)
- Full R20 source processor support

### Legacy / Bridge API

Many symbol names in the C4D SDK changed drastically in R15. Maxon provided a
`__LEGACY_API` preprocessor switch that enabled most of the old names, however
that switch is discontinued since R17.

This Craftr module provides the old C4D legacy API header as `"c4d_legacy.h"`,
which allows you to use much of the old API even in R17 to R19. It will be
available by adding the `net.maxon.c4d:addons` target to your plugins'
dependencies.

You can also depend on the `net.maxon.c4d:legacy` target instead which will
add the `c4d_legacy.h` as a prefix header, thus you won't need to manually
add this include to all source files.

---

The R16 SDK uses `#define override` on Windows which is actually invalid
and Visual Studio 2015 (aka. 14.0) complains about this. We provide a
`<r16_compilerdetection_fix.h>` header (depend on `net.maxon.c4d:addons`)
that has this error fixed.

---

With **R20**, the Cinema 4D SDK changed drastically. Most prominent are the
changes to enumerations which all changed to `enum class` declarations.
Macros like `NewObj()`/`NewMem()` and functions like `String::GetCStringCopy()`
return a `maxon::ResultPtr<T>` instead of a raw pointer which can not be
implicitly cast to the type `T*`, rendering all existing code using these
functions invalid.

This Craftr module provides a **bridge API** &ndash; meaning that it is a new
and separate API that is compatible with the pre-R20 and R20 SDK. This API
must be explicitly included with the `"c4d_apibridge.h"` header. It provides
the pre-R20 enumerations (generated using the `scripts/r20enums.py` script)
but encrouages use of API that is more similar to R20 (eg. aims to provide R19
compatible `iferr()` and `ifnoerr()` macros).

### Todolist

- R20 projectdefinition: Handle more of the `projectdefinition.txt` properties
- R20 Linux: Plugin suffix? Compile errors with StrongCOWHandler in `cpython.h`
- R20 Python: Choose the correct link targets on Mac/Linux. On Windows, search
  for a Python 2.7 x64 installation.
- pre R20 Linux: Plugin suffix is .so?

### Configuration

| Option       | Description  |
| ------------ | ------------ |
| `:directory` | The directory of the Cinema 4D installation. If this option is *not set*, it will be automatically determined from the install location of the `@craftr/maxon.c4d` package. |
| `:release`   | Specify the Cinema 4D release number if it can not be determined automatically from the `directory` option. In case no Cinema 4D Application directory was specified and none was automatically determined, the Cinema 4D SDK matching this release will be downloaded (if available). |
| `:rtti`      | Usually the Cinema 4D SDK is compiled without RTTI, thus the default value for this option is `false`. Set it to `true` to enable RTTI. |

### Version Matrix

| Cinema 4D | Windows      | OSX               |
| ----| ------------------ | ----------------- |
| R20 | Visual Studio 2015 | Apple XCode 9 (?) |
| R19 | Visual Studio 2015 | Apple XCode 8     |
| R18 | Visual Studio 2013 | Apple XCode 7     |
| R17 | Visual Studio 2013 | Apple XCode 6     |
| R16 | Visual Studio 2012 | Apple XCode 5.0.2 |
| R15 | Visual Studio 2012 | Apple XCode 4.6.3 |
| R14 | Visual Studio 2010 | Apple XCode 4.3.2 |
| R13 | Visual Studio 2005 | Apple XCode 3.2.6 |

Source: https://developers.maxon.net/?page_id=1108

### Example build script

```python
project('myplugin', '1.0-0')

c4d = require('net.maxon.c4d')

@target(builders=[c4d.build])
def plugin():
  depends('net.maxon.c4d:sdk')
  properties({
    'cxx.srcs': glob('src/**/*.cpp'),
    'cxx.includes': ['plugin'],
    'cxx.productName': 'myplugin' + c4d.plugin_suffix,
    'cxx.productDirectory': './plugin',
    'cxx.type': 'library',
    'cxx.preferredLinkage': 'shared'
  })
```

Depend on the `net.maxon.c4d:legacy` target instead if your project uses
old API (pre-R16).

### A note about R20

With R20, Maxon introduced a tool to produce project files from a
`projectdefinitions.txt` file. Craftr supports building R20 projects
*without* the MAXON Project Tool. Depending on the `net.maxon.c4d:sdk`
target is no longer required and will do nothing (for backwards compatibility
when building for previous Cinema 4D releases).

Craftr can however take the following information from the
`projectdefinitions.txt` into account:

- `Platform` (validating if the current platform is supported)
- `ModuleId` (alternatively with the `c4d.ModuleId` target property)
- `APIS` (additively to the `c4d.APIS` target property)
- `Type` (`Lib` or `DLL`, overriding the `cxx.type` and
  `cxx.preferredLinkage` properties)
- `Exclude`, `ExcludeFromBuild`

### FAQ

* **Could this be used to compile plugins with MinGW?**
  Unfortunately, no. The Cinema 4D API (actually, ABI) requires the
  `/vmg /vms` options in Visual Studio which render dynamic libraries
  compiled with MinGW incompatible. More info
  [here](https://stackoverflow.com/questions/11332585/g-equivalents-for-visualc-vmg-vms).

* **How to get the R20 Project Tool to work on non-Ubuntu systems?**
  You may get an error like `error while loading shared library: libprocps.so.3`.
  Make sure you have a version of libprocs installed, eg `libprocps7`. Symlink
  it like so: `sudo ln -s /usr/lib64/libprocps.so.{7,3}`

### Known Issues

* The following Cinema 4D SDK's (and most likely all SDK's in that general
  release) can not be built with Visual Studio 2015.
    * R15.064
    * R16.021
    * R16.050
