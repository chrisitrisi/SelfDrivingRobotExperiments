// GyroTest: Winkel anzeigen, Motoren aus, Button = 0

#include "RTEnvHL.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TmbMenues.h"
#include "MPU_Esp.h"

const float GYRO_LSB = 16.4; // +-2000 Grad/s

extern "C" void app_main(void)
{
  printf("GyroTest\n");
  InitRtEnvHL();
  InitMotors();
  motL.setPow2(0); motR.setPow2(0);
  InitTmbMenue();
  I2cInit();
  mpu.Init();

  long sum = 0;
  for (int i = 0; i < 100; i++) {
    sum += mpu.getGyroZ();
    MyDelay(10);
  }
  float offset = sum / 100.0f;
  printf("Offset Z = %.1f\n", offset);

  float angle = 0;
  int64_t last = esp_timer_get_time();
  int n = 0;
  while (1) {
    MyDelay(10);
    int64_t now = esp_timer_get_time();
    angle += (mpu.getGyroZ() - offset) / GYRO_LSB * (now - last) / 1e6f;
    last = now;
    if (hbtn.wasClicked()) {
      hbtn.listen();
      angle = 0;
      printf("--- Winkel auf 0 ---\n");
    }
    if (++n >= 20) {
      n = 0;
      printf("Winkel: %7.1f Grad\n", angle);
    }
  }
}
