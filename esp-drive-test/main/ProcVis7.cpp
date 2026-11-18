
#include "RTEnvHL.h"
#include "SvProtocol3.h"
#include "EspMotor.h"
#include "driver/gpio.h"

SvProtocol3 ua0;

void CommandLoop()
{
  // printf("CommandLoop\n");
  int cmd;
  while (1) {
    cmd = ua0.GetCommand();
    if (cmd == 2) {
      int v1 = ua0.ReadI16(); int v2 = ua0.ReadI16();
      // printf("Cmd2 %d %d\n", v1, v2);
      ua0.SvPrintf("Cmd2 %d %d", v1, v2);
    }
    if (cmd == 3) {
      float v3 = ua0.ReadF();
      ua0.SvPrintf("Cmd3 %1.1f", v3);
    }
    else if (cmd == 52) {
      wifi_disconnect();
      MyError("wifi discon");
    }
  }
}

extern "C" void Monitor(void* arg)
{
  int v1 = 0, v2 = 10; float v3 = 20;
  while(1) {
    vTaskDelay(1); // sleep 10ms == 100Hz
    if (ua0.acqON) {
      ua0.WriteSvI16(1, v1++);
      ua0.WriteSvI16(2, v2++);
      ua0.WriteSvF(3, v3 += 0.3);
      ua0.Flush();
    }
  }
}

extern "C" void app_main(void)
{
  printf("ProcVis7\n");
  InitRtEnvHL();
  InitUart(UART_NUM_0, 500000);
  // InitSoftAp("sepp", 4);
  xTaskCreate(Monitor, "Monitor", 2048, NULL, 10, NULL); // 10=Prio
  CommandLoop();
}


