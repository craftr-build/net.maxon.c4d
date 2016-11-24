# lib.cxx.maxon.c4d

This Craftr package provides capabilities to compile the Cinema 4D SDK and
plugins.

```python
load_module('lang.cxx.*')
load_module('lib.cxx.maxon.c4d.*')

plugin = cxx_library(
  inputs = cpp_compile(
    sources = glob(['src/**/*.cpp']),
    frameworks = [c4d_sdk]
  ),
  output = local('myplugin'),
  link_style = 'shared'
)
```
