// idf.py -p COM6 flash monitor
#include "RTEnvHL.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TmbMenues.h"

const float SPEED_L = 80;  // aussen ticks
const float SPEED_R = 20;  // innen ticks

const float FF = 0.3 / 58; // 0.3 -> 58 Ticks/s
const float K = 0.01;
const float MAX_RUECKSTAND = 10; // gegen Losrasen

// Leistung = Grundleistung + K * Rueckstand
float Leistung(float speed, float& soll, float ist)
{
  soll = soll + speed * 0.01;
  if (soll - ist > MAX_RUECKSTAND)
    soll = ist + MAX_RUECKSTAND;
  return FF * speed + K * (soll - ist); // FF * speed = Grundleistung und K * (soll - ist) = Rueckstandskorrektur
}

extern "C" void app_main(void)
{
  InitRtEnvHL();
  InitMotors();
  InitTmbMenue();

  while (1) {
    motL.setPow2(0); motR.setPow2(0);
    printf("Bereit: Button druecken\n");
    hbtn.waitBtnRelease();
    hbtn.wait();
    hbtn.waitBtnRelease();
    hbtn.listen();

    int startL = encL.cnt, startR = encR.cnt;
    float sollL = 0, sollR = 0;
    while (!hbtn.wasClicked()) {
      MyDelay(10);
      float istL = encL.cnt - startL;
      float istR = encR.cnt - startR;
      motL.setPow2(Leistung(SPEED_L, sollL, istL));
      motR.setPow2(Leistung(SPEED_R, sollR, istR));
    }
    printf("Gestoppt\n");
  }
}
