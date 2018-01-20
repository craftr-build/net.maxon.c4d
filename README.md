## @craftr/maxon-c4d

[![Build Status](https://travis-ci.org/craftr-build/craftr-maxon-c4d.svg?branch=master)](https://travis-ci.org/craftr-build/craftr-maxon-c4d)
[![Build status](https://ci.appveyor.com/api/projects/status/5drmctmptqgdq6cs?svg=true)](https://ci.appveyor.com/project/NiklasRosenstein/craftr-maxon-c4d)

  [Craftr]: https://craftr.net

&ndash; Build the Cinema 4D SDK and plugins with [Craftr].


__Features__:

- Provides `__LEGACY_API` functionality for R17+ (just use `c4d.legacy_sdk`
  instead of `c4d.sdk`).
- Provides a header `craftr/c4d_python.h` that conveniently includes `Python.h`
  which is not straight forward.
- Supports compilation with MSVC and Clang (Mac OS only).
- Automatically download the Cinema 4D SDK source when compiling outside
  of a Cinema 4D application environment.
- Support for compilation on Linux with GCC (experimental)

__Configuration__:

- `maxon-c4d.debug` &ndash; Inheritable option. Specifies whether the Cinema 4D SDK
  is built in debug mode and with debug symbols. Note that this enables some
  C4D SDK specific debug features, but the C++ toolkit's the `debug` option
  should be enabled as well. Thus, it is always a good idea to set the `debug`
  option globally.
- `maxon-c4d.rtti` &ndash; By default the Cinema 4D SDK compiles with RTTI, thus the
  default value for this option is `false`. Note that this option will be
  set globally if no explicit global value is present in the Craftrfile.
- `maxon-c4d.directory` &ndash; The directory of the Cinema 4D installation. If this
  option is not set, it will be automatically determined from the path of this
  Craftr package (TODO: Use the path of the MAIN Craftr package instead).
- `maxon-c4d.release` &ndash; The Cinema 4D release to compile for. If not specified,
  the script will attempt to automatically determine the number of the
  `maxon-c4d.directory` or `maxon-c4d.version` options.
- `maxon-c4d.version` &ndash; If specified, instead of using the `maxon-c4d.directory` option,
  the Cinema 4D SDK will be downloaded from the URL specified with the `.url`
  option. Check https://public.niklasrosenstein.com/cinema4dsdk/ for available
  versions if you keep the `.url` default value.
- `maxon-c4d.url` &ndash; The URL to download the Cinema 4D SDK source from. The default
  value for this option is `https://public.niklasrosenstein.com/cinema4dsdk/c4dsdk-${VERSION}.tar.gz`.

__Version Matrix__:

| Version       | Windows            | OSX               |
| ------------- | ------------------ | ----------------- |
| Cinema 4D R19 | Visual Studio 2015 | Apple XCode 8     |
| Cinema 4D R18 | Visual Studio 2013 | Apple XCode 7     |
| Cinema 4D R17 | Visual Studio 2013 | Apple XCode 6     |
| Cinema 4D R16 | Visual Studio 2012 | Apple XCode 5.0.2 |
| Cinema 4D R15 | Visual Studio 2012 | Apple XCode 4.6.3 |
| Cinema 4D R14 | Visual Studio 2010 | Apple XCode 4.3.2 |
| Cinema 4D R13 | Visual Studio 2005 | Apple XCode 3.2.6 |

> <sub>source: https://developers.maxon.net/?page_id=1108</sub>

__Example__:

```python
import craftr from 'craftr'
import cxx from 'craftr/lang/cxx'
import c4d from 'craftr-maxon-c4d'

cxx.library(
  name = 'plugin',
  deps = ['//@craftr/maxon-c4d:c4d'],
  outname = 'myplugin' + c4d.plugin_ext,
  srcs = craftr.glob('src/**/*.cpp')
)
```

To use the legacy API, use the `//@craftr/maxon-c4d:c4d_legacy` target instead.

__Known Issues__:

- Building R15.064, R16.021, R16.050 with **Visual Studio 2015** <sub>v140</sub> fails

__To do__:

- Support for MinGW
