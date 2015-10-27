// Copyright (C) <year> <name>
// All rights reserved.

#ifndef MAIN_H
#define MAIN_H

#include <c4d.h>
#include <res/c4d_symbols.h>

Bool PluginStart();
Bool PluginMessage(Int32, void*);
void PluginEnd();

#endif // MAIN_H
