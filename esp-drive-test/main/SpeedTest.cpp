// SpeedTest: 30/50/70/95 %, misst Ticks/s, geradeaus geregelt

#include "RTEnvHL.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TmbMenues.h"

const float STUFEN[] = {0.3, 0.5, 0.7, 0.95};
const int ANZAHL = 4;

// Geradeaus-Regler
const float K_GERADE = 0.01;
int startL0, startR0;

// Notstopp
UsDist us(5, 12); // Trig 5, Echo 12
const float STOP_CM = 30;
int usTakt = 0;

// true = Hindernis naeher als STOP_CM
bool HindernisNah()
{
  if (++usTakt < 5) return false; // nur alle 50 ms messen
  usTakt = 0;
  float cm = us.dist / 58.0f;     // Ergebnis der letzten Messung
  us.dist = 0;
  us.startMeas();                 // naechste Messung starten
  if (cm > 0 && cm < STOP_CM) {
    printf("NOTSTOPP bei %.0f cm\n", cm);
    return true;
  }
  return false;
}

// kurz rueckwaerts = Bremse, dann aus
void Bremsen(float leistung)
{
  motL.setPow2(-leistung); motR.setPow2(-leistung);
  MyDelay(150);
  motL.setPow2(0); motR.setPow2(0);
}

// false = Abbruch (Button oder Hindernis)
bool FahreGerade(float leistung, int ms)
{
  for (int t = 0; t < ms; t += 10) {
    // > 0: links voraus
    int unterschied = (encL.cnt - startL0) - (encR.cnt - startR0);
    float korr = K_GERADE * unterschied;
    motL.setPow2(leistung - korr);
    motR.setPow2(leistung + korr);
    MyDelay(10);
    if (hbtn.wasClicked()) return false;
    if (HindernisNah()) {
      Bremsen(leistung);
      return false;
    }
  }
  return true;
}

bool FahreUndMiss(float leistung)
{
  if (!FahreGerade(leistung, 300)) return false; // anfahren

  int startL = encL.cnt, startR = encR.cnt;
  if (!FahreGerade(leistung, 1000)) return false; // messen
  printf("Leistung %3.0f %%:  L = %4d Ticks/s   R = %4d Ticks/s\n",
         leistung * 100, (int)(encL.cnt - startL), (int)(encR.cnt - startR));
  return true;
}

extern "C" void app_main(void)
{
  InitRtEnvHL();
  InitMotors();
  InitTmbMenue();
  us.Init();

  while (1) {
    motL.setPow2(0); motR.setPow2(0);
    printf("Bereit: Button druecken\n");
    hbtn.waitBtnRelease();
    hbtn.wait();
    hbtn.waitBtnRelease();
    hbtn.listen();
    startL0 = encL.cnt; startR0 = encR.cnt;

    for (int i = 0; i < ANZAHL; i++) {
      if (!FahreUndMiss(STUFEN[i])) {
        printf("Abgebrochen\n");
        break;
      }
    }
  }
}
