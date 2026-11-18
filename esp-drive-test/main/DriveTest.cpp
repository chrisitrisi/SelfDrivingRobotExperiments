// Fahrtest nach Ticks, Button = Start/Stopp

#include "RTEnvHL.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TmbMenues.h"

const float SPEED = 60; // Ticks/s
const int DIST = 200;
const int TURN = 50;
const int PAUSE_MS = 500;

// Regler: Soll-Position + Vorsteuerung
const float FF = 0.3 / 58; // 0.3 -> 58 Ticks/s
const float K_POS = 0.01;
const float POW_MAX = 0.6;

float Clip(float v, float m)
{
  return v > m ? m : (v < -m ? -m : v);
}

void Stop()
{
  motL.setPow2(0); motR.setPow2(0);
}

void ShowLeds(int aHue)
{
  leds.clear();
  leds.setHueFT(0, 7, aHue);
  leds.refresh();
}

// false = Abbruch
bool Move(const char* aName, int dirL, int dirR, int aTicks)
{
  int startL = encL.cnt, startR = encR.cnt;
  float soll = 0;
  int t = 0;
  while (1) {
    MyDelay(10);
    if (hbtn.wasClicked()) {
      Stop();
      printf("ABBRUCH per Button\n");
      return false;
    }
    soll += SPEED * 0.01;
    if (soll > aTicks) soll = aTicks;
    float istL = dirL * (encL.cnt - startL);
    float istR = dirR * (encR.cnt - startR);
    float ff = (soll < aTicks) ? FF * SPEED : 0;
    motL.setPow2(dirL * Clip(ff + K_POS * (soll - istL), POW_MAX));
    motR.setPow2(dirR * Clip(ff + K_POS * (soll - istR), POW_MAX));
    t += 10;
    if ((soll >= aTicks && istL >= aTicks - 3 && istR >= aTicks - 3) || t > 10000)
      break;
  }
  Stop();
  int l = encL.cnt - startL, r = encR.cnt - startR;
  printf("%s  Ziel %4d  Ist L=%4d R=%4d  %d ms  (%.0f Ticks/s)\n",
         aName, aTicks, l, r, t, 1000.0f * (abs(l) + abs(r)) / 2 / t);
  return true;
}

bool Pause()
{
  for (int t = 0; t < PAUSE_MS; t += 10) {
    MyDelay(10);
    if (hbtn.wasClicked()) return false;
  }
  return true;
}

void RunSequence()
{
  hbtn.listen();
  ShowLeds(H_GREEN2);
  bool ok = Move("vor    ", 1, 1, DIST) && Pause()
         && Move("zurueck", -1, -1, DIST) && Pause()
         && Move("links  ", -1, 1, TURN) && Pause()
         && Move("rechts ", 1, -1, TURN);
  Stop();
  printf("%s\n", ok ? "Fertig" : "Abgebrochen");
}

extern "C" void app_main(void)
{
  printf("DriveTest\n");
  InitRtEnvHL();
  InitMotors();
  Stop();
  InitTmbMenue();
  while (1) {
    ShowLeds(H_BLUE);
    printf("Bereit: Button druecken zum Starten\n");
    hbtn.waitBtnRelease();
    hbtn.wait();
    hbtn.waitBtnRelease();
    MyDelay(500);
    RunSequence();
  }
}
