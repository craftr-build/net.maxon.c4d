This directory contains the `c4d_loves_python.h` header file that temporarily
disables the `_DEBUG` macro to include `<Python.h>`. Since Cinema 4D does
not deliver the debug binaries for the Python framework, this is necessary
to actually link with the release binaries.
