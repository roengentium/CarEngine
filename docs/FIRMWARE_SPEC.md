# Firmware requirements (spec only; no firmware written or tested)
Pin map: `firmware/pins.h`.

Power-up sequence
1. Boot with DRV_EN low (drivers stay disabled by the DRV_DIS pull-up). Read OCP_N: if low, stay off.
2. Check VSENSE ~0 V and ISENSE ~0 A; then raise DRV_EN.
3. Soft-start: start at minimum phase shift (low duty), ramp over >= 20 ms while watching ISENSE and VSENSE.
4. Closed loop on VSENSE (target 14.0 V), current limit ~40 A, over-temperature from TSENSE.

PWM
- 100 kHz, each leg 50 % duty complementary; phase-shift between legs sets effective duty (Deff = phase/180 deg).
- Use the ESP32 MCPWM peripheral for complementary outputs, with software dead time at least equal to the hardware RDT dead time.
- SR1/SR2 held LOW for first bring-up (body-diode rectification, low power). Enable synchronous rectification only after the primary waveforms are verified.

Faults (latch off, require explicit re-arm)
- OCP_N low, Vout > 15.5 V, Vout < 10 V after soft-start, ISENSE > limit, temperature > 100 C, loss of the 3.3 V rail.
- Hardware already forces DRV_DIS high on OCP; firmware must still latch and report.

Programming note: powering the ESP32 module from USB while U5 also feeds its 3V3 pin can back-feed; program with the converter unpowered or remove U5 power (J2 off).
