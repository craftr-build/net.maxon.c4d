# Craftr: `maxon.c4d`

A Craftr module to compile Cinema 4D plugins on Windows and OSX.

| Supported Platforms | Releases |
| --- | --- |
| Windows, OSX | Cinema 4D R13 - R17 |

### How to compile a Plugin

1. Copy the `template/Craftfile` script into your plugin directory or
   use the complete `template` directory as a base to kick off a plugin. Make
   sure to rename the `# craftr_module(plugin)` declaration to something
   useful.

2. Run `craftr -eb` to build the plugin. Use `-Ddebug` to produce a 
   debug build instead. You should use a different build directory for
   a debug build, eg. `-d build_dbg`.

  [Craftr]: https://github.com/craftr-build/craftr
