/**
 * Copyright (C) <Year> <Name>
 * All rights reserved.
 */

#include <c4d.h>
#include "c4d_symbols.h"


Bool PluginStart() {
  GePrint("Hello, World!");
  return true;
}


void PluginEnd() { }


Bool PluginMessage(Int32 msg, void* pdata) {
  switch (msg) {
    case C4DPL_INIT_SYS:
      return ::g_resource.Init();
  }
  return true;
}
