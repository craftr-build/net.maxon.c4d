# Cinema 4D SDK Compilation & Plugin Tools

This repository contains [Craftr][] python modules that implement
compiling the Cinema 4D SDK and Cinema 4D plugins as well as utilities
to aid developing Cinema 4D Python plugins.

__Supported Releases__: Cinema 4D R13 - R17

__Compiling a Plugin__:

1. Copy the `template/Craftr` script into your plugin directory or
use the complete `template` directory as a base to kick off a plugin.

2. Run `craftr` from the plugins directory or `craftr -D:debug` to
produce a debug build.

3. Run `ninja` to build the plugin.

[Craftr]: https://github.com/creator-build/craftr
