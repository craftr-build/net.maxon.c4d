/// Copyright (C) <Year> <Name>
/// All rights reserved.

#include <c4d.h>
#include <res/c4d_symbols.h>



Bool PluginStart()
{
  GePrint("Hello, World! from the Craftr maxon.c4d Template Project!");
  return true;
}


void PluginEnd()
{
}


Bool PluginMessage(Int32 msg, void* pdata)
{
  switch (msg) {
    case C4DPL_INIT_SYS:
      return ::resource.Init();
  }
  return true;
}
