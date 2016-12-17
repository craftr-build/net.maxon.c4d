# Maxon Cinema 4D SDK (`NiklasRosenstein.maxon.c4d`)

[![Build status](https://ci.appveyor.com/api/projects/status/sls9x3ic6nc1gosw/branch/master?svg=true)](https://ci.appveyor.com/project/NiklasRosenstein/niklasrosenstein-maxon-c4d/branch/master)

-- Compile the Cinema 4D SDK and plugins with [Craftr].

[Craftr]: https://github.com/craftr-build/craftr

__Features__:

- Provides `__LEGACY_API` functionality for R17+ (just use `c4d.legacy_sdk`
  instead of `c4d.sdk`)
- Provides a header `c4d_Python.h` that conveniently includes `Python.h`
  which is not straight forward
- Supports compilation with MSVC, Clang-CL and Clang (Mac OS only)
- Automatically download the Cinema 4D SDK source when compiling outside
  of a Cinema 4D installation environment

__Example__:

```python
cxx = load('craftr.lang.cxx')
c4d = load('NiklasRosenstein.maxon.c4d')

plugin = cxx.library(
  link_style = 'shared',
  inputs = cxx.cpp_compile(
    sources = glob(['src/**/*.cpp']),
    frameworks = [c4d.sdk]
  ),
  output = local('myplugin')
)
```

## FAW

__Why `NiklasRosenstein.maxon.c4d`?__

Craftr requires packages to be namespaced.

__Will MinGW be supported anytime soon?__

It is planned for the future.

__How do I compile outside of a Cinema 4D installation environment?__

By specifying either or both of the `.version` and `.url` options, the C4D
SDK source code will be downloaded form the URL. The default URL is
`https://public.niklasrosenstein.com/cinema4dsdk/c4dsdk-${VERSION}.tar.gz`.
Available version numbers are for example `12.032`, `15.064` or `17.048`.
Check out the [repository] for a list of all available versions.

[repository]: https://public.niklasrosenstein.com/cinema4dsdk/
