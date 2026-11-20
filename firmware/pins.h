// Pin map for the 14 V isolated DC-DC controller (ESP32 DevKitC-style module, U1).
// Matches converter_*/…kicad_sch net labels. Firmware itself is NOT included/tested.
#pragma once
#define PIN_PWM_AH   25   // UCC21520 U2 INA  -> Q1 (leg A high side)
#define PIN_PWM_AL   26   // UCC21520 U2 INB  -> Q2 (leg A low side)
#define PIN_PWM_BH   27   // UCC21520 U3 INA  -> Q3 (leg B high side)
#define PIN_PWM_BL   14   // UCC21520 U3 INB  -> Q4 (leg B low side)
#define PIN_SR1      32   // sync-rectifier 1 (via UCC27524 U4)
#define PIN_SR2      33   // sync-rectifier 2
#define PIN_VSENSE   34   // ADC1, 14 V via 47k/10k divider
#define PIN_ISENSE   35   // ADC1, INA180A1 output
#define PIN_TSENSE   36   // ADC1, 10k NTC divider
#define PIN_OCP_N    39   // input: LOW = hardware over-current tripped
#define PIN_DRV_EN   13   // output: HIGH = request drivers enabled (OCP can still override)
// Scaling
#define VSENSE_DIV   (10.0f/(47.0f+10.0f))     // Vout = Vadc / VSENSE_DIV
#define ISENSE_V_PER_A (0.002f*20.0f)          // 2 mohm shunt x 20 V/V = 0.04 V/A
#define OCP_TRIP_V   (3.3f*10.0f/(8.2f+10.0f)) // ~1.81 V  => ~45 A
// IMPORTANT: UCC21520 dead time is set by RDT (20k => ~200 ns, check datasheet); never tie DT to VCCI.
