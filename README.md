# lib.cxx.maxon.c4d

This Craftr package provides capabilities to compile the Cinema 4D SDK and
plugins.

```python
load_module('lang.cxx.*')
c4d = load_module('lib.cxx.maxon.c4d')

plugin = cxx_library(
  link_style = 'shared',
  inputs = cpp_compile(
    sources = glob(['src/**/*.cpp']),
    frameworks = [c4d.sdk]
  ),
  output = local('myplugin')
)
```

## Features

- Provides `__LEGACY_API` functionality for R17+ (just use `c4d.legacy_sdk`
  instead of `c4d.sdk`)
- Provides a header `c4d_Python.h` that conveniently includes `Python.h`
  which is not straight forward
- Supports compilation with MSVC, Clang-CL and Clang (Mac OS only)
