# Bring-up plan (lowest energy first)
1. Controller + gate drivers on a 12 V bench supply, no power stage: check PWM, dead-time (>=100 ns), shutdown on fault.
2. Power stage at 12-24 V input, current limit 0.5 A, resistive load: check waveforms and transformer saturation.
3. Raise to 60 V (current-limited): confirm 96 V profile ratio (4:1:1) gives ~14 V out; check FET temperature.
4. Only after 1-3 pass and the HV rework (BOM Leaf column, isolation, fuse, bleed) is done: test on a current-limited HV bench supply behind an isolation transformer.
5. Never first-test on a vehicle pack. Use a current-limited supply, insulated tools, and a second person.
Stop conditions: output > 15.5 V, FET > 100 C, any shoot-through, unexpected input current.
