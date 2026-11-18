// PID-Werte fuer SvVis PID-Fenster (Roboter mit den duennen Raedern):
//   KP = -0.01   KD = -0.0003   Rate = 500
//   negativ wegen Motor-Einstellung in MotorSetup.h
// Vorwaerts fahren: Geschwindigkeit negativ, z.B. quadrat 10 2 -0.4 1000
// Quadrat mit runden Ecken: rundquadrat 10 3 -0.4 1000

#include "RTEnvHL.h"
#include "SvProtocol3.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TTMailBox.h"
SvProtocol3 ua0;
#include "GyroControl.h"

#define CHECK_CANCEL() if( drCmd.doCancel() ) goto StopAll

TTMailBox drCmd;
bool calFlag = false;

void CommandLoop()
{
  int cmd;
  while (1) {
    cmd = ua0.GetCommand();
    if (cmd == 2) { // mot dir test
      motL.setPow2(ua0.ReadF()); motR.setPow2(ua0.ReadF());
      ua0.SvMessage("set pow L/R");
    }
    else if (cmd == 3) {
      ua0.SvMessage("cal start");
      calFlag = true;
      gyro.CalGyro(true);
      calFlag = false;
      integ.Reset();
      ua0.SvMessage("cal finished");
    }
    else if (cmd == 4) {
      integ.Reset();
      rgl.setDemand2(0);
      ua0.SvMessage("reset integ");
    }
    else if (cmd == 5) {
      rgl.on = ua0.ReadI16();
      if (!rgl.on) {
        rgl.forew = 0;
        vTaskDelay(2);
        motL.setPow2(0); motR.setPow2(0);
      }
      ua0.SvMessage2("rgl ", rgl.on);
    }
    else if (cmd == 6) {
      rgl.setDemand(ua0.ReadI16());
      ua0.SvMessage("demand");
    }
    else if (cmd == 7) {
      int val = ua0.ReadI16();
      stdby.Set(val);
      ua0.SvMessage2("stdby", val);
    }
    else if (cmd == 8) {
      rgl.forew = ua0.ReadF();
      ua0.SvMessage("forew");
    }
    else if (cmd == 9) {
      encL.cnt = encR.cnt = 0;
      ua0.SvMessage("Reset Enc");
    }
    else if (cmd == 10) { // IPC msg to DriveTask
      drCmd.send(ua0.ReadI16());
      // DriveTask takes Parameters from SvMessage
      vTaskDelay(5);
    }
    else if (cmd == 11) { // cancel msg to DriveTask
      drCmd.set(-1);
    }
    else if (cmd == 200 || cmd == 201)
      ControlParams(cmd);
  }
}

void Monitor(void* arg)
{
  while (1) {
    vTaskDelay(1); // 100Hz
    if (ua0.acqON) {
      ua0.LockOStream();
      ua0.WriteSvF(1, rgl.getActDemand());
      ua0.WriteSvF(2, integ.gySum);
      ua0.WriteSvI16(3, encL.cnt);
      ua0.WriteSvI16(4, encR.cnt);
      ua0.Flush();
      ua0.UnlockOStream();
    }
  }
}

// x, y, z  0, 1, 2
void RglTask(void* arg)
{
  if (calFlag)
    return;
  mpu.getGyro(); // read I2C
  gyro.CalcFilt(2);
  integ.CalcFilter(0, gyro.getFilt2(2));
  rgl.calcOneStep(integ.gySum);
  if (rgl.on) {
    motL.setPow2(-rgl.out + rgl.forew);
    motR.setPow2(rgl.out + rgl.forew);
  }
}


void StraightAndCurve(float forew, int dist)
{
  ua0.SvPrintf("drive %1.2f %d", forew, dist);
  MyDelay(500);
  while(1) {
    ua0.SvMessage("Straight");
    integ.Reset(); rgl.setDemand2(0); // no ramp
    rgl.on = 1; encL.cnt = 0;
    rgl.forew = forew;
    while (encL.absCnt() < dist) {
      CHECK_CANCEL();
      vTaskDelay(1);
    }
    ua0.SvMessage("Curve");
    integ.Reset(); rgl.setDemand(1800); // with ramp
    while (rgl.getActDemand() < 1800.0) {
      CHECK_CANCEL();
      vTaskDelay(1);
    }
  }
StopAll:
  drCmd.set(0); // encL.cnt = 0;
  rgl.on=0; vTaskDelay(2);
  motL.setPow2(0); motR.setPow2(0);
  integ.Reset(); rgl.setDemand2(0);
}


// eigene Fahrt: 4x gerade + 90 Grad drehen
// rund = true: an den Ecken eine Kurve fahren statt auf der Stelle drehen
void Quadrat(float forew, int dist, bool rund)
{
  ua0.SvPrintf("quadrat %1.2f %d", forew, dist);
  MyDelay(500);
  integ.Reset(); rgl.setDemand2(0);
  rgl.on = 1;
  for (int i = 0; i < 4; i++) {
    encL.cnt = 0;
    rgl.forew = forew;
    while (encL.absCnt() < dist) {
      CHECK_CANCEL();
      vTaskDelay(1);
    }
    if (!rund) rgl.forew = 0;
    rgl.setDemand((i + 1) * 900); // Winkel zaehlt weiter: 90, 180, 270, 360 Grad
    while (integ.gySum < (i + 1) * 900 - 30) {
      CHECK_CANCEL();
      vTaskDelay(1);
    }
  }
  rgl.forew = 0;
  MyDelay(500); // letzte Drehung genau ausregeln
StopAll:
  drCmd.set(0);
  rgl.on=0; vTaskDelay(2);
  motL.setPow2(0); motR.setPow2(0);
  integ.Reset(); rgl.setDemand2(0);
}

void DriveTask(void* arg)
{
  int cmd;
  while (1) {
    cmd = drCmd.recv();
    if (cmd == 1) {
      StraightAndCurve(ua0.ReadF(), ua0.ReadI16());
      ua0.SvMessage("Curve finished!!");
    }
    else if (cmd == 2) {
      float forew = ua0.ReadF(); int dist = ua0.ReadI16();
      Quadrat(forew, dist, false);
      ua0.SvMessage("Quadrat fertig");
    }
    else if (cmd == 3) {
      float forew = ua0.ReadF(); int dist = ua0.ReadI16();
      Quadrat(forew, dist, true);
      ua0.SvMessage("Rundes Quadrat fertig");
    }
  }
}

extern "C" void app_main(void)
{
  printf("GyroControl_1\n");
  InitRtEnvHL(); InitMotors();
  initMPU();
  rgl.KP = -1.0E-2; rgl.KD = -3.0E-4; // negativ, passt zu unseren Motoren
  // InitUart(UART_NUM_0, 500000);
  InitSoftAp("hugo", 5);
  createTask(Monitor, "Monitor", 2048, 10);
  xTaskCreate(DriveTask, "drt", 2048, NULL, 8, &(drCmd.t_recv));
  EspTimSetup(1000, RglTask, 0, false);
  CommandLoop();
}
