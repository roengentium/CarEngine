# Design review of the current files
Based on a read of parts, values, footprints and net labels (not an ERC/DRC run, KiCad was not available).

1. **Voltage mismatch (critical).** 96 V is not the Leaf pack voltage; see LEAF_2022_INTERFACE.md.
2. **U1 is labelled 96V_TO_12V but the part is Murata CRE1S2412SC.** The part code reads as a 24 V-in, 12 V-out low-power isolated module; check the Murata datasheet. It cannot take 96 V, let alone 400 V.
3. **MOSFETs are generic `Q_NMOS_GDS` symbols with no part numbers.** Choose parts per DESIGN_CALC.md (>= 143 V for 96 V; >= 524 V for the Leaf range).
4. **Cirkit Converter uses IRLZ44N (55 V).** Fine for a 9 V simulation, unusable above ~40 V. Its 60CPQ150 rectifier (150 V) is also wrong for a 14 V, 35 A output; use synchronous rectification.
5. **IR2101 half-bridge drivers** are rated 600 V offset, but a 400 V bus with ringing leaves little margin and they have no galvanic isolation. For the HV version use isolated gate drivers.
6. **CarEngine has PHASE_A/B/C and INV_FAULT labels (a 3-phase inverter stage) but no transformer or output filter,** so it is not yet a 96 V to 14 V converter. Decide which you are building: a motor inverter or a DC-DC.
7. **Housekeeping.** Remove the `.history` git folders from the shared copy, the `~*.lck` lock files (already removed from this pack), and rename `carenginefuckyouwin11.kicad_sch` before sharing publicly.
8. **Missing for any HV build:** input fuse, pre-charge, bleed resistor, creepage/clearance rules in the PCB (HV class), current sense, over-voltage/over-temperature cut-off.
