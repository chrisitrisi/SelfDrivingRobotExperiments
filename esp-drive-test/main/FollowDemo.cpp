
// FollowDemo: Roboter folgt der Hand mit dem Ultraschall-Sensor (PI-Regler, Soll 10 cm)
// Laeuft ohne PC: Button (GPIO 2) schaltet Folgen ein/aus
//   LEDs: gruen = folgt, 1x blau = bereit
// SvVis (optional, per USB): Kanaele 1 encL, 2 encR, 3 abst [cm], 4 pow, 5 followOn
//   Cmd 2 L R: Leistung setzen (schaltet Folgen aus), 3: Encoder reset
//   Cmd 4: Folgen ein, 5: Folgen aus + stop, 50: Reset uC

#include "RTEnvHL.h"
#include "SvProtocol3.h"
#include "EspMotor.h"
#include "ControlBasics.h"
#include "MotorSetup.h"
#include "TmbMenues.h"

SvProtocol3 ua0;
// trg echo
UsDist ds(5, 12);

// Reglerparameter (am 15.10. mit PC-Skript am Roboter getestet)
const float SOLL_CM = 10.0;
const float KP = 0.025;     // Leistung pro cm Fehler
const float KI = 0.02;      // Leistung pro cm*s
const float I_MAX = 0.15;   // Anti-Windup
const float MIN_POW = 0.18; // darunter faehrt er aus dem Stand nicht los
const float MAX_POW = 0.35;
const float TOTZONE = 2.0;  // cm um den Sollwert: stehen bleiben
const float LOST_CM = 60.0; // weiter weg = Hand verloren -> stehen

// HC-SR04 nur alle 5 Ticks (50ms = 20Hz) ausloesen, sonst stoeren alte Echos
const int US_TICKS = 5;
const float DT = US_TICKS * 0.01;

volatile bool followOn = false;
volatile float manL = 0, manR = 0; // Leistung im manuellen Betrieb
float abstCm = 0, powOut = 0;

class FollowCtrl {
public:
  void Reset()
  {
    integ = 0;
  }
  float Calc(float aDist);
private:
  float integ = 0;
};

float FollowCtrl::Calc(float aDist)
{
  float err = aDist - SOLL_CM; // >0: zu weit weg -> vor
  if (aDist > LOST_CM) {
    integ = 0; return 0;
  }
  if (fabsf(err) < TOTZONE) {
    integ *= 0.8f; return 0;
  }
  if ((err > 0) != (integ > 0))
    integ = 0; // nicht in die falsche Richtung nachschieben
  integ = ClipHL(integ + KI * err * DT, I_MAX);
  float p = KP * err + integ;
  if (fabsf(p) < MIN_POW)
    p = (p > 0) ? MIN_POW : -MIN_POW;
  return ClipHL(p, MAX_POW);
}

float Median3(float a, float b, float c)
{
  if (a > b) { float t = a; a = b; b = t; }
  if (b > c) b = c;
  return (a > b) ? a : b;
}

void SetFollow(bool aOn)
{
  manL = 0; manR = 0;
  followOn = aOn;
}

void ShowState(bool aOn)
{
  leds.clear();
  if (aOn)
    leds.setHueFT(0, 7, H_GREEN2);
  else
    leds.setHue(0, H_BLUE);
  leds.refresh();
}

// einziger Task, der Motoren und LEDs ansteuert
void ControlTask(void* arg)
{
  FollowCtrl ctrl;
  float hist[3] = { 999, 999, 999 };
  int tick = 0, hi = 0;
  float followPow = 0;
  bool shownOn = false;
  ShowState(false);
  while (1) {
    vTaskDelay(1); // 10ms
    if (++tick >= US_TICKS) {
      tick = 0;
      // Echo der letzten Messung ist nach max. ~38ms fertig
      hist[hi] = (ds.dist > 0) ? ds.dist / 58.0f : 999.0f;
      hi = (hi + 1) % 3;
      ds.dist = 0; // kein Echo -> bleibt 0 -> "verloren"
      ds.startMeas();
      abstCm = Median3(hist[0], hist[1], hist[2]);

      if (followOn)
        followPow = ctrl.Calc(abstCm);
      else {
        followPow = 0; ctrl.Reset();
      }

      if (ua0.acqON) {
        ua0.WriteSvI16(1, encL.cnt);
        ua0.WriteSvI16(2, encR.cnt);
        ua0.WriteSvF(3, (abstCm > 100) ? 100 : abstCm);
        ua0.WriteSvF(4, powOut);
        ua0.WriteSvI16(5, followOn);
        ua0.Flush();
      }
    }

    if (followOn) {
      powOut = followPow;
      motL.setPow2(followPow); motR.setPow2(followPow);
    }
    else {
      powOut = manL;
      motL.setPow2(manL); motR.setPow2(manR);
    }

    if (followOn != shownOn) {
      shownOn = followOn;
      ShowState(shownOn);
    }
  }
}

void ButtonTask(void* arg)
{
  while (1) {
    hbtn.waitBtnRelease();
    hbtn.wait();
    SetFollow(!followOn);
  }
}

void CommandLoop()
{
  int cmd;
  while (1) {
    cmd = ua0.GetCommand();
    if (cmd == 2) {
      float l = ua0.ReadF(); float r = ua0.ReadF();
      SetFollow(false);
      manL = l; manR = r;
      ua0.SvMessage("Set Pow");
    }
    else if (cmd == 3) {
      encL.cnt = encR.cnt = 0;
      ua0.SvMessage("reset enc");
    }
    else if (cmd == 4) {
      SetFollow(true);
      ua0.SvMessage("Follow ON");
    }
    else if (cmd == 5) {
      SetFollow(false);
      ua0.SvMessage("Follow OFF");
    }
    else if (cmd == 50) {
      esp_restart();
    }
  }
}

extern "C" void app_main(void)
{
  printf("FollowDemo\n");
  InitRtEnvHL();
  InitMotors(); ds.Init();
  InitTmbMenue();
  InitUart(UART_NUM_0, 500000);
  xTaskCreate(ControlTask, "Control", 3072, NULL, 10, NULL);
  xTaskCreate(ButtonTask, "Button", 2048, NULL, 5, NULL);
  CommandLoop();
}
