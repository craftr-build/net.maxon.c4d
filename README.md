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
