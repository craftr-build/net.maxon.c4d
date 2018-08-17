## Module `net.maxon.c4d`

[![Build Status](https://travis-ci.org/craftr-build/craftr-maxon.c4d.svg?branch=master)](https://travis-ci.org/craftr-build/craftr-maxon.c4d)
[![Build status](https://ci.appveyor.com/api/projects/status/nqvbfo3u7qpw6mkk?svg=true)](https://ci.appveyor.com/project/NiklasRosenstein/craftr-maxon-c4d)

  [Craftr]: https://craftr.net

&ndash; Build the Cinema 4D plugin with [Craftr 4][Craftr].

__Contents__

* [Features](#features)
* [Todolist](#todolist)
* [Configuration](#configuration)
* [Version Matrix](#version-matrix)
* [Example build script](#example-build-script)
* [A note about R20](#a-note-about-r20)
* [FAQ](#faq)
* [Known Issues](#known-issues)

### Features

- Supports Cinema 4D R12 &ndash; R20
- Provides `__LEGACY_API` functionality for R17+
- Compiles plugins on Windows (MSVC), macOS (Clang) and Linux (GCC)
- Can automatically detect your Cinema 4D release and compiler version to
  adjust command-line flags accordingly (given that you installed Cinema 4D
  to a directory that is called `Cinema 4D RX.YYY`)

### Todolist

- R20 Source processor: Proper dependencies must be determined (eg. by
  wrapping the command and writing the list of parsed files to a dependency
  file) or it must be executed everytime
- R20 projectdefinition: Handle more of the `projectdefinition.txt` properties
- R20 Legacy: Provide a legacy API support header (for R19 and older plugin code)
- R20 Linux: Plugin suffix? Compile flags/defines?
- pre R20 Linux/Python: Check how we should link with Python (see `python` target)
- pre R20 Linux: Plugin suffix is .so?
- pre R20: ClangCL flags

### Configuration

| Option       | Description  |
| ------------ | ------------ |
| `:directory` | The directory of the Cinema 4D installation. If this option is *not set*, it will be automatically determined from the install location of the `@craftr/maxon.c4d` package. |
| `:release`   | Specify the Cinema 4D release number if it can not be determined automatically from the `directory` option. In case no Cinema 4D Application directory was specified and none was automatically determined, the Cinema 4D SDK matching this release will be downloaded (if available). |
| `:rtti`      | Usually the Cinema 4D SDK is compiled without RTTI, thus the default value for this option is `false`. Set it to `true` to enable RTTI. |

### Version Matrix

| Cinema 4D | Windows      | OSX               |
| ----| ------------------ | ----------------- |
| R20 | Visual Studio 2017 | Apple XCode 9 (?) |
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

### FAQ

* **Could this be used to compile plugins with MinGW?**
  Unfortunately, no. The Cinema 4D API (actually, ABI) requires the
  `/vmg /vms` options in Visual Studio which render dynamic libraries
  compiled with MinGW incompatible. More info
  [here](https://stackoverflow.com/questions/11332585/g-equivalents-for-visualc-vmg-vms).

* **Will there be support for Clang-CL?** Yes. A former version of this
  package (for a previous Craftr version) already supported Clang-CL. In
  contrast to MinGW, dynamic libraries compiled with Clang-CL can be made
  ABI compatible with Visual C.

### Known Issues

* The following Cinema 4D SDK's (and most likely all SDK's in that general
  release) can not be built with Visual Studio 2015.
    * R15.064
    * R16.021
    * R16.050
