// WallTest: zur Wand, umdrehen, weiter. Button = Start/Stopp

#include "RTEnvHL.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TmbMenues.h"
#include "MPU_Esp.h"
#include <math.h>

UsDist us(5, 12); // Trig 5, Echo 12

const float POW = 0.3;
const float WALL_CM = 20;
const float TURN_DEG = 170; // < 180 wegen Nachrollen
const float K_SYNC = 0.01;

// MPU +-2000 Grad/s -> 16.4 pro Grad/s
const float GYRO_LSB = 16.4;
// gemessen: 170 Grad gemeldet = ca. 120 echt
const float GYRO_KORR = 0.7;
float gyroOffset = 0;

void CalibrateGyro()
{
  long sum = 0;
  for (int i = 0; i < 100; i++) {
    sum += mpu.getGyroZ();
    MyDelay(10);
  }
  gyroOffset = sum / 100.0f;
  printf("Gyro-Offset Z = %.1f\n", gyroOffset);
}

void Stop()
{
  motL.setPow2(0); motR.setPow2(0);
}

// 999 = kein Echo
float MeasureCm()
{
  us.dist = 0;
  us.startMeas();
  MyDelay(50);
  if (us.dist == 0) return 999;
  return us.dist / 58.0f; // Mikrosekunden -> cm
}

void TurnAround()
{
  Stop();
  MyDelay(300);
  motL.setPow2(-POW); motR.setPow2(POW);
  // Winkel = Drehrate * Zeit
  float angle = 0;
  int64_t last = esp_timer_get_time(), start = last;
  while (fabsf(angle) < TURN_DEG && last - start < 5000000) {
    MyDelay(10);
    int64_t now = esp_timer_get_time();
    float dt = (now - last) / 1e6f;
    last = now;
    angle += (mpu.getGyroZ() - gyroOffset) / GYRO_LSB * GYRO_KORR * dt;
  }
  Stop();
  printf("gedreht: %.0f Grad\n", fabsf(angle));
  MyDelay(300);
}

extern "C" void app_main(void)
{
  printf("WallTest\n");
  InitRtEnvHL();
  InitMotors();
  Stop();
  InitTmbMenue();
  us.Init();
  I2cInit();
  mpu.Init();
  CalibrateGyro(); // Auto stillhalten

  while (1) {
    printf("Bereit: Button druecken\n");
    hbtn.waitBtnRelease();
    hbtn.wait();
    hbtn.waitBtnRelease();
    MyDelay(500);
    hbtn.listen();

    int nah = 0;
    int startL = encL.cnt, startR = encR.cnt;
    while (!hbtn.wasClicked()) {
      float cm = MeasureCm();

      // 2x nah = Wand
      if (cm < WALL_CM) nah++;
      else nah = 0;

      if (nah >= 2) {
        printf("Wand bei %.0f cm -> umdrehen\n", cm);
        TurnAround();
        nah = 0;
        startL = encL.cnt; startR = encR.cnt;
        continue;
      }

      // Geradeaus-Korrektur
      int diff = (encL.cnt - startL) - (encR.cnt - startR);
      float corr = K_SYNC * diff;
      motL.setPow2(POW - corr); motR.setPow2(POW + corr);
    }
    Stop();
    printf("Gestoppt\n");
  }
}
