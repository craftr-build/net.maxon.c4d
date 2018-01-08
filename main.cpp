
#include <c4d.h>

Bool PluginStart() {
  MessageDialog("Hello m8!");
  return true;
}

void PluginEnd() {}

Bool PluginMessage(Int32 x, void* d) { return true; }
