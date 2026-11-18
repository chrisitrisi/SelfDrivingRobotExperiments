
#include "TmbMenues.h"

ButtonHandler hbtn(2);


void InitTmbMenue()
{
  hbtn.Init();
}


void IRAM_ATTR button_isr(void* arg)
{
  ((ButtonHandler*)arg)->ISRFunction();
}

void ButtonHandler::Init()
{
  GpIoInitInterrupt(_pin, button_isr, this, GPIO_INTR_POSEDGE);
  _sema = xSemaphoreCreateBinary();
}

void ButtonHandler::ISRFunction()
{
  if (check() != 1)
    return;
  if (_waiting ) {
    _waiting = false;
    BaseType_t prioThings = pdFALSE;
    xSemaphoreGiveFromISR(_sema, &prioThings);
    portYIELD_FROM_ISR(prioThings);
  } 
  cnt++;
}

void ButtonHandler::wait()
{
  while (1) {
    _waiting = true;
    xSemaphoreTake(_sema, portMAX_DELAY);
    vTaskDelay(10);
    if (check() == 1)
      return;
  }
}

void ButtonHandler::waitBtnRelease()
{
  while (check())
    vTaskDelay(1);
}



static int mSel = 1;
static int cols[] = { H_YELLOW2, H_YELLOW2, H_RED, H_GREEN2, H_BLUE };

void showLED()
{
  leds.setHueFT(0, 1, cols[mSel]);
  leds.refresh(); 
}

void blinkLED()
{
  for (int i = 1; i <= 5; i++) {
    leds.setHueFT(0, 1, cols[mSel]); leds.refresh();
    MyDelay(100);
    leds.clear();
    MyDelay(100);
  }
}

// one LED per sel
void showLED2()
{
  leds.setHue(mSel-1, H_RED);
  leds.refresh();
}

// one LED per sel
void blinkLED2()
{
  for (int i = 1; i <= 5; i++) {
    leds.setHue(mSel-1, H_BLUE); leds.refresh();
    MyDelay(100);
    leds.clear();
    MyDelay(100);
  }
}


int execMenue()
{
  leds.clear();
  mSel = 1;
  while (1) {
    hbtn.listen();
    showLED(); MyDelay(1200);
    if (hbtn.wasClicked())
      goto SelDone;
    mSel++;
    if (mSel > 4) mSel = 1;
  }
SelDone:
  blinkLED(); leds.clear();
  return mSel;
}


const int CLICK_DELAY = 300;
const int CNT_THRSH = 1;

int execMenueDBL()
{
  leds.clear();
  mSel = 1;
  while (1) {
    showLED();
    hbtn.waitBtnRelease();
    hbtn.cnt=0; hbtn.wait(); hbtn.cnt = 0;
    MyDelay(CLICK_DELAY);
    if (hbtn.cnt >= CNT_THRSH) // 100
      break;
    mSel++;
    if (mSel > 4) mSel = 1;
  }
  leds.clear();
  blinkLED(); leds.clear();
  return mSel;
}

int execMenueDBL2(int maxSel)
{
  if (maxSel > 8) maxSel = 8;
  leds.clear();
  mSel = 1;
  while (1) {
    showLED2();
    hbtn.waitBtnRelease();   
    hbtn.cnt = 0; hbtn.wait(); hbtn.cnt = 0;
    MyDelay(CLICK_DELAY);
    if (hbtn.cnt >= CNT_THRSH) // 100
      break;
    mSel++;
    if (mSel > maxSel) {
      mSel = 1;
      leds.clear();
    }
  }
  leds.clear();
  blinkLED2(); leds.clear();
  return mSel;
}








