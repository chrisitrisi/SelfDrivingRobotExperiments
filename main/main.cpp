#include <stdio.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#include "VL53L0X.h"

static const int NUM_SENSORS = 4;
static const gpio_num_t XSHUT_PINS[NUM_SENSORS] = {GPIO_NUM_27, GPIO_NUM_26, GPIO_NUM_25, GPIO_NUM_33};
static const uint8_t ADDRESSES[NUM_SENSORS]     = {0x30, 0x31, 0x32, 0x33};

static const i2c_port_t I2C_PORT = I2C_NUM_0;
static const gpio_num_t I2C_SDA  = GPIO_NUM_21;
static const gpio_num_t I2C_SCL  = GPIO_NUM_22;

static VL53L0X sensors[NUM_SENSORS];
static bool sensorOk[NUM_SENSORS] = {false, false, false, false};

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
  conf.master.clk_speed = 100000;
  ESP_ERROR_CHECK(i2c_param_config(I2C_PORT, &conf));
  ESP_ERROR_CHECK(i2c_driver_install(I2C_PORT, conf.mode, 0, 0, 0));
}

static void setup()
{
  delayMs(1000);
  printf("=== VL53L0X Test ===\n");

  initI2c();

  // alle Sensoren ueber XSHUT in Reset halten
  for (int i = 0; i < NUM_SENSORS; i++) {
    gpio_reset_pin(XSHUT_PINS[i]);
    gpio_set_direction(XSHUT_PINS[i], GPIO_MODE_OUTPUT);
    gpio_set_level(XSHUT_PINS[i], 0);
  }
  delayMs(10);

  // nacheinander aufwecken (Pin floatet -> Pull-up am Sensor), Adresse vergeben
  for (int i = 0; i < NUM_SENSORS; i++) {
    gpio_set_direction(XSHUT_PINS[i], GPIO_MODE_INPUT);
    delayMs(10);
    sensors[i].setPort(I2C_PORT);
    sensors[i].setTimeout(500);
    if (sensors[i].init()) {
      sensors[i].setAddress(ADDRESSES[i]);
      sensors[i].startContinuous();
      sensorOk[i] = true;
      printf("Sensor %d OK (Adresse 0x%02X)\n", i + 1, ADDRESSES[i]);
    } else {
      printf("Sensor %d FEHLER: nicht gefunden (XSHUT an GPIO%d pruefen)\n",
             i + 1, (int)XSHUT_PINS[i]);
    }
  }
  printf("--- Messung startet ---\n");
}

static void loop()
{
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (!sensorOk[i]) {
      printf("S%d: --- ", i + 1);
    } else {
      uint16_t d = sensors[i].readRangeContinuousMillimeters();
      if (sensors[i].timeoutOccurred()) {
        printf("S%d: Timeout ", i + 1);
      } else if (d >= 8190) {
        printf("S%d: nichts erkannt ", i + 1);
      } else {
        printf("S%d: %4u mm ", i + 1, (unsigned)d);
      }
    }
    printf(" | ");
  }
  printf("\n");
  delayMs(100);
}

extern "C" void app_main(void)
{
  setup();
  while (true) {
    loop();
  }
}
