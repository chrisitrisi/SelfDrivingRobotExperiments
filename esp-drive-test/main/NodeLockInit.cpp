
// Einmal-Programm: schreibt den Node-Lock-Schluessel (MAC + Features) ins NVS.
// Danach wieder die eigentliche App bauen und flashen.

#include "RTEnvHL.h"
#include "NodeLock.h"
#include "Features.h"

extern "C" void app_main(void)
{
  printf("NodeLockInit\n");
  InitNVS();
  openRtEnvStore();
  Mac2NVS(FEAT_SEM | SVVIS_BAS | SVVIS_ADV1 | SVVIS_ADV2 | SVVIS_ADV3
          | LIB_BAS | FILT_1 | FILT_2);
  ShowMacAll();
  CheckNodeLock();
  closeRtEnvStore();
  printf("NodeLock OK\n");
  while (1)
    vTaskDelay(100);
}
