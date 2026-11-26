## Worum geht es

Die Hauptplatine wird auf **Rev. 2.5** umgestellt: Der Roboter kann jetzt mit **2S-Akku** (wie bisher, 7,4 V nominal / 8,4 V voll) **oder 3S-Akku** (11,1 V nominal / 12,6 V voll) fahren. Die Motoren sind 12-V-Typen, mit 3S ist mehr Reserve da. Umgeschaltet wird auf der Platine mit vier 0-Ω-Brücken. Die Firmware muss erkennen, welcher Akku steckt, und sich danach richten.

**Kurz:** Beim Start Akku messen (> 9,0 V = 3S), Abschaltung bei 3,3 V je Zelle, PWM über die Akkuspannung ausgleichen, beim Bremsen rampen.

## Hardware (Rev. 2.5)

| | |
|---|---|
| Akkumessung | BAT_ADC an **GPIO 3** (ADC1_CH2), Teiler 100 k / 22 k → U_Akku = U_ADC × 122 / 22 |
| ADC-Bereich | 2S: max. 1,51 V am Pin, 3S: max. **2,27 V** → **ADC_ATTEN_DB_12** nötig |
| Messpunkt | hinter dem Hauptschalter (VBAT_SW, TP3). Der ESP läuft nur, wenn die Fahrfreigabe an ist. |
| Motortreiber | TB6612FNG, VM bis **13,5 V** (absolut 15 V) |
| Laden über USB-C | nur 2S (bei 3S ist der Lader abgetrennt) |

| | 2S | 3S |
|---|---:|---:|
| Fahrfreigabe Hardware Start / Aus | 6,42 V / 6,00 V | 9,66 V / 9,03 V |
| Software-Abschaltung (3,3 V/Zelle) | 6,6 V | 9,9 V |
| Voll | 8,4 V | 12,6 V |
| PWM-Faktor bei voll (6,0 V / U_Akku) | 0,71 | 0,48 |

## Was in der Firmware geändert werden muss

1. **ADC auf 12 dB umstellen** und kalibrieren:
   ```cpp
   adc_oneshot_chan_cfg_t cfg = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
   adc_oneshot_config_channel(adc1, ADC_CHANNEL_2, &cfg);   // GPIO 3
   // adc_cali_create_scheme_curve_fitting(...) fuer mV-Werte
   static float readVbat() {             // Mittelwert ueber 32 Messungen
     int sum = 0, mv;
     for (int i = 0; i < 32; i++) { int raw; adc_oneshot_read(adc1, ADC_CHANNEL_2, &raw);
       adc_cali_raw_to_voltage(cali, raw, &mv); sum += mv; }
     return (sum / 32.0f) / 1000.0f * 122.0f / 22.0f;
   }
   ```
2. **Akkutyp beim Start erkennen** (Motoren aus, STBY = 0), danach fest lassen:
   ```cpp
   const float u = readVbat();
   const int cells = (u > 9.0f) ? 3 : 2;
   const float U_CUTOFF = 3.3f * cells;   // 6,6 V bzw. 9,9 V
   ```
3. **Software-Abschaltung** bei gefilterter Spannung < `U_CUTOFF` (z. B. gleitender Mittelwert über 1–2 s, damit kurze Einbrüche beim Anfahren nicht auslösen): PWM auf 0 rampen, STBY = 0, LEDs rot, nicht selbst wieder starten.
4. **PWM-Ausgleich**, damit die Geschwindigkeit nicht vom Ladezustand abhängt:
   ```cpp
   static const float U_REF = 6.0f;      // Bezug: leerer 2S-Akku
   float duty = duty_soll * U_REF / u_filt;
   if (duty > 1.0f) duty = 1.0f;
   ```
   `u_filt` z. B. alle 10 ms messen und über 100 ms mitteln. Optional `U_REF` für 3S höher setzen (z. B. 9,0 V), wenn der Roboter mit 3S schneller fahren soll.
5. **Bremsrampen:** Nicht direkt von vorwärts auf rückwärts schalten. PWM in ≥ 100 ms auf 0 rampen, dann Richtung wechseln. Bremsen bei dieser Platine: U7 erzeugt IN2 immer als invertiertes IN1, IN1 = IN2 = HIGH ist also nicht möglich. **Kurzschlussbremse = PWM LOW bei STBY HIGH** (Richtung egal), **Freilauf = STBY LOW**. Kurzschlussbremse nur bei kleiner Drehzahl. Grund: Bei 3S liegt der TB6612 schon im Ruhezustand bei 12,6 V, Rückspeisung beim harten Bremsen kann über 13,5 V gehen.
6. Details und Pinbelegung: `PCB/Tumbler_Mainboard/Hinweise_Software_Rev2.5.md`.

## Bitte prüfen

- [ ] BAT_ADC mit Multimeter an TP3 vergleichen (2S und 3S), Abweichung < 2 %.
- [ ] Erkennung: 2S-Akku → `cells = 2`, 3S-Akku → `cells = 3`.
- [ ] Abschaltung mit Labornetzteil testen: Spannung langsam unter 6,6 V (2S) bzw. 9,9 V (3S) senken → Motoren stoppen, kein Wiederanlauf.
- [ ] Gleiche Fahrgeschwindigkeit mit vollem und halbvollem Akku (Encoder vergleichen).
- [ ] Mit vollem 3S-Akku hart bremsen und umpolen, VBAT_SW (TP3) mit Oszilloskop messen: Spitzen < 13,5 V.
