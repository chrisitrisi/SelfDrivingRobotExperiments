// Sensortest: alle Sensoren ausgeben, Motoren aus

#include "RTEnvHL.h"
#include "EspMotor.h"
#include "MotorSetup.h"
#include "TmbMenues.h"
#include "MPU_Esp.h"
#include "driver/i2c.h"

UsDist ds(5, 12);

// Liniensensor: LS1-6 = GPIO 36,39,32,33,34,35, LEDs = GPIO 13/14
const adc_channel_t LS_CH[6] = {ADC_CHANNEL_0, ADC_CHANNEL_3, ADC_CHANNEL_4,
                                ADC_CHANNEL_5, ADC_CHANNEL_6, ADC_CHANNEL_7};
const int LSC1 = 13, LSC2 = 14;
adc_oneshot_unit_handle_t hAdc1;

void InitLineSensor()
{
  GpIoInit((1ULL << LSC1) | (1ULL << LSC2));
  gpio_set_level((gpio_num_t)LSC1, 1);
  gpio_set_level((gpio_num_t)LSC2, 1);

  adc_oneshot_unit_init_cfg_t c1 = {};
  c1.unit_id = ADC_UNIT_1;
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&c1, &hAdc1));
  adc_oneshot_chan_cfg_t cc = {};
  cc.atten = ADC_ATTEN_DB_11;
  cc.bitwidth = ADC_BITWIDTH_DEFAULT;
  for (int i = 0; i < 6; i++)
    ESP_ERROR_CHECK(adc_oneshot_config_channel(hAdc1, LS_CH[i], &cc));
}

int ReadLs(int i)
{
  int v = -1;
  adc_oneshot_read(hAdc1, LS_CH[i], &v);
  return v;
}

void I2cScan()
{
  printf("I2C-Scan (SDA 21, SCL 22):");
  int found = 0;
  for (uint8_t a = 0x08; a < 0x78; a++) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (a << 1) | I2C_MASTER_WRITE, true);
    i2c_master_stop(cmd);
    esp_err_t r = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(20));
    i2c_cmd_link_delete(cmd);
    if (r == ESP_OK) {
      printf(" 0x%02X", a); found++;
    }
  }
  printf(found ? "\n" : " nichts gefunden\n");
}

extern "C" void app_main(void)
{
  printf("SensorTest\n");
  InitRtEnvHL();
  InitMotors();
  motL.setPow2(0); motR.setPow2(0);
  printf("Motoren aus\n"); fflush(stdout);
  ds.Init();
  InitTmbMenue();
  printf("Ultraschall + Button init\n"); fflush(stdout);

  I2cInit();
  printf("I2C init\n"); fflush(stdout);
  I2cScan();
  int who = mpu.testConnection();
  printf("MPU WHO_AM_I = 0x%02X (%s)\n", who, who == 0x68 ? "OK" : "FEHLER");
  mpu.Init();

  InitLineSensor();

  while (1) {
    for (int i = 0; i < 5; i++) {
      ds.dist = 0; ds.startMeas(); MyDelay(50);
    }
    float cm = ds.dist / 58.0f;

    mpu.getAccel(); mpu.getGyro();

    printf("ACC %6d %6d %6d | GYR %6d %6d %6d | US %5.1f cm | ENC L=%d R=%d | BTN %d\n",
           mpu.acc[0], mpu.acc[1], mpu.acc[2],
           mpu.gyro[0], mpu.gyro[1], mpu.gyro[2],
           cm, (int)encL.cnt, (int)encR.cnt, hbtn.check());

    for (int lvl = 1; lvl >= 0; lvl--) {
      gpio_set_level((gpio_num_t)LSC1, lvl);
      gpio_set_level((gpio_num_t)LSC2, lvl);
      MyDelay(5);
      printf("LINIE LSC=%d", lvl);
      for (int i = 0; i < 6; i++)
        printf(" LS%d=%4d", i + 1, ReadLs(i));
      printf("\n");
    }
  }
}
