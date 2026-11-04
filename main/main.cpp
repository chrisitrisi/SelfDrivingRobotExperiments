#include <stdio.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_timer.h"

#include "VL53L0X.h"

// Idee: Alle 4 Sensoren messen gleichzeitig und dauernd (Continuous-Modus).
// Die Schleife wartet nie auf einen einzelnen Sensor, sondern fragt reihum:
// "Hast du einen neuen Wert?" Wenn ja, wird er abgeholt, wenn nein, weiter.

static const int NUM_SENSORS = 4;
static const gpio_num_t XSHUT_PINS[NUM_SENSORS] = {GPIO_NUM_27, GPIO_NUM_26, GPIO_NUM_25, GPIO_NUM_33};
static const uint8_t ADDRESSES[NUM_SENSORS]     = {0x30, 0x31, 0x32, 0x33};

static const i2c_port_t I2C_PORT = I2C_NUM_0;
static const gpio_num_t I2C_SDA  = GPIO_NUM_21;
static const gpio_num_t I2C_SCL  = GPIO_NUM_22;
static const uint32_t I2C_SPEED_HZ = 400000;     // Fast Mode statt 100 kHz

static const uint32_t TIMING_BUDGET_US = 20000;  // 20 ms pro Messung (Minimum, Standard waere 33 ms)
static const int64_t  PRINT_EVERY_US   = 500000; // Ausgabe nur 2x pro Sekunde, printf ist langsam

static VL53L0X sensors[NUM_SENSORS];
static bool sensorOk[NUM_SENSORS] = {false, false, false, false};

// Letzter Messwert pro Sensor (in mm, 0xFFFF = noch kein Wert)
static uint16_t lastDistance[NUM_SENSORS] = {0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF};
// Zaehlt neue Werte seit der letzten Ausgabe, um die Messrate anzuzeigen
static uint32_t newValues[NUM_SENSORS] = {0, 0, 0, 0};

static void delayMs(uint32_t ms)
{
  vTaskDelay(pdMS_TO_TICKS(ms));
}

static void initI2c()
{
  i2c_config_t conf = {};
  conf.mode             = I2C_MODE_MASTER;
  conf.sda_io_num       = I2C_SDA;
  conf.scl_io_num       = I2C_SCL;
  conf.sda_pullup_en    = GPIO_PULLUP_ENABLE;
  conf.scl_pullup_en    = GPIO_PULLUP_ENABLE;
  conf.master.clk_speed = I2C_SPEED_HZ;
  ESP_ERROR_CHECK(i2c_param_config(I2C_PORT, &conf));
  ESP_ERROR_CHECK(i2c_driver_install(I2C_PORT, conf.mode, 0, 0, 0));
}

// true, wenn der Sensor eine fertige Messung hat. Wartet nicht.
static bool dataReady(VL53L0X &s)
{
  return (s.readReg(VL53L0X::RESULT_INTERRUPT_STATUS) & 0x07) != 0;
}

static void setup()
{
  delayMs(1000);
  printf("=== VL53L0X: 4 Sensoren gleichzeitig ===\n");

  initI2c();

  // 1. Alle Sensoren ueber XSHUT in Reset halten
  for (int i = 0; i < NUM_SENSORS; i++) {
    gpio_reset_pin(XSHUT_PINS[i]);
    gpio_set_direction(XSHUT_PINS[i], GPIO_MODE_OUTPUT);
    gpio_set_level(XSHUT_PINS[i], 0);
  }
  delayMs(10);

  // 2. Nacheinander aufwecken (Pin floatet -> Pull-up am Sensor),
  //    Adresse vergeben und Messzeit einstellen
  for (int i = 0; i < NUM_SENSORS; i++) {
    gpio_set_direction(XSHUT_PINS[i], GPIO_MODE_INPUT);
    delayMs(10);
    sensors[i].setPort(I2C_PORT);
    sensors[i].setTimeout(500);
    if (sensors[i].init()) {
      sensors[i].setAddress(ADDRESSES[i]);
      sensors[i].setMeasurementTimingBudget(TIMING_BUDGET_US);
      sensorOk[i] = true;
      printf("Sensor %d OK (Adresse 0x%02X)\n", i + 1, ADDRESSES[i]);
    } else {
      printf("Sensor %d FEHLER: nicht gefunden (XSHUT an GPIO%d pruefen)\n",
             i + 1, (int)XSHUT_PINS[i]);
    }
  }

  // 3. Erst jetzt alle zusammen starten. Ab hier misst jeder Sensor
  //    von allein immer weiter, ohne dass wir warten muessen.
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (sensorOk[i]) {
      sensors[i].startContinuous();
    }
  }
  printf("--- Messung startet (Timing Budget %lu us, I2C %lu kHz) ---\n",
         (unsigned long)TIMING_BUDGET_US, (unsigned long)(I2C_SPEED_HZ / 1000));
}

// Reihum abholen, was fertig ist. Kein Warten auf einen einzelnen Sensor.
static void pollSensors()
{
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (sensorOk[i] && dataReady(sensors[i])) {
      // Wert ist schon fertig, darum kehrt diese Funktion sofort zurueck
      lastDistance[i] = sensors[i].readRangeContinuousMillimeters();
      newValues[i]++;
    }
  }
}

static void printValues(int64_t elapsedUs)
{
  for (int i = 0; i < NUM_SENSORS; i++) {
    // Messungen pro Sekunde seit der letzten Ausgabe
    unsigned rate = (unsigned)((newValues[i] * 1000000LL) / elapsedUs);
    newValues[i] = 0;

    if (!sensorOk[i]) {
      printf("S%d: ---            ", i + 1);
    } else if (lastDistance[i] == 0xFFFF) {
      printf("S%d: noch kein Wert ", i + 1);
    } else if (lastDistance[i] >= 8190) {
      printf("S%d: frei   %3u/s  ", i + 1, rate);
    } else {
      printf("S%d: %4u mm %3u/s ", i + 1, (unsigned)lastDistance[i], rate);
    }
    printf("| ");
  }
  printf("\n");
}

extern "C" void app_main(void)
{
  setup();

  int64_t lastPrint = esp_timer_get_time();
  while (true) {
    pollSensors();

    // Hier spaeter: lastDistance[] an die Fahrlogik geben

    int64_t now = esp_timer_get_time();
    if (now - lastPrint >= PRINT_EVERY_US) {
      printValues(now - lastPrint);
      lastPrint = now;
    }

    // Kurz Pause, damit andere Tasks (und der Watchdog) Zeit bekommen.
    // 1 Tick = 1 ms, wenn CONFIG_FREERTOS_HZ=1000 ist (siehe sdkconfig).
    vTaskDelay(1);
  }
}
